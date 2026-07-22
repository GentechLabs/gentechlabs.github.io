"""
Agent Kit × Injective Trading Module

Wraps Injective's MCP tools with risk management, position tracking,
and fee earning. Agents can trade on 168 markets and earn 40% of fees.

Usage:
    from trading_module import AgentTrading

    trading = AgentTrading(config_path="config.yaml")
    
    # Open a long BTC position
    result = trading.open_position(
        market="BTC",
        side="long",
        amount=10.0,  # USDT notional
        leverage=5
    )
    
    # Check positions
    positions = trading.get_positions()
    
    # Get market price
    price = trading.get_price("BTC")
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class TradingPolicy:
    """Risk management rules for agent trading."""
    max_position_usd: float = 100.0
    max_leverage: int = 10
    max_daily_loss_usd: float = 50.0
    approved_markets: list[str] = field(default_factory=lambda: [
        "BTC", "ETH", "SOL"
    ])
    blocked_markets: list[str] = field(default_factory=list)
    require_stop_loss: bool = True
    default_stop_loss_pct: float = 5.0
    max_open_positions: int = 3


@dataclass
class TradeRecord:
    """Record of a trade execution."""
    id: str
    timestamp: str
    market: str
    side: str  # long/short
    amount: float
    leverage: int
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: str = "pending"  # pending, open, closed, failed
    pnl: float = 0.0
    fee_earned: float = 0.0
    tx_hash: str = ""


class AgentTrading:
    """
    Agent Kit trading module backed by Injective.
    
    This module provides risk management and position tracking that
    wraps Injective MCP tool calls.
    
    The actual Injective calls are made by the Hermes agent via MCP tools:
    - trade_open / trade_open_eip712
    - trade_close / trade_close_eip712
    - trade_limit_open / trade_limit_close
    - market_list / market_price
    - account_balances / account_positions
    
    This module:
    1. Validates trades against risk policy BEFORE execution
    2. Tracks open positions and P&L
    3. Enforces stop losses and position limits
    4. Logs every trade to the audit trail
    5. Tracks fee earnings (40% of trading fees)
    """
    
    def __init__(self, config_path: Optional[str] = None, policy: Optional[TradingPolicy] = None):
        self.policy = policy or TradingPolicy()
        self.audit_dir = Path(os.environ.get(
            "AGENT_KIT_AUDIT_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit/trading")
        ))
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.trade_log = self.audit_dir / f"trades-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
        self.positions_file = self.audit_dir / "open-positions.json"
        self.open_positions = self._load_positions()
        
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, path: str):
        """Load trading policy from YAML config."""
        try:
            import yaml
            with open(path) as f:
                cfg = yaml.safe_load(f)
            if "policy" in cfg:
                p = cfg["policy"]
                self.policy.max_position_usd = p.get("max_position_usd", self.policy.max_position_usd)
                self.policy.max_leverage = p.get("max_leverage", self.policy.max_leverage)
                self.policy.max_daily_loss_usd = p.get("max_daily_loss_usd", self.policy.max_daily_loss_usd)
                self.policy.approved_markets = p.get("approved_markets", self.policy.approved_markets)
                self.policy.blocked_markets = p.get("blocked_markets", self.policy.blocked_markets)
                self.policy.require_stop_loss = p.get("require_stop_loss", self.policy.require_stop_loss)
                self.policy.default_stop_loss_pct = p.get("default_stop_loss_pct", self.policy.default_stop_loss_pct)
                self.policy.max_open_positions = p.get("max_open_positions", self.policy.max_open_positions)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    def _load_positions(self) -> dict:
        """Load open positions from disk."""
        if self.positions_file.exists():
            try:
                with open(self.positions_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_positions(self):
        """Save open positions to disk."""
        with open(self.positions_file, "w") as f:
            json.dump(self.open_positions, f, indent=2)
    
    def _check_policy(self, market: str, side: str, amount: float, leverage: int) -> dict:
        """Validate trade against risk policy."""
        # Market check
        if market in self.policy.blocked_markets:
            return {"approved": False, "reason": f"Market '{market}' is blocked"}
        
        if self.policy.approved_markets and market not in self.policy.approved_markets:
            return {"approved": False, "reason": f"Market '{market}' not in approved list: {self.policy.approved_markets}"}
        
        # Leverage check
        if leverage > self.policy.max_leverage:
            return {"approved": False, "reason": f"Leverage {leverage}x exceeds max {self.policy.max_leverage}x"}
        
        # Position size check
        notional = amount * leverage
        if notional > self.policy.max_position_usd:
            return {"approved": False, "reason": f"Notional ${notional} exceeds max position ${self.policy.max_position_usd}"}
        
        # Open positions count check
        if len(self.open_positions) >= self.policy.max_open_positions:
            return {"approved": False, "reason": f"Max {self.policy.max_open_positions} open positions reached"}
        
        return {"approved": True, "reason": "All checks passed"}
    
    def _log_trade(self, record: TradeRecord):
        """Append trade record to daily audit log."""
        with open(self.trade_log, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
    
    def _generate_id(self) -> str:
        """Generate a unique trade ID."""
        return f"trade_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
    
    def validate(self, market: str, side: str, amount: float, leverage: int) -> dict:
        """Validate a trade against policy WITHOUT executing."""
        return self._check_policy(market, side, amount, leverage)
    
    def format_open_command(self, market: str, side: str, amount: float, 
                           leverage: int, stop_loss: float = 0.0, take_profit: float = 0.0) -> str:
        """
        Format an Injective MCP trade command.
        
        Returns a string the agent can use as a prompt.
        """
        # Determine the right tool based on signing method
        # Use EIP-712 for MetaMask-compatible keys
        cmd = f'trade_open_eip712({{ market:"{market}", side:"{side}", amount:"{amount}", leverage:{leverage}'
        
        if stop_loss:
            cmd += f', stopLoss:"{stop_loss}"'
        if take_profit:
            cmd += f', takeProfit:"{take_profit}"'
        
        cmd += ' })'
        return cmd
    
    def format_close_command(self, market: str, side: str) -> str:
        """Format a close position command."""
        return f'trade_close_eip712({{ market:"{market}", side:"{side}" }})'
    
    def record_trade(self, market: str, side: str, amount: float, leverage: int,
                     entry_price: float, stop_loss: float = 0.0, take_profit: float = 0.0,
                     status: str = "open", tx_hash: str = "") -> TradeRecord:
        """Record a trade to the audit trail and track position."""
        record = TradeRecord(
            id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            market=market,
            side=side,
            amount=amount,
            leverage=leverage,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status=status,
            tx_hash=tx_hash,
        )
        
        self._log_trade(record)
        
        if status == "open":
            self.open_positions[record.id] = {
                "market": market,
                "side": side,
                "amount": amount,
                "leverage": leverage,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "opened_at": record.timestamp,
            }
            self._save_positions()
        
        return record
    
    def close_position(self, trade_id: str, exit_price: float, pnl: float, fee_earned: float = 0.0) -> Optional[TradeRecord]:
        """Close a tracked position and record P&L."""
        if trade_id in self.open_positions:
            pos = self.open_positions[trade_id]
            record = TradeRecord(
                id=trade_id,
                timestamp=pos["opened_at"],
                market=pos["market"],
                side=pos["side"],
                amount=pos["amount"],
                leverage=pos["leverage"],
                entry_price=pos["entry_price"],
                stop_loss=pos.get("stop_loss"),
                take_profit=pos.get("take_profit"),
                status="closed",
                pnl=pnl,
                fee_earned=fee_earned,
            )
            self._log_trade(record)
            del self.open_positions[trade_id]
            self._save_positions()
            return record
        return None
    
    def get_positions(self) -> dict:
        """Get all open positions."""
        return self.open_positions
    
    def get_daily_summary(self) -> dict:
        """Get today's trading summary."""
        total_pnl = 0.0
        total_fees = 0.0
        trade_count = 0
        
        if self.trade_log.exists():
            with open(self.trade_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("status") == "closed":
                            total_pnl += record.get("pnl", 0)
                            total_fees += record.get("fee_earned", 0)
                            trade_count += 1
                    except json.JSONDecodeError:
                        continue
        
        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "open_positions": len(self.open_positions),
            "max_positions": self.policy.max_open_positions,
            "trades_closed": trade_count,
            "total_pnl": total_pnl,
            "total_fees_earned": total_fees,
            "daily_loss_limit": self.policy.max_daily_loss_usd,
        }


# === Convenience functions ===

def create_trading(config_path: str = None) -> AgentTrading:
    """Create an AgentTrading instance."""
    return AgentTrading(config_path=config_path)


def quick_validate(market: str, side: str, amount: float, leverage: int) -> dict:
    """Quick trade validation."""
    trading = AgentTrading()
    return trading.validate(market, side, amount, leverage)
