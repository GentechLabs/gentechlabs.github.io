#!/usr/bin/env python3
"""feegrowth_watch.py — measure REAL fee accrual over hours, not seconds.

Why this exists: a 40-second sample showed totalFeeGrowth flat, which proves
nothing (fee deltas over 20 blocks can truncate to zero at uint precision).
Conversely my FIRST test reported "POOL IS FROZEN" — that was a bad selector
(0xe76c7d71 instead of 0xe76c01e4) reverting and being read as 0.

Lesson baked in here: NEVER interpret an eth_call revert as a zero value.
Every call is checked for error/empty BEFORE its value is used.

Correct Algebra selectors (probed, not guessed):
    globalState()            0xe76c01e4   -> price, tick, fee, tpIdx
    totalFeeGrowth0Token()   0x6378ae44
    totalFeeGrowth1Token()   0xecdecf42
    liquidity()              0x1a686502

Appends a dated sample to a JSON ledger. Run it on a timer; the DELTA between
the first and last sample is the only honest fee number we have.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
SEL_GS = "0xe76c01e4"
SEL_TFG0 = "0x6378ae44"
SEL_TFG1 = "0xecdecf42"
SEL_LIQ = "0x1a686502"

LEDGER = os.path.expanduser("~/vaults/gentech/10-Labs/agent-kit-self-tracking/fee-growth-ledger.json")


def rpc(method, params, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                RPC,
                data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            )
            return json.load(urllib.request.urlopen(req, timeout=45))
        except Exception:
            if i == tries - 1:
                return {}
            time.sleep(2)


def call(to, data):
    """Returns int list, or None on revert/empty. NEVER silently returns 0."""
    r = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    if r.get("error"):
        return None
    res = r.get("result")
    if not res or res == "0x":
        return None
    h = res[2:]
    if len(h) % 64:
        return None
    try:
        return [int(h[i * 64:(i + 1) * 64], 16) for i in range(len(h) // 64)]
    except ValueError:
        return None


def s24(v):
    return v - (1 << 256) if v > (1 << 255) else v


def sample():
    gs = call(POOL, SEL_GS)
    f0 = call(POOL, SEL_TFG0)
    f1 = call(POOL, SEL_TFG1)
    lq = call(POOL, SEL_LIQ)
    if gs is None or f0 is None or f1 is None or lq is None:
        return {"ts": datetime.now(timezone.utc).isoformat(),
                "ok": False, "err": "revert/empty on a required call"}
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "block": int(rpc("eth_blockNumber", []).get("result", "0x0"), 16),
        "ok": True,
        "tick": s24(gs[1]),
        "price": str(gs[0]),
        "fee_ppm": gs[2],
        "tfg0": str(f0[0]),
        "tfg1": str(f1[0]),
        "pool_liq": str(lq[0]),
    }


def load():
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER) as fh:
                return json.load(fh)
        except Exception:
            pass
    return {"pool": POOL, "samples": []}


def save(d):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w") as fh:
        json.dump(d, fh, indent=1)


def main():
    quiet = "--quiet" in sys.argv
    d = load()
    s = sample()
    d["samples"].append(s)
    d["samples"] = d["samples"][-2000:]
    save(d)

    if not s.get("ok"):
        print(f"feegrowth_watch: !! CALL FAILED at {s['ts']}: {s.get('err')}")
        return

    ok = [x for x in d["samples"] if x.get("ok")]
    lines = []
    if len(ok) >= 2:
        a, b = ok[0], ok[-1]
        dt = (datetime.fromisoformat(b["ts"]) - datetime.fromisoformat(a["ts"])).total_seconds()
        d0 = int(b["tfg0"]) - int(a["tfg0"])
        d1 = int(b["tfg1"]) - int(a["tfg1"])
        if d0 or d1:
            lines.append(f"POOL IS ACCRUING FEES (measured over {dt/3600:.2f}h, {len(ok)} samples)")
            lines.append(f"  delta tfg0 = {d0:+,}   delta tfg1 = {d1:+,}")
            lines.append(f"  tick={s['tick']}  liq={s['pool_liq']}")
        elif not quiet:
            lines.append(f"flat over {dt/3600:.2f}h / {len(ok)} samples (tick={s['tick']})")
            lines.append(f"  NOTE: Algebra V3 dynamic fee can be 0 in a calm window — flat tfg does NOT mean the pool earns nothing. Check SwapFee events (topic 0x9443903d84c9719611). Only long-window deltas are meaningful.")
    elif not quiet:
        lines.append(f"seeded sample #{len(d['samples'])} tick={s['tick']}")

    # silence doctrine: quiet mode emits ONLY on a real change
    if lines and (not quiet or len(ok) >= 2 and (int(ok[-1]['tfg0']) - int(ok[0]['tfg0'])
                                                or int(ok[-1]['tfg1']) - int(ok[0]['tfg1']))):
        print("\n".join(lines))


if __name__ == "__main__":
    main()
