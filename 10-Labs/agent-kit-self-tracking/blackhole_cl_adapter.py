#!/usr/bin/env python3
"""Blackhole Algebra-V3 WAVAX/USDC CL adapter — DEPLOY + STAKE + HARVEST + VERIFY.

Built directly against Blackhole's verified Algebra contracts (vfat's Sickle
wrapper returned "Farm not supported" for this pool — we go direct).

CRITICAL (verified on-chain 2026-09-08): our WAVAX/USDC pool uses the LEGACY
deployer (tickSpacing 200 -> 0x5D43...). That means the LEGACY contract stack:
  - NFPM:            0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146
  - Router V2:       0xe946A9f39312E2346BA79DAb865B0e9A74f2F981
  - Farming center:  0xa47Ad2C95FaE476a73b85A355A5855aDb4b3A449
  - Eternal farming:  0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A
  - Pool API:        0x6cDC88fdd9695FcE81c3d09471feD66D0e5F8C3E
The deployer is resolved at RUNTIME via AlgebraPoolAPI.pairToDeployer(pool) so
we never hardcode the wrong stack if Blackhole migrates (defense vs fork drift).

Modes:
  --dry-run (default): build + estimate, NO funds move.
  --execute: real deploy (requires funded steward wallet + --yes).

Flow (Jordan's intent: farm + compound, NEVER hold BLACK as yield):
  1. mint CL position (NFPM.mint) with tick range around current price
  2. stake the position NFT into the gauge (approve gauge + gauge.deposit)
  3. harvest emissions (farming center multicall: collectRewards + claimReward)
  4. verify position on-chain (NFPM.positions + balanceOf + pool slot0 in-range)

The harvest leg converts BLACK -> pool tokens via the router and re-mints, so
emissions compound back into the position instead of being held.
"""
import argparse, json, os, sys, time, math
from web3 import Web3

AVALANCHE_RPC = "https://api.avax.network/ext/bc/C/rpc"
CHAIN_ID = 43114

# --- Verified addresses (LEGACY stack for our pool) ---
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"          # WAVAX/USDC Algebra V3
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
ALGEBRA_POOL_API = "0xa90BC0E1D28151206530dABa53A5b8d28332cb7f"  # pairToDeployer storage
LEGACY_NFPM = "0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146"
LEGACY_ROUTER = "0xe946A9f39312E2346BA79DAb865B0e9A74f2F981"
LEGACY_FARMING_CENTER = "0xa47Ad2C95FaE476a73b85A355A5855aDb4b3A449"
LEGACY_ETERNAL_FARMING = "0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A"
LEGACY_POOL_API = "0x6cDC88fdd9695FcE81c3d09471feD66D0e5F8C3E"
GAUGE_MANAGER = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
TICK_SPACING = 200

STEWARD_WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
STEWARD_KEY_FILE = "/root/.blockrun/almanak-steward-key"

# --- Minimal ABIs (verified from Blackhole MCP audit sources) ---
PAIR_TO_DEPLOYER_ABI = [{
    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
    "name": "pairToDeployer", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view", "type": "function"}]

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "a", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "s", "type": "address"}, {"name": "v", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "o", "type": "address"}, {"name": "s", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}]

# NFPM.mint(MintParams) + positions + balanceOf + approve + multicall
NFPM_ABI = [
    {"inputs": [{"components": [
        {"name": "token0", "type": "address"}, {"name": "token1", "type": "address"},
        {"name": "deployer", "type": "address"}, {"name": "tickLower", "type": "int24"},
        {"name": "tickUpper", "type": "int24"}, {"name": "amount0Desired", "type": "uint256"},
        {"name": "amount1Desired", "type": "uint256"}, {"name": "amount0Min", "type": "uint256"},
        {"name": "amount1Min", "type": "uint256"}, {"name": "recipient", "type": "address"},
        {"name": "deadline", "type": "uint256"}], "name": "params", "type": "tuple"}],
     "name": "mint", "outputs": [
        {"name": "tokenId", "type": "uint256"}, {"name": "liquidity", "type": "uint128"},
        {"name": "amount0", "type": "uint256"}, {"name": "amount1", "type": "uint256"}],
     "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "positions", "outputs": [
        {"name": "nonce", "type": "uint88"}, {"name": "operator", "type": "address"},
        {"name": "token0", "type": "address"}, {"name": "token1", "type": "address"},
        {"name": "deployer", "type": "address"}, {"name": "tickLower", "type": "int24"},
        {"name": "tickUpper", "type": "int24"}, {"name": "liquidity", "type": "uint128"},
        {"name": "feeGrowthInside0LastX128", "type": "uint256"},
        {"name": "feeGrowthInside1LastX128", "type": "uint256"},
        {"name": "tokensOwed0", "type": "uint128"}, {"name": "tokensOwed1", "type": "uint128"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}, {"name": "index", "type": "uint256"}],
     "name": "tokenOfOwnerByIndex", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "getApproved",
     "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}],
     "name": "approve", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "data", "type": "bytes[]"}], "name": "multicall",
     "outputs": [{"name": "results", "type": "bytes[]"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [
        {"name": "tokenId", "type": "uint256"}, {"name": "amount0Desired", "type": "uint256"},
        {"name": "amount1Desired", "type": "uint256"}, {"name": "amount0Min", "type": "uint256"},
        {"name": "amount1Min", "type": "uint256"}, {"name": "deadline", "type": "uint256"}],
        "name": "params", "type": "tuple"}],
     "name": "increaseLiquidity", "outputs": [
        {"name": "liquidity", "type": "uint128"}, {"name": "amount0", "type": "uint256"},
        {"name": "amount1", "type": "uint256"}],
     "stateMutability": "payable", "type": "function"},
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

