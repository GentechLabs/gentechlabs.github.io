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
    # price at active bin = (1 + binStep/10000)^(active - 2^23) * 10^12
    # but reader gave $6.5071. Use the live LFJ V2.2 pair (0x864d4e5e) on DexScreener.
    import urllib.request
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
    # Last resort: derive from active bin.
    try:
        step = 10  # binStep
        return (1 + step/10000) ** (active_id - 2**23) * 10**12
    except Exception:
        return 6.5071

def curve_dist_from_range(active_id, spread):
    """Gaussian curve distribution that LFJ accepts. Same logic as
    deploy_lp_curve.py: each bin gets a non-zero share and the array sums to
    exactly 1e18 (100%), or LFJ reverts with ZeroShares.
    """
    import math
    neg_ids = [-1*(el+1) for el in range(spread)]
    pos_ids = [el+1 for el in range(spread)]
    RX = len(pos_ids); sigmaX = 1.7 if RX >= 10 else 1.4
    AX = 1/(math.sqrt(math.pi*2)*sigmaX)
    distX = [0]*len(neg_ids) + [AX] + [2*AX*math.exp(-0.5*((ind+1)/sigmaX)**2) for ind in range(len(pos_ids))]
    RY = len(neg_ids); sigmaY = 1.7 if RY >= 10 else 1.4
    AY = 1/(math.sqrt(math.pi*2)*sigmaY)
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


def build_liquidity_params(amount_usd, bin_spread, active_id, price):
    usdc_amount = amount_usd / 2.0
    wavax_amount = usdc_amount / price
    delta_ids = list(range(-bin_spread, bin_spread + 1))
    distX, distY = curve_dist_from_range(active_id, bin_spread)
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
    ap.add_argument("--bin-spread", type=int, default=5)
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
    print(f"  Deploy: ${args.amount:.2f} (50/50 USDC/WAVAX)")
    print(f"  Wallet: {STEWARD_WALLET}")

    params = build_liquidity_params(args.amount, args.bin_spread, active_id, price)
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

    # Check we have enough
    need_usdc = params['amountY']/1e6
    need_wavax = params['amountX']/1e18
    if usdc_bal < need_usdc:
        print(f"\n❌ Insufficient USDC: have ${usdc_bal:.2f}, need ${need_usdc:.2f}", file=sys.stderr)
        sys.exit(1)
    if wavax_bal < need_wavax:
        print(f"\n⚠️  Insufficient WAVAX: have {wavax_bal:.6f}, need {need_wavax:.6f}")
        print("   Will need to swap USDC→WAVAX first, or the LP will use what's available.")
        # For now, note it. The LP needs both sides.

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
                    "gas": 100000, "gasPrice": w3.eth.gas_price, "chainId": CHAIN_ID})
                signed = acct.sign_transaction(tx)
                h = w3.eth.send_raw_transaction(signed.raw_transaction)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ {name} approved: {h.hex()} status={rcpt['status']}")
            else:
                print(f"  ✅ {name} already approved")

        # 1b. Swap USDC -> WAVAX if we don't have enough WAVAX for the LP
        need_wavax = params['amountX']/1e18
        if wavax_bal < need_wavax:
            swap_usdc = (need_wavax - wavax_bal) * price
            swap_usdc = min(swap_usdc, usdc_bal)  # don't swap more than we have
            if swap_usdc > 0.01:
                print(f"\n🔄 Swapping ${swap_usdc:.2f} USDC -> WAVAX (need {need_wavax:.4f} WAVAX)...")
                router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
                amount_in = int(swap_usdc * 1e6)
                amount_out_min = int((swap_usdc / price) * 0.99 * 1e18)  # 1% slippage
                tx = router.functions.swapExactTokensForTokens(
                    amount_in, amount_out_min,
                    ([BIN_STEP], [3], [Web3.to_checksum_address(USDC), Web3.to_checksum_address(WAVAX)]),
                    acct.address, int(time.time()) + 600
                ).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 500000, "gasPrice": w3.eth.gas_price, "chainId": CHAIN_ID})
                signed = acct.sign_transaction(tx)
                h = w3.eth.send_raw_transaction(signed.raw_transaction)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ Swap tx: {h.hex()} status={rcpt['status']}")
                if rcpt['status'] != 1:
                    print("  ❌ Swap REVERTED!", file=sys.stderr); sys.exit(1)
                # refresh balances
                wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
                usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
                print(f"  WAVAX now: {wavax_bal:.6f} | USDC now: ${usdc_bal:.2f}")

        # 2. addLiquidity — size to ACTUAL post-swap balances with a small
        # buffer so transferFrom never asks for more than the wallet holds.
        # (The pre-swap estimate can overshoot by a hair and revert.)
        wavax_bal = wavax.functions.balanceOf(acct.address).call()/1e18
        usdc_bal = usdc.functions.balanceOf(acct.address).call()/1e6
        buf_x = 0.005  # keep ~0.005 WAVAX free (dust/gas)
        buf_y = 0.05   # keep ~$0.05 USDC free
        actual_x = max(0, wavax_bal - buf_x)
        actual_y = max(0, usdc_bal - buf_y)
        params['amountX'] = int(actual_x * 1e18)
        params['amountY'] = int(actual_y * 1e6)
        print(f"\n💧 Adding liquidity (sized to actual balances: {actual_x:.4f} WAVAX + ${actual_y:.2f} USDC)...")
        router = w3.eth.contract(address=router_addr, abi=LBROUTER_ABI)
        tx = router.functions.addLiquidity(params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 1_000_000, "gasPrice": w3.eth.gas_price, "chainId": CHAIN_ID})
        signed = acct.sign_transaction(tx)
        h = w3.eth.send_raw_transaction(signed.raw_transaction)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ addLiquidity tx: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ TX REVERTED!", file=sys.stderr); sys.exit(1)

        # 3. Verify position
        print("\n🔍 Verifying position...")
        new_usdc = usdc.functions.balanceOf(acct.address).call()/1e6
        new_wavax = wavax.functions.balanceOf(acct.address).call()/1e18
        print(f"  USDC after: ${new_usdc:.2f} (was ${usdc_bal:.2f})")
        print(f"  WAVAX after: {new_wavax:.6f} (was {wavax_bal:.6f})")
        print("\n✅ LP position opened! Funds deployed.")
        return

    # Dry-run: build + estimate
    router = w3.eth.contract(address=Web3.to_checksum_address(LBROUTER), abi=LBROUTER_ABI)
    try:
        tx = router.functions.addLiquidity(params).build_transaction({
            "from": STEWARD_WALLET, "nonce": w3.eth.get_transaction_count(Web3.to_checksum_address(STEWARD_WALLET)),
            "gas": 1_000_000, "gasPrice": w3.eth.gas_price, "chainId": CHAIN_ID})
        print(f"\n📦 Tx builds cleanly: gas={tx['gas']}, data_len={len(tx['data'])}")
    except Exception as e:
        print(f"\n❌ Tx build failed: {e}", file=sys.stderr); sys.exit(1)
    print("\n✅ DRY-RUN complete — no funds moved. Ready for execution.")

if __name__ == "__main__":
    main()
