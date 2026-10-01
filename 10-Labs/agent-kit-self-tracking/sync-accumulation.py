#!/usr/bin/env python3
"""
sync-accumulation.py — measure ACCUMULATION in the Obsidian Sync state table, locally.

WHY (2026-09-28): the provider's `size` op would answer "how much does this account hold", but it is
UNREACHABLE — one line in the client, ZERO callers, no CLI command, no module exports, and the op
travels on a WebSocket needing an HKDF keyhash handshake (characterized, not exercised). The question
it would answer is whether a limit is charged on ACCUMULATION rather than on the live present. This
measures the accumulation the LOCAL table can see, without touching the wire.

THE MECHANISM: `uid` is assigned per server-side write and shares its counter with `meta.version`
(measured: both 6217, max uid == version). So:
    max_uid - live_rows  =  write slots NOT represented by a live row
which is an accumulation trace. It is NOT the provider's retention number, and the limits are named
in the output rather than hidden.

READ-ONLY. Opens state.db with mode=ro. Never writes, never syncs, never prints a secret.

EXIT CODES
  0 = measured
  2 = could not measure (state.db unreadable/missing) — never a pass

Usage: sync-accumulation.py [--db PATH] [--json]
"""
import argparse
import datetime
import json
import os
import sqlite3
import sys

DEFAULT_DB = ("/root/.config/obsidian-headless/sync/"
              "e2c92dacc2d71cc70e7e8d315741b4cb/state.db")


def measure(path):
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    meta = dict(c.execute("select key,value from meta"))
    uids, rows, total = [], 0, 0
    for (d,) in c.execute("select data from server_files"):
        rows += 1
        try:
            j = json.loads(d)
        except Exception:
            continue
        total += j.get("size") or 0
        if "uid" in j:
            uids.append(j["uid"])
    deletions = 0
    for (d,) in c.execute("select data from server_files"):
        try:
            if json.loads(d).get("deleted"):
                deletions += 1
        except Exception:
            pass
    high = max(uids) if uids else 0
    return {
        "read_time_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": int(meta.get("version", 0)),
        "max_uid": high,
        "live_rows": len(uids),
        "total_rows": rows,
        "accumulated_slots": high - len(uids),
        "live_deletion_records": deletions,
        "distinct_uids": len(set(uids)),
        "payload_bytes": total,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.db):
        print(f"❌ state.db not readable: {a.db}", file=sys.stderr)
        return 2
    try:
        r = measure(a.db)
    except (sqlite3.Error, ValueError) as e:
        print(f"❌ could not read the state table: {e}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(r, indent=2))
        return 0

    hw = r["max_uid"] or 1
    print(f"  READ TIME (UTC) : {r['read_time_utc']}   <- a live table; the writer does not stop")
    print(f"  version counter : {r['version']}")
    print(f"  max uid         : {r['max_uid']}")
    print(f"  live rows       : {r['live_rows']}")
    print(f"  ACCUMULATED SLOTS: {r['accumulated_slots']}   ({100.0*r['accumulated_slots']/hw:.2f}% of the high-water mark)")
    print(f"  live deletion records: {r['live_deletion_records']}   <- tombstones the table still carries")
    print(f"  distinct uids == live rows: {r['distinct_uids'] == r['live_rows']}"
          f"   (True = NO version-history rows locally)")
    print(f"  payload         : {r['payload_bytes']:,} bytes = {r['payload_bytes']/1048576:.2f} MiB")
    print()
    print("  WHAT THIS IS   : slots the server's write counter has consumed that no live row represents.")
    print("  WHAT IT IS NOT : a byte count. A removed 3.8 MiB file and a removed 200-byte stub are one")
    print("                   slot each, so this cannot give the provider's retention size. Renames are")
    print("                   a remove plus an add, so it is an UPPER BOUND on true deletions.")
    print("  THE PROVIDER'S OWN USAGE REPORT IS STILL THE ONLY AUTHORITATIVE MEASUREMENT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