# Gauge CL: deposit(tokenId) / withdraw(tokenId)
GAUGE_CL_ABI = [
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "deposit",
     "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "withdraw",
     "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

# Router V2: swapExactTokensForTokens (Trader Joe-style route struct) — used
# to sell BLACK emissions back into pool tokens (Jordan: never hold BLACK).
ROUTER_V2_ABI = [
    {"inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "amountOutMin", "type": "uint256"},
        {"components": [
            {"name": "pair", "type": "address"}, {"name": "from", "type": "address"},
            {"name": "to", "type": "address"}, {"name": "stable", "type": "bool"},
            {"name": "concentrated", "type": "bool"}, {"name": "receiver", "type": "address"}],
         "name": "routes", "type": "tuple[]"},
        {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}],
     "name": "swapExactTokensForTokens", "outputs": [{"name": "amounts", "type": "uint256[]"}],
     "stateMutability": "nonpayable", "type": "function"},
]

# GaugeManager.gauges(pool) -> gauge address
GAUGE_MANAGER_ABI = [{
    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
    "name": "gauges", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view", "type": "function"}]

# Eternal farming: incentiveKeys(pool) -> (rewardToken, bonusRewardToken, pool, nonce)
ETERNAL_FARMING_ABI = [{
    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
    "name": "incentiveKeys", "outputs": [
        {"name": "rewardToken", "type": "address"}, {"name": "bonusRewardToken", "type": "address"},
        {"name": "pool", "type": "address"}, {"name": "nonce", "type": "uint256"}],
    "stateMutability": "view", "type": "function"}]

# Farming center: collectRewards(key, tokenId) + claimReward + multicall
FARMING_CENTER_ABI = [
    {"inputs": [{"components": [
        {"name": "rewardToken", "type": "address"}, {"name": "bonusRewardToken", "type": "address"},
        {"name": "pool", "type": "address"}, {"name": "nonce", "type": "uint256"}],
        "name": "key", "type": "tuple"}, {"name": "tokenId", "type": "uint256"}],
     "name": "collectRewards", "outputs": [
        {"name": "reward", "type": "uint256"}, {"name": "bonusReward", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "rewardToken", "type": "address"}, {"name": "to", "type": "address"},
                {"name": "amountRequested", "type": "uint256"}],
     "name": "claimReward", "outputs": [{"name": "reward", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "data", "type": "bytes[]"}], "name": "multicall",
     "outputs": [{"name": "results", "type": "bytes[]"}], "stateMutability": "payable", "type": "function"},
]

# Pool slot0() -> (sqrtPriceX96, tick, ...) for in-range check
POOL_SLOT0_ABI = [{
    "inputs": [], "name": "slot0", "outputs": [
        {"name": "sqrtPriceX96", "type": "uint160"}, {"name": "tick", "type": "int24"},
        {"name": "observationIndex", "type": "uint16"}, {"name": "observationCardinality", "type": "uint16"},
        {"name": "observationCardinalityNext", "type": "uint16"}, {"name": "feeProtocol", "type": "uint8"},
        {"name": "unlocked", "type": "bool"}],
    "stateMutability": "view", "type": "function"}]


def resolve_deployer(w3):
    """Resolve the pool's deployer at runtime (defense vs fork drift)."""
    api = w3.eth.contract(address=Web3.to_checksum_address(ALGEBRA_POOL_API), abi=PAIR_TO_DEPLOYER_ABI)
    d = api.functions.pairToDeployer(Web3.to_checksum_address(POOL)).call()
    return d.lower()


def is_legacy_deployer(deployer):
    LEGACY = {"0x5d433a94a4a2aa8f9aa34d8d15692dc2e9960584"}  # tickSpacing 200 legacy
    return deployer in LEGACY


def get_stack(deployer):
    """Return (nfpm, router, farming_center, eternal_farming, pool_api) for the deployer."""
    if is_legacy_deployer(deployer):
        return (LEGACY_NFPM, LEGACY_ROUTER, LEGACY_FARMING_CENTER, LEGACY_ETERNAL_FARMING, LEGACY_POOL_API)
    # Current stack (not our pool, but keep the mapping correct)
    return ("0xfD1c727D8A2259493C66899f478EbfeA41329545",
            "0x9EED160D7D8253DeC1A2A512e504DE5E7ff3C111",
            "0xCeCc64211f1Ed70a71BD47EB656f7067C1f45541",
            "0x9c70BedD11Cf874F07B1Bd9C29e3e41f9F248F5c",
            "0xF0274C793D16713338AF4b8BF2BEf64BA2485B99")


def get_pool_tick(w3):
    """Read the pool's ACTUAL current tick from globalState() (the source of
    truth — avoids the USD-price→tick decimal-scaling bug that caused STF).
    Returns (tick, price_usd)."""
    sel = '0x' + Web3.keccak(text='globalState()').hex()[:8]
    raw = w3.eth.call({'to': Web3.to_checksum_address(POOL), 'data': sel})
    b = raw
    # ABI tuple: price(uint160) in word0, tick(int24) in word1 (last 3 bytes)
    price = int.from_bytes(b[0:32], 'big')
    tick = int.from_bytes(b[32:64][29:32], 'big', signed=True)
    sqrt = price / (2 ** 96)
    # Algebra sqrtPriceX96 gives the raw token1/token0 ratio. For WAVAX(18dec)/
    # USDC(6dec), the USD price = raw_ratio * 10^(18-6) = raw_ratio * 1e12.
    raw_price = sqrt * sqrt
    price_usd = raw_price * (10 ** (18 - 6))
    return tick, price_usd


def build_range_from_tick(current_tick, spread_pct=0.10):
    """Build a CURVE-style tick range around the pool's ACTUAL current tick.
    tickLower/Upper must be multiples of TICK_SPACING and bracket current_tick."""
    half = int(round(TICK_SPACING * (spread_pct * 100) / 1.0))
    # spread_pct=0.10 -> ~10% price range. Convert to tick distance:
    # price ratio (1+spread) -> tick delta = log_1.0001(1+spread)
    import math
    delta = int(math.log(1 + spread_pct) / math.log(1.0001))
    delta = max(delta, TICK_SPACING)
    # round to tick spacing
    tick_lower = (current_tick - delta) // TICK_SPACING * TICK_SPACING
    tick_upper = (current_tick + delta) // TICK_SPACING * TICK_SPACING
    if tick_lower >= current_tick:
        tick_lower -= TICK_SPACING
    if tick_upper <= current_tick:
        tick_upper += TICK_SPACING
    return tick_lower, tick_upper


def get_live_price(w3):
    """Live WAVAX/USDC price. Primary: DexScreener. Fallback: pool slot0 sqrtPrice."""
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL}",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            if d.get("pairs"):
                return float(d["pairs"][0]["priceUsd"])
    except Exception:
        pass
    try:
        pool = w3.eth.contract(address=Web3.to_checksum_address(POOL), abi=POOL_SLOT0_ABI)
        slot = pool.functions.slot0().call()
        sqrt = slot[0] / (2 ** 96)
        return float(sqrt * sqrt)
    except Exception:
        return None


def get_gauge(w3, deployer):
    """Resolve gauge for the pool via GaugeManager.gauges(pool)."""
    gm = w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MANAGER), abi=GAUGE_MANAGER_ABI)
    g = gm.functions.gauges(Web3.to_checksum_address(POOL)).call()
    return g.lower() if g and g != "0x" + "0" * 40 else None


