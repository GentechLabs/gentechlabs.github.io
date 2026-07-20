"""Tests for the Stablecoin Transfer Portal."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from stablecoin_portal import (
    Chain, Stablecoin, BridgeProtocol, SwapProtocol, RouteStatus,
    RoutePlanner, TransferExecutor, StablecoinPortal,
    TransferPlan, TransferResult, SlippageConfig, apply_slippage,
)


def assert_eq(actual, expected, msg=""):
    if actual != expected:
        print(f"  ❌ {msg or f'Expected {expected!r}, got {actual!r}'}")
        return False
    print(f"  ✅ {msg or f'{actual!r} == {expected!r}'}")
    return True

def assert_in(item, container, msg=""):
    if item not in container:
        print(f"  ❌ {msg or f'{item!r} not in {container!r}'}")
        return False
    print(f"  ✅ {msg or f'{item!r} found'}")
    return True

def assert_gt(a, b, msg=""):
    if not (a > b):
        print(f"  ❌ {msg or f'{a} <= {b}'}")
        return False
    print(f"  ✅ {msg or f'{a} > {b}'}")
    return True

def assert_close(actual, expected, tolerance=0.01, msg=""):
    if abs(actual - expected) > tolerance:
        print(f"  ❌ {msg or f'{actual} != {expected} (tolerance {tolerance})'}")
        return False
    print(f"  ✅ {msg or f'{actual} ~= {expected}'}")
    return True

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    print(f"\n{name}")
    result = fn()
    if result:
        passed += 1
    else:
        failed += 1
        print(f"  ❌ TEST FAILED")


# ── Tests ──────────────────────────────────────────────────────────

def test_slippage_default():
    cfg = SlippageConfig()
    ok = assert_eq(cfg.default_pct, 0.5, "Default slippage 0.5%")
    return ok

def test_slippage_clamp_min():
    cfg = SlippageConfig()
    ok = assert_eq(cfg.validate(0.01), 0.1, "Clamped to min 0.1%")
    return ok

def test_slippage_clamp_max():
    cfg = SlippageConfig()
    ok = assert_eq(cfg.validate(5.0), 3.0, "Clamped to max 3.0%")
    return ok

def test_apply_slippage():
    result = apply_slippage(100.0, 0.5)
    ok = assert_eq(result, 99.5, "0.5% slippage on $100 → $99.50")
    return ok

def test_plan_same_chain_same_token():
    """USDC on ARC → USDC on ARC = no-op."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ARC, Stablecoin.USDC, 100.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(plan.expected_output, 100.0, "Same chain/token → no loss")
    ok &= assert_eq(len(plan.bridges), 0, "No bridges needed")
    ok &= assert_eq(len(plan.swaps), 0, "No swaps needed")
    return ok

def test_plan_same_chain_different_token():
    """USDT on ARC → USDC on ARC = swap only."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ARC, Stablecoin.USDT, 100.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 0, "No bridges needed")
    ok &= assert_eq(len(plan.swaps), 1, "1 swap needed")
    ok &= assert_gt(plan.expected_output, 99.0, "Output close to 100 (small fees)")
    ok &= assert_gt(plan.min_output, 98.0, "Min output after slippage")
    return ok

def test_plan_cross_chain_same_token():
    """USDC on Ethereum → USDC on ARC = bridge only."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ETHEREUM, Stablecoin.USDC, 100.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 1, "1 bridge needed")
    ok &= assert_eq(len(plan.swaps), 0, "No swaps needed")
    ok &= assert_eq(plan.bridges[0].protocol, BridgeProtocol.CCTP, "CCTP bridge")
    ok &= assert_gt(plan.expected_output, 99.0, "Output after bridge fee")
    return ok

def test_plan_cross_chain_different_token():
    """USDT on Ethereum → USDC on ARC = bridge + swap."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ETHEREUM, Stablecoin.USDT, 100.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 1, "1 bridge needed")
    ok &= assert_eq(len(plan.swaps), 1, "1 swap needed")
    ok &= assert_gt(plan.expected_output, 98.0, "Output after bridge + swap fees")
    return ok

def test_plan_solana_to_arc():
    """USDC on Solana → USDC on ARC."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.SOLANA, Stablecoin.USDC, 50.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 1, "1 bridge needed")
    ok &= assert_in(plan.bridges[0].protocol, [BridgeProtocol.WORMHOLE, BridgeProtocol.CCTP],
                    "Wormhole or CCTP bridge")
    return ok

