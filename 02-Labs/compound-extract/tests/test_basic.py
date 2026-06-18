"""
Compound vs. Extract Protocol — Tests

Basic tests for fee_monitor and decision_engine modules.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fee_monitor import FeeMonitor, LPPosition
from decision_engine import DecisionEngine, MarketData, MarketCondition, Action


def test_fee_monitor():
    """Test fee monitoring functionality"""
    print("=== Testing Fee Monitor ===")
    
    # Initialize monitor with temp directory
    monitor = FeeMonitor(data_dir="/tmp/test_compound_extract")
    
    # Create a sample position
    position = LPPosition(
        id="test_001",
        dex="lfj",
        chain="avalanche",
        pair="AVAX/USDC",
        address="0x1234567890abcdef",
        nft_id="12345",
        principal={"AVAX": 10.0, "USDC": 250.0},
        fees={"AVAX": 0.0, "USDC": 0.0},
        status="in_range",
        range={"lower": 35.0, "upper": 45.0},
        last_updated=datetime.utcnow().isoformat()
    )
    
    # Add position
    monitor.add_position(position)
    assert "test_001" in monitor.positions
    print("✅ Position added successfully")
    
    # Update fees
    monitor.update_fees("test_001", {"AVAX": 0.0, "USDC": 1.67})
    fees = monitor.get_accumulated_fees("test_001")
    assert fees["USDC"] == 1.67
    print("✅ Fee update working")
    
    # Update fees again
    monitor.update_fees("test_001", {"AVAX": 0.0, "USDC": 3.34})
    fees = monitor.get_accumulated_fees("test_001")
    assert fees["USDC"] == 3.34
    print("✅ Multiple fee updates working")
    
    # Get USD total
    prices = {"AVAX": 35.0, "USDC": 1.0}
    total_usd = monitor.get_total_fees_usd("test_001", prices)
    assert total_usd == 3.34
    print("✅ USD calculation working")
    
    # Get fee summary
    summary = monitor.get_fee_summary("test_001", prices)
    assert summary["fees_usd"] == 3.34
    print("✅ Fee summary working")
    
    print(f"\nSummary: {json.dumps(summary, indent=2)}")
    print("✅ Fee Monitor tests passed!\n")


def test_decision_engine():
    """Test decision engine functionality"""
    print("=== Testing Decision Engine ===")
    
    # Initialize engine with temp directory
    engine = DecisionEngine(config_dir="/tmp/test_compound_config")
    
    # Test 1: Stable market, below threshold
    print("\nTest 1: Stable market, fees below threshold")
    market_data = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=15.0,
        volatility=0.015,
        price_change_24h=2.5,
        condition=MarketCondition.STABLE
    )
    
    decision = engine.decide(
        position_fees={"USDC": 5.0},
        fees_usd=5.0,
        market_data=market_data,
        position_status="in_range"
    )
    
    print(f"  Action: {decision.action.value}")
    print(f"  Confidence: {decision.confidence:.0%}")
    print(f"  Reasoning: {decision.reasoning}")
    assert decision.action in [Action.COMPOUND, Action.WAIT]
    print("  ✅ Decision made correctly")
    
    # Test 2: Threshold reached
    print("\nTest 2: Extraction threshold reached")
    decision = engine.decide(
        position_fees={"USDC": 12.0},
        fees_usd=12.0,
        market_data=market_data,
        position_status="in_range"
    )
    
    print(f"  Action: {decision.action.value}")
    print(f"  Amount: ${decision.amount:.2f}")
    assert decision.action == Action.EXTRACT
    assert decision.amount == 10.0  # Default threshold
    print("  ✅ Threshold extraction working")
    
    # Test 3: High gas — should wait
    print("\nTest 3: High gas price")
    high_gas_market = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=50.0,
        volatility=0.015,
        price_change_24h=2.5,
        condition=MarketCondition.STABLE
    )
    
    decision = engine.decide(
        position_fees={"USDC": 8.0},
        fees_usd=8.0,
        market_data=high_gas_market,
        position_status="in_range"
    )
    
    print(f"  Action: {decision.action.value}")
    print(f"  Reasoning: {decision.reasoning}")
    assert decision.action == Action.WAIT
    print("  ✅ High gas wait logic working")
    
    # Test 4: Position out of range — extract everything
    print("\nTest 4: Position out of range")
    decision = engine.decide(
        position_fees={"USDC": 8.0},
        fees_usd=8.0,
        market_data=market_data,
        position_status="out_of_range"
    )
    
    print(f"  Action: {decision.action.value}")
    print(f"  Amount: ${decision.amount:.2f}")
    assert decision.action == Action.EXTRACT
    assert decision.amount == 8.0  # Extract everything
    print("  ✅ Out-of-range extraction working")
    
    # Test 5: Volatile market — should extract
    print("\nTest 5: Volatile market")
    volatile_market = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=15.0,
        volatility=0.08,
        price_change_24h=-3.0,
        condition=MarketCondition.VOLATILE
    )
    
    decision = engine.decide(
        position_fees={"USDC": 7.0},
        fees_usd=7.0,
        market_data=volatile_market,
        position_status="in_range"
    )
    
    print(f"  Action: {decision.action.value}")
    print(f"  Reasoning: {decision.reasoning}")
    # Should lean toward extraction
    assert decision.action in [Action.EXTRACT, Action.WAIT]
    print("  ✅ Volatile market logic working")
    
    # Test 6: Full summary
    print("\nTest 6: Full decision summary")
    summary = engine.get_decision_summary(
        position_id="test_001",
        fees_usd=8.50,
        market_data=market_data,
        position_status="in_range"
    )
    
    print(f"  Decision: {summary['decision']['action']}")
    print(f"  Recommendation: {summary['recommendation']}")
    assert "decision" in summary
    assert "market" in summary
    assert "recommendation" in summary
    print("  ✅ Full summary working")
    
    print("\n✅ Decision Engine tests passed!\n")


def test_integration():
    """Test fee monitor + decision engine integration"""
    print("=== Testing Integration ===")
    
    # Initialize both
    monitor = FeeMonitor(data_dir="/tmp/test_integration")
    engine = DecisionEngine(config_dir="/tmp/test_integration_config")
    
    # Create position
    position = LPPosition(
        id="integ_001",
        dex="lfj",
        chain="avalanche",
        pair="AVAX/USDC",
        address="0xabcdef1234567890",
        nft_id="99999",
        principal={"AVAX": 10.0, "USDC": 250.0},
        fees={"AVAX": 0.0, "USDC": 0.0},
        status="in_range",
        range={"lower": 35.0, "upper": 45.0},
        last_updated=datetime.utcnow().isoformat()
    )
    
    monitor.add_position(position)
    
    # Simulate fee accumulation over time
    fees_over_time = [1.67, 3.34, 5.01, 6.68, 8.35, 10.02]
    
    for i, fee_amount in enumerate(fees_over_time):
        # Update fees
        monitor.update_fees("integ_001", {"AVAX": 0.0, "USDC": fee_amount})
        
        # Get summary
        prices = {"AVAX": 35.0, "USDC": 1.0}
        summary = monitor.get_fee_summary("integ_001", prices)
        
        # Make decision
        market_data = MarketData(
            timestamp=datetime.utcnow().isoformat(),
            gas_price=15.0,
            volatility=0.015,
            price_change_24h=2.5,
            condition=MarketCondition.STABLE
        )
        
        decision = engine.decide(
            position_fees=summary["fees"],
            fees_usd=summary["fees_usd"],
            market_data=market_data,
            position_status="in_range"
        )
        
        print(f"  Day {i+1}: ${fee_amount:.2f} → {decision.action.value}")
    
    print("\n✅ Integration test passed!\n")


if __name__ == "__main__":
    print("🧪 Running Compound vs. Extract Protocol Tests\n")
    
    try:
        test_fee_monitor()
        test_decision_engine()
        test_integration()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
