#!/usr/bin/env python3
"""GTA Full Exit — close the Blackhole CL farm and remit USDC to Jordan.

Orchestrator-authorized (Jordan 2026-09-15, message 44467):
  "Send it to this address: 0xeEe3fe6C5604C1069a50690043DE57848826e6C9
   via USDC via avax network"

Jordan's rationale (his words): he wants the capital out for personal use; the
chop may drag on and he'd rather re-enter lower later. This is an ORCHESTRATOR
override of the $7.19 exit rule — the rule governs autonomous operation, this
is a deliberate human call.  Executes it faithfully, no re-litigating.

Steps (each verified on-chain, abort on any revert):
  1. Harvest BLACK emissions (collectRewards + claimReward) -> sell to WAVAX
  2. gauge.withdraw(#3479882)                     — unstake the NFT
  3. nfpm.decreaseLiquidity(#3479882, all)        — remove all liquidity
  4. nfpm.collect(#3479882)                       — pull tokens to wallet
  5. Drain remnant #3476545 (unstaked)            — decrease + collect
  6. Swap ALL WAVAX -> USDC (our Algebra pool)
  7. Transfer ALL USDC -> DEST

Usage:
  python3 gta_full_exit.py              # dry-run (default) — builds + simulates
  python3 gta_full_exit.py --execute --yes
"""
import argparse, json, sys, time, urllib.request
from eth_account import Account
from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

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
CHAIN_ID = 43114
SLIPPAGE = 0.03

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC  = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
POOL  = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"          # our Algebra WAVAX/USDC pool
BLACK_WAVAX_POOL = "0x14e4A5beD2e5E688EE1A5Ca3a4914250D1aBD573"  # solidly (concentrated=False)
NFPM  = "0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146"
ROUTER = "0xe946A9f39312E2346BA79DAb865B0e9A74f2F981"
FARMING_CENTER = "0xa47Ad2C95FaE476a73b85A355A5855aDb4b3A449"
ETERNAL_FARMING = "0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A"
GAUGE_MANAGER = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"

MAIN_ID = 3479882      # live staked position
REMNANT_ID = 3476545   # unstaked remnant ($0.21)

DEST = Web3.to_checksum_address("0xeEe3fe6C5604C1069a50690043DE57848826e6C9")

