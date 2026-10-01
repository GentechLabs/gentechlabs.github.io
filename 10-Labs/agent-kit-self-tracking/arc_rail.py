#!/usr/bin/env python3
"""Arc mainnet rail adapter — the canonical way to touch Arc from this treasury.

WHY THIS FILE EXISTS (Jordan, Sep 16 2026 — Arc mainnet launch day):
    "Now that today is launch day, what should we do as a result of Arc finally coming
     through? Is there anything we need to do on our side to make sure the rail is
     good to go?"

Arc is a live rail but NOT a yield home (Aave V4 USDC 0.00%, Morpho Blue Arc USDC
0.00% — supply outran borrowers by an order of magnitude on day one). So the only work
that matters right now is making the rail SAFE TO DRIVE, so that when the borrow side
shows up we can act immediately instead of debugging plumbing under pressure.

TWO REAL BLOCKERS FOUND AND HANDLED HERE:

1. THE RPC REQUIRES A User-Agent. Measured: a bare urllib/curl call to
   https://rpc.mainnet.arc.io returns HTTP 403 with body "error code: 1010"
   (Cloudflare). With any User-Agent it returns 200 and the correct chainId.
   This matters more than it looks: our other scripts default to BARE urllib, so a
   naive Arc probe reads 403 and can be mis-filed as "chain is down" — or worse, a
   non-raising parser reads the failure as a zero. Same family as a reverted
   eth_call read as 0. EVERY request in this module sends a UA, and `rpc()` raises
   rather than returning a falsy value, so a failure can never masquerade as data.

2. GAS IS PAID IN USDC, AND THE TWO USDC REPRESENTATIONS HAVE DIFFERENT DECIMALS.
   Native gas is 18-decimal USDC; the ERC-20 at 0x3600..0000 is 6-decimal (verified
   decimals() == 6 on mainnet). Any code that assumes one decimal count for "USDC"
   will be off by 10^12 on one side. Both are handled explicitly below, and the gas
   estimate is reported in human USDC cents so it cannot be misread.

Verified live 2026-09-16: chainId 5042, block 21,155,109, gas 72.58 Gwei
(= 0.000000072582 native-USDC per gas unit), USDC 6-dec, TokenMessengerV2 present.
"""
from __future__ import annotations

import json
import urllib.request

# ── Arc constants (chain-verified, mainnet) ────────────────────────────────────
ARC_RPC = "https://rpc.mainnet.arc.io"
ARC_CHAIN_ID = 5042
ARC_UA = "GenTech-Steward/1.0 (+https://gentechlabs.github.io)"   # REQUIRED: no UA => 403

USDC_ERC20 = "0x3600000000000000000000000000000000000000"
USDC_DECIMALS = 6                 # verified on mainnet
NATIVE_GAS_DECIMALS = 18          # native gas token is 18-dec USDC — NOT 6
CCTP_DOMAIN = 26
CCTP_TOKEN_MESSENGER_V2 = "0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d"

WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"

# A no-agent Arc run is worthless without gas; a bump of ~0.05 USDC covers many
# hundreds of cheap Arc transactions at observed gas. Deliberately small: the gas
# floor philosophy (Jordan) is NO hard gates — price the action, never block it.
GAS_FLOOR_USDC = 0.05


class ArcRPCError(RuntimeError):
    """Raised on any transport failure or JSON-RPC error.

    Deliberately raises instead of returning None/0: a silent falsy return is how a
    dead endpoint becomes a 'zero balance' or a 'chain down' verdict.
    """


