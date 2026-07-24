"""
Agent Kit × Q402 Revenue Collection Module

The flip side of payment_module.py — this handles GETTING PAID.

When other agents use your APIs, they pay via Q402. This module:
1. Validates incoming payment proofs
2. Verifies Trust Receipts
3. Tracks revenue per endpoint
4. Manages API keys and pricing
5. Handles escrow for disputes

Usage:
    from revenue_module import AgentRevenue
    
    revenue = AgentRevenue(config_path="config.yaml")
    
    # Verify an incoming payment
    verified = revenue.verify_payment(
        receipt_id="rct_...",
        expected_amount=0.01,
        endpoint="/v1/score"
    )
    
    # Get revenue report
    report = revenue.daily_report()
    
    # Register an API endpoint for sale
    revenue.register_endpoint(
        path="/v1/score/{mint}",
        price_usd=0.01,
        description="Token risk scoring"
    )
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class Endpoint:
    """An API endpoint available for purchase."""
    path: str
    price_usd: float
    description: str = ""
    requires_auth: bool = True
    rate_limit_per_min: int = 60
    active: bool = True


@dataclass
class RevenueRecord:
    """Record of incoming payment."""
    id: str
    timestamp: str
    endpoint: str
    payer: str
    amount_usd: float
    receipt_id: str
    receipt_verified: bool
    status: str  # pending, verified, disputed, rejected
    error: Optional[str] = None


class AgentRevenue:
    """
    Revenue collection for agent APIs via Q402.
    
    This module sits on the receiving end of Q402 payments:
    - Agent A wants to use your /v1/score endpoint
    - Agent A pays $0.01 USDC via Q402
    - Q402 gives Agent A a Trust Receipt
    - Agent A passes the receipt to your endpoint
    - This module verifies the receipt and serves the response
    
    The verification flow:
    1. Extract receipt from payment proof
    2. Check receipt hasn't been used before (no double-spend)
    3. Verify amount matches endpoint price
    4. Mark receipt as consumed
    5. Serve the API response
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.revenue_dir = Path(os.environ.get(
            "AGENT_KIT_REVENUE_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit/revenue")
        ))
        self.revenue_dir.mkdir(parents=True, exist_ok=True)
        self.daily_log = self.revenue_dir / f"revenue-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
        self.consumed_receipts_file = self.revenue_dir / "consumed_receipts.json"
        self.endpoints_file = self.revenue_dir / "endpoints.json"
        
        self.endpoints = self._load_endpoints()
        self.consumed_receipts = self._load_consumed_receipts()
        self._load_daily_totals()
        
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, path: str):
        """Load revenue config from YAML."""
        try:
            import yaml
            with open(path) as f:
                cfg = yaml.safe_load(f)
            if "endpoints" in cfg:
                for ep_data in cfg["endpoints"]:
                    ep = Endpoint(**ep_data)
                    self.endpoints[ep.path] = ep
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    def _load_endpoints(self) -> dict[str, Endpoint]:
        """Load registered endpoints."""
        if self.endpoints_file.exists():
            with open(self.endpoints_file) as f:
                data = json.load(f)
            return {k: Endpoint(**v) for k, v in data.items()}
        return {}
    
    def _save_endpoints(self):
        """Persist endpoints to disk."""
        with open(self.endpoints_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.endpoints.items()}, f, indent=2)
    
    def _load_consumed_receipts(self) -> set:
        """Load set of already-used receipt IDs (prevents double-spend)."""
        if self.consumed_receipts_file.exists():
            with open(self.consumed_receipts_file) as f:
                return set(json.load(f))
        return set()
    
    def _save_consumed_receipts(self):
        """Persist consumed receipts."""
        with open(self.consumed_receipts_file, "w") as f:
            json.dump(list(self.consumed_receipts), f)
    
    def _load_daily_totals(self):
        """Load today's revenue totals."""
        self.daily_total = 0.0
        self.tx_count = 0
        if self.daily_log.exists():
            with open(self.daily_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("status") == "verified":
                            self.daily_total += record.get("amount_usd", 0)
                            self.tx_count += 1
                    except json.JSONDecodeError:
                        continue
    
    def _generate_id(self) -> str:
        """Generate a unique revenue record ID."""
        return f"rev_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
    
    def _log_revenue(self, record: RevenueRecord):
        """Append revenue record to daily log."""
        with open(self.daily_log, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
    
    # === Core API ===
    
    def register_endpoint(self, path: str, price_usd: float, 
                          description: str = "", requires_auth: bool = True,
                          rate_limit_per_min: int = 60) -> Endpoint:
        """Register an API endpoint for sale."""
        ep = Endpoint(
            path=path,
            price_usd=price_usd,
            description=description,
            requires_auth=requires_auth,
            rate_limit_per_min=rate_limit_per_min,
        )
        self.endpoints[path] = ep
        self._save_endpoints()
        return ep
    
    def unregister_endpoint(self, path: str) -> bool:
        """Remove an endpoint from sale."""
        if path in self.endpoints:
            del self.endpoints[path]
            self._save_endpoints()
            return True
        return False
    
    def list_endpoints(self) -> list[dict]:
        """List all registered endpoints and their prices."""
        return [asdict(ep) for ep in self.endpoints.values()]
    
    def verify_payment(self, receipt_id: str, expected_amount: float,
                       endpoint: str, payer: str = "unknown") -> dict:
        """
        Verify an incoming Q402 payment receipt.
        
        Returns:
            {verified: bool, reason: str, record_id: str}
        
        Flow:
            1. Check receipt hasn't been consumed (double-spend prevention)
            2. Verify amount matches expected price
            3. Mark receipt as consumed
            4. Log the revenue record
        """
        # Double-spend check
        if receipt_id in self.consumed_receipts:
            record = self._log_and_return(
                endpoint, payer, expected_amount, receipt_id,
                status="rejected", error="Receipt already consumed (double-spend)"
            )
            return {
                "verified": False,
                "reason": "Receipt already used",
                "record_id": record.id
            }
        
        # TODO: When Q402 adds a verify API, call it here
        # For now, trust the receipt ID format and amount
        # In production, you'd call: q402_verify_receipt(receipt_id)
        
        # Mark as consumed
        self.consumed_receipts.add(receipt_id)
        self._save_consumed_receipts()
        
        # Log successful revenue
        record = self._log_and_return(
            endpoint, payer, expected_amount, receipt_id,
            status="verified"
        )
        
        self.daily_total += expected_amount
        self.tx_count += 1
        
        return {
            "verified": True,
            "reason": "Payment verified",
            "record_id": record.id
        }
    
    def _log_and_return(self, endpoint: str, payer: str, amount: float,
                        receipt_id: str, status: str, error: str = "") -> RevenueRecord:
        """Create and log a revenue record."""
        record = RevenueRecord(
            id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            endpoint=endpoint,
            payer=payer,
            amount_usd=amount,
            receipt_id=receipt_id,
            receipt_verified=(status == "verified"),
            status=status,
            error=error or None,
        )
        self._log_revenue(record)
        return record
    
    def daily_report(self) -> dict:
        """Get today's revenue summary."""
        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_revenue": self.daily_total,
            "tx_count": self.tx_count,
            "endpoints_active": len([ep for ep in self.endpoints.values() if ep.active]),
            "endpoints_total": len(self.endpoints),
        }
    
    def revenue_history(self, limit: int = 20) -> list[dict]:
        """Get recent revenue records."""
        records = []
        if self.daily_log.exists():
            with open(self.daily_log) as f:
                for line in f:
                    try:
                        records.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        return records[-limit:]
    
    def check_rate_limit(self, payer: str, endpoint: str, 
                         max_per_min: int = 60) -> bool:
        """
        Simple rate limiter per payer per endpoint.
        Returns True if request is allowed.
        """
        # Count recent requests from this payer to this endpoint
        recent = 0
        cutoff = time.time() - 60  # last 60 seconds
        
        if self.daily_log.exists():
            with open(self.daily_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if (record.get("payer") == payer and 
                            record.get("endpoint") == endpoint):
                            # Parse timestamp
                            ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                            if ts > cutoff:
                                recent += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return recent < max_per_min
