"""
Dry Powder Mode — Phase 2: Auto-Retreat to Swap
================================================
Active defense for LP positions. Detects breakouts, executes tactical retreat
to stablecoins, monitors for re-entry signals, and re-deploys.

Phase 1 (breakout timer + FOMC defense) is already shipped.
Phase 2 adds: auto-withdraw from LFJ pools, swap to stables, sentinel monitoring,
recovery signal detection, and auto-redeploy.

Simulation mode by default. Real execution requires wallet + LFJ integration.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional


# ── Types ──────────────────────────────────────────────────────────────

class DefenseState(Enum):
    NORMAL = "normal"                # In range, earning fees
    HOLD = "hold"                    # Breakout detected, waiting 2-5 min
    RETREATING = "retreating"        # Executing withdrawal + swap
    SENTINEL = "sentinel"            # 100% USDC, monitoring for re-entry
    RE_ENTERING = "re-entering"      # Re-deploying position
    ERROR = "error"                  # Something went wrong


class SignalType(Enum):
    FEAR_AND_GREED = "fear_and_greed"
    VOLUME_STABILIZATION = "volume_stabilization"
    PRICE_CONSOLIDATION = "price_consolidation"
    MACRO_CALENDAR = "macro_calendar"


class ShapeType(Enum):
    CURVE = "curve"                  # Tight range for choppy markets
    BID_ASK = "bid-ask"              # Wider range for macro events


# ── Data Models ───────────────────────────────────────────────────────

@dataclass
class PositionState:
    """Current state of the LP position."""
    total_usd: float = 0.0
    token0_amount: float = 0.0       # e.g. AVAX
    token1_amount: float = 0.0       # e.g. USDC
    range_low: float = 0.0
    range_high: float = 0.0
    current_price: float = 0.0
    shape: str = "curve"
    in_range: bool = True
    daily_fees_usd: float = 0.0
    efficiency_pct: float = 100.0


@dataclass
class DefenseConfig:
    """Configuration for the tactical defense system."""
    enabled: bool = True
    retreat_timer_seconds: int = 300       # 5 min hold before retreat
    sentinel_interval_minutes: int = 30    # Check every 30 min in sentinel
    re_entry_threshold: float = 0.75       # 3/4 signals needed
    max_retreat_slippage_pct: float = 0.5  # Max slippage during swap
    min_position_usd: float = 10.0         # Don't retreat tiny positions
    signals: dict[str, dict] = field(default_factory=lambda: {
        "fear_and_greed": {"min_value": 35, "weight": 0.25},
        "volume_stabilization": {"window_hours": 1, "weight": 0.25},
        "price_consolidation": {"min_hours": 2, "weight": 0.25},
        "macro_calendar_clear": {"min_hours_until_next": 48, "weight": 0.25},
    })
    shapes: dict = field(default_factory=lambda: {
        "default": "curve",
        "pre_macro_event": "bid-ask",
        "macro_event_hours_before": 24,
        "macro_event_hours_after": 24,
    })


@dataclass
class SignalResult:
    """Result of checking a single re-entry signal."""
    signal: SignalType
    positive: bool
    value: float
    threshold: float
    weight: float
    detail: str = ""


@dataclass
class ReEntryAssessment:
    """Assessment of whether conditions are right for re-entry."""
    signals: list[SignalResult] = field(default_factory=list)
    positive_count: int = 0
    total_weight: float = 0.0
    threshold: float = 0.75
    ready: bool = False

    @property
    def score(self) -> float:
        if not self.signals:
            return 0.0
        return sum(s.weight for s in self.signals if s.positive)


@dataclass
class RetreatLog:
    """Log entry for a retreat event."""
    timestamp: str
    exit_price: float
    total_usd_before: float
    usdc_after: float
    il_realized_usd: float
    reason: str
    duration_seconds: int = 0


# ── Defense Engine ─────────────────────────────────────────────────────

class DryPowderDefense:
    """
    Active defense engine for LP positions.
    
    State machine: NORMAL → HOLD → RETREATING → SENTINEL → RE_ENTERING → NORMAL
    
    Simulation mode by default. Real execution requires wallet + DEX integration.
    """

    def __init__(self, config: Optional[DefenseConfig] = None,
                 simulation: bool = True):
        self.config = config or DefenseConfig()
        self.simulation = simulation
        self.state = DefenseState.NORMAL
        self._hold_start: Optional[datetime] = None
        self._sentinel_start: Optional[datetime] = None
        self._last_check: Optional[datetime] = None
        self._retreat_logs: list[RetreatLog] = []
        self._position_history: list[PositionState] = []

    # ── Core Loop ──────────────────────────────────────────────────

    def tick(self, position: PositionState, current_price: float,
             market_signals: Optional[dict] = None) -> DefenseState:
        """
        One tick of the defense loop. Call every 10 minutes in NORMAL mode,
        every 30 minutes in SENTINEL mode.
        
        Returns the new state.
        """
        self._last_check = datetime.now(timezone.utc)
        position.current_price = current_price
        position.in_range = position.range_low <= current_price <= position.range_high

        if self.state == DefenseState.NORMAL:
            return self._tick_normal(position)

        elif self.state == DefenseState.HOLD:
            return self._tick_hold(position)

        elif self.state == DefenseState.SENTINEL:
            return self._tick_sentinel(position, market_signals or {})

        return self.state

    def _tick_normal(self, position: PositionState) -> DefenseState:
        """Check if price has exited the range."""
        if not position.in_range:
            self.state = DefenseState.HOLD
            self._hold_start = datetime.now(timezone.utc)
            return self.state

        return DefenseState.NORMAL

    def _tick_hold(self, position: PositionState) -> DefenseState:
        """Wait for hold timer, then decide: recover or retreat."""
        if not self._hold_start:
            self.state = DefenseState.NORMAL
            return self.state

        elapsed = (datetime.now(timezone.utc) - self._hold_start).total_seconds()

        # Price re-entered range → back to normal
        if position.in_range:
            self.state = DefenseState.NORMAL
            self._hold_start = None
            return self.state

        # Timer expired → retreat
        if elapsed >= self.config.retreat_timer_seconds:
            return self._execute_retreat(position)

        # Still waiting
        return DefenseState.HOLD

    def _execute_retreat(self, position: PositionState) -> DefenseState:
        """Execute the tactical retreat: withdraw LP → swap to USDC."""
        if self.simulation:
            # Simulate retreat
            il = self._estimate_impermanent_loss(position)
            usdc_value = position.total_usd - il

            log = RetreatLog(
                timestamp=datetime.now(timezone.utc).isoformat(),
                exit_price=position.current_price,
                total_usd_before=round(position.total_usd, 2),
                usdc_after=round(usdc_value, 2),
                il_realized_usd=round(il, 4),
                reason="price_exited_range",
            )
            self._retreat_logs.append(log)

        self.state = DefenseState.SENTINEL
        self._sentinel_start = datetime.now(timezone.utc)
        return self.state

    def _tick_sentinel(self, position: PositionState,
                       market_signals: dict) -> DefenseState:
        """Monitor for re-entry signals."""
        assessment = self.assess_re_entry(market_signals)

        if assessment.ready:
            return self._execute_re_entry(position)

        return DefenseState.SENTINEL

    def _execute_re_entry(self, position: PositionState) -> DefenseState:
        """Re-deploy the position."""
        if self.simulation:
            pass  # Would execute swap + LP deposit

        self.state = DefenseState.NORMAL
        self._hold_start = None
        self._sentinel_start = None
        return self.state

    # ── Signal Assessment ──────────────────────────────────────────

    def assess_re_entry(self, signals: dict) -> ReEntryAssessment:
        """Check all re-entry signals and determine if ready."""
        assessment = ReEntryAssessment(
            threshold=self.config.re_entry_threshold,
        )

        # Fear & Greed
        fg = signals.get("fear_and_greed", 50)
        fg_threshold = self.config.signals["fear_and_greed"]["min_value"]
        fg_weight = self.config.signals["fear_and_greed"]["weight"]
        assessment.signals.append(SignalResult(
            signal=SignalType.FEAR_AND_GREED,
            positive=fg >= fg_threshold,
            value=fg,
            threshold=fg_threshold,
            weight=fg_weight,
            detail=f"Fear & Greed: {fg} (need ≥ {fg_threshold})",
        ))

        # Volume stabilization
        vol_ratio = signals.get("volume_ratio_24h", 1.0)
        vol_weight = self.config.signals["volume_stabilization"]["weight"]
        assessment.signals.append(SignalResult(
            signal=SignalType.VOLUME_STABILIZATION,
            positive=vol_ratio >= 0.5,  # Volume at least 50% of 24h avg
            value=vol_ratio,
            threshold=0.5,
            weight=vol_weight,
            detail=f"Volume ratio: {vol_ratio:.2f}x (need ≥ 0.5x)",
        ))

        # Price consolidation
        price_range_pct = signals.get("price_range_pct_2h", 5.0)
        pc_weight = self.config.signals["price_consolidation"]["weight"]
        assessment.signals.append(SignalResult(
            signal=SignalType.PRICE_CONSOLIDATION,
            positive=price_range_pct <= 2.0,  # Price range < 2% in 2h
            value=price_range_pct,
            threshold=2.0,
            weight=pc_weight,
            detail=f"Price range (2h): {price_range_pct:.1f}% (need ≤ 2.0%)",
        ))

        # Macro calendar
        hours_to_next = signals.get("hours_to_next_event", 72)
        mc_weight = self.config.signals["macro_calendar_clear"]["weight"]
        min_hours = self.config.signals["macro_calendar_clear"]["min_hours_until_next"]
        assessment.signals.append(SignalResult(
            signal=SignalType.MACRO_CALENDAR,
            positive=hours_to_next >= min_hours,
            value=hours_to_next,
            threshold=min_hours,
            weight=mc_weight,
            detail=f"Hours to next event: {hours_to_next:.0f}h (need ≥ {min_hours}h)",
        ))

        assessment.positive_count = sum(1 for s in assessment.signals if s.positive)
        assessment.ready = assessment.score >= assessment.threshold

        return assessment

    # ── Helpers ───────────────────────────────────────────────────

    def _estimate_impermanent_loss(self, position: PositionState) -> float:
        """Estimate IL based on price movement from entry."""
        # Simplified IL estimation for a range position
        # In a real implementation, this would use the actual pool math
        if position.current_price <= 0 or position.range_low <= 0:
            return 0.0

        # If price is below range, IL is roughly the % below range low
        if position.current_price < position.range_low:
            pct_below = (position.range_low - position.current_price) / position.range_low
            return position.total_usd * min(pct_below * 0.5, 0.1)  # Cap at 10%

        # If price is above range, IL is roughly the % above range high
        if position.current_price > position.range_high:
            pct_above = (position.current_price - position.range_high) / position.range_high
            return position.total_usd * min(pct_above * 0.5, 0.1)

        return 0.0

    def get_retreat_logs(self, limit: int = 10) -> list[RetreatLog]:
        """Get recent retreat logs."""
        return self._retreat_logs[-limit:]

    def get_status(self) -> dict:
        """Get a human-readable status summary."""
        return {
            "state": self.state.value,
            "in_hold": self.state == DefenseState.HOLD,
            "in_sentinel": self.state == DefenseState.SENTINEL,
            "retreats_executed": len(self._retreat_logs),
            "last_retreat": self._retreat_logs[-1] if self._retreat_logs else None,
        }

    def reset(self):
        """Reset to NORMAL state."""
        self.state = DefenseState.NORMAL
        self._hold_start = None
        self._sentinel_start = None


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Dry Powder Mode — Phase 2")
    sub = parser.add_subparsers(dest="command")

    # simulate
    sim = sub.add_parser("simulate", help="Run a defense simulation")
    sim.add_argument("--price", type=float, default=6.56)
    sim.add_argument("--range-low", type=float, default=6.40)
    sim.add_argument("--range-high", type=float, default=6.55)
    sim.add_argument("--position-usd", type=float, default=45.24)
    sim.add_argument("--ticks", type=int, default=5)
    sim.add_argument("--price-drop", type=float, default=0.0,
                     help="Simulate price drop per tick")

    # status
    status = sub.add_parser("status", help="Show current defense status")

    # assess
    assess = sub.add_parser("assess", help="Assess re-entry signals")
    assess.add_argument("--fear-greed", type=float, default=50)
    assess.add_argument("--volume-ratio", type=float, default=1.0)
    assess.add_argument("--price-range", type=float, default=1.5)
    assess.add_argument("--hours-to-event", type=float, default=72)

    args = parser.parse_args()

    if args.command == "simulate":
        defense = DryPowderDefense(simulation=True)
        position = PositionState(
            total_usd=args.position_usd,
            range_low=args.range_low,
            range_high=args.range_high,
            shape="curve",
        )

        print(f"Starting defense simulation...")
        print(f"  Position: ${position.total_usd:.2f}")
        print(f"  Range: ${position.range_low:.2f}–${position.range_high:.2f}")
        print(f"  Initial price: ${args.price:.2f}")
        print()

        price = args.price
        for i in range(args.ticks):
            price -= args.price_drop
            state = defense.tick(position, price)
            print(f"Tick {i+1}: price=${price:.2f} → state={state.value}")
            if state == DefenseState.RETREATING:
                log = defense._retreat_logs[-1]
                print(f"  ⚠️  RETREAT: ${log.total_usd_before:.2f} → ${log.usdc_after:.2f} USDC")
                print(f"     IL realized: ${log.il_realized_usd:.4f}")
            elif state == DefenseState.SENTINEL:
                print(f"  🛡️  Sentinel mode — monitoring for re-entry")

        print()
        print(f"Final state: {defense.state.value}")
        print(f"Retreats: {len(defense._retreat_logs)}")

    elif args.command == "status":
        defense = DryPowderDefense(simulation=True)
        status = defense.get_status()
        print(f"State: {status['state']}")
        print(f"In hold: {status['in_hold']}")
        print(f"In sentinel: {status['in_sentinel']}")
        print(f"Retreats executed: {status['retreats_executed']}")

    elif args.command == "assess":
        defense = DryPowderDefense(simulation=True)
        signals = {
            "fear_and_greed": args.fear_greed,
            "volume_ratio_24h": args.volume_ratio,
            "price_range_pct_2h": args.price_range,
            "hours_to_next_event": args.hours_to_event,
        }
        assessment = defense.assess_re_entry(signals)
        print("Re-entry Assessment:")
        for s in assessment.signals:
            icon = "✅" if s.positive else "❌"
            print(f"  {icon} {s.detail}")
        print(f"\nScore: {assessment.score:.2f}/{assessment.threshold:.2f}")
        print(f"Ready: {'✅ YES' if assessment.ready else '❌ NO'}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
