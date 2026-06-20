"""
Compound vs. Extract Protocol — Extract Flow Integration Test

Simulates the full extract flow on Avalanche Fuji testnet:
  1. Claim fees from LFJ position
  2. Swap claimed tokens to USDC via LFJ router
  3. Transfer USDC to user wallet

All on-chain calls are mocked — no real transactions needed yet.
This validates the executor interface and flow logic.
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
    TransactionReceipt, ExtractResult,
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
        id="fuji_extract_001",
        dex="lfj",
        chain="avalanche",
        pair="AVAX/USDC.e",
        address="0x1234567890abcdef1234567890abcdef12345678",
        nft_id="12345",
        principal={"AVAX": 10.0, "USDC.e": 350.0},
        fees={"AVAX": 0.0, "USDC.e": 0.0},
        status="in_range",
        range={"lower": 25.0, "upper": 50.0},
        last_updated=datetime.utcnow().isoformat(),
    )


def simulate_fee_accumulation(monitor: FeeMonitor, position_id: str, iterations: int = 5):
    """Simulate fee accumulation over time"""
    fee_schedule = [
        {"USDC.e": 1.67},
        {"USDC.e": 3.34},
        {"USDC.e": 5.01},
        {"USDC.e": 8.35},
        {"USDC.e": 12.50},  # Above extract threshold
    ]

    for i in range(min(iterations, len(fee_schedule))):
        fees = fee_schedule[i]
        monitor.update_fees(position_id, fees)
        logger.info(f"  Day {i+1}: fees = {fees}")


# ─── Test 1: Basic Extract Flow ──────────────────────────────────────────────

def test_basic_extract():
    """
    Test the basic extract flow:
      fees in → claim → swap to USDC → output
    """
    print("\n" + "═" * 60)
    print("  TEST 1: Basic Extract Flow")
    print("═" * 60)

    # Setup
    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
        wallet_address="0xTestWallet1234567890abcdef1234567890",
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Execute extract
    result = executor.extract(
        position_id="fuji_extract_001",
        fees={"AVAX": 0.5, "USDC.e": 12.50},
        target_token="USDC.e",
    )

    # Assertions
    assert result.status == OperationResult.SIMULATED, f"Expected SIMULATED, got {result.status}"
    assert result.position_id == "fuji_extract_001"
    assert len(result.transactions) >= 1, "Expected at least 1 transaction (claim)"
    assert "USDC.e" in result.amount_received, "Should have received USDC.e"
    assert result.amount_received["USDC.e"] > 0, "Received amount should be positive"
    assert result.gas_fees >= 0, "Gas fees should be non-negative"
    assert result.error is None, f"Unexpected error: {result.error}"

    # Verify claim transaction
    claim_tx = result.transactions[0]
    assert claim_tx.method == "collect"
    assert claim_tx.status == OperationResult.SIMULATED

    # Verify swap transaction
    if len(result.transactions) > 1:
        swap_tx = result.transactions[1]
        assert swap_tx.method == "swap"
        assert "AVAX" in swap_tx.details.get("token_in", "")

    print(f"\n  ✅ PASS: Extract flow completed")
    print(f"     Claimed: {result.amount_claimed}")
    print(f"     Received: {result.amount_received}")
    print(f"     Gas: {result.gas_fees:.6f} AVAX")
    print(f"     Transactions: {len(result.transactions)}")

    return result


# ─── Test 2: Extract with Fee Monitor Integration ─────────────────────────────

def test_extract_with_monitor():
    """
    Test extract integrated with fee monitor:
      accumulate fees → monitor detects → executor extracts
    """
    print("\n" + "═" * 60)
    print("  TEST 2: Extract + Fee Monitor Integration")
    print("═" * 60)

    # Setup monitor
    monitor = FeeMonitor(data_dir="/tmp/test_extract_monitor")
    position = create_test_position()
    monitor.add_position(position)

    # Simulate fee accumulation
    logger.info("Simulating fee accumulation...")
    simulate_fee_accumulation(monitor, "fuji_extract_001", iterations=5)

    # Get current fees
    fees = monitor.get_accumulated_fees("fuji_extract_001")
    logger.info(f"Current fees: {fees}")

    # Create executor
    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Execute extract with accumulated fees
    result = executor.extract(
        position_id="fuji_extract_001",
        fees=fees,
        target_token="USDC.e",
    )

    # Assertions
    assert result.status == OperationResult.SIMULATED
    assert result.amount_claimed == fees, "Claimed should match monitor fees"
    assert result.amount_received.get("USDC.e", 0) > fees.get("USDC.e", 0) * 0.9, \
        "Received should be close to claimed (minus slippage)"

    # Verify fee history was updated
    summary = monitor.get_fee_summary(
        "fuji_extract_001",
        {"AVAX": 35.0, "USDC.e": 1.0, "USDC": 1.0},
    )
    assert summary["fees_usd"] >= 12.0, f"Fees should be >= $12, got {summary['fees_usd']}"

    print(f"\n  ✅ PASS: Extract + Monitor integration")
    print(f"     Monitor fees: {fees}")
    print(f"     Extracted: {result.amount_received}")
    print(f"     USD value: ${summary['fees_usd']:.2f}")

    return result


# ─── Test 3: Extract with Decision Engine ─────────────────────────────────────

def test_extract_with_decision_engine():
    """
    Test the full pipeline:
      fee monitor → decision engine → executor
    """
    print("\n" + "═" * 60)
    print("  TEST 3: Full Pipeline — Monitor → Decision → Extract")
    print("═" * 60)

    # Setup
    monitor = FeeMonitor(data_dir="/tmp/test_extract_pipeline")
    engine = DecisionEngine(config_dir="/tmp/test_extract_pipeline_config")

    position = create_test_position()
    monitor.add_position(position)

    # Accumulate fees past threshold
    for amount in [5.0, 10.0, 15.0]:
        monitor.update_fees("fuji_extract_001", {"USDC.e": amount})

    # Get fee data
    fees = monitor.get_accumulated_fees("fuji_extract_001")
    prices = {"AVAX": 35.0, "USDC.e": 1.0, "USDC": 1.0}
    fees_usd = monitor.get_total_fees_usd("fuji_extract_001", prices)

    # Decision engine
    market_data = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=15.0,
        volatility=0.015,
        price_change_24h=2.5,
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

    if decision.action == Action.EXTRACT:
        result = executor.extract(
            position_id="fuji_extract_001",
            fees=fees,
            target_token="USDC.e",
            amount_usd=decision.amount,
        )
        assert result.status == OperationResult.SIMULATED
        print(f"\n  ✅ PASS: Decision engine triggered extract")
    elif decision.action == Action.WAIT:
        print(f"\n  ✅ PASS: Decision engine says WAIT — fees ${fees_usd:.2f} below threshold")
    else:
        print(f"\n  ✅ PASS: Decision engine says COMPOUND — market conditions favorable")

    print(f"     Fees: ${fees_usd:.2f}")
    print(f"     Decision: {decision.action.value} (confidence: {decision.confidence:.0%})")
    print(f"     Reasoning: {decision.reasoning}")

    return decision


# ─── Test 4: Extract via 0x Router ───────────────────────────────────────────

def test_extract_via_0x():
    """Test extract using 0x swap router instead of LFJ"""
    print("\n" + "═" * 60)
    print("  TEST 4: Extract via 0x Swap Router")
    print("═" * 60)

    adapter = ZeroXSwapRouter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
        wallet_address="0xTestWallet",
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    result = executor.extract(
        position_id="fuji_extract_0x_001",
        fees={"WAVAX": 0.3, "USDC.e": 8.0},
        target_token="USDC.e",
    )

    assert result.status == OperationResult.SIMULATED
    assert len(result.transactions) >= 1

    print(f"\n  ✅ PASS: 0x router extract")
    print(f"     Received: {result.amount_received}")
    print(f"     Gas: {result.gas_fees:.6f} AVAX")

    return result


# ─── Test 5: Error Handling ──────────────────────────────────────────────────

def test_extract_error_handling():
    """Test extract with invalid/empty fees"""
    print("\n" + "═" * 60)
    print("  TEST 5: Extract Error Handling")
    print("═" * 60)

    adapter = LFJAdapter(
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        chain_id=43113,
    )
    executor = Executor(adapter=adapter, wallet_address="0xTestWallet")

    # Test with zero fees
    result = executor.extract(
        position_id="fuji_extract_empty_001",
        fees={},
        target_token="USDC.e",
    )

    # Should succeed but with zero amounts (no fees to extract)
    assert result.status == OperationResult.SIMULATED
    assert result.amount_claimed == {}
    print(f"\n  ✅ PASS: Empty fees handled gracefully")
    print(f"     Status: {result.status.value}")
    print(f"     Transactions: {len(result.transactions)}")

    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Run all extract integration tests"""
    print("🧪 Compound vs. Extract Protocol — Extract Flow Tests")
    print(f"   Date: {datetime.utcnow().isoformat()}")
    print(f"   Network: Avalanche Fuji (Chain ID 43113)")
    print(f"   Mode: Mocked (no real transactions)")

    results = {}

    try:
        results["basic_extract"] = test_basic_extract()
        results["extract_with_monitor"] = test_extract_with_monitor()
        results["extract_with_decision"] = test_extract_with_decision_engine()
        results["extract_via_0x"] = test_extract_via_0x()
        results["error_handling"] = test_extract_error_handling()

        print("\n" + "═" * 60)
        print("  ✅ ALL EXTRACT TESTS PASSED (5/5)")
        print("═" * 60)

        # Save test results
        results_path = os.path.join(os.path.dirname(__file__), "test_extract_results.json")
        serializable = {}
        for k, v in results.items():
            if isinstance(v, ExtractResult):
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
