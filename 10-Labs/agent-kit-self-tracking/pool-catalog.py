#!/usr/bin/env python3
"""pool-catalog.py — bookmark the pools we care about, and record WHY.

Jordan (2026-09-18):
  "A way to bookmark favorites or catolog the ones you use"

The ranking job answers "what earns most in fees right now". That is a different question
from "what have we actually decided about this venue". Without a catalog, every review we do
gets re-done from scratch and every rejection gets re-litigated — and a venue we REJECTED for
good reason can quietly reappear at the top of a ranking and look attractive again.

So this holds the decisions, with the reason attached.

STATUS
  ACTIVE    we are in it, or it is the designated venue for the next entry
  WATCH     reviewed, plausible, not yet used — evidence incomplete
  RETIRED   used before, out of it now
  AVOID     reviewed and rejected, WITH the reason. Re-check before ignoring.

Usage
  python3 pool-catalog.py list
  python3 pool-catalog.py add --venue "LFJ (Joe v2.2)" --pair WAVAX-USDC \
      --status WATCH --note "highest measured fee generation; no emissions in the APY"
  python3 pool-catalog.py set --id lfj-joe-v22-wavax-usdc --status ACTIVE
  python3 pool-catalog.py show --id <id>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "pool-catalog.json")

STATUS_ORDER = {"ACTIVE": 0, "WATCH": 1, "RETIRED": 2, "AVOID": 3}
STATUS_ICON = {"ACTIVE": "🟢", "WATCH": "👁️", "RETIRED": "⚪", "AVOID": "🚫"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slug(venue: str, pair: str) -> str:
    s = f"{venue}-{pair}".lower()
    return "".join(c if (c.isalnum() or c == "-") else "-" for c in s).replace("--", "-").strip("-")


def load() -> dict:
    if not os.path.exists(CATALOG):
        return {"entries": []}
    try:
        with open(CATALOG) as f:
            return json.load(f)
    except Exception as e:                                            # noqa: BLE001
        print(f"⚠️ catalog unreadable ({type(e).__name__}) — refusing to overwrite it blindly")
        sys.exit(1)


def save(d: dict) -> None:
    with open(CATALOG, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")


def cmd_list(_a) -> int:
    d = load()
    ents = sorted(d.get("entries", []),
                  key=lambda e: (STATUS_ORDER.get(e.get("status"), 9), e.get("venue", "")))
    if not ents:
        print("catalog is empty — add one with `add`")
        return 0
    print("=" * 100)
    print(f"  POOL CATALOG — {len(ents)} entries ({_now()})")
    print("=" * 100)
    cur = None
    for e in ents:
        st = e.get("status", "WATCH")
        if st != cur:
            cur = st
            print(f"\n  ── {STATUS_ICON.get(st, '·')} {st} " + "─" * 60)
        fee = e.get("measured_fee_apr_pct")
        # A measured fee must carry its AGE. "fee 47.0%" printed bare reads exactly like a live
        # number; the catalog's own entry was measured 2026-09-17 and was still being reprinted
        # as current. Same failure the ranker had — a number without a date is not evidence.
        #
        # IT MUST ALSO CARRY ITS SOURCE, or the field name lies. `measured_fee_apr_pct` is the
        # only slot, so an AGGREGATOR-reported number stored here printed identically to one we
        # decoded off the chain — the same false-value shape the ranker has a whole src column
        # for. Entries predating this field render exactly as before (no behaviour change);
        # fee_src is opt-in, so it can never silently relabel an existing number.
        if fee is not None:
            asof = e.get("measured_at") or e.get("last_reviewed") or e.get("added")
            src = e.get("fee_src")
            feestr = (f"  fee {fee}%  [{src}]" if src else f"  fee {fee}%") \
                     + (f" (as of {asof})" if asof else " (undated)")
        else:
            feestr = ""
        print(f"  {e.get('venue',''):<20} {e.get('pair',''):<16} {e.get('chain',''):<10}{feestr}")
        if e.get("note"):
            for i in range(0, len(e["note"]), 88):
                print(f"      {e['note'][i:i+88]}")
        print(f"      id={e.get('id')}  added {e.get('added','')}"
              + (f"  last_reviewed {e['last_reviewed']}" if e.get("last_reviewed") else ""))
    print("\n" + "=" * 100)
    print("  ACTIVE = in it or next to enter · WATCH = plausible, evidence incomplete")
    print("  RETIRED = used before · AVOID = rejected, reason recorded — re-check before ignoring")
    print("=" * 100)
    return 0


def cmd_show(a) -> int:
    d = load()
    e = next((x for x in d.get("entries", []) if x.get("id") == a.id), None)
    if not e:
        print(f"  no entry with id {a.id}")
        return 1
    print(json.dumps(e, indent=2))
    return 0


def cmd_add(a) -> int:
    d = load()
    eid = a.id or slug(a.venue, a.pair)
    if any(x.get("id") == eid for x in d.get("entries", [])):
        print(f"  entry {eid} already exists — use `set` to change it, or pass --id to add a variant")
        return 1
    d.setdefault("entries", []).append({
        "id": eid, "venue": a.venue, "pair": a.pair,
        "chain": a.chain, "status": a.status.upper(),
        "note": a.note or "", "added": _now(), "last_reviewed": _now(),
        "measured_fee_apr_pct": a.fee_apr,
        "fee_src": (a.fee_src or None) if a.fee_apr is not None else None,
        "audit": a.audit or "",
    })
    save(d)
    print(f"  ✅ added {eid} [{a.status.upper()}]")
    return 0


def cmd_set(a) -> int:
    d = load()
    e = next((x for x in d.get("entries", []) if x.get("id") == a.id), None)
    if not e:
        print(f"  no entry with id {a.id}")
        return 1
    if a.status:
        e["status"] = a.status.upper()
    if a.note:
        e["note"] = a.note
    if a.fee_apr is not None:
        e["measured_fee_apr_pct"] = a.fee_apr
    if getattr(a, "fee_src", None):
        e["fee_src"] = a.fee_src
    e["last_reviewed"] = _now()
    save(d)
    print(f"  ✅ {a.id} -> {e['status']}")
    return 0


def cmd_remove(a) -> int:
    d = load()
    before = len(d.get("entries", []))
    d["entries"] = [x for x in d.get("entries", []) if x.get("id") != a.id]
    if len(d["entries"]) == before:
        print(f"  no entry with id {a.id}")
        return 1
    save(d)
    print(f"  ✅ removed {a.id}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Pool catalog — bookmark venues and why")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("list").set_defaults(fn=cmd_list)
    s = sub.add_parser("show"); s.add_argument("--id", required=True); s.set_defaults(fn=cmd_show)

    a = sub.add_parser("add")
    a.add_argument("--venue", required=True); a.add_argument("--pair", required=True)
    a.add_argument("--chain", default="Avalanche")
    a.add_argument("--status", default="WATCH",
                   choices=["ACTIVE", "WATCH", "RETIRED", "AVOID", "active", "watch", "retired", "avoid"])
    a.add_argument("--note", default=""); a.add_argument("--id")
    a.add_argument("--fee-apr", type=float, dest="fee_apr"); a.add_argument("--audit", default="")
    # PROVENANCE IS NOT OPTIONAL IN PRACTICE. There is one numeric slot, so an aggregator's
    # reported figure and our own chain decode print identically unless the source travels with
    # the number. Default the label rather than leaving it blank: an untagged number is the
    # false-value shape this catalog exists to prevent.
    a.add_argument("--fee-src", dest="fee_src", default="reported (DefiLlama)")
    a.set_defaults(fn=cmd_add)

    st = sub.add_parser("set")
    st.add_argument("--id", required=True); st.add_argument("--status")
    st.add_argument("--note"); st.add_argument("--fee-apr", type=float, dest="fee_apr")
    st.add_argument("--fee-src", dest="fee_src")
    st.set_defaults(fn=cmd_set)

    rm = sub.add_parser("remove"); rm.add_argument("--id", required=True); rm.set_defaults(fn=cmd_remove)

    args = ap.parse_args()
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
