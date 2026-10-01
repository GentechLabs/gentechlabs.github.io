#!/usr/bin/env python3
"""Sync health from the size column — the corrected version of HQ's one-line check.

THE IDEA (HQ's, and it is sound): every synced file shows a CONSTANT +28-byte offset between the
server's size field and the local file, because the server column is the CIPHERTEXT size (a nonce
and a tag) and disk is plaintext. So a file whose delta is NOT the expected offset is a file whose
two copies have diverged — a size comparison is a sync-health check.

AS PROPOSED IT WOULD HAVE FIRED FOREVER ON FOUR FILES, and reported 15 problems where there are 10.
Three corrections, each measured:

 1. ZERO-BYTE FILES HAVE NO OVERHEAD. An empty file has no payload and therefore no nonce or tag, so
    its expected delta is 0, not 28. Comparing it to 28 flags a perfectly synced empty file as a
    fault.
 2. THE UNSUPPORTED CLASS CAN NEVER SYNC, SO ITS DIVERGENCE IS EXPECTED. `allowTypes` carries
    image/pdf/audio/video plus notes; `.json` is not in it. Measured: 0 `.json` transfers in the
    sync log against 3,412 `.md` Push/Upload lines, and the four `.obsidian/*.json` server copies are
    one-time snapshots. They diverge freely and always will — flagging them reports the same files
    every run for the life of the vault, which is how a real finding gets skimmed past.
 3. THE SIGN IS THE FINDING. delta < expected means the LOCAL copy is ahead (an edit pending
    upload); delta > expected means the SERVER copy is larger (the remote is newer than this
    checkout). Reporting both as "unsynced" cannot tell a pending upload from a stale tree.

Reports; never writes. Exit 2 when it cannot measure.
"""
import argparse
import json
import os
import sqlite3
import sys
import time

DEFAULT_VAULT = "/root/vaults/gentech"
SYNC_ID = "e2c92dacc2d71cc70e7e8d315741b4cb"
SYNC_DIR = f"/root/.config/obsidian-headless/sync/{SYNC_ID}"
CIPHER_OVERHEAD = 28      # measured: server - disk for 3,349 of 3,364 files
FRESH_WINDOW_S = 900      # an edit this recent with no upload yet is a pending sync, not a fault


def expected_delta(disk_size):
    """0 bytes of payload -> no nonce, no tag. Only a non-empty file carries the 28."""
    return 0 if disk_size == 0 else CIPHER_OVERHEAD


def load_classes(config_path):
    """Extension classes the transport actually carries, as a set of lowercase extensions.

    Notes are always carried; `allowTypes` adds binary classes. A file whose extension is neither is
    in the `unsupported` class and CANNOT sync — excluded from the health verdict by design, with
    the count printed so the exclusion is visible rather than silent.
    """
    try:
        cfg = json.load(open(config_path))
    except (OSError, ValueError) as e:
        raise RuntimeError(f"cannot read sync config {config_path}: {e}")
    types = cfg.get("allowTypes") or []
    ext_map = {"image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"},
               "pdf": {".pdf"},
               "audio": {".mp3", ".wav", ".m4a", ".flac", ".ogg"},
               "video": {".mp4", ".mov", ".webm", ".mkv"}}
    exts = {".md", ".markdown"}
    for t in types:
        exts |= ext_map.get(t, set())
    return exts


def measure(vault, db_path, config_path):
    if not os.path.isdir(vault):
        raise RuntimeError(f"vault not readable: {vault}")
    if not os.path.isfile(db_path):
        raise RuntimeError(f"state db not readable: {db_path}")
    carried = load_classes(config_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    checked = unsupported = missing = 0
    pending_up, server_ahead, anomalies = [], [], []

    for path, data in conn.execute("select path,data from server_files"):
        try:
            rec = json.loads(data)
        except ValueError:
            continue
        if rec.get("folder") or rec.get("deleted") or rec.get("size") is None:
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext not in carried:
            unsupported += 1
            continue
        local = os.path.join(vault, path)
        if not os.path.isfile(local):
            missing += 1
            continue
        checked += 1
        dsz = os.path.getsize(local)
        exp = expected_delta(dsz)
        delta = rec["size"] - dsz
        if delta == exp:
            continue
        age = time.time() - os.path.getmtime(local)
        row = {"path": path, "delta": delta, "expected": exp,
               "disk_size": dsz, "server_size": rec["size"], "age_s": int(age)}
        if delta < exp:
            # local ahead. A RECENT edit with no upload is a healthy pending sync; an OLD one is a
            # genuine stall and only the age separates them — the offset alone cannot.
            if age > FRESH_WINDOW_S:
                anomalies.append(row)
            else:
                pending_up.append(row)
        else:
            server_ahead.append(row)
    return {"checked": checked, "unsupported": unsupported, "missing": missing,
            "pending_upload": pending_up, "server_ahead": server_ahead, "anomalies": anomalies,
            "overhead": CIPHER_OVERHEAD}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--db", default=f"{SYNC_DIR}/state.db")
    ap.add_argument("--config", default=f"{SYNC_DIR}/config.json")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        r = measure(a.vault, a.db, a.config)
    except RuntimeError as e:
        print(f"❌ cannot measure: {e}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(r, indent=2))
        return 1 if (r["anomalies"] or r["server_ahead"]) else 0

    print(f"  compared      : {r['checked']} synced file(s) present on both sides")
    print(f"  overhead      : +{r['overhead']} B (ciphertext) expected, 0 B for an empty file")
    print(f"  excluded      : {r['unsupported']} file(s) in the UNSUPPORTED class — cannot sync,")
    print(f"                  so their divergence is EXPECTED, not a fault (not a silent skip)")
    if r["missing"]:
        print(f"  on server only: {r['missing']} (no local copy to compare)")
    if r["pending_upload"]:
        print(f"\n  ⏳ {len(r['pending_upload'])} edit(s) pending upload (local ahead, fresh):")
        for x in sorted(r["pending_upload"], key=lambda y: y["age_s"])[:10]:
            print(f"        delta {x['delta']:+7d}  {x['age_s']:5d}s ago  {x['path'][:64]}")
    if r["server_ahead"]:
        print(f"\n  🔴 {len(r['server_ahead'])} file(s) where the SERVER copy is LARGER — the remote")
        print("     is newer than this checkout (a pending download, or a stale tree):")
        for x in r["server_ahead"]:
            print(f"        delta {x['delta']:+7d}  {x['path'][:64]}")
    if r["anomalies"]:
        print(f"\n  🔴 {len(r['anomalies'])} STALLED local-ahead file(s) (older than "
              f"{FRESH_WINDOW_S}s with no upload) — a real sync fault:")
        for x in r["anomalies"]:
            print(f"        delta {x['delta']:+7d}  age {x['age_s']:6d}s  {x['path'][:60]}")
    if not (r["anomalies"] or r["server_ahead"]):
        # The sentence must not claim more than was measured. With pending uploads present, "every
        # file matches its expected offset" is FALSE — 10 of them do not, they are simply fresh.
        if r["pending_upload"]:
            print(f"\n  ✅ no STALLED or server-ahead faults — "
                  f"{len(r['pending_upload'])} fresh edit(s) pending upload, which is normal")
        else:
            print("\n  ✅ no sync faults — every carried file matches its expected offset")
    return 1 if (r["anomalies"] or r["server_ahead"]) else 0


if __name__ == "__main__":
    sys.exit(main())
