#!/usr/bin/env python3
"""Close the stranded-BLACK gap in the harvest path (Jordan Sep 11 2026).

THE GAP: if a claim succeeds but the swap fails, BLACK strands in the wallet.
On the NEXT cycle, `collectRewards` reverts for an already-claimed position
(nothing left to collect), so `claimable` becomes None and the old check
returned "nothing to do" — the stranded BLACK would sit in the wallet FOREVER,
violating Jordan's rule (never hold BLACK as yield).

THE FIX: decide based on `max(claimable, wallet_balance)` and always try to SELL
whatever the wallet holds, regardless of whether there is anything new to claim.
So a stranded balance is recovered on the very next cycle, automatically.

Also: verify the swap tx status before printing success (audit class 1).
Idempotent.
"""
import pathlib

V = pathlib.Path('/root/vaults/gentech/10-Labs/agent-kit-self-tracking')
A = V / 'blackhole_cl_adapter.py'
s = A.read_text()

old = '''    if dry_run:
        if claimable is None or claimable < 0.0001:
            print("  ℹ️  No meaningful BLACK to harvest — nothing to do.")
            return {"ok": True, "stage": "noop", "black": claimable or 0.0}
    else:
        # after the collect above, the wallet holds the claimed amount
        if black_bal < 0.0001:
            print("  ℹ️  No meaningful BLACK to compound — nothing to do.")
            return {"ok": True, "stage": "noop", "black": black_bal}
'''

new = '''    # RECOVERY-AWARE GATE (Sep 11 2026): decide on the TOTAL we could sell, not
    # just what is newly claimable. If an earlier cycle claimed successfully but
    # the swap failed, BLACK strands in the wallet — and `collectRewards` then
    # reverts (nothing left to collect), so a claimable-only check would skip it
    # forever. max(claimable, wallet) means a stranded balance is recovered on
    # the very next cycle. Jordan's rule: never hold BLACK as yield.
    stranded = black_bal
    available = max(claimable or 0.0, stranded)
    if stranded > 0.0001 and (claimable is None or claimable < 0.0001):
        print(f"  ♻️  recovering {stranded:.6f} BLACK already stranded in the wallet")
    if available < 0.0001:
        print("  ℹ️  No meaningful BLACK to harvest — nothing to do.")
        return {"ok": True, "stage": "noop", "black": available}
    # In non-dry-run the collect above already moved `claimable` into the
    # wallet, so the balance is authoritative; in dry-run nothing has moved yet.
    sell_amount = black_bal if not dry_run else available
'''

if old in s:
    s = s.replace(old, new, 1)
    A.write_text(s)
    print('✓ harvest gate is now recovery-aware (max of claimable and wallet)')
else:
    print('✗ anchor not found — inspect manually')

# The sell leg uses black_bal; in dry-run that is 0 while `available` may be >0.
# Make the sell leg use the resolved amount so the probe is meaningful.
old2 = '''    if claimable and claimable > 0.0001:
        try:
            probe_in = min(int(claimable * 1e18), int(5e18))  # probe with <=5 BLACK'''
new2 = '''    if available > 0.0001:
        try:
            probe_in = min(int(available * 1e18), int(5e18))  # probe with <=5 BLACK'''
s = A.read_text()
if old2 in s:
    s = s.replace(old2, new2, 1)
    A.write_text(s)
    print('✓ sell-route probe now uses the resolved available amount')

old3 = '''            return {"ok": False, "stage": "swap_route_blocked",
                    "claimable": claimable, "note": sell_note}'''
new3 = '''            return {"ok": False, "stage": "swap_route_blocked",
                    "claimable": claimable, "stranded": stranded, "note": sell_note}'''
s = A.read_text()
if old3 in s:
    s = s.replace(old3, new3, 1)
    A.write_text(s)
    print('✓ blocked-result now reports the stranded balance too')

# swap tx: verify status BEFORE the success print
old4 = '''        print(f"  ✅ swapped: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ swap REVERTED", file=sys.stderr)
            return {"ok": False, "stage": "swap"}'''
new4 = '''        if rcpt['status'] != 1:
            print(f"  ❌ swap REVERTED: {h.hex()} status={rcpt['status']}", file=sys.stderr)
            return {"ok": False, "stage": "swap"}
        print(f"  ✅ swapped: {h.hex()} status={rcpt['status']}")'''
s = A.read_text()
if old4 in s:
    s = s.replace(old4, new4, 1)
    A.write_text(s)
    print('✓ swap success print moved after the status check')
