"""
Compound vs. Extract Protocol — Decision Engine Module

AI-powered decision making for optimal compound vs. extract timing.
Phase 1: Rule-based decisions
Phase 2: Machine learning optimization
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Action(Enum):
    """Available actions"""
    COMPOUND = "compound"
    EXTRACT = "extract"
    WAIT = "wait"


class MarketCondition(Enum):
    """Market condition states"""
    STABLE = "stable"
    VOLATILE = "volatile"
    CRASHING = "crashing"
    PUMPING = "pumping"


@dataclass
class MarketData:
    """Market condition data"""
    timestamp: str
    gas_price: float  # gwei
    volatility: float  # 0-1 scale
    price_change_24h: float  # percentage
    condition: MarketCondition


@dataclass
class UserPreferences:
    """User configuration"""
    extract_threshold: float  # USD amount to trigger extraction
    compound_split: float  # 0-1, percentage to compound (rest extracted)
    gas_threshold: float  # gwei, max gas price for operations
    default_action: str  # 'compound', 'extract', or 'auto'
    auto_enabled: bool
    max_slippage: float  # 0-1, max acceptable slippage


@dataclass
class Decision:
    """Decision output"""
    action: Action
    confidence: float  # 0-1
    reasoning: str
    amount: Optional[float] = None  # For extract: amount to extract
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class DecisionEngine:
    """
    AI-powered decision engine for compound vs. extract operations.
    
    Uses rule-based decisions in Phase 1, with ML optimization in Phase 2.
    """
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.prefs_file = self.config_dir / "user_preferences.json"
        
        # Load user preferences
        self.user_prefs = self._load_preferences()
        
        logger.info("DecisionEngine initialized")
    
    def _load_preferences(self) -> UserPreferences:
        """Load user preferences from disk"""
        if self.prefs_file.exists():
            with open(self.prefs_file, 'r') as f:
                data = json.load(f)
                return UserPreferences(**data)
        
        # Default preferences
        return UserPreferences(
            extract_threshold=10.0,
            compound_split=0.7,
            gas_threshold=25.0,
            default_action="auto",
            auto_enabled=True,
            max_slippage=0.005
        )
    
    def save_preferences(self):
        """Persist user preferences"""
        with open(self.prefs_file, 'w') as f:
            json.dump(asdict(self.user_prefs), f, indent=2)
    
    def update_preferences(self, **kwargs):
        """Update user preferences"""
        for key, value in kwargs.items():
            if hasattr(self.user_prefs, key):
                setattr(self.user_prefs, key, value)
        self.save_preferences()
        logger.info(f"Preferences updated: {kwargs}")
    
    def analyze_market(self, prices: Dict[str, float], 
                      price_history: List[Dict]) -> MarketData:
        """
        Analyze current market conditions.
        
        Args:
            prices: Current token prices
            price_history: Recent price data for volatility calculation
        """
        # Calculate volatility from price history
        if len(price_history) >= 2:
            returns = []
            for i in range(1, len(price_history)):
                prev_price = price_history[i-1].get("price", 0)
                curr_price = price_history[i].get("price", 0)
                if prev_price > 0:
                    returns.append((curr_price - prev_price) / prev_price)
            
            # Standard deviation of returns
            if returns:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                volatility = variance ** 0.5
            else:
                volatility = 0
        else:
            volatility = 0
        
        # 24h price change
        if len(price_history) >= 2:
            oldest = price_history[0].get("price", 0)
            newest = price_history[-1].get("price", 0)
            if oldest > 0:
                price_change_24h = (newest - oldest) / oldest * 100
            else:
                price_change_24h = 0
        else:
            price_change_24h = 0
        
        # Determine market condition
        if volatility < 0.02:
            condition = MarketCondition.STABLE
        elif volatility > 0.1:
            condition = MarketCondition.CRASHING if price_change_24h < -5 else MarketCondition.PUMPING
        else:
            condition = MarketCondition.VOLATILE
        
        return MarketData(
            timestamp=datetime.utcnow().isoformat(),
            gas_price=prices.get("gas_price", 25.0),
            volatility=volatility,
            price_change_24h=price_change_24h,
            condition=condition
        )
    
    def decide(self, 
               position_fees: Dict[str, float],
               fees_usd: float,
               market_data: MarketData,
               position_status: str = "in_range") -> Decision:
        """
        Make compound vs. extract decision.
        
        Args:
            position_fees: Current accumulated fees
            fees_usd: Total fees in USD
            market_data: Current market conditions
            position_status: 'in_range' or 'out_of_range'
        
        Returns:
            Decision with action, confidence, and reasoning
        """
        prefs = self.user_prefs
        
        # Rule 1: Position out of range — extract everything
        if position_status == "out_of_range":
            return Decision(
                action=Action.EXTRACT,
                confidence=1.0,
                reasoning="Position out of range, extracting to prevent impermanent loss",
                amount=fees_usd
            )
        
        # Rule 2: User threshold reached — extract
        if fees_usd >= prefs.extract_threshold:
            if prefs.default_action == "auto":
                # In auto mode, extract the threshold amount
                return Decision(
                    action=Action.EXTRACT,
                    confidence=1.0,
                    reasoning=f"Fees hit extraction threshold (${prefs.extract_threshold:.2f})",
                    amount=prefs.extract_threshold
                )
            elif prefs.default_action == "extract":
                return Decision(
                    action=Action.EXTRACT,
                    confidence=1.0,
                    reasoning=f"Fees hit threshold, user prefers extraction",
                    amount=fees_usd
                )
        
        # Rule 3: Gas too high — wait
        if market_data.gas_price > prefs.gas_threshold:
            return Decision(
                action=Action.WAIT,
                confidence=0.9,
                reasoning=f"Gas price ({market_data.gas_price:.1f} gwei) exceeds threshold ({prefs.gas_threshold:.1f} gwei)"
            )
        
        # Rule 4: Auto mode — apply decision matrix
        if prefs.default_action == "auto":
            return self._auto_decision(fees_usd, market_data, prefs)
        
        # Rule 5: User preference — follow it
        if prefs.default_action == "compound":
            return Decision(
                action=Action.COMPOUND,
                confidence=0.8,
                reasoning="Following user preference to compound"
            )
        else:
            return Decision(
                action=Action.EXTRACT,
                confidence=0.8,
                reasoning="Following user preference to extract"
            )
    
    def _auto_decision(self, fees_usd: float, 
                      market_data: MarketData, 
                      prefs: UserPreferences) -> Decision:
        """
        Auto mode decision matrix.
        
        Considers:
        - Market volatility
        - Fee velocity
        - Gas price
        - User balance (TODO)
        """
        # Score each action
        compound_score = 0
        extract_score = 0
        
        # Market volatility
        if market_data.condition == MarketCondition.STABLE:
            compound_score += 2  # Stable = compound to grow
        elif market_data.condition == MarketCondition.VOLATILE:
            extract_score += 1  # Volatile = secure some profits
        elif market_data.condition == MarketCondition.CRASHING:
            extract_score += 3  # Crashing = get out
        elif market_data.condition == MarketCondition.PUMPING:
            compound_score += 3  # Pumping = ride the wave
        
        # Price momentum
        if market_data.price_change_24h > 5:
            compound_score += 2  # Uptrend = compound
        elif market_data.price_change_24h < -5:
            extract_score += 2  # Downtrend = extract
        
        # Gas efficiency
        if market_data.gas_price < prefs.gas_threshold * 0.5:
            compound_score += 1  # Very low gas = good time to act
            extract_score += 1
        
        # Make decision
        if compound_score > extract_score + 1:
            return Decision(
                action=Action.COMPOUND,
                confidence=min(0.9, 0.5 + (compound_score - extract_score) * 0.1),
                reasoning=f"Market conditions favor compounding (score: {compound_score} vs {extract_score})"
            )
        elif extract_score > compound_score + 1:
            return Decision(
                action=Action.EXTRACT,
                confidence=min(0.9, 0.5 + (extract_score - compound_score) * 0.1),
                reasoning=f"Market conditions favor extraction (score: {extract_score} vs {compound_score})"
            )
        else:
            # Scores are close — wait for clearer signal
            return Decision(
                action=Action.WAIT,
                confidence=0.6,
                reasoning=f"Market conditions unclear (score: {compound_score} vs {extract_score}), waiting for clearer signal"
            )
    
    def calculate_optimal_amount(self, 
                                fees_usd: float,
                                action: Action,
                                market_data: MarketData) -> float:
        """
        Calculate optimal amount for compound/extract.
        
        For compound: amount to reinvest
        For extract: amount to withdraw
        """
        if action == Action.COMPOUND:
            # Compound all available fees
            return fees_usd
        elif action == Action.EXTRACT:
            # Extract based on user split preference
            if self.user_prefs.compound_split < 1.0:
                # Extract (1 - compound_split) of fees
                extract_ratio = 1.0 - self.user_prefs.compound_split
                return fees_usd * extract_ratio
            else:
                # User wants 100% compound, but we're extracting
                # Extract minimum viable amount
                return min(fees_usd, self.user_prefs.extract_threshold)
        else:
            return 0
    
    def get_decision_summary(self, 
                            position_id: str,
                            fees_usd: float,
                            market_data: MarketData,
                            position_status: str) -> Dict:
        """
        Get comprehensive decision summary.
        
        Returns dict with decision, reasoning, and recommended actions.
        """
        fees = {"USD": fees_usd}  # Simplified
        decision = self.decide(fees, fees_usd, market_data, position_status)
        
        optimal_amount = self.calculate_optimal_amount(
            fees_usd, decision.action, market_data
        )
        
        return {
            "position_id": position_id,
            "decision": {
                "action": decision.action.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "amount": optimal_amount,
                "timestamp": decision.timestamp
            },
            "market": {
                "condition": market_data.condition.value,
                "gas_price": market_data.gas_price,
                "volatility": market_data.volatility,
                "price_change_24h": market_data.price_change_24h
            },
            "preferences": {
                "extract_threshold": self.user_prefs.extract_threshold,
                "compound_split": self.user_prefs.compound_split,
                "auto_enabled": self.user_prefs.auto_enabled
            },
            "recommendation": self._generate_recommendation(decision, market_data)
        }
    
    def _generate_recommendation(self, decision: Decision, 
                                market_data: MarketData) -> str:
        """Generate human-readable recommendation"""
        if decision.action == Action.COMPOUND:
            amount = decision.amount or 0
            return (
                f"Recommend compounding ${amount:.2f} back into your position. "
                f"Market is {market_data.condition.value} with {market_data.volatility:.1%} volatility. "
                f"Compounding now will grow your position and increase future fee generation."
            )
        elif decision.action == Action.EXTRACT:
            amount = decision.amount or 0
            return (
                f"Recommend extracting ${amount:.2f} from your position. "
                f"{'Market is volatile — securing profits now.' if market_data.condition == MarketCondition.VOLATILE else 'Fees have accumulated to a meaningful amount.'} "
                f"Position will continue earning after extraction."
            )
        else:
            return (
                f"Recommend waiting for better conditions. "
                f"Current gas: {market_data.gas_price:.1f} gwei, volatility: {market_data.volatility:.1%}. "
                f"Will alert when conditions improve."
            )


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = DecisionEngine(config_dir="./config")
    
    # Simulate market data
    market_data = MarketData(
        timestamp=datetime.utcnow().isoformat(),
        gas_price=15.0,
        volatility=0.015,
        price_change_24h=2.5,
        condition=MarketCondition.STABLE
    )
    
    # Make decision
    decision = engine.decide(
        position_fees={"USDC": 8.50},
        fees_usd=8.50,
        market_data=market_data,
        position_status="in_range"
    )
    
    print(f"Decision: {decision.action.value}")
    print(f"Confidence: {decision.confidence:.0%}")
    print(f"Reasoning: {decision.reasoning}")
    
    # Get full summary
    summary = engine.get_decision_summary(
        position_id="lfj_avax_usdc_001",
        fees_usd=8.50,
        market_data=market_data,
        position_status="in_range"
    )
    
    print("\nFull Summary:")
    print(json.dumps(summary, indent=2))