def test_plan_bsc_to_arc():
    """USDT on BSC → USDC on ARC."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.BSC, Stablecoin.USDT, 200.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 1, "1 bridge needed")
    ok &= assert_eq(len(plan.swaps), 1, "1 swap needed")
    return ok

def test_plan_avalanche_to_arc():
    """DAI on Avalanche → USDC on ARC."""
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.AVALANCHE, Stablecoin.DAI, 75.0, Chain.ARC, Stablecoin.USDC)
    ok = assert_eq(len(plan.bridges), 1, "1 bridge needed")
    ok &= assert_eq(len(plan.swaps), 1, "1 swap needed")
    return ok

def test_plan_status():
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ETHEREUM, Stablecoin.USDT, 100.0)
    ok = assert_eq(plan.status, RouteStatus.SIMULATED, "Status = SIMULATED")
    return ok

def test_plan_created_at():
    planner = RoutePlanner(simulation=True)
    plan = planner.plan(Chain.ARC, Stablecoin.USDC, 100.0)
    ok = assert_gt(len(plan.created_at), 0, "Has created_at timestamp")
    return ok

def test_portal_transfer_success():
    portal = StablecoinPortal(simulation=True)
    result = portal.transfer(Chain.ETHEREUM, Stablecoin.USDT, 100.0)
    ok = assert_eq(result.success, True, "Transfer succeeds in simulation")
    ok &= assert_gt(result.plan.expected_output, 0, "Has expected output")
    return ok

def test_portal_transfer_zero_amount():
    portal = StablecoinPortal(simulation=True)
    result = portal.transfer(Chain.ARC, Stablecoin.USDC, 0)
    ok = assert_eq(result.success, False, "Zero amount fails")
    ok &= assert_in("> 0", result.message, "Error message mentions > 0")
    return ok

def test_portal_transfer_negative():
    portal = StablecoinPortal(simulation=True)
    result = portal.transfer(Chain.ARC, Stablecoin.USDC, -10)
    ok = assert_eq(result.success, False, "Negative amount fails")
    return ok

def test_portal_transfer_slippage_override():
    portal = StablecoinPortal(simulation=True)
    result = portal.transfer(Chain.ARC, Stablecoin.USDT, 100.0, slippage_pct=1.0)
    ok = assert_eq(result.plan.slippage_tolerance_pct, 1.0, "Slippage override applied")
    return ok

def test_portal_transfer_slippage_clamped():
    portal = StablecoinPortal(simulation=True)
    result = portal.transfer(Chain.ARC, Stablecoin.USDT, 100.0, slippage_pct=10.0)
    ok = assert_eq(result.plan.slippage_tolerance_pct, 3.0, "Slippage clamped to max 3%")
    return ok

def test_executor_simulation():
    executor = TransferExecutor(simulation=True)
    plan = TransferPlan(source_chain=Chain.ARC, source_token=Stablecoin.USDC,
                        source_amount=100.0)
    result = executor.execute(plan)
    ok = assert_eq(result.status, RouteStatus.SIMULATED, "Simulation mode → SIMULATED")
    return ok

def test_plan_properties():
    plan = TransferPlan(source_chain=Chain.ARC, source_token=Stablecoin.USDC,
                        source_amount=100.0, target_chain=Chain.ARC,
                        target_token=Stablecoin.USDC)
    ok = assert_eq(plan.is_same_chain, True, "Same chain detected")
    ok &= assert_eq(plan.is_same_token, True, "Same token detected")
    ok &= assert_eq(plan.needs_bridge, False, "No bridge needed")
    ok &= assert_eq(plan.needs_swap, False, "No swap needed")
    return ok

def test_plan_properties_cross():
    plan = TransferPlan(source_chain=Chain.ETHEREUM, source_token=Stablecoin.USDT,
                        source_amount=100.0, target_chain=Chain.ARC,
                        target_token=Stablecoin.USDC)
    ok = assert_eq(plan.is_same_chain, False, "Different chain detected")
    ok &= assert_eq(plan.is_same_token, False, "Different token detected")
    ok &= assert_eq(plan.needs_bridge, True, "Bridge needed")
    ok &= assert_eq(plan.needs_swap, True, "Swap needed")
    return ok

def test_stablecoin_enum_values():
    ok = assert_eq(Stablecoin.USDC.value, "USDC", "USDC enum")
    ok &= assert_eq(Stablecoin.USDT.value, "USDT", "USDT enum")
    ok &= assert_eq(Stablecoin.DAI.value, "DAI", "DAI enum")
    ok &= assert_eq(Stablecoin.PYUSD.value, "PYUSD", "PYUSD enum")
    return ok

def test_chain_enum_values():
    ok = assert_eq(Chain.ARC.value, "arc", "ARC chain")
    ok &= assert_eq(Chain.ETHEREUM.value, "ethereum", "Ethereum chain")
    ok &= assert_eq(Chain.SOLANA.value, "solana", "Solana chain")
    return ok

def test_bridge_paths_coverage():
    """All supported source chains have at least one bridge path to ARC."""
    planner = RoutePlanner(simulation=True)
    source_chains = [Chain.ETHEREUM, Chain.BASE, Chain.SOLANA, Chain.ARBITRUM,
                     Chain.OPTIMISM, Chain.POLYGON, Chain.AVALANCHE, Chain.BSC]
    for sc in source_chains:
        ok = assert_in((sc, Chain.ARC), planner.BRIDGE_PATHS,
                       f"{sc.value} → ARC has bridge path")
        if not ok:
            return False
    return True

def test_swap_protocols_coverage():
    """ARC has at least one swap protocol."""
    planner = RoutePlanner(simulation=True)
    ok = assert_in(SwapProtocol.JUPITER, planner.SWAP_PROTOCOLS[Chain.ARC],
                   "ARC supports Jupiter swaps")
    return ok

def test_cli_transfer():
    """Test CLI transfer output."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "stablecoin_portal.py", "transfer",
         "--from-chain", "ethereum", "--from-token", "USDT",
         "--amount", "100"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI transfer exits 0")
    ok &= assert_in("Transfer Planned", result.stdout, "CLI shows success")
    return ok

