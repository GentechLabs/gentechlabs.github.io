"""
Compound vs. Extract Protocol — Fee Monitor Module

Tracks real-time fee accumulation for LP positions on concentrated liquidity DEXs.
Phase 1: LFJ (Trader Joe) on Avalanche.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LPPosition:
    """Represents a liquidity provider position"""
    id: str
    dex: str
    chain: str
    pair: str
    address: str
    nft_id: str
    principal: Dict[str, float]
    fees: Dict[str, float]
    status: str
    range: Dict[str, float]
    last_updated: str


@dataclass
class FeeVelocity:
    """Tracks fee accumulation rate"""
    position_id: str
    hourly_rate: float
    daily_rate: float
    trend: str  # 'accelerating', 'stable', 'decelerating'
    last_calculated: str


class FeeMonitor:
    """
    Monitors LP position fees across concentrated liquidity DEXs.
    
    Phase 1: LFJ on Avalanche
    Phase 2: Multi-DEX, multi-chain
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.positions_file = self.data_dir / "positions.json"
        self.fee_history_file = self.data_dir / "fee_history.json"
        self.velocity_file = self.data_dir / "fee_velocity.json"
        
        # Load existing data
        self.positions = self._load_positions()
        self.fee_history = self._load_fee_history()
        
        logger.info(f"FeeMonitor initialized with {len(self.positions)} positions")
    
    def _load_positions(self) -> Dict[str, LPPosition]:
        """Load positions from disk"""
        if self.positions_file.exists():
            with open(self.positions_file, 'r') as f:
                data = json.load(f)
                return {k: LPPosition(**v) for k, v in data.items()}
        return {}
    
    def _save_positions(self):
        """Persist positions to disk"""
        data = {k: asdict(v) for k, v in self.positions.items()}
        with open(self.positions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_fee_history(self) -> List[Dict]:
        """Load fee history from disk"""
        if self.fee_history_file.exists():
            with open(self.fee_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_fee_history(self):
        """Persist fee history to disk"""
        with open(self.fee_history_file, 'w') as f:
            json.dump(self.fee_history, f, indent=2)
    
    def add_position(self, position: LPPosition):
        """Add or update a position"""
        self.positions[position.id] = position
        self._save_positions()
        logger.info(f"Position {position.id} added: {position.pair} on {position.dex}")
    
    def get_position(self, position_id: str) -> Optional[LPPosition]:
        """Get position by ID"""
        return self.positions.get(position_id)
    
    def list_positions(self) -> List[LPPosition]:
        """List all positions"""
        return list(self.positions.values())
    
    def update_fees(self, position_id: str, new_fees: Dict[str, float]):
        """
        Update fees for a position.
        
        This is called by the RPC connector when fresh fee data is available.
        """
        if position_id not in self.positions:
            logger.error(f"Position {position_id} not found")
            return
        
        position = self.positions[position_id]
        
        # Calculate fee delta
        fee_delta = {}
        for token, amount in new_fees.items():
            old_amount = position.fees.get(token, 0)
            fee_delta[token] = amount - old_amount
        
        # Update position
        position.fees = new_fees
        position.last_updated = datetime.utcnow().isoformat()
        self.positions[position_id] = position
        
        # Log to history
        self.fee_history.append({
            "position_id": position_id,
            "timestamp": position.last_updated,
            "fees_before": {k: v - fee_delta.get(k, 0) for k, v in new_fees.items()},
            "fees_after": new_fees,
            "fee_delta": fee_delta,
            "action": "update"
        })
        
        self._save_positions()
        self._save_fee_history()
        
        logger.info(f"Position {position_id} fees updated: {fee_delta}")
    
    def get_accumulated_fees(self, position_id: str) -> Dict[str, float]:
        """Get current accumulated fees for a position"""
        position = self.get_position(position_id)
        if not position:
            return {}
        return position.fees
    
    def get_total_fees_usd(self, position_id: str, prices: Dict[str, float]) -> float:
        """
        Calculate total fees in USD.
        
        Args:
            position_id: Position to calculate for
            prices: Dict of token -> USD price (e.g., {"AVAX": 35.0, "USDC": 1.0})
        """
        fees = self.get_accumulated_fees(position_id)
        total = 0.0
        for token, amount in fees.items():
            price = prices.get(token, 0)
            total += amount * price
        return total
    
    def calculate_fee_velocity(self, position_id: str) -> Optional[FeeVelocity]:
        """
        Calculate fee accumulation rate.
        
        Returns velocity metrics including hourly/daily rate and trend.
        """
        # Get fee history for this position
        position_history = [
            h for h in self.fee_history 
            if h["position_id"] == position_id
        ]
        
        if len(position_history) < 2:
            return None
        
        # Sort by timestamp
        position_history.sort(key=lambda x: x["timestamp"])
        
        # Calculate time deltas and fee changes
        rates = []
        for i in range(1, len(position_history)):
            prev = position_history[i-1]
            curr = position_history[i]
            
            # Parse timestamps
            t1 = datetime.fromisoformat(prev["timestamp"])
            t2 = datetime.fromisoformat(curr["timestamp"])
            hours = (t2 - t1).total_seconds() / 3600
            
            if hours <= 0:
                continue
            
            # Calculate fee change (use first token for simplicity)
            # In production, handle multi-token pairs properly
            for token in curr["fee_delta"]:
                delta = curr["fee_delta"][token]
                if delta > 0:
                    rate = delta / hours
                    rates.append({
                        "hourly_rate": rate,
                        "token": token,
                        "timestamp": curr["timestamp"]
                    })
        
        if not rates:
            return None
        
        # Calculate average hourly rate
        avg_hourly = sum(r["hourly_rate"] for r in rates) / len(rates)
        daily_rate = avg_hourly * 24
        
        # Determine trend (compare recent rates to average)
        if len(rates) >= 3:
            recent_avg = sum(r["hourly_rate"] for r in rates[-3:]) / 3
            if recent_avg > avg_hourly * 1.2:
                trend = "accelerating"
            elif recent_avg < avg_hourly * 0.8:
                trend = "decelerating"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        velocity = FeeVelocity(
            position_id=position_id,
            hourly_rate=avg_hourly,
            daily_rate=daily_rate,
            trend=trend,
            last_calculated=datetime.utcnow().isoformat()
        )
        
        # Save velocity
        self._save_velocity(velocity)
        
        return velocity
    
    def _save_velocity(self, velocity: FeeVelocity):
        """Save velocity data"""
        data = {}
        if self.velocity_file.exists():
            with open(self.velocity_file, 'r') as f:
                data = json.load(f)
        
        data[velocity.position_id] = asdict(velocity)
        
        with open(self.velocity_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_fee_summary(self, position_id: str, prices: Dict[str, float]) -> Dict:
        """
        Get comprehensive fee summary for a position.
        
        Returns dict with:
        - fees: current accumulated fees
        - fees_usd: total in USD
        - velocity: fee accumulation rate
        - days_to_threshold: estimated days to reach extraction threshold
        """
        position = self.get_position(position_id)
        if not position:
            return {"error": "Position not found"}
        
        fees = position.fees
        fees_usd = self.get_total_fees_usd(position_id, prices)
        velocity = self.calculate_fee_velocity(position_id)
        
        summary = {
            "position_id": position_id,
            "pair": position.pair,
            "dex": position.dex,
            "status": position.status,
            "fees": fees,
            "fees_usd": fees_usd,
            "velocity": asdict(velocity) if velocity else None,
        }
        
        # Calculate days to threshold
        if velocity and velocity.daily_rate > 0:
            # Use USDC for threshold calculation
            daily_usd = velocity.daily_rate * prices.get("USDC", 1.0)
            summary["daily_fee_usd"] = daily_usd
        else:
            summary["daily_fee_usd"] = 0
        
        return summary


# Example usage
if __name__ == "__main__":
    # Initialize monitor
    monitor = FeeMonitor(data_dir="./data")
    
    # Create a sample position
    position = LPPosition(
        id="lfj_avax_usdc_001",
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
    
    monitor.add_position(position)
    
    # Simulate fee updates
    monitor.update_fees("lfj_avax_usdc_001", {"AVAX": 0.0, "USDC": 1.67})
    monitor.update_fees("lfj_avax_usdc_001", {"AVAX": 0.0, "USDC": 3.34})
    monitor.update_fees("lfj_avax_usdc_001", {"AVAX": 0.0, "USDC": 5.01})
    
    # Get summary
    prices = {"AVAX": 35.0, "USDC": 1.0}
    summary = monitor.get_fee_summary("lfj_avax_usdc_001", prices)
    
    print(json.dumps(summary, indent=2))
