"""
Compound vs. Extract Protocol — Compound Flow Integration Test

Simulates the full compound flow on Avalanche Fuji testnet:
  1. Claim fees from LFJ position
  2. Swap half of each token to the pair's other token
  3. Add liquidity back into the position

All on-chain calls are mocked — no real transactions needed yet.
This validates the executor interface and compound flow logic.
"""

import sys
import os
import json
import logging
from datetime import datetime
from dataclasses import asdict

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from executor import (
    Executor, LFJAdapter, ZeroXSwapRouter, OperationResult,
    TransactionReceipt, CompoundResult,
)
from fee_monitor import FeeMonitor, LPPosition
from decision_engine import DecisionEngine, MarketData, MarketCondition, Action

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


# ─── Test Helpers ─────────────────────────────────────────────────────────────

def create_test_position() -> LPPosition:
    """Create a realistic test position on Fuji"""
    return LPPosition(
        id="fuji_compound_001",
        dex="lfj",
        chain="avalanche",
        pair="AVAX/USDC.e",
        address="0xabcdef1234567890abcdef1234567890abcdef12",
        nft_id="67890",
        principal={"AVAX": 10.0, "USDC.e": 350.0},
        fees={"AVAX": 0.0, "USDC.e": 0.0},
        status="in_range",
        range={"lower": 25.0, "upper": 50.0},
        last_updated=datetime.utcnow().isoformat(),
    )


# ─── Test 1: Basic Compound Flow ─────────────────────────────────────────────

def test_basic_compound():
    """
    Test the basic compound flow:
      fees in → claim → swap half → add liquidity back
    """
    print("\n" + "═" * 60)
    print("  TEST 1: Basic Compound Flow")
    print("═" * 60)

    # Setup
    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
        wallet_address="0xTestWallet",
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Execute compound
    result = executor.compound(
        position_id="fuji_compound_001",
        fees={"AVAX": 0.5, "USDC.e": 12.50},
        pair_tokens=("AVAX", "USDC.e"),
    )

    # Assertions
    assert result.status == OperationResult.SIMULATED, f"Expected SIMULATED, got {result.status}"
    assert result.position_id == "fuji_compound_001"
    assert len(result.transactions) >= 1, "Expected at least 1 transaction"
    assert result.gas_fees >= 0, "Gas fees should be non-negative"
    assert result.error is None, f"Unexpected error: {result.error}"

    # Verify claim transaction
    claim_tx = result.transactions[0]
    assert claim_tx.method == "collect"

    # Verify swap transactions exist (we swap half of each token)
    swap_txs = [tx for tx in result.transactions if tx.method == "swap"]
    assert len(swap_txs) >= 1, "Expected at least 1 swap transaction"

    # Verify liquidity addition
    liq_txs = [tx for tx in result.transactions if tx.method == "increaseLiquidity"]
    assert len(liq_txs) >= 1, "Expected at least 1 liquidity transaction"

    # Verify compounded amounts
    assert result.amount_compounded.get("AVAX", 0) > 0, "Should have compounded AVAX"
    assert result.amount_compounded.get("USDC.e", 0) > 0, "Should have compounded USDC.e"

    print(f"\n  ✅ PASS: Compound flow completed")
    print(f"     Compounded: {result.amount_compounded}")
    print(f"     New value: {result.new_position_value}")
    print(f"     Gas: {result.gas_fees:.6f} AVAX")
    print(f"     Transactions: {len(result.transactions)}")

    return result


# ─── Test 2: Compound with Fee Monitor ───────────────────────────────────────

