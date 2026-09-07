#!/usr/bin/env python3
"""
Agentic Treasury — Trader Joe V2 AVAX/USDC LP Entry (Direct LBRouter) — EXECUTION
Real signing + sending path. Builds on the dry-run scaffold but actually:
  1. Reads LIVE price + active bin from chain
  2. Approves USDC + WAVAX to the LBRouter
  3. Calls addLiquidity with a Curve distribution
  4. Verifies the position on-chain

Modes:
  --dry-run (default): build + estimate, NO funds move.
  --execute: real LP open (requires funded steward wallet + --yes).
"""
import argparse, json, os, sys, time
from web3 import Web3

AVALANCHE_RPC = "https://api.avax.network/ext/bc/C/rpc"
CHAIN_ID = 43114
LBROUTER = "0x18556DA13313f3532c54711497A8FedAC273220E"  # LFJ V2.2 router (matches V2.2 factory 0xb43120c4)
LBFACTORY = "0xb43120c4745967fa9b93e79c149e66b0f2d6fe0c"  # LFJ V2.2 factory
LBPAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"  # WAVAX/USDC binStep 10 (canonical LFJ V2.2)
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BIN_STEP = 10
BIN_ID_OFFSET = 8388608
STEWARD_WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
STEWARD_KEY_FILE = "/root/.blockrun/almanak-steward-key"

LBROUTER_ABI = [{
    "inputs": [{"components": [
        {"name": "tokenX", "type": "address"},
        {"name": "tokenY", "type": "address"},
        {"name": "binStep", "type": "uint256"},
        {"name": "amountX", "type": "uint256"},
        {"name": "amountY", "type": "uint256"},
        {"name": "amountXMin", "type": "uint256"},
        {"name": "amountYMin", "type": "uint256"},
        {"name": "activeIdDesired", "type": "uint256"},
        {"name": "idSlippage", "type": "uint256"},
        {"name": "deltaIds", "type": "int256[]"},
        {"name": "distributionX", "type": "uint256[]"},
        {"name": "distributionY", "type": "uint256[]"},
        {"name": "to", "type": "address"},
        {"name": "refundTo", "type": "address"},
        {"name": "deadline", "type": "uint256"},
    ], "name": "liquidityParameters", "type": "tuple"}],
    "name": "addLiquidity",
    "outputs": [
        {"name": "amountXAdded", "type": "uint256"},
        {"name": "amountYAdded", "type": "uint256"},
        {"name": "amountXLeft", "type": "uint256"},
        {"name": "amountYLeft", "type": "uint256"},
        {"name": "depositIds", "type": "uint256[]"},
        {"name": "liquidityMinted", "type": "uint256[]"},
    ],
    "stateMutability": "nonpayable", "type": "function",
}, {
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "amountOutMin", "type": "uint256"},
        {"name": "swapParameters", "components": [
            {"name": "pairBinSteps", "type": "uint256[]"},
            {"name": "versions", "type": "uint8[]"},
            {"name": "tokenPath", "type": "address[]"},
        ], "type": "tuple"},
        {"name": "to", "type": "address"},
        {"name": "deadline", "type": "uint256"},
    ],
    "name": "swapExactTokensForTokens",
    "outputs": [{"name": "amounts", "type": "uint256[]"}],
    "stateMutability": "nonpayable", "type": "function",
}]

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "a", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "s", "type": "address"}, {"name": "v", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "o", "type": "address"}, {"name": "s", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]

def get_active_id(w3):
    raw = w3.eth.call({'to': Web3.to_checksum_address(LBPAIR), 'data': '0xdbe65edc'})
    return int.from_bytes(raw, 'big')

