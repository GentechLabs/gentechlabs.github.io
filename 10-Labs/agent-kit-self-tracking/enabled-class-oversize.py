#!/usr/bin/env python3
"""
enabled-class-oversize.py — FAIL-CLOSED check for the ONE Obsidian Sync failure mode that
reports success: a file whose type is ENABLED but whose size exceeds the SERVER's per-file cap
(the client's default is 199 MiB; the server may set lower) is skipped while `ob sync` still
reports "Fully synced". NOTE: the skip is LOGGED via logSkip() per path, deduped — it is not
silent at the log level, and this vault's log has never recorded one.

WHY THIS EXISTS (2026-09-28):
  `allowTypes` was widened from ['image','pdf'] to ['image','pdf','audio','video'] while the
  server-side cap was unmeasured locally. Widening the enabled classes widens the surface
  that no local instrument can see (measured: this vault's sync.log has 0 size fields). The client gives NO signal either way, so the only way to
  make this class fail-closed is to count it ourselves.

THE UNIT MATTERS (tonight's lesson, applied here):
  - The check measures ENABLED-class files OUTSIDE the exclusion set. A file inside an
    excluded tree is not a finding (it is excluded on purpose).
  - A file whose type is NOT enabled is not a finding (it never synced and never was meant to).
  - Exclusion is matched the way the CLIENT matches it: ignoreFolders entries are PATH
    prefixes for nested entries, and TOP-LEVEL names for bare entries. A bare name does NOT
    exclude a nested folder of the same name — that was the original 553MB bug.

EXIT CODES:
  0 = no enabled-class file outside the exclusions exceeds the cap  (safe)
  1 = at least one does  (SILENT NON-SYNC — this is the alarm)
  2 = could not measure (config or vault unreadable) — NOT a pass

USAGE:
  python3 scripts/enabled-class-oversize.py [--vault DIR] [--config FILE] [--json]
"""
import argparse
import json
import os
import sys

# CAP_BYTES — CORRECTED 2026-09-28 by gentech (HQ), announced in
# 01-HANDOFFS/gentech-to-gentech-treasury/2026-09-28-your-drift-finding-is-inverted-and-your-tool-rests-on-my-withdrawn-cap.md
# The 5 MiB figure was NEVER a client constant. Measured at source in
# /usr/local/node/lib/node_modules/obsidian-headless/cli.js:
#   the only numeric token in that range is 52428800 = 50 MiB ("File exceeds 50MB upload limit")
#   5242880 (5 MiB) has ZERO standalone occurrences — it is a SUBSTRING of 52428800
#   the real per-file limit is perFileMax = 199*1024*1024, SET BY THE SERVER at login
# So this is used as a CONSERVATIVE pre-filter, not a measured client limit. A file over it
# is a candidate to investigate; the authoritative threshold is server-supplied and unreachable
# from any local instrument (this vault's sync.log carries 0 size fields, ever).
CAP_BYTES = 5 * 1024 * 1024          # CONSERVATIVE PRE-FILTER — NOT a client constant (was a myth)
DEFAULT_VAULT = "/root/vaults/gentech"
SYNC_ID = "e2c92dacc2d71cc70e7e8d315741b4cb"
DEFAULT_CONFIG = f"/root/.config/obsidian-headless/sync/{SYNC_ID}/config.json"

# extension sets per Obsidian's type buckets (the buckets `allowTypes` names)
TYPE_EXT = {
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".avif", ".ico", ".tiff"},
    "pdf":   {".pdf"},
    "audio": {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".aiff"},
    "video": {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v", ".wmv", ".flv", ".mpg", ".mpeg"},
    "other": {".md", ".txt", ".json", ".canvas", ".html", ".css", ".js", ".py", ".csv", ".yml", ".yaml"},
}


def load_config(path):
    with open(path) as fh:
        return json.load(fh)


def enabled_extensions(cfg):
    allow = cfg.get("allowTypes") or []
    exts = set()
    for t in allow:
        exts |= TYPE_EXT.get(t, set())
    return allow, exts


def is_excluded(rel, ignore_folders):
    """Mirror the client's matching rule.

    A nested entry ('a/b') excludes by PATH PREFIX. A bare entry ('music') excludes only a
    TOP-LEVEL directory — it does NOT exclude 'a/music'. Getting this wrong is what let
    node_modules be pushed; getting it wrong in the other direction would hide a real finding.
    """
    parts = rel.split("/")
    top = parts[0] if parts else ""
    for entry in ignore_folders:
        if not entry:
            continue
        e = entry.strip().rstrip("/")
        if not e:
            continue
        if "*" in e or e.startswith("!"):
            continue                      # glob/negation forms are out of scope; say so, don't guess
        if "/" in e:
            if rel == e or rel.startswith(e + "/"):
                return True
        else:
            if top == e:                  # bare name == top-level only
                return True
    return False


def scan(vault, cfg):
    allow, exts = enabled_extensions(cfg)
    ignore = cfg.get("ignoreFolders") or []
    oversize, measured = [], 0
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext not in exts:
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, vault)
            if is_excluded(rel, ignore):
                continue
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            measured += 1
            if size > CAP_BYTES:
                oversize.append({"path": rel, "bytes": size,
                                 "mb": round(size / 1048576, 2),
                                 "ext": ext})
    oversize.sort(key=lambda r: -r["bytes"])
    return {"allowTypes": allow, "ignore_entries": len(ignore),
            "measured": measured, "oversize": oversize, "cap_mb": 5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    # fail CLOSED: an unreadable input is exit 2, never a pass
    if not os.path.isdir(a.vault):
        print(f"❌ vault not readable: {a.vault}", file=sys.stderr)
        return 2
    if not os.path.isfile(a.config):
        print(f"❌ sync config not readable: {a.config}", file=sys.stderr)
        return 2
    try:
        cfg = load_config(a.config)
    except (OSError, ValueError) as e:
        print(f"❌ sync config unparseable: {e}", file=sys.stderr)
        return 2

    r = scan(a.vault, cfg)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        st = os.stat(a.config)
        import datetime
        mt = datetime.datetime.utcfromtimestamp(st.st_mtime).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"  config      : {a.config}")
        print(f"  config READ : {mt}  ({st.st_size} bytes)   <- the exclusion set carries a TIME")
        print(f"  allowTypes  : {r['allowTypes']}")
        print(f"  ignored     : {r['ignore_entries']} entries")
        print(f"  measured    : {r['measured']} enabled-class file(s) OUTSIDE the exclusions")
        print(f"  threshold   : {r['cap_mb']} MB per file — a CONSERVATIVE PRE-FILTER, not a client constant")
        print("                the client's own default is perFileMax = 199 MiB, set by the SERVER at login;")
        print("                the authoritative value is unreachable locally (this vault's sync.log")
        print("                carries 0 size fields). A skip IS logged per path (logSkip), never silent.")
        print("                nothing over this line means nothing to investigate — NOT 'under the real cap'.")
        if r["oversize"]:
            print(f"\n  🔴 {len(r['oversize'])} file(s) OVER THE PRE-FILTER — investigate before trusting them to sync:")
            for o in r["oversize"]:
                print(f"      {o['mb']:8.2f} MB  {o['path']}")
        else:
            print("\n  ✅ none over the cap — the enabled-class surface is inside the limit")
    return 1 if r["oversize"] else 0


if __name__ == "__main__":
    sys.exit(main())