def test_cli_list():
    """Test CLI list output."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "stablecoin_portal.py", "list"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI list exits 0")
    ok &= assert_in("Supported Source Chains", result.stdout, "CLI shows chains")
    ok &= assert_in("Supported Stablecoins", result.stdout, "CLI shows tokens")
    return ok


# ── Run ────────────────────────────────────────────────────────────

tests = [
    ("Slippage default", test_slippage_default),
    ("Slippage clamp min", test_slippage_clamp_min),
    ("Slippage clamp max", test_slippage_clamp_max),
    ("Apply slippage", test_apply_slippage),
    ("Same chain/token = no-op", test_plan_same_chain_same_token),
    ("Same chain, different token = swap", test_plan_same_chain_different_token),
    ("Cross chain, same token = bridge", test_plan_cross_chain_same_token),
    ("Cross chain, different token = bridge+swap", test_plan_cross_chain_different_token),
    ("Solana → ARC", test_plan_solana_to_arc),
    ("BSC → ARC", test_plan_bsc_to_arc),
    ("Avalanche → ARC", test_plan_avalanche_to_arc),
    ("Plan status = SIMULATED", test_plan_status),
    ("Plan has created_at", test_plan_created_at),
    ("Portal transfer success", test_portal_transfer_success),
    ("Portal zero amount", test_portal_transfer_zero_amount),
    ("Portal negative amount", test_portal_transfer_negative),
    ("Portal slippage override", test_portal_transfer_slippage_override),
    ("Portal slippage clamped", test_portal_transfer_slippage_clamped),
    ("Executor simulation mode", test_executor_simulation),
    ("Plan properties same", test_plan_properties),
    ("Plan properties cross", test_plan_properties_cross),
    ("Stablecoin enum values", test_stablecoin_enum_values),
    ("Chain enum values", test_chain_enum_values),
    ("Bridge paths coverage", test_bridge_paths_coverage),
    ("Swap protocols coverage", test_swap_protocols_coverage),
    ("CLI transfer", test_cli_transfer),
    ("CLI list", test_cli_list),
]

for name, fn in tests:
    test(name, fn)

total = passed + failed
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