# ── ABIs ──────────────────────────────────────────────────────────────────
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "a", "type": "address"}], "name": "balanceOf",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "s", "type": "address"}, {"name": "v", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "o", "type": "address"}, {"name": "s", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "v", "type": "uint256"}],
     "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
]
NFPM_ABI = [
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "positions", "outputs": [
        {"name": "nonce", "type": "uint88"}, {"name": "operator", "type": "address"},
        {"name": "token0", "type": "address"}, {"name": "token1", "type": "address"},
        {"name": "deployer", "type": "address"}, {"name": "tickLower", "type": "int24"},
        {"name": "tickUpper", "type": "int24"}, {"name": "liquidity", "type": "uint128"},
        {"name": "feeGrowthInside0LastX128", "type": "uint256"},
        {"name": "feeGrowthInside1LastX128", "type": "uint256"},
        {"name": "tokensOwed0", "type": "uint128"}, {"name": "tokensOwed1", "type": "uint128"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "", "type": "uint256"}], "name": "ownerOf",
     "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"components": [
        {"name": "tokenId", "type": "uint256"}, {"name": "liquidity", "type": "uint128"},
        {"name": "amount0Min", "type": "uint256"}, {"name": "amount1Min", "type": "uint256"},
        {"name": "deadline", "type": "uint256"}], "name": "params", "type": "tuple"}],
     "name": "decreaseLiquidity", "outputs": [
        {"name": "amount0", "type": "uint256"}, {"name": "amount1", "type": "uint256"}],
     "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [
        {"name": "tokenId", "type": "uint256"}, {"name": "recipient", "type": "address"},
        {"name": "amount0Max", "type": "uint128"}, {"name": "amount1Max", "type": "uint128"}],
        "name": "params", "type": "tuple"}],
     "name": "collect", "outputs": [
        {"name": "amount0", "type": "uint256"}, {"name": "amount1", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
]
GAUGE_ABI = [{"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "withdraw",
              "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
ROUTER_ABI = [{"inputs": [
    {"name": "amountIn", "type": "uint256"}, {"name": "amountOutMin", "type": "uint256"},
    {"components": [{"name": "pair", "type": "address"}, {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"}, {"name": "stable", "type": "bool"},
                    {"name": "concentrated", "type": "bool"}, {"name": "receiver", "type": "address"}],
     "name": "routes", "type": "tuple[]"},
    {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}],
    "name": "swapExactTokensForTokens", "outputs": [{"name": "amounts", "type": "uint256[]"}],
    "stateMutability": "nonpayable", "type": "function"}]
FC_ABI = [
    {"inputs": [{"components": [
        {"name": "rewardToken", "type": "address"}, {"name": "bonusRewardToken", "type": "address"},
        {"name": "pool", "type": "address"}, {"name": "nonce", "type": "uint256"}],
        "name": "key", "type": "tuple"}, {"name": "tokenId", "type": "uint256"}],
     "name": "collectRewards", "outputs": [{"name": "reward", "type": "uint256"},
        {"name": "bonusReward", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "rewardToken", "type": "address"}, {"name": "to", "type": "address"},
                {"name": "amountRequested", "type": "uint256"}], "name": "claimReward",
     "outputs": [{"name": "reward", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "data", "type": "bytes[]"}], "name": "multicall",
     "outputs": [{"name": "results", "type": "bytes[]"}], "stateMutability": "payable", "type": "function"},
]
EF_ABI = [{"inputs": [{"name": "", "type": "address"}], "name": "incentiveKeys", "outputs": [
    {"name": "rewardToken", "type": "address"}, {"name": "bonusRewardToken", "type": "address"},
    {"name": "pool", "type": "address"}, {"name": "nonce", "type": "uint256"}],
    "stateMutability": "view", "type": "function"}]


# ── plumbing ──────────────────────────────────────────────────────────────
def send(w3, acct, tx, label, tries=3):
    """Sign, send, wait. Returns receipt or None on failure."""
    h = None
    for attempt in range(1, tries + 1):
        try:
            tx["nonce"] = w3.eth.get_transaction_count(acct.address, "pending")
            h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
            break
        except Exception as e:
            if ("nonce" in str(e).lower()) and attempt < tries:
                continue
            print(f"  ❌ {label} send failed: {str(e)[:160]}", file=sys.stderr)
            return None
    if h is None:
        print(f"  ❌ {label}: no tx hash after {tries} attempts", file=sys.stderr)
        return None
    r = w3.eth.wait_for_transaction_receipt(h, timeout=300)
    ok = r["status"] == 1
    print(f"  {'✅' if ok else '❌'} {label}: {h.hex()} status={r['status']}")
    return r if ok else None


def approve_if_needed(w3, acct, token, spender, amount, gp, dry_run):
    t = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
    cur = t.functions.allowance(acct.address, Web3.to_checksum_address(spender)).call()
    if cur >= amount:
        print(f"  ✓ already approved ({token[:10]}…)")
        return True
    tx = t.functions.approve(Web3.to_checksum_address(spender), amount).build_transaction({
        "from": acct.address, "gas": 70000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
    if dry_run:
        print(f"  [dry-run] approve {token[:10]}… -> {spender[:10]}…")
        return True
    return send(w3, acct, tx, f"approve {token[:10]}…") is not None


def swap(w3, acct, frm, to, pair, concentrated, amount_in, gp, dry_run, label):
    """Swap via Blackhole router (Trader Joe-style route struct).

    Returns the expected out (int) on success, None on failure. Callers MUST
    treat None as fatal — a silently-skipped swap would remit dust and look
    like a completed exit (the exact silent-failure class we refuse).
    """
    if amount_in <= 0:
        print(f"  ⏭  {label}: amount is 0 — nothing to swap")
        return None
    router = w3.eth.contract(address=Web3.to_checksum_address(ROUTER), abi=ROUTER_ABI)
    route = [{"pair": Web3.to_checksum_address(pair), "from": Web3.to_checksum_address(frm),
              "to": Web3.to_checksum_address(to), "stable": False,
              "concentrated": concentrated, "receiver": acct.address}]
    try:
        out = router.functions.swapExactTokensForTokens(
            amount_in, 0, route, acct.address, int(time.time()) + 600).call({"from": acct.address})
        expected = out[-1]
    except Exception as e:
        print(f"  ❌ {label} ROUTE PROBE FAILED: {str(e)[:180]}", file=sys.stderr)
        return None
    min_out = int(expected * (1 - SLIPPAGE))
    print(f"  {label}: expected out {expected} (min {min_out}, slip {SLIPPAGE:.0%})")
    tx = router.functions.swapExactTokensForTokens(
        amount_in, min_out, route, acct.address, int(time.time()) + 600).build_transaction({
        "from": acct.address, "gas": 600000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
    if dry_run:
        print(f"  [dry-run] {label}")
        return expected
    r = send(w3, acct, tx, label)
    return expected if r is not None else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    dry_run = not args.execute
    if args.execute and not args.yes:
        print("refusing --execute without --yes"); sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
    if not w3.is_connected():
        print("ERROR: RPC unreachable", file=sys.stderr); sys.exit(1)
    with open(_sw_keypath()) as f:
        acct = Account.from_key(f.read().strip())
    W = Web3.to_checksum_address(_sw_wallet())
    assert acct.address.lower() == W.lower(), "key/wallet mismatch — refusing"

    nfpm = w3.eth.contract(address=Web3.to_checksum_address(NFPM), abi=NFPM_ABI)
    gauge = w3.eth.contract(address=Web3.to_checksum_address(
        w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MANAGER),
                        abi=[{"inputs": [{"name": "", "type": "address"}], "name": "gauges",
                              "outputs": [{"name": "", "type": "address"}],
                              "stateMutability": "view", "type": "function"}]
                        ).functions.gauges(Web3.to_checksum_address(POOL)).call()), abi=GAUGE_ABI)
    fc = w3.eth.contract(address=Web3.to_checksum_address(FARMING_CENTER), abi=FC_ABI)
    ef = w3.eth.contract(address=Web3.to_checksum_address(ETERNAL_FARMING), abi=EF_ABI)
    gp = w3.eth.gas_price

    print("=" * 62)
    print(f"🛑  GTA FULL EXIT  —  {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print("=" * 62)
    print(f"  wallet : {W}")
    print(f"  dest   : {DEST}")
    print(f"  gauge  : {gauge.address}")

    key = ef.functions.incentiveKeys(Web3.to_checksum_address(POOL)).call()
    key = {"rewardToken": key[0], "bonusRewardToken": key[1], "pool": key[2], "nonce": key[3]}

    # ---- 1. harvest BLACK -> WAVAX ----
    print("\n🌾 1. Harvest BLACK emissions")
    claimable = 0
    try:
        cr = fc.functions.collectRewards(key, MAIN_ID).call({"from": W})
        claimable = int(cr[0]) / 1e18
    except Exception as e:
        print(f"  (claimable read failed: {str(e)[:90]})")
    black_bal = w3.eth.contract(address=Web3.to_checksum_address(BLACK),
                                abi=ERC20_ABI).functions.balanceOf(W).call() / 1e18
    print(f"  claimable {claimable:.6f} BLACK | wallet {black_bal:.6f} BLACK")
    if claimable > 0.0001:
        collect_cd = fc.encode_abi("collectRewards", [key, MAIN_ID])
        claim_cd = fc.encode_abi("claimReward", [key["rewardToken"], W, 0])
        tx = fc.functions.multicall([collect_cd, claim_cd]).build_transaction({
            "from": W, "gas": 600000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
        if dry_run:
            print("  [dry-run] collectRewards + claimReward")
        else:
            if send(w3, acct, tx, "collect+claim BLACK") is None:
                print("  ⚠️ harvest failed — continuing (not fatal to the exit)", file=sys.stderr)

    # ── Sep 15 2026 ROOT-CAUSE FIX (Jordan: "convert the black to USDC so it
    # goes with everything, instead of two separate things") ────────────────
    # BUG: this code read black_bal BEFORE harvesting, then approximated the
    # post-harvest total with `black_bal += claimable`. The claimable preview
    # is a DIFFERENT number from what the claim actually pays: on Sep 15 the
    # harvest paid 215.009714 BLACK but the stale preview said 116.644001, so
    # the swap sold only 116.64 and 98.365713 BLACK stranded — needing a whole
    # second recovery run (4 extra txs) to rescue $0.21.
    # FIX: never approximate. RE-READ the true on-chain balance after the
    # claim, sell the FULL balance, and let the WAVAX merge into the single
    # WAVAX->USDC swap + single remit that already follow. One exit, one send.
    if not dry_run:
        live_black = w3.eth.contract(address=Web3.to_checksum_address(BLACK),
                                     abi=ERC20_ABI).functions.balanceOf(W).call() / 1e18
        if abs(live_black - black_bal) > 0.000001:
            print(f"  ℹ️  BLACK re-read after harvest: {black_bal:.6f} -> {live_black:.6f} "
                  f"(the claimable preview understated the payout)")
        black_bal = live_black

    # sell the FULL BLACK balance so it merges into the single USDC remit
    if black_bal > 0.0001:
        amt = int(black_bal * 1e18)
        if approve_if_needed(w3, acct, BLACK, ROUTER, amt, gp, dry_run):
            got = swap(w3, acct, BLACK, WAVAX, BLACK_WAVAX_POOL, False, amt, gp, dry_run,
                       f"sell {black_bal:.4f} BLACK -> WAVAX")
            # Self-heal: one retry with a fresh balance read before giving up,
            # so a transient failure cannot strand emissions.
            if got is None and not dry_run:
                retry_bal = w3.eth.contract(address=Web3.to_checksum_address(BLACK),
                                            abi=ERC20_ABI).functions.balanceOf(W).call()
                if retry_bal > 0:
                    print(f"  ↻ retrying BLACK sell with a fresh balance read "
                          f"({retry_bal/1e18:.6f})", file=sys.stderr)
                    approve_if_needed(w3, acct, BLACK, ROUTER, retry_bal, gp, dry_run)
                    got = swap(w3, acct, BLACK, WAVAX, BLACK_WAVAX_POOL, False, retry_bal,
                               gp, dry_run, f"retry sell {retry_bal/1e18:.4f} BLACK -> WAVAX")
            if got is None and not dry_run:
                print(f"  ⚠️ BLACK sell FAILED — {black_bal:.4f} BLACK left in the wallet. "
                      "Exit continues (principal is unaffected) but this MUST be recovered: "
                      "run the BLACK recovery leg before calling the wind-down complete.",
                      file=sys.stderr)
        else:
            print("  ⚠️ BLACK approve failed — emissions will strand", file=sys.stderr)
    else:
        print("  nothing to sell")

    # ---- 2-4. unstake, remove liquidity, collect (main position) ----
    print("\n🔓 2. Unstake #%d" % MAIN_ID)
    tx = gauge.functions.withdraw(MAIN_ID).build_transaction({
        "from": W, "gas": 350000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
    if dry_run:
        print("  [dry-run] gauge.withdraw(%d)" % MAIN_ID)
    elif send(w3, acct, tx, f"gauge.withdraw({MAIN_ID})") is None:
        print("  ❌ unstake failed — ABORT (do not decrease against a staked NFT)", file=sys.stderr)
        return 1

    for label, tid in (("3. Remove liquidity #%d" % MAIN_ID, MAIN_ID),
                       ("3b. Drain remnant #%d" % REMNANT_ID, REMNANT_ID)):
        try:
            pos = nfpm.functions.positions(tid).call()
        except Exception as e:
            print(f"\n⚠️ {label}: cannot read positions() — {str(e)[:120]}"); continue
        liq = pos[7]
        owed0, owed1 = pos[10], pos[11]
        print(f"\n💧 {label}  liq={liq}  owed={owed0}/{owed1}")
        if liq > 0:
            tx = nfpm.functions.decreaseLiquidity(
                {"tokenId": tid, "liquidity": liq, "amount0Min": 0, "amount1Min": 0,
                 "deadline": int(time.time()) + 900}).build_transaction({
                "from": W, "gas": 400000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
            if dry_run:
                print(f"  [dry-run] decreaseLiquidity({tid}, {liq})")
            elif send(w3, acct, tx, f"decreaseLiquidity({tid})") is None:
                print(f"  ⚠️ decrease failed for #{tid} — continuing", file=sys.stderr)
        # always collect (fees owed may exist even at liq=0)
        tx = nfpm.functions.collect(
            {"tokenId": tid, "recipient": W, "amount0Max": 2**128 - 1,
             "amount1Max": 2**128 - 1}).build_transaction({
            "from": W, "gas": 300000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
        if dry_run:
            print(f"  [dry-run] collect({tid})")
        else:
            send(w3, acct, tx, f"collect({tid})")

    # ---- 6. swap all WAVAX -> USDC ----
    print("\n💱 4. Swap WAVAX -> USDC")
    wavax_bal = w3.eth.contract(address=Web3.to_checksum_address(WAVAX),
                                abi=ERC20_ABI).functions.balanceOf(W).call()
    print(f"  wallet WAVAX: {wavax_bal/1e18:.6f}")
    if wavax_bal > 0:
        if not approve_if_needed(w3, acct, WAVAX, ROUTER, wavax_bal, gp, dry_run):
            print("  ❌ WAVAX approve failed — ABORT before remitting dust", file=sys.stderr)
            return 1
        got = swap(w3, acct, WAVAX, USDC, POOL, True, wavax_bal, gp, dry_run,
                   f"sell {wavax_bal/1e18:.6f} WAVAX -> USDC")
        if got is None:
            print("  ❌ WAVAX->USDC swap FAILED — ABORT. Capital is safe in the wallet as "
                  "WAVAX; do NOT remit dust and call this a completed exit.", file=sys.stderr)
            return 1
        if not dry_run:
            print(f"  ✅ swapped {wavax_bal/1e18:.6f} WAVAX -> USDC")
    elif wavax_bal == 0:
        print("  (no WAVAX in wallet — expected in dry-run before liquidity is removed)")

    # ── PRE-REMIT SWEEP (Jordan, Sep 15: "so it gets sent with everything,
    # instead of two separate things" — sending twice costs double gas) ─────
    # Order matters: sweep BLACK -> WAVAX FIRST, then WAVAX -> USDC. Doing it
    # the other way round would re-strand the WAVAX that BLACK just produced.
    usdc_bal = 0
    if not dry_run:
        for _ in range(2):   # pass 1: BLACK->WAVAX, WAVAX->USDC; pass 2: catch leftovers
            resid_b = w3.eth.contract(address=Web3.to_checksum_address(BLACK),
                                      abi=ERC20_ABI).functions.balanceOf(W).call()
            if resid_b > 1000:   # > 0.000001 BLACK
                print(f"  ↻ sweep: {resid_b/1e18:.6f} BLACK left behind — folding into the exit",
                      file=sys.stderr)
                if approve_if_needed(w3, acct, BLACK, ROUTER, resid_b, gp, dry_run):
                    swap(w3, acct, BLACK, WAVAX, BLACK_WAVAX_POOL, False, resid_b, gp,
                         dry_run, f"sweep {resid_b/1e18:.6f} BLACK -> WAVAX")
            resid_w = w3.eth.contract(address=Web3.to_checksum_address(WAVAX),
                                      abi=ERC20_ABI).functions.balanceOf(W).call()
            if resid_w > 1000:   # > 0.000001 WAVAX
                print(f"  ↻ sweep: {resid_w/1e18:.6f} WAVAX left behind — folding into the exit",
                      file=sys.stderr)
                if approve_if_needed(w3, acct, WAVAX, ROUTER, resid_w, gp, dry_run):
                    swap(w3, acct, WAVAX, USDC, POOL, True, resid_w, gp, dry_run,
                         f"sweep {resid_w/1e18:.6f} WAVAX -> USDC")
        usdc_bal = w3.eth.contract(address=Web3.to_checksum_address(USDC),
                                   abi=ERC20_ABI).functions.balanceOf(W).call()

    # ---- 7. send all USDC to Jordan (ONE transfer, everything included) ----
    print("\n📤 5. Send USDC -> Jordan")
    if dry_run:
        usdc_bal = w3.eth.contract(address=Web3.to_checksum_address(USDC),
                                   abi=ERC20_ABI).functions.balanceOf(W).call()
    print(f"  USDC to send: {usdc_bal/1e6:.6f}")
    # Guard: never remit a dust-only amount as if the exit succeeded.
    if not dry_run and usdc_bal < 1_000_000:   # < 1.00 USDC
        print(f"  ❌ REFUSING to remit {usdc_bal/1e6:.6f} USDC — that is dust, which would "
              "look like a completed exit but is not. Investigate the upstream steps.",
              file=sys.stderr)
        return 1
    if usdc_bal > 0:
        u = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
        tx = u.functions.transfer(DEST, usdc_bal).build_transaction({
            "from": W, "gas": 100000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
        if dry_run:
            print(f"  [dry-run] transfer {usdc_bal/1e6:.6f} USDC -> {DEST}")
        elif send(w3, acct, tx, f"send {usdc_bal/1e6:.6f} USDC -> Jordan") is None:
            print("  ❌ transfer failed", file=sys.stderr)
            return 1

    print("\n" + ("✅ DRY-RUN complete — no funds moved."
                  if dry_run else "✅ EXIT COMPLETE."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