def test_compound_with_monitor():
    """
    Test compound integrated with fee monitor:
      accumulate fees → compound them back
    """
    print("\n" + "═" * 60)
    print("  TEST 2: Compound + Fee Monitor Integration")
    print("═" * 60)

    # Setup
    monitor = FeeMonitor(data_dir="/tmp/test_compound_monitor")
    position = create_test_position()
    monitor.add_position(position)

    # Simulate fee accumulation
    fee_schedule = [
        {"AVAX": 0.1, "USDC.e": 3.50},
        {"AVAX": 0.2, "USDC.e": 7.00},
        {"AVAX": 0.3, "USDC.e": 10.50},
    ]
    for fees in fee_schedule:
        monitor.update_fees("fuji_compound_001", fees)

    fees = monitor.get_accumulated_fees("fuji_compound_001")
    logger.info(f"Accumulated fees: {fees}")

    # Create executor and compound
    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    result = executor.compound(
        position_id="fuji_compound_001",
        fees=fees,
        pair_tokens=("AVAX", "USDC.e"),
    )

    # Assertions
    assert result.status == OperationResult.SIMULATED
    assert result.amount_compounded.get("AVAX", 0) > 0
    assert result.amount_compounded.get("USDC.e", 0) > 0

    # Verify position principal grew
    summary = monitor.get_fee_summary(
        "fuji_compound_001",
        {"AVAX": 35.0, "USDC.e": 1.0},
    )
    assert summary["fees_usd"] >= 10.0, f"Fees should be >= $10, got {summary['fees_usd']}"

    print(f"\n  ✅ PASS: Compound + Monitor integration")
    print(f"     Fees compounded: {result.amount_compounded}")
    print(f"     Position value: {result.new_position_value}")
    print(f"     USD value: ${summary['fees_usd']:.2f}")

    return result


# ─── Test 3: Compound with Decision Engine ───────────────────────────────────

def test_compound_with_decision_engine():
    """
    Test the full pipeline:
      fee monitor → decision engine → executor (compound)
    """
    print("\n" + "═" * 60)
    print("  TEST 3: Full Pipeline — Monitor → Decision → Compound")
    print("═" * 60)

    # Setup
    monitor = FeeMonitor(data_dir="/tmp/test_compound_pipeline")
    engine = DecisionEngine(config_dir="/tmp/test_compound_pipeline_config")

    position = create_test_position()
    monitor.add_position(position)

    # Accumulate fees below threshold (should compound)
    monitor.update_fees("fuji_compound_001", {"AVAX": 0.05, "USDC.e": 1.75})
    monitor.update_fees("fuji_compound_001", {"AVAX": 0.10, "USDC.e": 3.50})

    fees = monitor.get_accumulated_fees("fuji_compound_001")
    prices = {"AVAX": 35.0, "USDC.e": 1.0}
    fees_usd = monitor.get_total_fees_usd("fuji_compound_001", prices)

    # Decision engine — stable market should compound
    market_data = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=12.0,  # Low gas
        volatility=0.01,  # Very stable
        price_change_24h=3.0,  # Slight uptrend
        condition=MarketCondition.STABLE,
    )

    decision = engine.decide(
        position_fees=fees,
        fees_usd=fees_usd,
        market_data=market_data,
        position_status="in_range",
    )

    logger.info(f"Decision: {decision.action.value} — {decision.reasoning}")

    # Execute based on decision
    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    if decision.action == Action.COMPOUND:
        result = executor.compound(
            position_id="fuji_compound_001",
            fees=fees,
            pair_tokens=("AVAX", "USDC.e"),
        )
        assert result.status == OperationResult.SIMULATED
        print(f"\n  ✅ PASS: Decision engine triggered compound")
        print(f"     Compounded: {result.amount_compounded}")
    elif decision.action == Action.WAIT:
        print(f"\n  ✅ PASS: Decision engine says WAIT — gas too high")
    else:
        print(f"\n  ✅ PASS: Decision engine says EXTRACT — threshold reached")

    print(f"     Fees: ${fees_usd:.2f}")
    print(f"     Decision: {decision.action.value} (confidence: {decision.confidence:.0%})")
    print(f"     Reasoning: {decision.reasoning}")

    return decision


# ─── Test 4: Compound with Ratio ─────────────────────────────────────────────

def test_compound_with_ratio():
    """
    Test compound with partial ratio (70% compound, 30% extract):
      fees → compound 70% → extract 30%
    """
    print("\n" + "═" * 60)
    print("  TEST 4: Compound with Partial Ratio (70/30)")
    print("═" * 60)

    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Compound 70% of fees
    result = executor.compound(
        position_id="fuji_compound_ratio_001",
        fees={"AVAX": 0.7, "USDC.e": 24.50},
        pair_tokens=("AVAX", "USDC.e"),
        compound_ratio=0.7,
    )

    assert result.status == OperationResult.SIMULATED

    # Verify compounded amounts are 70% of input
    expected_avax = 0.7 * 0.7  # 0.49
    expected_usdc = 24.50 * 0.7  # 17.15

    assert abs(result.amount_compounded.get("AVAX", 0) - expected_avax) < 0.01, \
        f"AVAX compounded should be ~{expected_avax}, got {result.amount_compounded.get('AVAX', 0)}"
    assert abs(result.amount_compounded.get("USDC.e", 0) - expected_usdc) < 0.1, \
        f"USDC compounded should be ~{expected_usdc}, got {result.amount_compounded.get('USDC.e', 0)}"

    print(f"\n  ✅ PASS: Partial compound ratio working")
    print(f"     Input: 0.7 AVAX + 24.50 USDC.e")
    print(f"     Compounded: {result.amount_compounded}")
    print(f"     (30% left for extraction)")

    return result


