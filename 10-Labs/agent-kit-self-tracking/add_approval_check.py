#!/usr/bin/env python3
"""Add CHECK 9 (stale-approvals) to the treasury self-audit.

WHY (Jordan, Sep 11 2026 — he forwarded an ExVul alert on the ether.fi/Veda
AtomicQueue approval exploit): the whole attack class is "a contract you once
approved can pull your tokens". Our audit had NO check for standing approvals,
so a live UNLIMITED approval to a RETIRED rail sat unnoticed.

This check enumerates live ERC-20 allowances from the treasury wallet and
flags:
  - UNLIMITED (or very large) allowances          -> HIGH
  - allowances to a contract we no longer use     -> HIGH (stale authority)
  - allowances to an address with no code         -> MED (dead/burner address)
Idempotent.
"""
import pathlib
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

V = pathlib.Path('/root/vaults/gentech/10-Labs/agent-kit-self-tracking')
A = V / 'treasury_self_audit.py'
s = A.read_text()

if 'check_approvals' in s:
    print('already present'); raise SystemExit

CHECK = '''

# ── CHECK 9: standing token approvals (the ether.fi/Veda attack class) ──
# An approval is a persistent grant: any contract you ever approved can pull
# that token until you revoke it. The Sep 11 ExVul alert (ether.fi Liquid,
# ~15.45 ETH via the Veda AtomicQueue) drained users who had "simply approved"
# a contract. A retired rail with a live UNLIMITED approval is exactly that.
RPC = RPC  # reuse

# Spenders the treasury STILL uses. Anything else holding an allowance is stale.
LIVE_SPENDERS = {
    # our NFPM (position manager) — needs allowance to move pool tokens
    "0x3fed017ec0f5517cdf2e8a9a4156c64d74252146",
}
TOKENS = {
    "USDC":  ("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", 6),
    "WAVAX": ("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", 18),
    "BLACK": ("0xcd94a87696FAC69EdAE3a70fE5725307Ae1c43f6", 18),
}
WALLET = _sw_wallet()


def check_approvals():
    """Flag live approvals — especially unlimited ones to unused contracts."""
    for name, (tok, dec) in TOKENS.items():
        # find every spender that ever received an Approval from us
        topic = "0x" + __import__("web3").Web3.keccak(
            text="Approval(address,address,uint256)").hex()
        owner_topic = "0x" + "0" * 24 + WALLET[2:].lower()
        head = rpc("eth_blockNumber", [])
        if not head:
            continue
        head = int(head, 16)
        spenders = set()
        b = head - 500000
        while b <= head:
            e = min(b + 1999, head)
            r = rpc("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e),
                                     "address": tok,
                                     "topics": [topic, owner_topic]}])
            for l in (r or {}).get("result", []):
                spenders.add("0x" + l["topics"][2][-40:])
            b = e + 1
        for sp in spenders:
            data = "0xdd62ed3e" + WALLET[2:].rjust(64, "0") + sp[2:].rjust(64, "0")
            res = rpc("eth_call", [{"to": tok, "data": data}, "latest"])
            if not res or res == "0x":
                continue
            v = int(res, 16)
            if v == 0:
                continue
            unlimited = v > 2 ** 200
            stale = sp.lower() not in LIVE_SPENDERS
            code = rpc("eth_getCode", [sp, "latest"])
            dead = code in ("0x", "0x0")
            if unlimited and stale:
                add("HIGH", "stale-approval", f"{name} -> {sp}",
                    f"UNLIMITED allowance to a contract we no longer use"
                    + ("" if not dead else " (and it has NO code)"),
                    "revoke: approve(spender, 0) — an approval is a standing grant")
            elif unlimited:
                add("LOW", "wide-approval", f"{name} -> {sp}",
                    "unlimited allowance to a live spender (acceptable, but wide)",
                    "consider a bounded allowance instead of MaxUint256")
            elif stale:
                add("MED", "stale-approval", f"{name} -> {sp}",
                    f"live allowance ({v/10**dec:.6f}) to a contract we no longer use",
                    "revoke: approve(spender, 0)")

'''

# insert the check function before main(), and register it in main()
s = s.replace("def main():", CHECK + "\ndef main():", 1)
s = s.replace("    check_swap_routes()", "    check_swap_routes()\n    check_approvals()", 1)
A.write_text(s)
print('added check_approvals + registered in main()')
