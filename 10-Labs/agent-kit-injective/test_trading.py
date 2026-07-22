#!/usr/bin/env python3
"""Tests for Agent Kit × Injective Trading Module."""

import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_module import AgentTrading, TradingPolicy, quick_validate


def test_policy_validation():
    """Test that risk policy checks work correctly."""
    policy = TradingPolicy(
        max_position_usd=100.0,
        max_leverage=10,
        approved_markets=["BTC", "ETH", "SOL"],
        max_open_positions=3,
    )
    
    trading = AgentTrading(policy=policy)
    
    # Should pass — valid trade
    result = trading.validate("BTC", "long", 10.0, 5)
    assert result["approved"], f"Expected approved, got: {result}"
    
    # Should fail — unapproved market
    result = trading.validate("DOGE", "long", 10.0, 5)
    assert not result["approved"], f"Expected blocked (unapproved market), got: {result}"
    
    # Should fail — over leverage limit
    result = trading.validate("BTC", "long", 10.0, 20)
    assert not result["approved"], f"Expected blocked (over leverage), got: {result}"
    
    # Should fail — over position size
    result = trading.validate("BTC", "long", 50.0, 10)
    assert not result["approved"], f"Expected blocked (over position size), got: {result}"
    
    print("✅ Policy validation tests passed")


def test_position_tracking():
    """Test open/close position tracking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        audit_dir.mkdir()
        
        policy = TradingPolicy(max_open_positions=2)
        trading = AgentTrading(policy=policy)
        trading.audit_dir = audit_dir
        trading.trade_log = audit_dir / "test-trades.jsonl"
        trading.positions_file = audit_dir / "positions.json"
        
        # Open a position
        record = trading.record_trade(
            "BTC", "long", 10.0, 5, entry_price=65000.0,
            stop_loss=61750.0, take_profit=71500.0
        )
        assert record.status == "open"
        assert len(trading.open_positions) == 1
        
        # Open another
        record = trading.record_trade(
            "ETH", "short", 20.0, 3, entry_price=3500.0
        )
        assert len(trading.open_positions) == 2
        
        # Now validate should fail (max 2 positions)
        result = trading.validate("SOL", "long", 5.0, 2)
        assert not result["approved"], f"Expected blocked (max positions), got: {result}"
        
        # Close one
        closed = trading.close_position(record.id, exit_price=3400.0, pnl=20.0, fee_earned=1.2)
        assert closed is not None
        assert closed.pnl == 20.0
        assert len(trading.open_positions) == 1
        
        # Now validate should pass again
        result = trading.validate("SOL", "long", 5.0, 2)
        assert result["approved"], f"Expected approved, got: {result}"
        
    print("✅ Position tracking tests passed")


def test_command_formatting():
    """Test that trading commands are formatted correctly."""
    trading = AgentTrading()
    
    cmd = trading.format_open_command("BTC", "long", 10.0, 5, stop_loss=61750.0)
    assert "trade_open_eip712" in cmd
    assert "BTC" in cmd
    assert "long" in cmd
    assert "5" in cmd
    
    cmd = trading.format_close_command("BTC", "long")
    assert "trade_close_eip712" in cmd
    assert "BTC" in cmd
    
    print("✅ Command formatting tests passed")


def test_daily_summary():
    """Test daily summary generation."""
    trading = AgentTrading()
    summary = trading.get_daily_summary()
    
    assert "date" in summary
    assert "open_positions" in summary
    assert "total_pnl" in summary
    assert "total_fees_earned" in summary
    
    print("✅ Daily summary tests passed")


def test_quick_validate():
    """Test the quick_validate convenience function."""
    result = quick_validate("BTC", "long", 10.0, 5)
    assert result["approved"]
    
    result = quick_validate("DOGE", "long", 10.0, 5)
    assert not result["approved"]
    
    print("✅ Quick validate tests passed")


if __name__ == "__main__":
    print("🧪 Agent Kit × Injective Trading Module Tests\n")
    
    test_policy_validation()
    test_position_tracking()
    test_command_formatting()
    test_daily_summary()
    test_quick_validate()
    
    print("\n✅ All tests passed!")
