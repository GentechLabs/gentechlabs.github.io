#!/usr/bin/env python3
"""Tests for Agent Kit × Q402 Payment Module."""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from payment_module import AgentPayment, PaymentPolicy, quick_pay


def test_policy_validation():
    """Test that policy checks work correctly."""
    policy = PaymentPolicy(
        daily_limit_usd=100.0,
        per_tx_limit_usd=50.0,
        approved_chains=["base", "bnb"],
        approved_tokens=["USDC"],
        require_memo=True,
    )
    
    payment = AgentPayment(policy=policy)
    
    # Should pass — valid chain, token, amount, memo
    result = payment.validate("base", "USDC", "0x1234", 10.0, "API fee")
    assert result["approved"], f"Expected approved, got: {result}"
    
    # Should fail — wrong chain
    result = payment.validate("ethereum", "USDC", "0x1234", 10.0, "API fee")
    assert not result["approved"], f"Expected blocked (wrong chain), got: {result}"
    
    # Should fail — wrong token
    result = payment.validate("base", "USDT", "0x1234", 10.0, "API fee")
    assert not result["approved"], f"Expected blocked (wrong token), got: {result}"
    
    # Should fail — over per-tx limit
    result = payment.validate("base", "USDC", "0x1234", 100.0, "Big payment")
    assert not result["approved"], f"Expected blocked (over limit), got: {result}"
    
    # Should fail — no memo
    result = payment.validate("base", "USDC", "0x1234", 10.0, "")
    assert not result["approved"], f"Expected blocked (no memo), got: {result}"
    
    print("✅ Policy validation tests passed")


def test_daily_limit():
    """Test daily spending limit tracking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        audit_dir.mkdir()
        
        policy = PaymentPolicy(daily_limit_usd=50.0, per_tx_limit_usd=50.0, require_memo=False)
        payment = AgentPayment(policy=policy)
        payment.audit_dir = audit_dir
        payment.daily_log = audit_dir / "test-payments.jsonl"
        
        # Record a $30 payment
        record = payment.record_attempt("base", "USDC", "0x1234", 30.0, status="settled")
        assert record.status == "settled"
        assert payment.daily_total == 30.0
        
        # Record another $15 payment
        record = payment.record_attempt("base", "USDC", "0x5678", 15.0, status="settled")
        assert payment.daily_total == 45.0
        
        # Now $10 more should fail (would exceed $50 limit)
        result = payment.validate("base", "USDC", "0x9999", 10.0)
        assert not result["approved"], f"Expected blocked (daily limit), got: {result}"
        
        # $5 should pass
        result = payment.validate("base", "USDC", "0x9999", 5.0)
        assert result["approved"], f"Expected approved, got: {result}"
        
    print("✅ Daily limit tests passed")


def test_command_formatting():
    """Test that payment commands are formatted correctly."""
    payment = AgentPayment()
    
    cmd = payment.format_pay_command("base", "USDC", "0xd8dA6045", 5.0, "API access")
    assert "q402_pay" in cmd
    assert "base" in cmd
    assert "0xd8dA6045" in cmd
    assert "5.0" in cmd
    
    batch_cmd = payment.format_batch_command("base", "USDC", [
        {"to": "0x1111", "amount": 2.0, "memo": "Task 1"},
        {"to": "0x2222", "amount": 3.0, "memo": "Task 2"},
    ])
    assert "q402_batch_pay" in batch_cmd
    assert "0x1111" in batch_cmd
    
    print("✅ Command formatting tests passed")


def test_quick_pay():
    """Test the quick_pay convenience function."""
    # Should be valid
    result = quick_pay("base", "USDC", "0x1234", 5.0, "Test")
    assert result["valid"], f"Expected valid, got: {result}"
    assert result["command"] is not None
    assert "q402_pay" in result["command"]
    
    # Should be invalid — over limit
    result = quick_pay("base", "USDC", "0x1234", 100.0, "Too much")
    assert not result["valid"]
    assert result["command"] is None
    
    print("✅ Quick pay tests passed")


def test_daily_summary():
    """Test daily summary generation."""
    payment = AgentPayment()
    summary = payment.get_daily_summary()
    
    assert "date" in summary
    assert "total_spent" in summary
    assert "daily_limit" in summary
    assert "remaining" in summary
    assert "tx_count" in summary
    
    print("✅ Daily summary tests passed")


def test_audit_trail():
    """Test that audit records are written correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        audit_dir.mkdir()
        
        policy = PaymentPolicy(require_memo=False)
        payment = AgentPayment(policy=policy)
        payment.audit_dir = audit_dir
        payment.daily_log = audit_dir / "test-payments.jsonl"
        
        # Record a payment
        record = payment.record_attempt(
            "base", "USDC", "0x1234", 5.0,
            memo="Test payment", status="settled", receipt_id="rct_abc123"
        )
        
        # Verify the record was written
        assert payment.daily_log.exists()
        with open(payment.daily_log) as f:
            lines = f.readlines()
        assert len(lines) == 1
        
        data = json.loads(lines[0])
        assert data["id"].startswith("pay_")
        assert data["chain"] == "base"
        assert data["amount"] == 5.0
        assert data["receipt_id"] == "rct_abc123"
        assert data["status"] == "settled"
        
        # Record a blocked payment
        record = payment.record_attempt(
            "ethereum", "USDC", "0x5678", 5.0,
            status="blocked", error="Chain not approved"
        )
        
        with open(payment.daily_log) as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[1])["status"] == "blocked"
        
    print("✅ Audit trail tests passed")


if __name__ == "__main__":
    print("🧪 Agent Kit × Q402 Payment Module Tests\n")
    
    test_policy_validation()
    test_daily_limit()
    test_command_formatting()
    test_quick_pay()
    test_daily_summary()
    test_audit_trail()
    
    print("\n✅ All tests passed!")