def get_live_price(w3, active_id):
    """Live WAVAX/USDC price in USDC per WAVAX.
    Primary: DexScreener (works even when on-chain pair reverts — the pair
    contract at 0x864d4e... is intermittently dead on public RPCs).
    Fallback 1: on-chain sqrtPrice via eth_call (when pair is alive).
    Fallback 2: active-bin math (always available, accurate to ~0.1%).
    Hard floor: 6.50 if everything fails (prevents deploy math from blowing up).
    """
    import urllib.request
    # --- Primary: DexScreener (doesn't depend on pair contract) ---
    for pair in (
        "0x864d4e5ee7318e97483db7eb0912e09f161516ea",  # canonical LFJ V2.2 WAVAX/USDC
        "0xD446eb1660F766d533BeCeEf890Df7A69d26f7d1",
    ):
        try:
            req = urllib.request.Request(
                f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{pair}",
                headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                d = json.loads(resp.read())
                if d.get("pairs"):
                    return float(d["pairs"][0]["priceUsd"])
        except Exception:
            continue
    # --- Fallback 1: on-chain sqrtPrice (when pair contract is alive) ---
    try:
        sqrt_raw = w3.eth.call({
            'to': Web3.to_checksum_address(LBPAIR),
            'data': '0x62fa3338',  # sqrtPrice()
        })
        if sqrt_raw and sqrt_raw != '0x':
            sqrt_price = int(sqrt_raw, 16)
            price = float((sqrt_price / (2**96)) ** 2)
            if price > 0.01:
                return price
    except Exception:
        pass
    # --- Fallback 2: active bin math (always works, no contract call) ---
    try:
        step = 10  # binStep
        price = (1 + step/10000) ** (active_id - 2**23) * 10**12
        if price > 0.01:
            return price
    except Exception:
        pass
    # Hard floor — prevents zero/negative price from breaking deploy math.
    return 6.50

def get_wavax_market_price():
    """Real USD market price of WAVAX — used ONLY for wallet affordability checks.
    The LP pair price (get_live_price) is used for deposit math; this market
    price is used to decide whether the wallet can afford a deploy at all.
    """
    import urllib.request
    for url in (
        "https://api.coingecko.com/api/v3/simple/price?ids=wavax&vs_currencies=usd",
        "https://api.binance.com/api/v3/ticker/price?symbol=WAVAXUSDT",
    ):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                d = json.loads(resp.read())
            if "wavax" in d and d["wavax"].get("usd"):
                return float(d["wavax"]["usd"])
            if d.get("price"):
                return float(d["price"])
        except Exception:
            continue
    return None

def curve_dist_from_range(active_id, spread, distribution="gaussian"):
    """Distribution of liquidity across bins that LFJ accepts. Each bin gets a
    non-zero share and the array sums to exactly 1e18 (100%), or LFJ reverts
    with ZeroShares.

    distribution:
      "gaussian" — narrow Gaussian (sigma 1.4/1.7). Concentrates at active bin
                   (max fee capture in tight chop) but STARVES tail bins, so
                   wide spreads revert on LBPair__ZeroShares (sub-wei tail).
      "flat"     — wide-sigma curve (sigma scales with spread). Keeps tail bins
                   funded so wider spreads (15-25 bins curve, ~30 bid-ask) pass
                   the router. Slightly less per-bin concentration but stays in
                   range longer and survives small price moves.

    The router has NO hard spread cap (verified in LBRouter.sol/LBPair.sol
    2026-09-07) — the only constraint is LBPair__ZeroShares: ANY bin with
    sub-wei shares reverts the whole tx. So spread width is bounded by how much
    capital lands in the tail bins, which the distribution controls.
    """
    import math
    neg_ids = [-1*(el+1) for el in range(spread)]
    pos_ids = [el+1 for el in range(spread)]
    if distribution == "flat":
        # Wide-sigma: sigma scales with spread so tail bins stay funded.
        # sigma = max(1.4, spread * 0.45) keeps the curve flat enough that the
        # tail bin gets a meaningful share at any spread.
        sigmaX = max(1.4, spread * 0.45)
        sigmaY = max(1.4, spread * 0.45)
    else:
        sigmaX = 1.7 if len(pos_ids) >= 10 else 1.4
        sigmaY = 1.7 if len(neg_ids) >= 10 else 1.4
    AX = 1/(math.sqrt(math.pi*2)*sigmaX)
    distX = [0]*len(neg_ids) + [AX] + [2*AX*math.exp(-0.5*((ind+1)/sigmaX)**2) for ind in range(len(pos_ids))]
    AY = 1/(math.sqrt(math.pi*2)*sigmaY)
    RY = len(neg_ids)
    distY = [2*AY*math.exp(-0.5*((RY-ind)/sigmaY)**2) for ind in range(len(neg_ids))] + [AY] + [0]*len(pos_ids)
    dx = [int(round(x*1e18)) for x in distX]
    dy = [int(round(y*1e18)) for y in distY]
    def _norm(arr):
        # LFJ verifyAmounts requires bins below active to hold ONLY Y (0 X)
        # and bins above active to hold ONLY X (0 Y). Preserve structural
        # zeros; floor only non-zero entries at 1 wei, then rebalance the
        # largest non-zero entry so the array sums to exactly 1e18.
        arr = [max(1, v) if v > 0 else 0 for v in arr]
        s = sum(arr)
        nz = [i for i, v in enumerate(arr) if v > 0]
        if nz:
            idx = max(nz, key=lambda i: arr[i])
            arr[idx] += 10**18 - s
        return arr
    return _norm(dx), _norm(dy)


def build_liquidity_params(amount_usd, bin_spread, active_id, price, allocation_ratio=0.5, distribution="flat"):
    usdc_amount = amount_usd * allocation_ratio
    wavax_amount = (amount_usd * (1.0 - allocation_ratio)) / price
    delta_ids = list(range(-bin_spread, bin_spread + 1))
    distX, distY = curve_dist_from_range(active_id, bin_spread, distribution)
    return {
        "tokenX": Web3.to_checksum_address(WAVAX),
        "tokenY": Web3.to_checksum_address(USDC),
        "binStep": BIN_STEP,
        "amountX": int(wavax_amount * 1e18),
        "amountY": int(usdc_amount * 1e6),
        "amountXMin": 0,
        "amountYMin": 0,
        "activeIdDesired": active_id,
        "idSlippage": bin_spread,
        "deltaIds": delta_ids,
        "distributionX": distX,
        "distributionY": distY,
        "to": STEWARD_WALLET,
        "refundTo": STEWARD_WALLET,
        "deadline": int(time.time()) + 600,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--amount", type=float, required=True)
    ap.add_argument("--bin-spread", type=int, default=5,
                    help="half-width in bins (Jordan's lever: ±5 = 11 bins is the "
                    "PROVEN setting — ±11 reverts on LFJ, verified by read-only "
                    "eth_call simulation 2026-09-03)")
    ap.add_argument("--allocation", type=float, default=0.5,
                    help="USDC allocation ratio (0.0-1.0, default 0.5 for 50/50)")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    w3 = Web3(Web3.HTTPProvider(AVALANCHE_RPC))
    if not w3.is_connected():
        print("ERROR: cannot connect to Avalanche RPC", file=sys.stderr); sys.exit(1)

    active_id = get_active_id(w3)
    price = get_live_price(w3, active_id)
    print("=" * 50)
    print("💧 Agentic Treasury — Trader Joe V2 AVAX/USDC LP Entry (Direct)")
    print("=" * 50)
    print(f"\n📊 Pool: {LBPAIR}")
    print(f"  Active bin: {active_id} | binStep: {BIN_STEP}")
    print(f"  Live price: ${price:.4f} USDC/WAVAX")
    print(f"  Range: bins {active_id - args.bin_spread} – {active_id + args.bin_spread} (±{args.bin_spread})")
    print(f"  Deploy: ${args.amount:.2f} ({args.allocation*100:.0f}% USDC / {(1-args.allocation)*100:.0f}% WAVAX)")
    print(f"  Wallet: {STEWARD_WALLET}")

    params = build_liquidity_params(args.amount, args.bin_spread, active_id, price, args.allocation)
    print(f"\n📦 LiquidityParameters:")
    print(f"  amountX (WAVAX): {params['amountX']/1e18:.6f}")
    print(f"  amountY (USDC):  {params['amountY']/1e6:.2f}")
    print(f"  deltaIds: {params['deltaIds']}")

    # Balances
    usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
    wavax = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
    usdc_bal = usdc.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()/1e6
    wavax_bal = wavax.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()/1e18
    avax_bal = w3.eth.get_balance(Web3.to_checksum_address(STEWARD_WALLET))/1e18
    print(f"\n💰 Steward wallet balances:")
    print(f"  USDC:  ${usdc_bal:.2f}")
    print(f"  WAVAX: {wavax_bal:.6f}")
    print(f"  AVAX:  {avax_bal:.6f} (gas)")

    # Check we have enough.
    # Affordability uses MARKET price for WAVAX — what the wallet would get
    # if it sold WAVAX for USDC externally. The deposit math below uses the
    # LP pair price (price), which is correct for the contract call.
    need_usdc = params['amountY']/1e6
    need_wavax = params['amountX']/1e18
    market_price = get_wavax_market_price()
    if market_price:
        wallet_value_usd = usdc_bal + wavax_bal * market_price
        deploy_cost_usd = need_usdc + need_wavax * market_price
    else:
        wallet_value_usd = usdc_bal + wavax_bal * price
        deploy_cost_usd = need_usdc + need_wavax * price
    if wallet_value_usd < deploy_cost_usd - 0.20:
        price_src = f" (market ${market_price:.2f})" if market_price else f" (LP ${price:.2f})"
        print(f"\n❌ Wallet value ${wallet_value_usd:.2f}{price_src} below deploy target "
              f"${deploy_cost_usd:.2f} — insufficient even after rebalancing.", file=sys.stderr)
        sys.exit(1)
    if usdc_bal < need_usdc:
        print(f"\n⚠️  Low USDC (${usdc_bal:.2f}) but WAVAX available — will rebalance in execute.")
    if wavax_bal < need_wavax:
        print(f"\n⚠️  Low WAVAX ({wavax_bal:.4f}) but USDC available — will rebalance in execute.")

    if args.execute:
        if not args.yes:
            print("\n❌ Refusing to execute without --yes. Dry-run only."); sys.exit(1)
        if not os.path.exists(STEWARD_KEY_FILE):
            print("\n❌ Steward key not found. Cannot sign.", file=sys.stderr); sys.exit(1)
        key = open(STEWARD_KEY_FILE).read().strip()
        acct = w3.eth.account.from_key(key)
        if acct.address.lower() != STEWARD_WALLET.lower():
            print("\n❌ Key mismatch!", file=sys.stderr); sys.exit(1)

        # 1. Approve USDC + WAVAX to LBRouter
        router_addr = Web3.to_checksum_address(LBROUTER)
        max_uint = 2**256 - 1
        for token, name in [(USDC, "USDC"), (WAVAX, "WAVAX")]:
            c = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
            allowance = c.functions.allowance(acct.address, router_addr).call()
            if allowance < max_uint:
                print(f"\n🔓 Approving {name} to LBRouter...")
                tx = c.functions.approve(router_addr, max_uint).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                signed = acct.sign_transaction(tx)
                h = _send_with_nonce_retry(w3, acct, tx)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ {name} approved: {h.hex()} status={rcpt['status']}")
            else:
                print(f"  ✅ {name} already approved")

        # 1b. Rebalance to ~50/50 if the wallet is imbalanced.
        # Handles three cases:
        #   (a) WAVAX short, USDC ample  → swap USDC → WAVAX
        #   (b) USDC short, WAVAX ample  → swap WAVAX → USDC
        #   (c) BOTH short relative to target — one side has more total value.
        #       Swap from the richer side to cover the poorer side so the full
        #       deploy amount can go through instead of scaling down.
        need_wavax = params['amountX']/1e18
        need_usdc = params['amountY']/1e6
        val_wavax = wavax_bal * price   # USD value of WAVAX holding
        val_usdc = usdc_bal             # USD value of USDC holding
        total_val = val_wavax + val_usdc
        if total_val < need_wavax * price + need_usdc - 0.15:
            print(f"\\n⚠️  Wallet total (${total_val:.2f}) below deploy target "
                  f"(${need_wavax*price+need_usdc:.2f}) — will deploy what fits.")
        elif wavax_bal < need_wavax and usdc_bal > need_usdc + 0.1:
            swap_usdc = (need_wavax - wavax_bal) * price
            swap_usdc = min(swap_usdc, usdc_bal - 0.05)
            if swap_usdc > 0.01:
                print(f"\\n🔄 Swapping ${swap_usdc:.2f} USDC -> WAVAX (need {need_wavax:.4f} WAVAX)...")
                router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
                amount_in = int(swap_usdc * 1e6)
                amount_out_min = int((swap_usdc / price) * 0.99 * 1e18)
                tx = router.functions.swapExactTokensForTokens(
                    amount_in, amount_out_min,
                    ([BIN_STEP], [3], [Web3.to_checksum_address(USDC), Web3.to_checksum_address(WAVAX)]),
                    acct.address, int(time.time()) + 600
                ).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                signed = acct.sign_transaction(tx)
                h = _send_with_nonce_retry(w3, acct, tx)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ Swap tx: {h.hex()} status={rcpt['status']}")
                if rcpt['status'] != 1:
                    print("  ❌ Swap REVERTED!", file=sys.stderr); sys.exit(1)
                wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
                usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
                print(f"  WAVAX now: {wavax_bal:.6f} | USDC now: ${usdc_bal:.2f}")
        elif usdc_bal < need_usdc and wavax_bal > need_wavax + 0.01:
            # SWAP HEADROOM (Sep 7 2026): swap ~1.5% MORE WAVAX than the bare
            # need so slippage can't leave the post-swap USDC a cent short of
            # need. Previously this swapped exactly (need_usdc - usdc_bal)/price
            # with a 99% min_out; in a fast market the 1% slippage left USDC a
            # few cents under need, the safety check (need*0.99) passed, and
            # addLiquidity reverts on the sub-cent shortfall -> flat pool.
            swap_wavax = ((need_usdc - usdc_bal) / price) * 1.015
            swap_wavax = min(swap_wavax, wavax_bal - 0.1)
            if swap_wavax > 0.001:
                print(f"\\n🔄 Swapping {swap_wavax:.4f} WAVAX -> USDC (need ${need_usdc:.2f} USDC, +1.5% headroom)...")
                router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
                amount_in = int(swap_wavax * 1e18)
                amount_out_min = int(swap_wavax * price * 0.99 * 1e6)
                tx = router.functions.swapExactTokensForTokens(
                    amount_in, amount_out_min,
                    ([BIN_STEP], [3], [Web3.to_checksum_address(WAVAX), Web3.to_checksum_address(USDC)]),
                    acct.address, int(time.time()) + 300
                ).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                signed = acct.sign_transaction(tx)
                h = _send_with_nonce_retry(w3, acct, tx)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ Swap tx: {h.hex()} status={rcpt['status']}")
                if rcpt['status'] != 1:
                    print("  ❌ Swap REVERTED!", file=sys.stderr); sys.exit(1)
                wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
                usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
                print(f"  WAVAX now: {wavax_bal:.6f} | USDC now: ${usdc_bal:.2f}")
        elif wavax_bal < need_wavax and usdc_bal < need_usdc:
            # Both short — swap from the richer side to cover the poorer side.
            # Move the poorer side up to its target, then re-check.
            if val_wavax > val_usdc:
                # WAVAX-rich: swap WAVAX → USDC to cover USDC shortfall
                usdc_short = need_usdc - usdc_bal
                wavax_to_swap = (usdc_short / price) * 1.015
                wavax_to_swap = min(wavax_to_swap, wavax_bal - need_wavax - 0.01)
                if wavax_to_swap > 0.001:
                    print(f"\\n🔄 Both short — WAVAX-rich: swapping {wavax_to_swap:.4f} WAVAX -> USDC "
                          f"(need ${usdc_short:.2f} more USDC)...")
                    router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
                    amount_in = int(wavax_to_swap * 1e18)
                    amount_out_min = int(wavax_to_swap * price * 0.99 * 1e6)
                    tx = router.functions.swapExactTokensForTokens(
                        amount_in, amount_out_min,
                        ([BIN_STEP], [3], [Web3.to_checksum_address(WAVAX), Web3.to_checksum_address(USDC)]),
                        acct.address, int(time.time()) + 300
                    ).build_transaction({
                        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                        "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                    signed = acct.sign_transaction(tx)
                    h = _send_with_nonce_retry(w3, acct, tx)
                    rcpt = w3.eth.wait_for_transaction_receipt(h)
                    print(f"  ✅ Swap tx: {h.hex()} status={rcpt['status']}")
                    if rcpt['status'] != 1:
                        print("  ❌ Swap REVERTED!", file=sys.stderr); sys.exit(1)
                    wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
                    usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
                    print(f"  WAVAX now: {wavax_bal:.6f} | USDC now: ${usdc_bal:.2f}")
            else:
                # USDC-rich: swap USDC → WAVAX to cover WAVAX shortfall
                wavax_short = need_wavax - wavax_bal
                usdc_to_swap = wavax_short * price
                usdc_to_swap = min(usdc_to_swap, usdc_bal - need_usdc - 0.05)
                if usdc_to_swap > 0.01:
                    print(f"\\n🔄 Both short — USDC-rich: swapping ${usdc_to_swap:.2f} USDC -> WAVAX "
                          f"(need {wavax_short:.4f} more WAVAX)...")
                    router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
                    amount_in = int(usdc_to_swap * 1e6)
                    amount_out_min = int((usdc_to_swap / price) * 0.99 * 1e18)
                    tx = router.functions.swapExactTokensForTokens(
                        amount_in, amount_out_min,
                        ([BIN_STEP], [3], [Web3.to_checksum_address(USDC), Web3.to_checksum_address(WAVAX)]),
                        acct.address, int(time.time()) + 600
                    ).build_transaction({
                        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                        "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                    signed = acct.sign_transaction(tx)
                    h = _send_with_nonce_retry(w3, acct, tx)
                    rcpt = w3.eth.wait_for_transaction_receipt(h)
                    print(f"  ✅ Swap tx: {h.hex()} status={rcpt['status']}")
                    if rcpt['status'] != 1:
                        print("  ❌ Swap REVERTED!", file=sys.stderr); sys.exit(1)
                    wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
                    usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
                    print(f"  WAVAX now: {wavax_bal:.6f} | USDC now: ${usdc_bal:.2f}")

        # 2. addLiquidity — use the calculated parameters with safety checks
        # (Only reduce if wallet balance is insufficient, never increase)
        wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
        usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
        need_x = params['amountX']/1e18
        need_y = params['amountY']/1e6
        
        # Safety check: ensure we have enough funds (with small buffer)
        buf_x = 0.005  # keep ~0.005 WAVAX free (dust/gas)
        buf_y = 0.05   # keep ~$0.05 USDC free
        available_x = max(0, wavax_bal - buf_x)
        available_y = max(0, usdc_bal - buf_y)
        
        if available_x < need_x * 0.99 or available_y < need_y * 0.99:
            print(f"\n⚠️  Insufficient funds after rebalancing:")
            print(f"   Need: {need_x:.6f} WAVAX + ${need_y:.2f} USDC")
            print(f"   Have: {available_x:.6f} WAVAX + ${available_y:.2f} USDC")
            print(f"   Proceeding with reduced deployment to match available funds.")
            # Scale down proportionally to what we have
            scale_x = available_x / need_x if need_x > 0 else 1
            scale_y = available_y / need_y if need_y > 0 else 1
            scale = min(scale_x, scale_y, 1.0)  # Never scale above 1.0
            params['amountX'] = int(params['amountX'] * scale)
            params['amountY'] = int(params['amountY'] * scale)
            print(f"   Deploying: {params['amountX']/1e18:.6f} WAVAX + ${params['amountY']/1e6:.2f} USDC")
        else:
            print(f"\n💧 Adding liquidity (as calculated: {need_x:.6f} WAVAX + ${need_y:.2f} USDC)...")
        
        router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
        tx = router.functions.addLiquidity(params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 1_000_000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        signed = acct.sign_transaction(tx)
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ addLiquidity tx: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ TX REVERTED!", file=sys.stderr); sys.exit(1)

        # 3. Verify position on-chain (balance drop + position scan)
        # SETTLED VERIFY (Sep 7 2026): the public Avalanche RPC lags a
        # freshly-mined addLiquidity — reading balances/bins immediately after
        # the receipt can show stale balances (0 drop) and 0 bins, falsely
        # reporting "NOT verified / funds may be stuck" right after a GOOD
        # deploy (happened live — alarmed Jordan, funds were fine, RPC lag).
        # Re-read up to 3x ~3s apart, accepting verification on ANY read that
        # shows the position (bins>0) or a real balance drop. Only after all
        # settled reads fail do we declare it a genuine problem.
        print("\n🔍 Verifying position (settled re-read)...")
        verified = False
        verify_msgs = []
        for vtry in range(3):
            new_usdc = usdc.functions.balanceOf(acct.address).call()/1e6
            new_wavax = wavax.functions.balanceOf(acct.address).call()/1e18
            usdc_dropped = usdc_bal - new_usdc
            wavax_dropped = wavax_bal - new_wavax
            bal_dropped = (usdc_dropped > 0.50 and wavax_dropped > 0.01)
            # Probe bins (settled) for the LP position
            found_liquidity = 0
            try:
                bal_sel = "0x00fdd58e"
                addr_hex = acct.address.lower().replace("0x", "")
                for offset in range(-args.bin_spread - 2, args.bin_spread + 3):
                    bin_id = active_id + offset
                    data = bal_sel + addr_hex.zfill(64) + hex(bin_id)[2:].zfill(64)
                    try:
                        b = int(w3.eth.call({'to': Web3.to_checksum_address(LBPAIR), 'data': data}), 16)
                    except Exception:
                        continue
                    if b > 0:
                        found_liquidity += 1
            except Exception as e:
                verify_msgs.append(f"attempt {vtry+1}: bin scan error {e}")
            bins_ok = found_liquidity >= args.bin_spread
            verify_msgs.append(
                f"attempt {vtry+1}: bins={found_liquidity} "
                f"USDC_drop=${usdc_dropped:.2f} WAVAX_drop={wavax_dropped:.4f}")
            if bins_ok:
                verified = True
                print(f"  ✅ {found_liquidity} bins with liquidity confirmed on-chain")
                break
            if bal_dropped:
                # balances moved — the tx went through (fallback)
                verified = True
                print(f"  ✅ Balance moved: USDC -${usdc_dropped:.2f}, WAVAX -{wavax_dropped:.4f}")
                break
            if vtry < 2:
                time.sleep(3)  # let the RPC settle before declaring failure
        print(f"  {verify_msgs[-1] if verify_msgs else 'n/a'}")

        if not verified:
            # All settled reads failed to show the position or a balance drop.
            print(f"  ❌ Position NOT verified after 3 settled reads — funds may be stuck.", file=sys.stderr)
            print(f"     Manual investigation needed.", file=sys.stderr)
            sys.exit(1)

        print("\n✅ LP position opened! Funds deployed.")
        return

    # Dry-run: build + estimate
    router = w3.eth.contract(address=Web3.to_checksum_address(LBROUTER), abi=LBROUTER_ABI)
    try:
        tx = router.functions.addLiquidity(params).build_transaction({
            "from": STEWARD_WALLET, "nonce": w3.eth.get_transaction_count(Web3.to_checksum_address(STEWARD_WALLET)),
            "gas": 1_000_000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        print(f"\n📦 Tx builds cleanly: gas={tx['gas']}, data_len={len(tx['data'])}")
    except Exception as e:
        print(f"\n❌ Tx build failed: {e}", file=sys.stderr); sys.exit(1)
    print("\n✅ DRY-RUN complete — no funds moved. Ready for execution.")

    return 0


# STEWARD_NONCE_RETRY_V1: self-heal nonce-race retry (Detect-Fix-Verify 2026-09-03)
def _send_with_nonce_retry(w3, acct, tx, tries: int = 3):
    """Send a signed tx; on 'nonce too low' re-fetch the nonce, re-sign,
    resend (max 3). Returns the tx hash. Raises on final failure."""
    for attempt in range(1, tries + 1):
        try:
            return w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
        except Exception as e:
            msg = str(e)
            if ("nonce too low" in msg or "nonce has been used" in msg) and attempt < tries:
                tx["nonce"] = w3.eth.get_transaction_count(acct.address)
                continue
            raise

if __name__ == "__main__":
    main()