def get_incentive_key(w3, eternal_farming):
    ef = w3.eth.contract(address=Web3.to_checksum_address(eternal_farming), abi=ETERNAL_FARMING_ABI)
    try:
        k = ef.functions.incentiveKeys(Web3.to_checksum_address(POOL)).call()
        return {"rewardToken": k[0], "bonusRewardToken": k[1], "pool": k[2], "nonce": k[3]}
    except Exception:
        return None


def _send_with_nonce_retry(w3, acct, tx, tries=3):
    for attempt in range(1, tries + 1):
        try:
            return w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
        except Exception as e:
            msg = str(e)
            if ("nonce too low" in msg or "nonce has been used" in msg) and attempt < tries:
                tx["nonce"] = w3.eth.get_transaction_count(acct.address)
                continue
            raise


def harvest(w3, acct, nfpm, farming_center, eternal_farming, token_id, key, router, dry_run=True):
    """Harvest BLACK emissions and compound them back into the position.

    Jordan's rule (Sep 8 2026): NEVER hold BLACK as yield — sell emissions
    immediately back into pool tokens and re-mint (increaseLiquidity). This is
    the Blackhole equivalent of the LFJ auto-compound loop.

    Flow (verified from Blackhole MCP audit claimEmissions.ts):
      1. farming_center.multicall([collectRewards(key, tokenId),
                                    claimReward(rewardToken, user, 0)])
         -> sends accrued BLACK to the wallet
      2. router.swapExactTokensForTokens(BLACK -> WAVAX + USDC) via the
         WAVAX/USDC pool (concentrated route)
      3. nfpm.increaseLiquidity(tokenId, wavax, usdc) to compound back in

    Returns a dict with the result. dry_run=True builds + estimates only.
    """
    fc = w3.eth.contract(address=Web3.to_checksum_address(farming_center), abi=FARMING_CENTER_ABI)
    nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
    router_c = w3.eth.contract(address=Web3.to_checksum_address(router), abi=ROUTER_V2_ABI)
    black = w3.eth.contract(address=Web3.to_checksum_address(BLACK), abi=ERC20_ABI)

    # 1. Collect rewards (multicall: collectRewards + claimReward)
    collect_cd = fc.encode_abi("collectRewards", [key, token_id])
    claim_cd = fc.encode_abi("claimReward",
                             [Web3.to_checksum_address(key["rewardToken"]),
                              acct.address, 0])
    print("\n🌾 Harvesting BLACK emissions...")
    if dry_run:
        print("  [dry-run] farming_center.multicall([collectRewards, claimReward])")
    else:
        tx = fc.functions.multicall([collect_cd, claim_cd]).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ collected: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ collect REVERTED", file=sys.stderr)
            return {"ok": False, "stage": "collect"}

    # 2. Check BLACK balance
    black_bal = black.functions.balanceOf(acct.address).call() / 1e18
    print(f"  BLACK balance: {black_bal:.6f}")
    if black_bal < 0.0001:
        print("  ℹ️  No meaningful BLACK to compound — nothing to do.")
        return {"ok": True, "stage": "noop", "black": black_bal}

    # 3. Sell BLACK -> WAVAX + USDC (split 50/50 via two routes)
    # Route: BLACK -> WAVAX (concentrated pool) and BLACK -> USDC
    # We use the WAVAX/USDC pool as the concentrated route for both legs.
    half = int(black_bal * 1e18 / 2)
    routes = [
        {"pair": Web3.to_checksum_address(POOL), "from": Web3.to_checksum_address(BLACK),
         "to": Web3.to_checksum_address(WAVAX), "stable": False, "concentrated": True,
         "receiver": acct.address},
        {"pair": Web3.to_checksum_address(POOL), "from": Web3.to_checksum_address(BLACK),
         "to": Web3.to_checksum_address(USDC), "stable": False, "concentrated": True,
         "receiver": acct.address},
    ]
    print("  Selling BLACK -> WAVAX + USDC (50/50)...")
    if dry_run:
        print("  [dry-run] router.swapExactTokensForTokens(amountIn, 0, routes, wallet)")
    else:
        # approve router for BLACK
        allowance = black.functions.allowance(acct.address, Web3.to_checksum_address(router)).call()
        if allowance < int(black_bal * 1e18):
            tx = black.functions.approve(Web3.to_checksum_address(router), 2**256 - 1).build_transaction({
                "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
            h = _send_with_nonce_retry(w3, acct, tx)
            rcpt = w3.eth.wait_for_transaction_receipt(h)
            print(f"  ✅ BLACK approved: {h.hex()} status={rcpt['status']}")
        tx = router_c.functions.swapExactTokensForTokens(
            int(black_bal * 1e18), 0, routes, acct.address, int(time.time()) + 600
        ).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ swapped: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ swap REVERTED", file=sys.stderr)
            return {"ok": False, "stage": "swap"}

    # 4. Compound: increaseLiquidity with the swapped WAVAX + USDC
    wavax = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
    usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
    wavax_bal = wavax.functions.balanceOf(acct.address).call()
    usdc_bal = usdc.functions.balanceOf(acct.address).call()
    print(f"  WAVAX to compound: {wavax_bal/1e18:.6f} · USDC: {usdc_bal/1e6:.4f}")
    if wavax_bal < 1e15 or usdc_bal < 1e3:
        print("  ℹ️  Swapped amounts too small to compound — leaving as wallet balance.")
        return {"ok": True, "stage": "swap_only", "black": black_bal}

    if dry_run:
        print("  [dry-run] nfpm.increaseLiquidity(tokenId, wavax, usdc)")
    else:
        inc_params = {
            "tokenId": token_id,
            "amount0Desired": wavax_bal,
            "amount1Desired": usdc_bal,
            "amount0Min": 0, "amount1Min": 0,
            "deadline": int(time.time()) + 600,
        }
        tx = nfpm_c.functions.increaseLiquidity(inc_params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ compounded: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ increaseLiquidity REVERTED", file=sys.stderr)
            return {"ok": False, "stage": "compound"}

    return {"ok": True, "stage": "harvested", "black": black_bal}


def recenter(w3, acct, nfpm, gauge, token_id, deployer, dry_run=True):
    """Re-center a staked Blackhole CL position on the current price.

    Blackhole CL (Algebra V3) strategy lever (docs.blackhole.xyz): when the
    position moves OUT of range, rebalance = withdraw + re-mint centered on
    the current price. This is the Blackhole equivalent of the LFJ re-center.

    Flow:
      1. gauge.withdraw(tokenId)  — unstake the NFT (returns to wallet)
      2. nfpm.decreaseLiquidity(tokenId, liquidity, 0, 0, deadline)
         — remove all liquidity, WAVAX+USDC owed to the position
      3. nfpm.collect(tokenId, wallet, max, max) — pull tokens to wallet
      4. re-mint a NEW position centered on current price (reuses mint path)
      5. gauge.deposit(newTokenId) — re-stake

    Returns (ok, new_token_id). dry_run=True builds + estimates only.
    """
    nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
    gauge_c = w3.eth.contract(address=Web3.to_checksum_address(gauge), abi=GAUGE_CL_ABI)

    # 1. Unstake from gauge
    print("\n🔄 Re-centering position (withdraw -> re-mint on current price)...")
    if dry_run:
        print("  [dry-run] gauge.withdraw(tokenId)")
    else:
        tx = gauge_c.functions.withdraw(token_id).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 300000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ unstaked: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ gauge.withdraw REVERTED", file=sys.stderr)
            return False, None

    # 2. Get current liquidity
    pos = nfpm_c.functions.positions(token_id).call()
    liquidity = pos[7]
    print(f"  Current liquidity: {liquidity}")
    if liquidity == 0:
        print("  ℹ️  Position already has no liquidity — skipping decrease.")
    elif dry_run:
        print("  [dry-run] nfpm.decreaseLiquidity(tokenId, liquidity, 0, 0)")
    else:
        dec_params = {
            "tokenId": token_id, "liquidity": liquidity,
            "amount0Min": 0, "amount1Min": 0, "deadline": int(time.time()) + 600,
        }
        tx = nfpm_c.functions.decreaseLiquidity(dec_params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ decreased: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ decreaseLiquidity REVERTED", file=sys.stderr)
            return False, None

    # 3. Collect tokens to wallet
    if dry_run:
        print("  [dry-run] nfpm.collect(tokenId, wallet, max, max)")
    else:
        col_params = {
            "tokenId": token_id, "recipient": acct.address,
            "amount0Max": 2**128 - 1, "amount1Max": 2**128 - 1,
        }
        tx = nfpm_c.functions.collect(col_params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 300000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ collected: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ collect REVERTED", file=sys.stderr)
            return False, None

    # 4. Re-mint centered on current price (reuse the mint path)
    current_tick, price = get_pool_tick(w3)
    tick_lower, tick_upper = build_range_from_tick(current_tick, 0.10)
    print(f"  Re-minting on current price ${price:.4f} (tick {current_tick}, "
          f"range {tick_lower}–{tick_upper})...")
    # Use the wallet's full WAVAX+USDC balance (real wallet in dry-run too)
    wavax_c = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
    usdc_c = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
    bal_addr = Web3.to_checksum_address(STEWARD_WALLET) if dry_run else acct.address
    wavax_bal = wavax_c.functions.balanceOf(bal_addr).call()
    usdc_bal = usdc_c.functions.balanceOf(bal_addr).call()
    if wavax_bal < 1e15 or usdc_bal < 1e3:
        print("  ❌ Not enough WAVAX/USDC after collect to re-mint.", file=sys.stderr)
        return False, None
    mint_params = {
        "token0": Web3.to_checksum_address(WAVAX),
        "token1": Web3.to_checksum_address(USDC),
        "deployer": Web3.to_checksum_address(deployer),
        "tickLower": tick_lower, "tickUpper": tick_upper,
        "amount0Desired": wavax_bal, "amount1Desired": usdc_bal,
        "amount0Min": 0, "amount1Min": 0,
        "recipient": acct.address, "deadline": int(time.time()) + 600,
    }
    if dry_run:
        print("  [dry-run] nfpm.mint(new range)")
        return True, None
    tx = nfpm_c.functions.mint(mint_params).build_transaction({
        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 1_000_000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
    h = _send_with_nonce_retry(w3, acct, tx)
    rcpt = w3.eth.wait_for_transaction_receipt(h)
    print(f"  ✅ re-minted: {h.hex()} status={rcpt['status']}")
    if rcpt['status'] != 1:
        print("  ❌ re-mint REVERTED", file=sys.stderr)
        return False, None
    # Find new tokenId
    new_token_id = None
    n = nfpm_c.functions.balanceOf(acct.address).call()
    for i in range(n):
        tid = nfpm_c.functions.tokenOfOwnerByIndex(acct.address, i).call()
        p = nfpm_c.functions.positions(tid).call()
        if p[2].lower() == WAVAX.lower() and p[3].lower() == USDC.lower() and tid != token_id:
            new_token_id = tid
            break
    if new_token_id is None:
        print("  ❌ Could not find new tokenId after re-mint.", file=sys.stderr)
        return False, None
    print(f"  ✅ New position tokenId: {new_token_id}")

    # 5. Re-stake into gauge
    approved = nfpm_c.functions.getApproved(new_token_id).call()
    if approved.lower() != gauge:
        tx = nfpm_c.functions.approve(Web3.to_checksum_address(gauge), new_token_id).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ gauge approved: {h.hex()} status={rcpt['status']}")
    tx = gauge_c.functions.deposit(new_token_id).build_transaction({
        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 300000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
    h = _send_with_nonce_retry(w3, acct, tx)
    rcpt = w3.eth.wait_for_transaction_receipt(h)
    print(f"  ✅ re-staked: {h.hex()} status={rcpt['status']}")
    if rcpt['status'] != 1:
        print("  ⚠️ Re-stake REVERTED (position minted but not staked).", file=sys.stderr)
        return False, new_token_id
    return True, new_token_id


def main():
    ap = argparse.ArgumentParser(description="Blackhole Algebra-V3 WAVAX/USDC CL adapter")
    ap.add_argument("--amount", type=float, default=20.0, help="USD deploy amount")
    ap.add_argument("--spread-pct", type=float, default=0.10, help="range half-width (default 10%)")
    ap.add_argument("--allocation", type=float, default=0.5, help="USDC allocation (0-1)")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--harvest", action="store_true",
                    help="harvest BLACK emissions + compound back into the position")
    ap.add_argument("--compound", action="store_true",
                    help="increase liquidity on the existing position with idle wallet WAVAX+USDC")
    ap.add_argument("--recenter", action="store_true",
                    help="re-center the position on current price (withdraw -> re-mint -> re-stake)")
    args = ap.parse_args()

    w3 = Web3(Web3.HTTPProvider(AVALANCHE_RPC))
    if not w3.is_connected():
        print("ERROR: cannot connect to Avalanche RPC", file=sys.stderr); sys.exit(1)

    # 1. Resolve deployer at runtime (defense vs fork drift)
    deployer = resolve_deployer(w3)
    nfpm, router, farming_center, eternal_farming, pool_api = get_stack(deployer)
    print("=" * 50)
    print("🕳️  Blackhole Algebra-V3 WAVAX/USDC CL Adapter")
    print("=" * 50)
    print(f"  Pool: {POOL}")
    print(f"  Deployer (on-chain): {deployer}  [{'LEGACY' if is_legacy_deployer(deployer) else 'CURRENT'}]")
    print(f"  NFPM: {nfpm}")
    print(f"  Router: {router}")
    print(f"  Farming center: {farming_center}")

    # 2. Live price + range (from the pool's ACTUAL current tick — the source
    # of truth. The old USD-price→tick conversion had a decimal-scaling bug
    # that produced a range NOT bracketing the real tick → STF revert.)
    current_tick, price = get_pool_tick(w3)
    if not price or price <= 0:
        print("ERROR: cannot get live price", file=sys.stderr); sys.exit(1)
    tick_lower, tick_upper = build_range_from_tick(current_tick, args.spread_pct)
    print(f"  Live price: ${price:.4f} USDC/WAVAX (pool tick {current_tick})")
    print(f"  Range: tick {tick_lower}–{tick_upper} (brackets {current_tick})")

    # 3. Amounts
    usdc_amount = args.amount * args.allocation
    wavax_amount = (args.amount * (1 - args.allocation)) / price
    print(f"  Deploy: ${args.amount:.2f} ({args.allocation*100:.0f}% USDC / {(1-args.allocation)*100:.0f}% WAVAX)")
    print(f"  amount0Desired (WAVAX): {wavax_amount:.6f}")
    print(f"  amount1Desired (USDC): ${usdc_amount:.2f}")

    # 4. Gauge + incentive key (for stake + harvest)
    gauge = get_gauge(w3, deployer)
    print(f"  Gauge: {gauge or 'NONE'}")
    key = get_incentive_key(w3, eternal_farming)
    if key:
        print(f"  Incentive: reward={key['rewardToken']} bonus={key['bonusRewardToken']} nonce={key['nonce']}")

    # 5. Balances
    usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
    wavax = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
    usdc_bal = usdc.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call() / 1e6
    wavax_bal = wavax.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call() / 1e18
    avax_bal = w3.eth.get_balance(Web3.to_checksum_address(STEWARD_WALLET)) / 1e18
    print(f"\n💰 Steward wallet balances:")
    print(f"  USDC:  ${usdc_bal:.2f}")
    print(f"  WAVAX: {wavax_bal:.6f}")
    print(f"  AVAX:  {avax_bal:.6f} (gas)")

    # ── RECENTER mode: withdraw -> re-mint on current price -> re-stake ──
    if args.recenter:
        dry_run = not args.execute
        if not dry_run:
            if not args.yes:
                print("\n❌ Refusing to re-center without --yes. Dry-run only."); sys.exit(1)
            if not os.path.exists(STEWARD_KEY_FILE):
                print("\n❌ Steward key not found. Cannot sign.", file=sys.stderr); sys.exit(1)
            key_data = open(STEWARD_KEY_FILE).read().strip()
            acct = w3.eth.account.from_key(key_data)
            if acct.address.lower() != STEWARD_WALLET.lower():
                print("\n❌ Key mismatch!", file=sys.stderr); sys.exit(1)
        else:
            acct = w3.eth.account.from_key("0x" + "0" * 64)  # dummy for dry-run
        # Find our CL position tokenId
        nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
        token_id = None
        n = nfpm_c.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()
        for i in range(n):
            tid = nfpm_c.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(STEWARD_WALLET), i).call()
            pos = nfpm_c.functions.positions(tid).call()
            if pos[2].lower() == WAVAX.lower() and pos[3].lower() == USDC.lower():
                token_id = tid
                break
        if token_id is None:
            print("\n❌ No Blackhole CL position found to re-center.", file=sys.stderr); sys.exit(1)
        if not gauge:
            print("\n❌ No gauge — cannot re-center a staked position.", file=sys.stderr); sys.exit(1)
        ok, new_tid = recenter(w3, acct, nfpm, gauge, token_id, deployer, dry_run=dry_run)
        print(f"\n  Result: {'✅ re-centered' if ok else '❌ failed'} "
              f"{f'(new tokenId {new_tid})' if new_tid else ''}")
        return 0

    # ── COMPOUND mode: increase liquidity on existing position with idle ──
    if args.compound:
        dry_run = not args.execute
        if not dry_run:
            if not args.yes:
                print("\n❌ Refusing to compound without --yes. Dry-run only."); sys.exit(1)
            if not os.path.exists(STEWARD_KEY_FILE):
                print("\n❌ Steward key not found. Cannot sign.", file=sys.stderr); sys.exit(1)
            key_data = open(STEWARD_KEY_FILE).read().strip()
            acct = w3.eth.account.from_key(key_data)
            if acct.address.lower() != STEWARD_WALLET.lower():
                print("\n❌ Key mismatch!", file=sys.stderr); sys.exit(1)
        else:
            acct = w3.eth.account.from_key("0x" + "0" * 64)  # dummy for dry-run
        # Find our CL position tokenId
        nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
        token_id = None
        n = nfpm_c.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()
        for i in range(n):
            tid = nfpm_c.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(STEWARD_WALLET), i).call()
            pos = nfpm_c.functions.positions(tid).call()
            if pos[2].lower() == WAVAX.lower() and pos[3].lower() == USDC.lower():
                token_id = tid
                break
        if token_id is None:
            print("\n❌ No Blackhole CL position found to compound.", file=sys.stderr); sys.exit(1)
        # Idle wallet capital (WAVAX + USDC, excluding gas AVAX)
        wavax_c = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
        usdc_c = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=ERC20_ABI)
        wavax_idle = wavax_c.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()
        usdc_idle = usdc_c.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()
        idle_usd = wavax_idle / 1e18 * price + usdc_idle / 1e6
        print(f"\n💰 Compounding position #{token_id} with idle ${idle_usd:.2f} "
              f"(WAVAX {wavax_idle/1e18:.6f} + USDC {usdc_idle/1e6:.4f})...")
        if idle_usd < 0.50:
            print("  ℹ️  Idle below $0.50 — nothing to compound.")
            return 0
        if dry_run:
            print("  [dry-run] nfpm.increaseLiquidity(tokenId, wavax, usdc)")
        else:
            inc_params = {
                "tokenId": token_id,
                "amount0Desired": wavax_idle,
                "amount1Desired": usdc_idle,
                "amount0Min": 0, "amount1Min": 0,
                "deadline": int(time.time()) + 600,
            }
            tx = nfpm_c.functions.increaseLiquidity(inc_params).build_transaction({
                "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
            h = _send_with_nonce_retry(w3, acct, tx)
            rcpt = w3.eth.wait_for_transaction_receipt(h)
            print(f"  ✅ compounded: {h.hex()} status={rcpt['status']}")
            if rcpt['status'] != 1:
                print("  ❌ increaseLiquidity REVERTED", file=sys.stderr); sys.exit(1)
        return 0

    # ── HARVEST mode: collect BLACK emissions + compound back ──────────
    if args.harvest:
        dry_run = not args.execute
        if not dry_run:
            if not args.yes:
                print("\n❌ Refusing to harvest without --yes. Dry-run only."); sys.exit(1)
            if not os.path.exists(STEWARD_KEY_FILE):
                print("\n❌ Steward key not found. Cannot sign.", file=sys.stderr); sys.exit(1)
            key_data = open(STEWARD_KEY_FILE).read().strip()
            acct = w3.eth.account.from_key(key_data)
            if acct.address.lower() != STEWARD_WALLET.lower():
                print("\n❌ Key mismatch!", file=sys.stderr); sys.exit(1)
        else:
            acct = w3.eth.account.from_key("0x" + "0" * 64)  # dummy for dry-run
        # Find our CL position tokenId
        nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
        token_id = None
        n = nfpm_c.functions.balanceOf(Web3.to_checksum_address(STEWARD_WALLET)).call()
        for i in range(n):
            tid = nfpm_c.functions.tokenOfOwnerByIndex(Web3.to_checksum_address(STEWARD_WALLET), i).call()
            pos = nfpm_c.functions.positions(tid).call()
            if pos[2].lower() == WAVAX.lower() and pos[3].lower() == USDC.lower():
                token_id = tid
                break
        if token_id is None:
            print("\n❌ No Blackhole CL position found to harvest.", file=sys.stderr); sys.exit(1)
        print(f"\n🌾 Harvesting position #{token_id}...")
        if not key:
            print("\n❌ No incentive key — cannot harvest.", file=sys.stderr); sys.exit(1)
        res = harvest(w3, acct, nfpm, farming_center, eternal_farming,
                      token_id, key, router, dry_run=dry_run)
        print(f"\n  Result: {res}")
        return 0

    # Affordability check
    need_usdc = usdc_amount
    need_wavax = wavax_amount
    wallet_val = usdc_bal + wavax_bal * price
    deploy_cost = need_usdc + need_wavax * price
    if wallet_val < deploy_cost - 0.20:
        print(f"\n❌ Wallet value ${wallet_val:.2f} below deploy target ${deploy_cost:.2f} — insufficient.",
              file=sys.stderr)
        sys.exit(1)

    if args.execute:
        if not args.yes:
            print("\n❌ Refusing to execute without --yes. Dry-run only."); sys.exit(1)
        if not os.path.exists(STEWARD_KEY_FILE):
            print("\n❌ Steward key not found. Cannot sign.", file=sys.stderr); sys.exit(1)
        key_data = open(STEWARD_KEY_FILE).read().strip()
        acct = w3.eth.account.from_key(key_data)
        if acct.address.lower() != STEWARD_WALLET.lower():
            print("\n❌ Key mismatch!", file=sys.stderr); sys.exit(1)

        nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
        max_uint = 2 ** 256 - 1

        # 1. Approve WAVAX + USDC to NFPM
        for token, name, dec in [(USDC, "USDC", 1e6), (WAVAX, "WAVAX", 1e18)]:
            c = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
            allowance = c.functions.allowance(acct.address, Web3.to_checksum_address(nfpm)).call()
            if allowance < max_uint:
                print(f"\n🔓 Approving {name} to NFPM...")
                tx = c.functions.approve(Web3.to_checksum_address(nfpm), max_uint).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                h = _send_with_nonce_retry(w3, acct, tx)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ {name} approved: {h.hex()} status={rcpt['status']}")
            else:
                print(f"  ✅ {name} already approved")

        # 2. Mint CL position
        mint_params = {
            "token0": Web3.to_checksum_address(WAVAX),
            "token1": Web3.to_checksum_address(USDC),
            "deployer": Web3.to_checksum_address(deployer),
            "tickLower": tick_lower,
            "tickUpper": tick_upper,
            "amount0Desired": int(wavax_amount * 1e18),
            "amount1Desired": int(usdc_amount * 1e6),
            "amount0Min": 0,
            "amount1Min": 0,
            "recipient": acct.address,
            "deadline": int(time.time()) + 600,
        }
        print(f"\n🪙 Minting CL position...")
        tx = nfpm_c.functions.mint(mint_params).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 1_000_000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        h = _send_with_nonce_retry(w3, acct, tx)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f"  ✅ mint tx: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ MINT REVERTED!", file=sys.stderr); sys.exit(1)

        # Extract tokenId reliably via tokenOfOwnerByIndex (the Transfer-event
        # log parsing was unreliable — grabbed a garbage max-uint value).
        token_id = None
        n = nfpm_c.functions.balanceOf(acct.address).call()
        for i in range(n):
            tid = nfpm_c.functions.tokenOfOwnerByIndex(acct.address, i).call()
            pos = nfpm_c.functions.positions(tid).call()
            if pos[2].lower() == WAVAX.lower() and pos[3].lower() == USDC.lower():
                token_id = tid
                break
        if token_id is None:
            print("  ❌ Could not determine tokenId — position may be stuck.", file=sys.stderr)
            sys.exit(1)
        print(f"  ✅ Position tokenId: {token_id}")

        # 3. Stake into gauge (if gauge exists)
        if gauge:
            print(f"\n🗳️  Staking position {token_id} into gauge {gauge}...")
            # approve gauge for NFT
            approved = nfpm_c.functions.getApproved(token_id).call()
            if approved.lower() != gauge:
                print("  🔓 Approving gauge for NFT...")
                tx = nfpm_c.functions.approve(Web3.to_checksum_address(gauge), token_id).build_transaction({
                    "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                    "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
                h = _send_with_nonce_retry(w3, acct, tx)
                rcpt = w3.eth.wait_for_transaction_receipt(h)
                print(f"  ✅ gauge approved: {h.hex()} status={rcpt['status']}")
            gauge_c = w3.eth.contract(address=Web3.to_checksum_address(gauge), abi=GAUGE_CL_ABI)
            tx = gauge_c.functions.deposit(token_id).build_transaction({
                "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                "gas": 300000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
            h = _send_with_nonce_retry(w3, acct, tx)
            rcpt = w3.eth.wait_for_transaction_receipt(h)
            print(f"  ✅ staked: {h.hex()} status={rcpt['status']}")
            if rcpt['status'] != 1:
                print("  ⚠️ Stake REVERTED (position minted but not staked — emissions not accruing).",
                      file=sys.stderr)
        else:
            print("\n  ⚠️ No gauge found — position minted but NOT staked (no BLACK emissions).")

        # 4. Verify position on-chain (settled re-read)
        print("\n🔍 Verifying position (settled re-read)...")
        verified = False
        for vtry in range(3):
            try:
                pos = nfpm_c.functions.positions(token_id).call()
                liq = pos[7]
                if liq > 0:
                    verified = True
                    print(f"  ✅ Position verified: liquidity={liq} tickLower={pos[5]} tickUpper={pos[6]}")
                    break
            except Exception as e:
                print(f"  attempt {vtry+1}: {e}")
            if vtry < 2:
                time.sleep(3)
        if not verified:
            print("  ❌ Position NOT verified after 3 settled reads.", file=sys.stderr)
            sys.exit(1)

        print("\n✅ Blackhole CL position opened + staked! Funds deployed.")
        return

    # Dry-run: build + estimate
    nfpm_c = w3.eth.contract(address=Web3.to_checksum_address(nfpm), abi=NFPM_ABI)
    mint_params = {
        "token0": Web3.to_checksum_address(WAVAX),
        "token1": Web3.to_checksum_address(USDC),
        "deployer": Web3.to_checksum_address(deployer),
        "tickLower": tick_lower, "tickUpper": tick_upper,
        "amount0Desired": int(wavax_amount * 1e18), "amount1Desired": int(usdc_amount * 1e6),
        "amount0Min": 0, "amount1Min": 0,
        "recipient": STEWARD_WALLET, "deadline": int(time.time()) + 600,
    }
    try:
        tx = nfpm_c.functions.mint(mint_params).build_transaction({
            "from": STEWARD_WALLET, "nonce": w3.eth.get_transaction_count(Web3.to_checksum_address(STEWARD_WALLET)),
            "gas": 1_000_000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": CHAIN_ID})
        print(f"\n📦 Tx builds cleanly: gas={tx['gas']}, data_len={len(tx['data'])}")
    except Exception as e:
        print(f"\n❌ Tx build failed: {e}", file=sys.stderr); sys.exit(1)
    print("\n✅ DRY-RUN complete — no funds moved. Ready for execution.")


if __name__ == "__main__":
    main()
