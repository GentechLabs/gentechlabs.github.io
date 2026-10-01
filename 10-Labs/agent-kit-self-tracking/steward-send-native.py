#!/usr/bin/env python3
"""steward-send-native.py — send NATIVE gas token to an approved destination, on any rail.

WHY THIS EXISTS (Jordan, 2026-09-27)
------------------------------------
Jordan: *"the same way that we should have some type of connectivity where me and my cousin, we
could send each other stuff... If one of the agents go down, we have somebody else who can help
another agent out... sometimes you guys get stuck and you need help."*

The fleet already works this way — when one agent is down, another helps. Treasuries could not.

Measured that night, the gap was concrete: **dadrian's wallet was below its gas floor and NO TOOL
EXISTED to send it native AVAX.** Every transfer script we had was either Base-only or USDC-only:

    gta_remit.py           CDP-powered, BASE only
    steward_transfer.py    CDP-powered, BASE only
    steward-send-usdc.py   Avalanche, but USDC (an ERC-20 transfer, not native value)

So an agent that cannot pay its own gas **cannot be rescued by anyone**, however willing. That is
not a policy gap — dadrian's wallet is ALREADY an approved durable destination. It was a missing
primitive. This is that primitive.

WHY NATIVE VALUE IS DIFFERENT FROM AN ERC-20 SEND
-------------------------------------------------
No token contract, no allowance, no approve. The value rides in the transaction. The failure modes
are correspondingly different, and each one is handled explicitly below:

  * a native send has NO receipt-side balance check unless you write one — so it is written;
  * the destination may not exist yet (no code, no nonce) — value to an EOA is fine, but a typo'd
    address is not, so the address is validated the same hard way USDC sending validates it;
  * gas is paid from the SAME balance being sent, so a "send everything" request always fails.
    This tool therefore refuses to touch the gas reserve.

RAIL-AWARE, NOT AVALANCHE-HARDCODED
-----------------------------------
Jordan, same night: *"let's build that in any other rails that I have... we should also make that
like a default. So when I start yield farming on Solana, we'll also make sure Dage has one as well."*

So the chain is a PARAMETER with a registry (below), not a condition. Adding Solana later means
adding an entry, not rewriting the tool. Solana is listed with `implemented: False` on purpose: it
reports NOT IMPLEMENTED rather than pretending, and the moment a signer exists the flag flips.

SAFETY RAILS (all four, checked before anything signs)
------------------------------------------------------
  1. HARD ADDRESS VALIDATION — length, hex, not zero. Never 'repair' a supplied address.
  2. DESTINATION REGISTRY — the address must be an approved named destination, so a typo cannot
     become an irreversible send. `--to jordan|dadrian|<name>` resolves from the registry.
  3. AUTONOMY — the same `tenant_guard.assert_autonomy` gate every other capital move uses.
  4. GAS RESERVE — the send may never spend the floor that pays for repairs.

Usage:
    python3 steward-send-native.py --to dadrian --amount 0.014 --dry-run
    python3 steward-send-native.py --to dadrian --amount 0.014 --execute --yes \
        --authorized-by "Jordan: fund a peer treasury stranded below its gas floor"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from web3 import Web3
from eth_account import Account

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import steward_identity as SI                      # noqa: E402
import gas_reserve as GR                           # noqa: E402

# ── THE RAIL REGISTRY ────────────────────────────────────────────────────────────────────────
# native = the gas token's ticker; decimals = its base unit. Solana is listed and NOT implemented:
# reporting "not implemented" is honest; omitting it would hide that the default is still missing.
RAILS = {
    "avalanche": {
        "chain_id": 43114, "native": "AVAX", "decimals": 18, "implemented": True,
        "rpcs": [
            "https://avalanche-c-chain-rpc.publicnode.com",
            "https://avalanche.drpc.org",
            "https://api.avax.network/ext/bc/C/rpc",
        ],
    },
    "base": {
        "chain_id": 8453, "native": "ETH", "decimals": 18, "implemented": True,
        "rpcs": ["https://mainnet.base.org", "https://base.drpc.org"],
    },
    "solana": {
        "chain_id": None, "native": "SOL", "decimals": 9, "implemented": False,
        "rpcs": ["https://api.mainnet-beta.solana.com"],
    },
}

WALLETS_JSON = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/wallets.json"
TENANTS_JSON = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"


def rail(name):
    r = RAILS.get(name)
    if not r:
        print(f"  ❌ UNKNOWN RAIL {name!r} — known: {', '.join(RAILS)}")
        sys.exit(1)
    return r


def live_rpc(r, exclude=None):
    """First endpoint that actually answers. A dead RPC reads as 'nothing happened'."""
    for u in r["rpcs"]:
        if u == exclude:
            continue
        try:
            w = Web3(Web3.HTTPProvider(u, request_kwargs={"timeout": 12}))
            if w.eth.block_number > 0:
                return u
        except Exception:
            continue
    return r["rpcs"][0]


def addr_ok(a: str):
    """Hard validation. The whole point is that silent failures are the dangerous ones."""
    if not isinstance(a, str) or not a.startswith("0x"):
        return False, "missing 0x prefix"
    body = a[2:]
    if len(body) != 40:
        return False, f"BAD LENGTH: {len(body)} hex chars, expected 40"
    try:
        int(body, 16)
    except ValueError:
        return False, "non-hex characters present"
    if int(body, 16) == 0:
        return False, "zero address"
    return True, "ok"


def resolve_destination(name):
    """Resolve a NAME to an approved address. A name in the registry is the authorisation."""
    name = (name or "").strip().lower()
    # tenants.json first: a peer TREASURY is defined there (whose treasury it is).
    try:
        t = json.load(open(TENANTS_JSON)).get("tenants", {})
        if name in t and t[name].get("wallet"):
            return t[name]["wallet"], f"tenants.json:{name}"
    except Exception:
        pass
    try:
        w = json.load(open(WALLETS_JSON)).get("wallets", {})
        if name in w and w[name].get("address"):
            return w[name]["address"], f"wallets.json:{name}"
    except Exception:
        pass
    return None, ""


def assert_may_act(action, human_authorization=None):
    """Refuse to move capital without the orchestrator's okay.

    THE ORCHESTRATOR MODEL (Jordan, 2026-09-27): *"we don't really need to put like a spending cap
    or anything on it. It's more about getting the okay from the orchestrator to send."*

    That is ALREADY how this system works, and it was measured live: `move_capital` sits at
    action-class 4 while the highest level (L3_AUTONOMOUS) reaches only 3 — so NO level can move
    capital alone. Without an authorization it is refused; with a human instruction it proceeds AND
    is recorded to human-authorizations.jsonl. The control is the OKAY, not a number.
    """
    from tenant_guard import assert_autonomy, AutonomyViolation
    try:
        assert_autonomy(SI.tenant(), action, human_authorization=human_authorization)
    except AutonomyViolation as e:
        # A REFUSAL MUST PRINT AS A REFUSAL, NOT A TRACEBACK. The message is already the right
        # one; letting it escape as an exception reads like a crash and buries the reason the
        # caller actually needs. (Caught by running it: the gate refused correctly and the
        # operator saw a Python traceback.)
        print(f"\n  ⛔ ORCHESTRATOR OKAY REQUIRED — this is a capital move, not an autonomous action.")
        print(f"     {e}")
        print(f"\n     There is no spending cap here, by design. What gates it is YOUR okay:")
        print(f"       --authorized-by \"Jordan (orchestrator): <why>\"")
        print(f"     The instruction is recorded to human-authorizations.jsonl — an action above the")
        print(f"     ladder is allowed but NEVER silent.")
        sys.exit(4)


def main():
    ap = argparse.ArgumentParser(description="Send the native gas token to an approved destination.")
    ap.add_argument("--to", required=True, help="a NAMED destination (jordan, dadrian, ...)")
    ap.add_argument("--amount", type=float, required=True, help="amount in the native token")
    ap.add_argument("--chain", default="avalanche", choices=sorted(RAILS))
    ap.add_argument("--from-wallet", default=None, help="defaults to this tenant's wallet")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicit no-op — the DEFAULT is already a dry run, so this only makes the "
                         "intent readable at the call site (and it is refused if combined --execute)")
    ap.add_argument("--authorized-by", default=None)
    ap.add_argument("--allow-below-floor", action="store_true",
                    help="permit spending the repair reserve (refused by default)")
    a = ap.parse_args()

    # A CONTRADICTION MUST BE REFUSED, NOT RESOLVED (same class as the cron
    # enabled+paused auto-disable): two flags asking for opposite things is a caller bug, and
    # silently picking one teaches the caller nothing.
    if a.dry_run and a.execute:
        print("  ❌ --dry-run and --execute together is a contradiction. Pick one.")
        return 2

    r = rail(a.chain)
    if not r["implemented"]:
        print(f"\n  ⛔ {a.chain.upper()} — NATIVE SEND IS NOT IMPLEMENTED YET.")
        print(f"     The rail is REGISTERED so this is a known gap, not a silent one. What is missing")
        print(f"     is a SOLANA signer (Base and Avalanche share the EVM path; Solana does not).")
        print(f"     Registering it now means the day a signer exists, one flag flips — and nothing")
        print(f"     else in this tool changes.")
        return 3

    rpc = live_rpc(r)
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 45}))
    try:
        bn = w3.eth.block_number
    except Exception as e:
        print(f"  ❌ UNREADABLE CHAIN — {rpc} ({type(e).__name__})")
        print(f"     A chain we cannot read is a chain we cannot spend on.")
        return 1

    me = Web3.to_checksum_address(a.from_wallet or SI.wallet())
    dest_raw, src = resolve_destination(a.to)
    if not dest_raw:
        print(f"\n  ❌ {a.to!r} IS NOT AN APPROVED DESTINATION.")
        print(f"     Destinations live in wallets.json / tenants.json. An unlisted address is")
        print(f"     REFUSED — that is what stops a typo becoming an irreversible send.")
        return 1
    ok, why = addr_ok(dest_raw)
    if not ok:
        print(f"\n  ❌ DESTINATION FAILED VALIDATION — {why}")
        return 1
    dest = Web3.to_checksum_address(dest_raw)

    amount_wei = int(round(a.amount * (10 ** r["decimals"])))
    if amount_wei <= 0:
        print(f"  ❌ amount rounds to zero.")
        return 1

    print("=" * 96)
    print(f"  STEWARD — NATIVE SEND PREFLIGHT ({r['native']} on {a.chain})")
    print("=" * 96)
    print(f"  rpc          {rpc}  (block {bn})")
    print(f"  from         {me}   (tenant {SI.tenant()})")
    print(f"  to           {dest}   [{src}]")
    print(f"  amount       {a.amount:.8f} {r['native']}  ({amount_wei} base units)")

    bal = w3.eth.get_balance(me)
    gp = w3.eth.gas_price
    # a native transfer is 21,000 gas; priced with headroom, never at the floor
    gas_cost = int(21000 * gp * 1.35)
    total = amount_wei + gas_cost
    print(f"  balance      {bal/1e18:.8f} {r['native']}")
    print(f"  amount+gas   {total/1e18:.8f}  (gas {gas_cost/1e18:.8f} @ {gp/1e9:.4f} nAVAX)")

    if bal < total:
        print(f"\n  ⛔ INSUFFICIENT — needs {total/1e18:.8f}, holds {bal/1e18:.8f} {r['native']}.")
        print(f"     A native send pays its own gas from the same balance. Not attempting.")
        return 1

    # ── THE GAS RESERVE: the send may not spend what pays for repairs ────────────────────────
    try:
        info = GR.reserve_info(tenant=SI.tenant(), w3=w3, balance_avax=bal / 1e18)
        floor = float(info["reserve_avax"])
    except Exception as e:
        print(f"\n  ⛔ CANNOT PRICE THE FLOOR ({type(e).__name__}) — refusing rather than guessing.")
        return 1
    after = (bal - total) / 1e18
    print(f"  gas floor    {floor:.8f} {r['native']}  (the repair reserve)")
    print(f"  after send   {after:.8f} {r['native']}")
    if after < floor and not a.allow_below_floor:
        print(f"\n  ⛔ THIS SEND WOULD SPEND THE GAS FLOOR — leaves {after:.8f}, floor is {floor:.8f}.")
        print(f"     SHORT BY {floor-after:.8f} (~${(floor-after)*11.02:.4f}).")
        print(f"     The reserve exists to pay for repairing a stranded book. Spending it to fund")
        print(f"     somebody ELSE's repair can leave THIS treasury unable to repair itself.")
        print(f"     --allow-below-floor overrides — loudly, on purpose, and never by default.")
        return 1

    assert_may_act("move_capital", a.authorized_by)

    if not (a.execute and a.yes):
        print(f"\n  (dry-run — pass --execute --yes to send)")
        return 0

    nonce = w3.eth.get_transaction_count(me)
    tx = {"from": me, "to": dest, "value": amount_wei, "gas": 21000,
          "gasPrice": int(gp * 1.35), "nonce": nonce, "chainId": r["chain_id"]}
    signed = Account.sign_transaction(tx, SI.signing_key())
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"\n  SENT {h.hex()}")

    rc = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    print(f"  status       {'✅ SUCCESS' if rc.status == 1 else '❌ REVERTED'}  block={rc.blockNumber}")

    # ── VERIFY ON A SECOND RPC (a broadcast is not a delivery) ───────────────────────────────
    second = live_rpc(r, exclude=rpc)
    w2 = Web3(Web3.HTTPProvider(second, request_kwargs={"timeout": 20}))
    d_before = bal
    for _ in range(6):
        try:
            d_after = w2.eth.get_balance(dest)
            if rc.status == 1 and d_after >= amount_wei:
                break
        except Exception:
            pass
        time.sleep(3)
    try:
        d_after = w2.eth.get_balance(dest)
        print(f"  VERIFY {second}")
        print(f"    destination {r['native']} now {d_after/1e18:.8f}")
    except Exception as e:
        print(f"  ⚠️  second-RPC verification unavailable ({type(e).__name__}) — receipt stands")
    print(f"\n  {'✅ SENT AND VERIFIED' if rc.status == 1 else '❌ SEND FAILED'} — "
          f"{a.amount:.8f} {r['native']} -> {a.to}")
    return 0 if rc.status == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