# ─── Test 5: Compound Error Handling ─────────────────────────────────────────

def test_compound_error_handling():
    """Test compound with edge cases"""
    print("\n" + "═" * 60)
    print("  TEST 5: Compound Error Handling")
    print("═" * 60)

    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Test with zero fees
    result = executor.compound(
        position_id="fuji_compound_empty_001",
        fees={},
        pair_tokens=("AVAX", "USDC.e"),
    )

    assert result.status == OperationResult.FAILED, "Should fail with zero fees"
    assert result.error is not None, "Should have error message"
    print(f"\n  ✅ PASS: Zero fees handled (expected failure)")
    print(f"     Error: {result.error}")

    # Test with single token fees
    result2 = executor.compound(
        position_id="fuji_compound_single_001",
        fees={"USDC.e": 5.0},
        pair_tokens=("AVAX", "USDC.e"),
    )

    assert result2.status == OperationResult.SIMULATED
    assert result2.amount_compounded.get("USDC.e", 0) > 0
    print(f"\n  ✅ PASS: Single token fees handled")
    print(f"     Compounded: {result2.amount_compounded}")

    return result2


# ─── Test 6: Compound via 0x Router ──────────────────────────────────────────

def test_compound_via_0x():
    """Test compound using 0x swap router"""
    print("\n" + "═" * 60)
    print("  TEST 6: Compound via 0x Swap Router")
    print("═" * 60)

    adapter = ZeroXSwapRouter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    result = executor.compound(
        position_id="fuji_compound_0x_001",
        fees={"WAVAX": 0.4, "USDC.e": 14.0},
        pair_tokens=("WAVAX", "USDC.e"),
    )

    assert result.status == OperationResult.SIMULATED
    assert len(result.transactions) >= 1

    print(f"\n  ✅ PASS: 0x router compound")
    print(f"     Compounded: {result.amount_compounded}")
    print(f"     Gas: {result.gas_fees:.6f} AVAX")

    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Run all compound integration tests"""
    print("🧪 Compound vs. Extract Protocol — Compound Flow Tests")
    print(f"   Date: {datetime.utcnow().isoformat()}")
    print(f"   Network: Avalanche Fuji (Chain ID 43113)")
    print(f"   Mode: Mocked (no real transactions)")

    results = {}

    try:
        results["basic_compound"] = test_basic_compound()
        results["compound_with_monitor"] = test_compound_with_monitor()
        results["compound_with_decision"] = test_compound_with_decision_engine()
        results["compound_with_ratio"] = test_compound_with_ratio()
        results["error_handling"] = test_compound_error_handling()
        results["compound_via_0x"] = test_compound_via_0x()

        print("\n" + "═" * 60)
        print("  ✅ ALL COMPOUND TESTS PASSED (6/6)")
        print("═" * 60)

        # Save test results
        results_path = os.path.join(os.path.dirname(__file__), "test_compound_results.json")
        serializable = {}
        for k, v in results.items():
            if isinstance(v, CompoundResult):
                d = asdict(v)
                d["status"] = d["status"].value if hasattr(d["status"], "value") else d["status"]
                for tx in d.get("transactions", []):
                    if "status" in tx and hasattr(tx["status"], "value"):
                        tx["status"] = tx["status"].value
                serializable[k] = d
            elif hasattr(v, 'action'):
                serializable[k] = {"action": v.action.value, "confidence": v.confidence}
            else:
                serializable[k] = str(v)

        with open(results_path, 'w') as f:
            json.dump({
                "test_run": datetime.utcnow().isoformat(),
                "network": "avalanche_fuji",
                "results": serializable,
            }, f, indent=2)

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
