#!/usr/bin/env python3
"""steward-send-usdc.py — send native Avalanche USDC to a Jordan-approved address.

WHY THE CHECKS ARE THIS PARANOID
--------------------------------
A wrong-LENGTH address fails loudly. A right-length typo fails silently and reads zero. And the
wrong TOKEN on the right chain is unrecoverable just as quietly: Avalanche has TWO things called
USDC — the native one (0xB97E...6E) and bridged USDC.e (0xA7D7...64) — and they are different
contracts. Sending the wrong one to an exchange deposit address is a permanent loss.

So: validate the address, assert the token contract, read the balance, quote gas, and only then
sign. Every step prints. Nothing is assumed.
"""

from __future__ import annotations

# ── wallet resolution (wired 2026-09-22) ────────────────────────────────────
# This file used to hardcode the operator's address. Fine for one person, catastrophic
# for a fleet: a second tenant running this script with their own config would still act
# on the FIRST tenant's wallet, and would do it silently. Resolve it instead - and prove
# it, because steward_identity.signer() refuses a key that does not match the resolved
# wallet, and asserts the tenant boundary before handing one back.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from steward_identity import wallet as _steward_wallet

import json
import sys

from web3 import Web3

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
# RPC failover (2026-09-22). A fixed primary endpoint began returning 429 and these tools
# died on it — an exit could not read activeId and a send could not read a balance. A
# rate-limited endpoint must never be able to read as an unreachable chain or block a
# withdrawal. Probe the pool, take the first that actually answers. The "second RPC" used
# for verification is deliberately a DIFFERENT host — a second read from the same endpoint
# proves nothing.
RPC_CANDIDATES = [
    "https://avalanche-c-chain-rpc.publicnode.com",
    "https://avalanche.drpc.org",
    "https://rpc.ankr.com/avalanche",
    _avax_url(),
]


def _live_rpc(exclude=None):
    """First candidate that answers eth_blockNumber. Never returns `exclude`."""
    for _u in RPC_CANDIDATES:
        if exclude and _u == exclude:
            continue
        try:
            if Web3(Web3.HTTPProvider(_u, request_kwargs={"timeout": 20})).eth.block_number:
                return _u
        except Exception:
            continue
    return RPC_CANDIDATES[0]

WALLET = _steward_wallet()

# NATIVE Avalanche USDC. NOT USDC.e.
USDC_NATIVE = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
USDC_E_BRIDGED = Web3.to_checksum_address("0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664")

DESTINATION_RAW = sys.argv[1] if len(sys.argv) > 1 else ""

ERC20 = json.loads("""[
 {"name":"symbol","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"string"}]},
 {"name":"name","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"string"}]},
 {"name":"decimals","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint8"}]},
 {"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"}],
  "outputs":[{"type":"uint256"}]},
 {"name":"transfer","type":"function","stateMutability":"nonpayable",
  "inputs":[{"type":"address"},{"type":"uint256"}],"outputs":[{"type":"bool"}]}
]""")


def addr_ok(a: str) -> tuple[bool, str]:
    """Hard address validation — the whole point is that silent failures are the dangerous ones."""
    if not a.startswith("0x"):
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



def _assert_may_act(action, human_authorization=None):
    """Refuse to execute unless THIS tenant is licensed to do it ALONE.

    Wired 2026-09-22. Until now the autonomy levels were documentation - nothing consulted
    them, so any box holding a wallet could re-center capital regardless of its level. The
    check sits at the EXECUTION point because that is the one place it cannot be skipped.

    `human_authorization` (--authorized-by) is passed through so a HUMAN-INSTRUCTED send is
    distinguishable from the agent deciding for itself. Without it, `move_capital` is refused
    for EVERYONE including Jordan at L3 - the ladder would block the owner, and the send path
    could never work at all.
    """
    import os as _o, sys as _s
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    import steward_identity as _SI
    from tenant_guard import assert_autonomy
    assert_autonomy(_SI.tenant(), action, human_authorization=human_authorization)


def _authorized_by():
    """Read --authorized-by 'who: why'. Absent means the agent is acting alone."""
    argv = sys.argv
    for i, a in enumerate(argv):
        if a == "--authorized-by" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--authorized-by="):
            return a.split("=", 1)[1]
    return None