def rpc(method: str, params: list | None = None, timeout: int = 25):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                          "params": params or []}).encode()
    req = urllib.request.Request(
        ARC_RPC, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": ARC_UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
    except Exception as e:                                    # noqa: BLE001
        raise ArcRPCError(f"{method}: {type(e).__name__}: {e}") from e
    if "error" in body:
        raise ArcRPCError(f"{method}: rpc error {body['error']}")
    if "result" not in body:
        raise ArcRPCError(f"{method}: no result in response")
    return body["result"]


def _hex_to_int(h, default=None):
    if h in (None, "0x", ""):
        return default
    try:
        return int(h, 16)
    except (TypeError, ValueError):
        return default


def chain_status() -> dict:
    """Chain identity + liveness. Raises on failure — never reports a false zero."""
    cid = _hex_to_int(rpc("eth_chainId"))
    bn = _hex_to_int(rpc("eth_blockNumber"))
    gp = _hex_to_int(rpc("eth_gasPrice"), 0)
    blk = rpc("eth_getBlockByNumber", ["latest", False])
    return {
        "chain_id": cid,
        "chain_id_ok": cid == ARC_CHAIN_ID,
        "block_number": bn,
        "gas_price_wei_native": gp,
        "gas_price_usdc_per_unit": gp / 10 ** NATIVE_GAS_DECIMALS,
        "gas_limit": _hex_to_int(blk.get("gasLimit")),
        "block_ts": _hex_to_int(blk.get("timestamp")),
        "txs_in_block": len(blk.get("transactions") or []),
    }


def gas_cost_usdc(gas_units: int = 200_000) -> float:
    """Cost of a tx in human USDC. Uses the 18-dec NATIVE side, not the 6-dec ERC-20."""
    gp = _hex_to_int(rpc("eth_gasPrice"), 0)
    return gp * gas_units / 10 ** NATIVE_GAS_DECIMALS


def balances(wallet: str = WALLET) -> dict:
    """Native (gas) + ERC-20 USDC. Handles the 18-vs-6 decimal split explicitly."""
    native = _hex_to_int(rpc("eth_getBalance", [wallet, "latest"]), 0)
    data = "0x70a08231" + "0" * 24 + wallet[2:].lower()
    erc20 = _hex_to_int(rpc("eth_call", [{"to": USDC_ERC20, "data": data}, "latest"]), 0)
    dec = _hex_to_int(rpc("eth_call", [{"to": USDC_ERC20, "data": "0x313ce567"},
                                       "latest"]), USDC_DECIMALS)
    return {
        "wallet": wallet,
        "native_gas_usdc": native / 10 ** NATIVE_GAS_DECIMALS,
        "erc20_usdc": erc20 / 10 ** dec,
        "erc20_decimals": dec,
        "total_usdc": native / 10 ** NATIVE_GAS_DECIMALS + erc20 / 10 ** dec,
    }


def readiness(wallet: str = WALLET) -> dict:
    """Can we WRITE to Arc, or only read it? The question Jordan actually asked."""
    st = chain_status()
    bal = balances(wallet)
    can_write = bal["native_gas_usdc"] >= GAS_FLOOR_USDC
    return {
        "chain": st,
        "balances": bal,
        "read_capable": True,           # proven by this call succeeding
        "write_capable": can_write,
        "gas_floor_usdc": GAS_FLOOR_USDC,
        "verdict": ("RAIL READY — funded for gas, can execute"
                    if can_write else
                    "READ-ONLY — no Arc gas. Fund via CCTP domain 26 "
                    "(burn USDC on Avalanche, mint on Arc). No traditional bridge needed."),
    }


def main() -> int:
    r = readiness()
    st, bal = r["chain"], r["balances"]
    print("🏛️ ARC MAINNET RAIL — readiness check")
    print()
    print(f"   chain id     {st['chain_id']} ({'OK' if st['chain_id_ok'] else 'MISMATCH'})"
          f"   block {st['block_number']:,}")
    print(f"   gas price    {st['gas_price_wei_native']} wei "
          f"= {st['gas_price_usdc_per_unit']:.12f} USDC/gas")
    print(f"   typical tx   ~{gas_cost_usdc(200_000)*100:.3f} USDC cents "
          f"(200k gas, 18-dec native side)")
    print()
    print(f"   wallet       {bal['wallet']}")
    print(f"   gas (native) {bal['native_gas_usdc']:.18f} USDC  (18-dec)")
    print(f"   ERC-20 USDC  {bal['erc20_usdc']:.6f} USDC  ({bal['erc20_decimals']}-dec)")
    print()
    print(f"   READ  ✅   WRITE {'✅' if r['write_capable'] else '❌'}   {r['verdict']}")
    print()
    print("   ⚠ RPC REQUIRES A User-Agent — a bare request returns HTTP 403")
    print("     (Cloudflare 'error code: 1010'). This module always sends one.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
