#!/usr/bin/env python3
"""exit_plan.py — turn (rail, exit_mode) into the exact exit sequence.

Jordan (2026-09-17): "we should probably update the exit plan to be able to go into whatever
the pool mode is, which would be just holding the token, right? So now we need to look into
building that next for the agentic treasury."

The insight behind this: leaving an LP means leaving the FEE ENGINE, not the ASSET. Those are
separate decisions, and collapsing them (swap everything to USDC, always) quietly makes the
directional call for you every time.

So this is a PLANNER, not an executor. It moves no money. It reads exit-rails.json and emits
the exact ordered sequence for a chosen mode, so the executor follows a rehearsed path rather
than inventing one mid-withdrawal — which is the whole reason exit-rails.json exists.

Design rules enforced here:
  - The sequence is IDENTICAL up to and including COLLECT in every mode. Modes differ ONLY at
    the terminal step. Fewer divergent branches = fewer untested paths.
  - No mode is assumed. Running without an explicit --mode is an ERROR, because a default is
    a decision made silently.
  - Every mode states what it gives up, so the trade is visible before it is taken.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAILS = HERE / "exit-rails.json"

# Steps common to every mode, up to and including COLLECT.
COMMON = [
    ("SETTLE",   "Re-read state 3x ~2s on public RPCs; take the highest settled read. "
                 "Public RPCs lag fresh txs and will report a phantom-empty position."),
    ("HARVEST",  "Claim emissions BEFORE removing liquidity, or they strand. Skipped only "
                 "on an unstaked position that has nothing to harvest."),
    ("UNSTAKE",  "gauge.withdraw(tid) if staked. SIMULATE first — a stale tokenId burned "
                 "gas 22x on Sep 10 2026."),
    ("REMOVE",   "nfpm.decreaseLiquidity({tid, liquidity, 0, 0, deadline}) — FULL removal."),
    ("COLLECT",  "nfpm.collect({tid, wallet, MAX, MAX}) — ALWAYS, even at liq=0. "
                 "Fees stay owed otherwise."),
]

TERMINAL = {
    "STABLE": [
        ("SWAP",   "ALL legs -> USDC via a PROVEN route (state-override probe first). "
                   "A failed swap ABORTS the remit; capital stays as the source token."),
        ("REMIT",  "usdc.transfer(DEST, all) — ONE remit, not several. Sweep residue first; "
                   "a second send doubles gas for cents."),
        ("VERIFY", "Read balances back for EVERY token touched + the tx receipt. Report the "
                   "actual delta. A non-zero balance means a leg failed silently."),
    ],
    "HOLD_SPLIT": [
        ("KEEP",   "Do NOT swap. Both legs remain in the wallet exactly as collected."),
        ("VERIFY", "Read balances back for BOTH legs. Confirm liquidity is 0 and fees are "
                   "collected. No remit, no router, no slippage."),
    ],
    "HOLD_TOKEN": [
        ("SWAP",   "stable leg -> token leg ONLY. Proven route, bounded slippage. "
                   "This is a directional conversion — it is the mode, not a side effect."),
        ("VERIFY", "Read balances back for the token. Confirm liquidity is 0, fees collected, "
                   "and the position is fully consolidated."),
    ],
}

GIVES_UP = {
    "STABLE":     "All price exposure — you hold cash and wait.",
    "HOLD_SPLIT": "Fees. You keep a neutral half-and-half exposure.",
    "HOLD_TOKEN": "Fees AND the stable half. You take FULL directional exposure.",
}


def plan(rail_key: str, mode: str, data: dict) -> int:
    modes = data.get("exit_modes", {}).get("modes", {})
    rails = data.get("rails", {})

    if mode not in modes:
        print(f"❌ unknown exit_mode {mode!r}. Valid: {', '.join(sorted(modes))}")
        return 2
    if rail_key not in rails:
        print(f"❌ unknown rail {rail_key!r}. Valid: {', '.join(sorted(rails))}")
        return 2

    r = rails[rail_key]
    m = modes[mode]


    print("=" * 84)
    print(f"  EXIT PLAN — rail={rail_key}  mode={mode}")
    print(f"  {m.get('label')}")
    print("=" * 84)
    print(f"  rail status   : {r.get('status')}   chain={r.get('chain')}")
    print(f"  terminal asset: {m.get('terminal_asset')}")
    print(f"  swaps         : {m.get('swaps')}")
    print(f"  remit         : {m.get('remit')}")
    print(f"  gives up      : {GIVES_UP.get(mode,'?')}")
    if m.get("risk"):
        print(f"  risk          : {m['risk']}")

    print(f"\n  ── SEQUENCE ──")
    # Skipped steps must not consume a number, or the plan reads as though it has two
    # step 2s and an operator can act on the wrong line. Skips are reported separately.
    skipped = []
    n = 0
    for name, desc in COMMON:
        if (rail_key == "blackhole_cl" and not r.get("staked_path")
                and name in ("HARVEST", "UNSTAKE")):
            skipped.append(name)
            continue
        n += 1
        print(f"   {n:>2}. {name:<9} {desc[:74]}")

    for name, desc in TERMINAL[mode]:
        n += 1
        print(f"   {n:>2}. {name:<9} {desc[:74]}")

    if skipped:
        print(f"\n   ⏭  SKIPPED for this rail: {', '.join(skipped)}"
              f"  (unstaked position — never staked, nothing to harvest or withdraw)")

    print(f"\n  ── RAIL NOTES ({rail_key}) ──")
    for p in (r.get("pitfalls") or [])[:4]:
        print(f"   ⚠ {p[:96]}")
    if r.get("unstaked_note"):
        print(f"   ℹ {r['unstaked_note'][:180]}...")

    print(f"\n  ── INVARIANTS ──")
    for inv in data.get("exit_modes", {}).get("invariants", []):
        print(f"   • {inv[:96]}")

    if mode == "HOLD_TOKEN":
        print(f"\n  🔶 MODE CHANGE REQUIRED: this converts a FEE position into a DIRECTIONAL")
        print(f"     bet. Log YIELD_FARM -> HOLD in treasury-state.json with the trigger and")
        print(f"     the thesis. An LP that quietly becomes a holder stops paying for waiting.")
    print("=" * 84)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan an LP exit for a given mode.")
    ap.add_argument("rail", nargs="?", help="rail key, e.g. blackhole_cl")
    ap.add_argument("--mode", required=False,
                    help="exit mode: STABLE | HOLD_SPLIT | HOLD_TOKEN (REQUIRED)")
    ap.add_argument("--list", action="store_true", help="list rails and modes")
    a = ap.parse_args()

    if not RAILS.exists():
        print(f"❌ {RAILS} not found")
        return 2
    data = json.loads(RAILS.read_text())

    if a.list or not a.rail:
        modes = data.get("exit_modes", {}).get("modes", {})
        print("RAILS:")
        for k, v in data.get("rails", {}).items():
            print(f"   {k:<20} {v.get('status')}")
        print("\nEXIT MODES:")
        for k, v in modes.items():
            print(f"   {k:<12} {v.get('label')}")
            print(f"                terminal: {v.get('terminal_asset')}")
        return 0

    if not a.mode:
        # a default would be a decision made silently
        print("❌ --mode is REQUIRED. There is no default exit mode on purpose:")
        print("   the choice between cash, a split, and the token IS the decision.")
        print("   re-run with --mode STABLE | HOLD_SPLIT | HOLD_TOKEN")
        return 2

    return plan(a.rail, a.mode, data)


if __name__ == "__main__":
    sys.exit(main())