def main() -> int:
    _rpc = _live_rpc()
    w3 = Web3(Web3.HTTPProvider(_rpc, request_kwargs={"timeout": 45}))
    print(f"  rpc {_rpc}")

    print("=" * 96)
    print("  STEWARD — USDC SEND PREFLIGHT (read-only until the final step)")
    print("=" * 96)

    # 1 ── destination
    print(f"\n1 ── DESTINATION")
    print(f"   supplied verbatim : {DESTINATION_RAW!r}")
    ok, why = addr_ok(DESTINATION_RAW)
    print(f"   length check      : {why}")
    if not ok:
        print("\n   ❌ REFUSING — address failed validation. Not guessing a 'fixed' version of it.")
        return 1
    try:
        DEST = Web3.to_checksum_address(DESTINATION_RAW)
        checksum_note = "EIP-55 checksum VALID"
    except Exception:
        # all-lowercase/all-uppercase input has no checksum to verify; still a valid address
        DEST = Web3.to_checksum_address(DESTINATION_RAW.lower())
        checksum_note = "no checksum present in input (fine, but noted)"
    print(f"   normalized        : {DEST}")
    print(f"   checksum          : {checksum_note}")
    if DEST.lower() == WALLET.lower():
        print("\n   ❌ destination IS our own wallet — that is a no-op, not a transfer")
        return 1
    print(f"   is our wallet?    : no")

    # 2 ── token identity — the silent-loss trap
    print(f"\n2 ── TOKEN IDENTITY (Avalanche has TWO 'USDC' contracts)")
    for label, c in (("NATIVE (want this)", USDC_NATIVE), ("bridged USDC.e (NOT this)", USDC_E_BRIDGED)):
        t = w3.eth.contract(address=c, abi=ERC20)
        try:
            sym, dec, nm = t.functions.symbol().call(), t.functions.decimals().call(), t.functions.name().call()
            print(f"   {label:<26} {c}  {sym} / {nm} / {dec} dec")
        except Exception as e:
            print(f"   {label:<26} {c}  read failed {type(e).__name__}")
    token = w3.eth.contract(address=USDC_NATIVE, abi=ERC20)
    dec = token.functions.decimals().call()
    assert dec == 6, "native USDC should be 6 decimals — stopping"

    # 3 ── balances
    print(f"\n3 ── BALANCES")
    bal = token.functions.balanceOf(WALLET).call()
    gas_wei = w3.eth.get_balance(WALLET)
    gas_price = w3.eth.gas_price
    gp_gwei = w3.to_wei(gas_price, "wei") / 1e9 if False else gas_price / 1e9
    print(f"   USDC (native)     : {bal / 10**dec:,.6f}")
    print(f"   AVAX for gas      : {gas_wei / 1e18:,.9f}")
    print(f"   gas price         : {gp_gwei:.4f} gwei")
    print(f"   destination USDC before: {token.functions.balanceOf(DEST).call() / 10**dec:,.6f}")
    token_before_dest = token.functions.balanceOf(DEST).call()

    # 4 ── gas quote
    # MEASURED BUG (2026-09-28): this was a flat `est_gas = 51_000`, used BOTH to quote the fee AND
    # as the transaction's gas limit. Avalanche's native USDC is a PROXY and its transfer() does not
    # fit in 51,000: a real send at 51,000 gas REVERTED with no data, and the SAME call at 100,000
    # succeeded — proven by replaying the failed tx at its own block across three gas limits.
    # 50,692 gas was consumed before it ran out, so the estimate was never "roughly right" — it was
    # short by construction, and the failure mode was a silently reverted payment.
    #
    # NOTE ON ORDER: the real gas estimate needs `amount`, which is resolved at step 5. So this step
    # quotes the FEE against a conservative fixed size (it only decides "is there enough gas"), and
    # the TRANSACTION's gas limit is estimated properly at step 5b, once `amount` exists. Estimating
    # before the amount exists is how the 51k constant survived unnoticed.
    est_gas_quote = 150_000          # conservative quote size for the "is gas sufficient" check
    fee_wei = est_gas_quote * gas_price
    print(f"   est. fee          : {fee_wei / 1e18:.9f} AVAX  (${fee_wei / 1e18 * 0:.0f} at AVAX, negligible)")
    print(f"   gas floor rule    : fee + ~20c equivalent; NO hard gate (Jordan)")
    if gas_wei < fee_wei * 3:
        print(f"   ❌ gas too thin to send safely")
        return 1
    print(f"   ✅ gas sufficient")

    # 5 ── the amount
    # --amount <USD> sends a SPECIFIC amount (Jordan 2026-09-22: "withdraw, convert $100
    # into USDC and then send it"). Absent --amount = full balance, which is the previous
    # behaviour, kept as the default so nothing already relying on this script changes.
    _amt_raw = None
    for _i, _a in enumerate(sys.argv):
        if _a == "--amount" and _i + 1 < len(sys.argv):
            _amt_raw = sys.argv[_i + 1]
        elif _a.startswith("--amount="):
            _amt_raw = _a.split("=", 1)[1]

    if _amt_raw is None:
        amount = bal
        _mode = "full balance"
    else:
        try:
            _usd = float(_amt_raw)
        except ValueError:
            print(f"\n   ❌ --amount {_amt_raw!r} is not a number")
            return 1
        if _usd <= 0:
            print(f"\n   ❌ --amount must be > 0 (got {_usd})")
            return 1
        amount = int(round(_usd * 10**dec))
        _mode = f"requested ${_usd:,.2f}"

    print(f"\n5 ── AMOUNT")
    print(f"   mode              : {_mode}")
    print(f"   sending           : {amount / 10**dec:,.6f} USDC")
    print(f"   wallet holds      : {bal / 10**dec:,.6f} USDC")
    if amount > bal:
        print(f"   ❌ INSUFFICIENT — requested {amount / 10**dec:,.6f} but wallet holds "
              f"{bal / 10**dec:,.6f}. Not partially filling an under-funded send.")
        return 1
    _left = bal - amount
    print(f"   remaining after   : {_left / 10**dec:,.6f} USDC")
    if _left < 10**dec:
        print(f"   ⚠️  leaves < $1 idle in the wallet")
    print(f"   sending           : {amount / 10**dec:,.6f} USDC")
    print(f"   token             : {USDC_NATIVE}  (native, 6 dec)")
    print(f"   chain             : Avalanche C-Chain (43114)")
    print(f"   from              : {WALLET}")
    print(f"   to                : {DEST}")

    # 5b ── GAS LIMIT (now that `amount` exists)
    # Estimate against the CHAIN, not a constant, with a hard floor. Avalanche's USDC is a proxy:
    # a real 51,000-gas send REVERTED where 100,000 succeeded (measured 2026-09-28).
    try:
        est_gas = int(w3.eth.estimate_gas({
            "from": WALLET, "to": USDC_NATIVE,
            "data": token.encode_abi("transfer", args=[DEST, amount])}))
        est_gas = max(est_gas * 2, 120_000)   # 2x headroom; below 120k is measurably unsafe here
        gas_src = "eth_estimateGas x2"
    except Exception as _e:
        est_gas = 150_000
        gas_src = f"estimate failed ({type(_e).__name__}) — conservative 150k"
    print(f"   gas limit         : {est_gas:,}   ({gas_src}, floor 120k)")

    # 6 ── simulate BEFORE signing (read-only)
    # eth_call ignores the gas limit we will actually send with, so it can pass while the REAL send
    # fails for want of gas. Simulate at the exact limit we intend to use — the earlier code signed
    # at 51k on the strength of an eth_call that was never bounded by it.
    print(f"\n6 ── SIMULATION (no signing)")
    try:
        w3.eth.call({"from": WALLET, "to": USDC_NATIVE,
                     "data": token.encode_abi("transfer", args=[DEST, amount]),
                     "gas": est_gas})
        print(f"   ✅ eth_call succeeded at the real gas limit ({est_gas:,})")
    except Exception as e:
        print(f"   ❌ eth_call failed at {est_gas:,} gas: {str(e)[:220]}")
        return 1

    if "--execute" not in sys.argv:
        print(f"\n{'='*96}")
        print(f"  PREFLIGHT PASSED — nothing signed yet. Re-run with --execute to broadcast.")
        print(f"{'='*96}")
        return 0

    # Sending capital out is class 4 — above every level ON PURPOSE. It needs an explicit
    # human instruction, carried here via --authorized-by "who: why" and written to
    # human-authorizations.jsonl. The check sits AFTER the dry-run gate: preparing and
    # simulating a transfer needs no licence; broadcasting one never escapes the check.
    _assert_may_act("move_capital", _authorized_by())

    # 7 ── EXECUTE. The key is read from disk and never printed, never logged, never returned.
    print(f"\n7 ── EXECUTING")
    from eth_account import Account
    # ── TENANT-AWARE SIGNING (fixed 2026-09-28) ────────────────────────────────────────────────
    # This hardcoded ONE key path — `/root/.blockrun/almanak-steward-key`, the LIVE treasury's — and
    # then asserted the resulting address matched `WALLET`. So the tool was single-tenant by
    # construction: it only ever worked for jordan. Running it for dadrian resolved WALLET correctly
    # (from steward_identity.wallet()) and then read JORDAN'S key, so the assertion tripped and the
    # send refused. The guard did its job — no money moved — but the tool could never serve a second
    # tenant at all.
    # `steward_identity.signer()` is the correct accessor: it resolves the tenant's OWN key from
    # STEWARD_KEY_PATH / the tenant's encrypted store AND enforces the tenant boundary, refusing a
    # key that does not match the resolved wallet. Use the guard the rest of the fleet uses rather
    # than re-implementing key loading here — a second key path is a second place to get it wrong.
    import steward_identity as _SI2
    acct = _SI2.signer()
    if acct is None:
        print("   ❌ REFUSING — no signing key resolved for this tenant.")
        return 1
    assert acct.address.lower() == WALLET.lower(), "key does not match the treasury wallet — STOP"
    print(f"   signer          : {acct.address}  (key never printed)")

    nonce = w3.eth.get_transaction_count(WALLET, "pending")
    # ── HEADROOM ON THE PRICE, NOT JUST THE LIMIT (fixed 2026-09-26) ──────────────────────
    # This sent `"gasPrice": gas_price` — the RAW `eth_gasPrice`, which on Avalanche IS the
    # current base fee with no margin. The base fee moves every block, so a tx built at this
    # snapshot is invalid the moment it ticks up: the node returns a hash, nothing propagates,
    # the nonce never advances, and this function waits out its full 180s receipt timeout for a
    # receipt that can never arrive. That exact shape emptied dadrian's book today. Same defect
    # class as lfj_bid_deploy's zero-slack approval: never price an action at the floor.
    from gas_reserve import gas_price_wei as _gpw
    _gp = _gpw(w3)
    print(f"   gas price       : {_gp/1e9*1e3:.6f} nAVAX (with headroom; floor "
          f"{gas_price/1e9*1e3:.6f})")
    tx = token.functions.transfer(DEST, amount).build_transaction({
        "from": WALLET, "nonce": nonce, "chainId": 43114,
        "gas": est_gas, "gasPrice": _gp,
    })
    signed = acct.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    h = tx_hash.hex()
    print(f"   broadcast       : 0x{h}")
    print(f"   explorer        : https://snowtrace.io/tx/0x{h}")

    print(f"\n8 ── VERIFY (read-back — a broadcast is not a delivery)")
    rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    print(f"   status          : {'✅ SUCCESS' if rcpt.status == 1 else '❌ REVERTED'}")
    print(f"   block           : {rcpt.blockNumber}")
    print(f"   gas used        : {rcpt.gasUsed:,}")
    after_sender = token.functions.balanceOf(WALLET).call()
    after_dest = token.functions.balanceOf(DEST).call()
    print(f"   sender after    : {after_sender / 10**dec:,.6f} USDC")
    print(f"   dest after      : {after_dest / 10**dec:,.6f} USDC")
    delta = after_dest - token_before_dest
    print(f"   dest delta      : {delta / 10**dec:+,.6f} USDC  "
          f"{'✅ matches the amount sent' if delta == amount else '❌ DOES NOT MATCH — investigate'}")

    print(f"\n{'='*96}")
    print(f"  SENT AND VERIFIED" if rcpt.status == 1 and delta == amount else "  ⚠️ CHECK THE RESULT ABOVE")
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
