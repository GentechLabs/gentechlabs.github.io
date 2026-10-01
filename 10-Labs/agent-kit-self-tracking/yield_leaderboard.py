#!/usr/bin/env python3
"""
yield_leaderboard.py — the fleet's yield board. One row per ACTIVE tenant, ranked.

WHY A SUBPROCESS PER TENANT
---------------------------
The ledger resolves its wallet, key and state paths from the environment at IMPORT time
(`WALLET = _sw_wallet()` at module level). Importing it twice in one process would give the
second tenant the first tenant's wallet - silently, and in a report that looks completely
normal. That is the same class of bug as the 23 hardcoded wallets: correct output for one
person, wrong for everyone else, and nothing says so.

So each tenant is valued in its OWN process with its OWN environment. It costs a few hundred
milliseconds and it means a row cannot be another tenant's numbers wearing a different name.

WHAT IT RANKS
-------------
Not raw size. Size is just capital. This board ranks the thing the farm is FOR: how hard the
capital is working - fees per dollar per day, annualised, measured against the two honest
alternatives a holder actually has (staking, and simply holding the token).

A tenant with $30 out-earning a tenant with $500 is the point of the board.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"

# Honest baselines, measured (see benchmark-feeds.py / staking_benchmark.py), not assumed.
AVG_STAKER_APY = 4.97      # %/yr, mean across live Avalanche staking providers
HODL_30D = 50.16           # % over 29.9d - AVAX's own move; the bar a farm must beat to matter


def _run(tenant, wallet, code):
    """Run a snippet in the tenant's OWN process. Isolation is the feature."""
    env = dict(os.environ)
    env["STEWARD_TENANT"] = tenant
    env["STEWARD_WALLET"] = wallet
    env.pop("STEWARD_KEY_PATH", None)      # let key_path() resolve per tenant
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return {"error": (r.stderr.strip().splitlines() or ["unknown"])[-1][:160]}
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": "unparseable output"}


SNAP = r'''
import json, steward_fee_ledger as L
s = L.snapshot()
hist = L.load()
print(json.dumps({"snap": s, "hist_len": len(hist.get("snapshots") or [])}))
'''

FEES = r'''
import json, steward_fee_ledger as L
hist = L.load().get("snapshots") or []
# Shortest CLEAN window wins. fees_since(0, ...) spans everything, so any deposit or
# re-center inside it trips the churn guard and the board reports no yield at all - which
# is what happened on the first run. Walk outward until a window is clean.
for n in (2, 3, 4, 6, 8):
    d = L.fees_between(hist, n)
    if d.get("fees_usd") is not None:
        d["window_n"] = n
        break
print(json.dumps(d))
'''


def _shape_of(bins: int) -> str:
    """Which shape does this bin count belong to?

    Classify against lfj_shapes' own totals rather than a guess: curve resolves to 25 bins
    (bid 12 + ask 13) and bidask to 45. A live book can read a bin or two off -- a redeploy
    whose two legs landed at slightly different active bins overlaps and reads 23 on a curve
    -- so compare to the MIDPOINT between the two rules instead of to an exact count.
    """
    try:
        import lfj_shapes as _ls
        curve = _ls.widths("curve")["total"]
        bidask = _ls.widths("bidask")["total"]
    except Exception:
        curve, bidask = 25, 45
    if bins <= 0:
        return ""
    return "bidask" if bins > (curve + bidask) / 2 else "curve"


def collect(tenant, wallet):
    row = {"tenant": tenant, "wallet": wallet}
    s = _run(tenant, wallet, SNAP)
    if "error" in s:
        row["error"] = s["error"]
        return row
    snap = s["snap"]
    if not isinstance(snap, dict):
        row["error"] = f"snapshot returned {type(snap).__name__}, expected dict"
        return row
    row.update({
        "total_usd": float(snap.get("total_usd") or 0),
        "liquid_usd": float(snap.get("liquid_usd") or 0),
        "lp_usd": float(snap.get("lp_usd") or 0),
        "bins": int(snap.get("lp_bins") or 0),
        "shape": _shape_of(int(snap.get("lp_bins") or 0)),
        "price": float(snap.get("price_usd") or 0),
        "history": s.get("hist_len", 0),
    })
    row["deployed_pct"] = (row["lp_usd"] / row["total_usd"] * 100) if row["total_usd"] else 0.0

    f = _run(tenant, wallet, FEES)
    if "error" not in f:
        row["fees_usd"] = float(f.get("fees_usd") or f.get("total_usd") or 0)
        row["window_h"] = float(f.get("hours") or 0)
        if row["window_h"] > 0:
            row["fees_per_day"] = row["fees_usd"] / row["window_h"] * 24
            base = row["lp_usd"] or row["total_usd"]
            row["apy"] = (row["fees_per_day"] * 365 / base * 100) if base else 0.0
    return row


def main():
    reg = json.load(open(REGISTRY))
    tenants = [(n, t) for n, t in (reg.get("tenants") or {}).items()
               if t.get("status") == "ACTIVE" and t.get("wallet")]

    rows = [collect(n, t["wallet"]) for n, t in tenants]
    ok = [r for r in rows if "error" not in r]
    bad = [r for r in rows if "error" in r]
    ok.sort(key=lambda r: (r.get("apy") or 0), reverse=True)

    # ── SEPARATE TREASURIES, NOT A RANKING (Jordan, 2026-09-22) ────────────────────
    # "can you separate our info to individuals, me and my cousin. I love the leader board
    # but we run two different treasuries."
    # So: one self-contained block per tenant, no medals between them -- nobody is beating
    # anybody, these are two books. The fleet line stays because the total is still useful.
    print("=" * 74)
    print("  YIELD BOARD — separate treasuries, each valued on its own")
    print("=" * 74)
    if ok and ok[0].get("price"):
        print(f"  AVAX ${ok[0]['price']:.4f}   |   avg staker {AVG_STAKER_APY}%/yr   "
              f"|   HODL 30d +{HODL_30D}%")
    print()

    for r in ok:
        name = r["tenant"].upper()
        shape = r.get("shape")
        print("─" * 74)
        print(f"  {name}" + (f"   ({shape})" if shape else ""))
        print("─" * 74)
        print(f"    capital   ${r['total_usd']:,.2f}")
        print(f"    deployed  ${r['lp_usd']:,.2f}  ({r['deployed_pct']:.1f}%)"
              f"   idle ${r['liquid_usd']:,.2f}")
        print(f"    position  {r['bins']} bins")
        apy = r.get("apy")
        if apy is not None:
            vs = apy / AVG_STAKER_APY if AVG_STAKER_APY else 0
            print(f"    yield     {apy:,.1f}%/yr   "
                  f"(${r.get('fees_per_day', 0):,.2f}/day over {r.get('window_h', 0):,.1f}h)")
            print(f"    vs staker {vs:,.1f}x the average staker")
        else:
            print(f"    yield     not enough fee history yet "
                  f"({r.get('history', 0)} snapshots)")
        print()

    for r in bad:
        print(f"  ⚠️  {r['tenant'].upper()}: could not be valued — {r['error']}")
        print()

    total = sum(r["total_usd"] for r in ok)
    fees = sum(r.get("fees_per_day") or 0 for r in ok)
    print(f"  COMBINED (both treasuries): ${total:,.2f}  |  "
          f"${fees:,.2f}/day  |  ${fees*365:,.2f}/yr at this rate")


if __name__ == "__main__":
    main()
