#!/usr/bin/env python3
"""
AAE Signal Monitor v2 — LFJ LP Position + Milestone Tracker
Outputs structured AAE signals for squad treasury + progression ingestion.

Features:
  - Multi-pool support via JSON config
  - Structured AAE signal output (JSON + human readable)
  - Updated milestone tiers matching Jordan's dashboard
  - Fee efficiency with Curve/Spot/Bidirectional shape awareness
  - Birdeye x402 → DexScreener → on-chain RPC fallback
  - Smart alerting: SILENT | OK | ALERT | CRITICAL
  - Squad context support (squad_id, contribution %)

Pool: LFJ V2.2 AVAX/USDC, binStep 10
Address: 0x864d4e5ee7318e97483db7eb0912e09f161516ea
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

# ── Config ─────────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    "chain": "avalanche",
    "rpc_url": "https://api.avax.network/ext/bc/C/rpc",
    "token0": {"symbol": "AVAX", "address": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", "decimals": 18},
    "token1": {"symbol": "USDC", "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", "decimals": 6},
    "bin_step": 10,
    "fee_tier_bps": 5,
    "position": {
        "total_usd": 134.94,
        "token0_amount": 3.446,
        "token1_amount": 103.38,
        "range_low": 9.00,
        "range_high": 9.45,
        "shape": "curve"
    },
    "milestones": [
        {"tier": 1, "label": "Scout", "daily_fees": 3.0, "description": "Entry rank — basic strategies unlocked"},
        {"tier": 2, "label": "Scout+", "daily_fees": 5.0, "description": "Consistent earner — SPOT shape unlocked"},
        {"tier": 3, "label": "Raider", "daily_fees": 8.0, "description": "Intermediate — BIDIRECTIONAL shape unlocked"},
        {"tier": 4, "label": "Raider+", "daily_fees": 10.0, "description": "Building momentum — multi-pool view unlocked"},
        {"tier": 5, "label": "Warlord", "daily_fees": 15.0, "description": "Advanced — custom range presets unlocked"},
        {"tier": 6, "label": "Warlord+", "daily_fees": 20.0, "description": "Veteran — squad treasury analytics unlocked"},
        {"tier": 7, "label": "Sovereign", "daily_fees": 55.0, "description": "Elite — strategy sharing + leaderboard unlocked"},
        {"tier": 8, "label": "Freedom", "daily_fees": 200.0, "description": "Freedom milestone — custom strategy creation + mentorship"}
    ],
    "compound_threshold_usd": 50.0,
    "dca": {"amount": 50, "day_of_week": 0, "enabled": True},
    "micro_dca": {"enabled": True, "threshold_10": 50, "threshold_20": 40},
    "quiet_hours": {"start": 23, "end": 6, "timezone_offset": -4},
    "squad": {"squad_id": None, "contribution_pct": 100.0},
    "alert_rules": {
        "silent_if": ["in_range", "efficiency_ok", "no_action_needed"],
        "alert_if": ["out_of_range", "efficiency_low", "milestone_hit", "compound_ready", "dca_day"],
        "critical_if": ["price_crash", "il_severe"]
    }
}

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.expanduser("~/.hermes/scripts")
STATE_FILE = os.path.join(STATE_DIR, ".lfj-aae-state.json")

# --- Alert thresholds ---
EFFICIENCY_WARNING_THRESHOLD = 30.0  # Below 30% → efficiency warning
EFFICIENCY_RED_THRESHOLD = 25.0      # Below 25% → red alert (severe)
OUT_OF_RANGE_WARNING_MINUTES = 10    # After 10min out of range → warning
OUT_OF_RANGE_RED_MINUTES = 15        # After 15min total → red alert (10 + 5 confirm)
CONFIG_FILE = os.path.join(STATE_DIR, ".lfj-aae-config.json")

# Import Birdeye client if available
BIRDEYE_AVAILABLE = False
try:
    sys.path.insert(0, SCRIPT_DIR)
    from birdeye_x402_client import BirdeyeClient, BirdeyeConfig
    BIRDEYE_AVAILABLE = True
except ImportError:
    pass

# ── Data Classes ────────────────────────────────────────────────────────────────────────

@dataclass
class AAESignal:
    """Structured signal for AAE squad treasury + progression ingestion."""
    timestamp: str
    signal_type: str  # POSITION | MILESTONE | ALERT | COMPOUND | DCA
    severity: str     # SILENT | OK | ALERT | CRITICAL
    
    # Position data
    pool_address: str
    chain: str
    token0_symbol: str
    token1_symbol: str
    price: float
    price_change_24h: Optional[float]
    
    # Range data
    range_low: float
    range_high: float
    in_range: bool
    fee_efficiency: float
    shape: str
    
    # Squad treasury
    position_value_usd: float
    token0_split_pct: float
    token1_split_pct: float
    fees_24h: float
    fees_since_deposit: float
    claimable_rewards_usd: float
    apr: float
    
    # Progression
    current_tier: int
    current_tier_label: str
    next_tier: int
    next_tier_label: str
    progress_to_next_pct: float
    days_in_range: float
    
    # Action signals
    compound_ready: bool
    dca_ready: bool
    micro_dca_ready: bool
    micro_dca_amount: int
    suggested_action: str
    
    # Metadata
    data_source: str
    squad_id: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

# ── Config Management ────────────────────────────────────────────────────────────────────────

def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            # Merge with defaults for any missing keys
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except Exception:
        # Write default config if not exists
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(cfg: Dict[str, Any]):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

# ── State Management ────────────────────────────────────────────────────────────────────────

def load_state() -> Dict[str, Any]:
    default = {
        "tracking_started": None,
        "total_fees_earned_usd": 0.0,
        "total_days_in_range": 0.0,
        "last_in_range_check": None,
        "current_milestone_idx": -1,  # -1 = unranked
        "last_compound_date": None,
        "last_dca_date": None,
        "compound_events": [],
        "daily_fee_log": [],
        "price_history": [],  # Last 100 price points for volatility
        "alert_history": [],
        "out_of_range_since": None,
        "tvl_history": [],  # Last 168 checks (7 days @ 1h) for TVL trend
        "pool_dominant_pair": None,
        "last_check": None,
        "last_position_usd": None,
    }
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            for k, v in default.items():
                state.setdefault(k, v)
            return state
    except Exception:
        return default

def save_state(state: Dict[str, Any]):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ── Data Fetchers ────────────────────────────────────────────────────────────────────────

def fetch_onchain(cfg: Dict) -> Optional[Dict[str, Any]]:
    pool_address = cfg["pool_address"]
    rpc_url = cfg["rpc_url"]
    token0_decimals = cfg["token0"]["decimals"]
    token1_decimals = cfg["token1"]["decimals"]
    
    def _rpc_call(data: str) -> str:
        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1,
            "method": "eth_call",
            "params": [{"to": pool_address, "data": data}, "latest"]
        }).encode()
        req = urllib.request.Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())["result"]

    try:
        # getSwapOut(1 token0, swapForY=true)
        swap_data = (
            "0xe77366f8"
            "0000000000000000000000000000000000000000000000000de0b6b3a7640000"
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
        swap_result = _rpc_call(swap_data)
        amount_out = int(swap_result[2 + 64 : 2 + 128], 16)
        price = amount_out / (10 ** token1_decimals)

        # getReserves() → (reserveX, reserveY)
        reserves_result = _rpc_call("0x0902f1ac")
        reserve_x = int(reserves_result[2 : 2 + 64], 16)
        reserve_y = int(reserves_result[2 + 64 : 2 + 128], 16)
        reserve0 = reserve_x / (10 ** token0_decimals)
        reserve1 = reserve_y / (10 ** token1_decimals)
        liquidity_usd = reserve0 * price + reserve1

        return {
            "source": "onchain",
            "price": price,
            "volume_24h": 0.0,
            "liquidity_usd": liquidity_usd,
            "price_change_24h": 0.0,
            "reserves_token0": reserve0,
            "reserves_token1": reserve1,
        }
    except Exception:
        return None

def fetch_dexscreener(cfg: Dict) -> Dict[str, Any]:
    pool_address = cfg["pool_address"]
    chain = cfg["chain"]
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
    return {
        "source": "dexscreener",
        "price": float(pair.get("priceNative", 0)),
        "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
    }

def fetch_birdeye(cfg: Dict) -> Optional[Dict[str, Any]]:
    if not BIRDEYE_AVAILABLE:
        return None
    try:
        config = BirdeyeConfig.load()
        if not config.is_configured:
            return None
        config.chain = cfg["chain"]
        token0_address = cfg["token0"]["address"]
        with BirdeyeClient(config) as client:
            overview = client.token_overview(token0_address, cfg["chain"])
            if "error" in overview:
                return None
            security = client.token_security(token0_address, cfg["chain"])
            trades = client.token_trade_data(token0_address, cfg["chain"])
            return {
                "source": "birdeye",
                "price": float(overview.get("price", 0)),
                "liquidity_usd": float(overview.get("liquidity", 0)),
                "volume_24h": float(overview.get("volume24h", overview.get("v24h", 0))),
                "price_change_24h": float(overview.get("priceChange24h", overview.get("priceChange", 0))),
                "market_cap": float(overview.get("mc", overview.get("marketCap", 0))),
                "security_score": security.get("securityScore", security.get("score", None)) if "error" not in security else None,
                "buy_sell_ratio": _calc_buy_sell_ratio(trades) if "error" not in trades else None,
            }
    except Exception:
        return None

def _calc_buy_sell_ratio(trades: dict) -> Optional[float]:
    if "error" in trades:
        return None
    buys = trades.get("buys24h", trades.get("buy", 0))
    sells = trades.get("sells24h", trades.get("sell", 0))
    if sells and sells > 0:
        return round(buys / sells, 2)
    return None

# ── Analysis Engine ────────────────────────────────────────────────────────────────────────

def calc_fee_efficiency(price: float, range_low: float, range_high: float, shape: str = "curve") -> float:
    """Calculate fee efficiency based on position within range and shape."""
    if price < range_low or price > range_high:
        return 0.0
    
    position = (price - range_low) / (range_high - range_low)
    
    if shape == "spot":
        # Spot: uniform distribution, efficiency is binary (in range = 100%)
        return 100.0
    elif shape == "bidirectional":
        # Bidirectional: higher efficiency at edges
        edge_dist = abs(position - 0.5) * 2
        return round(max(0, min(100, edge_dist * 100)), 1)
    else:  # curve (default)
        # Curve: highest efficiency at center, tapering to edges
        return round(max(0, min(100, (1 - abs(position - 0.5) * 2) * 100)), 1)

def estimate_daily_fees(pool: Dict, position_usd: float, fee_tier_bps: int = 5) -> float:
    """Estimate daily fees from pool volume and position share."""
    fee_rate = fee_tier_bps / 10000
    volume_24h = pool.get("volume_24h", 0)
    liquidity = pool.get("liquidity_usd", 1)
    if liquidity <= 0 or volume_24h <= 0:
        return 0.0
    return round((volume_24h * fee_rate) * (position_usd / liquidity), 4)

def calc_apr_from_volume(pool: Dict, fee_tier_bps: int = 5) -> float:
    """Calculate APR from 24h volume and liquidity."""
    fee_rate = fee_tier_bps / 10000
    volume_24h = pool.get("volume_24h", 0)
    liquidity = pool.get("liquidity_usd", 1)
    if liquidity <= 0:
        return 0.0
    return round(((volume_24h * fee_rate) / liquidity) * 100 * 365, 1)

def is_quiet_hours(cfg: Dict) -> bool:
    """Check if current time is within quiet hours."""
    tz_offset = cfg.get("quiet_hours", {}).get("timezone_offset", -4)
    start = cfg.get("quiet_hours", {}).get("start", 23)
    end = cfg.get("quiet_hours", {}).get("end", 6)
    eastern = timezone(timedelta(hours=tz_offset))
    now = datetime.now(eastern)
    return now.hour >= start or now.hour < end

def get_current_tier(est_fees: float, milestones: List[Dict]) -> int:
    """Determine current milestone tier from estimated daily fees.

    Returns -1 if below the first milestone threshold (Unranked).
    """
    if est_fees < milestones[0]["daily_fees"]:
        return -1
    current_idx = 0
    for i, ms in enumerate(milestones):
        if est_fees >= ms["daily_fees"]:
            current_idx = i
        else:
            break
    return current_idx

def calc_progress_to_next(est_fees: float, current_idx: int, milestones: List[Dict]) -> float:
    """Calculate percentage progress to next milestone."""
    if current_idx == -1:
        # Progress from 0 to first milestone
        first_target = milestones[0]["daily_fees"]
        if first_target <= 0:
            return 0.0
        return round(max(0, min(100, (est_fees / first_target) * 100)), 1)
    if current_idx >= len(milestones) - 1:
        return 100.0
    current_target = milestones[current_idx]["daily_fees"]
    next_target = milestones[current_idx + 1]["daily_fees"]
    if next_target <= current_target:
        return 100.0
    progress = ((est_fees - current_target) / (next_target - current_target)) * 100
    return round(max(0, min(100, progress)), 1)

def determine_severity(in_range: bool, efficiency: float, compound_ready: bool, dca_ready: bool,
                       milestone_changed: bool, pool_tvl_drop_pct: float, micro_dca_ready: bool, cfg: Dict,
                       out_of_range_confirmed: bool = True, oor_duration_minutes: float = 0.0,
                       just_recovered: bool = False) -> str:
    """Determine alert severity using time-based out-of-range escalation.
    
    Severity: SILENT (first check / monitoring), LOW (warning), HIGH (action required), CELEBRATE (milestone)
    """
    # Milestone celebration
    if milestone_changed:
        return "CELEBRATE"
    
    # Recovery alert — price returned to range after being out
    if just_recovered:
        return "OK"
    
    # TVL collapse — always high
    if pool_tvl_drop_pct > 30:
        return "HIGH"
    
    # Out-of-range escalation based on duration
    if not in_range:
        if oor_duration_minutes >= OUT_OF_RANGE_RED_MINUTES:
            return "HIGH"    # 15+ min out → RED alert
        elif oor_duration_minutes >= OUT_OF_RANGE_WARNING_MINUTES:
            return "LOW"     # 10–15 min → WARNING
        else:
            return "SILENT"  # <10min, still in confirmation window
    
    # Efficiency tiered alerts
    if efficiency < EFFICIENCY_RED_THRESHOLD:
        return "HIGH"    # <25% → critically low
    if efficiency < EFFICIENCY_WARNING_THRESHOLD:
        return "LOW"     # 25–30% → warning
    
    # Action triggers that merit attention even if range/efficiency ok
    if compound_ready or dca_ready or micro_dca_ready:
        return "LOW"
    
    return "SILENT"
def get_suggested_action(in_range: bool, efficiency: float, compound_ready: bool, dca_ready: bool,
                        milestone_changed: bool, current_tier: int, pool_tvl_drop_pct: float,
                        micro_dca_ready: bool, micro_dca_amount: int, cfg: Dict,
                        oor_duration_minutes: float = 0.0, just_recovered: bool = False) -> str:
    """Generate human-readable suggested action with duration-based out-of-range guidance."""
    if milestone_changed:
        tier_label = cfg["milestones"][current_tier]["label"]
        return f"MILESTONE: {tier_label} unlocked! New strategies available."
    if just_recovered:
        return "🟢 Recovered — back in range"
    if not in_range:
        dur = oor_duration_minutes
        if dur >= OUT_OF_RANGE_RED_MINUTES:
            return "🚨 RED ALERT — Rebalance IMMEDIATE"
        elif dur >= OUT_OF_RANGE_WARNING_MINUTES:
            return f"⚠️ WARNING — {dur:.0f}min out of range. Rebalance soon."
        else:
            return f"👀 Monitoring — {dur:.0f}min elapsed. Confirming..."
    if pool_tvl_drop_pct > 30:
        return "🚨 POOL TVL COLLAPSING: Consider exit or reduce exposure."
    if efficiency < EFFICIENCY_RED_THRESHOLD:
        return f"🚨 CRITICAL EFFICIENCY {efficiency:.1f}% — rebalance immediately."
    if efficiency < EFFICIENCY_WARNING_THRESHOLD:
        return f"⚠️ Efficiency low ({efficiency:.1f}%) — consider rebalancing."
    if compound_ready:
        return f"💰 Compound ready — {state['total_fees_earned_usd']:.2f} USD"
    if dca_ready or micro_dca_ready:
        amount = micro_dca_amount if micro_dca_ready else cfg["dca"]["amount"]
        return f"📈 DCA day — auto-buy ${amount} USDC"
    return "✅ Position healthy — maintain current range."
def calc_tvl_trend(tvl_history: List[float]) -> float:
    """Calculate 7-day TVL trend percentage. Returns 0.0 if insufficient data."""
    if len(tvl_history) < 2 or tvl_history[0] <= 0:
        return 0.0
    oldest = tvl_history[0]
    newest = tvl_history[-1]
    return round(((newest - oldest) / oldest) * 100, 2)

def calc_pool_tvl_drop(tvl_history: List[float]) -> float:
    """Calculate max TVL drop from peak in recent history."""
    if not tvl_history:
        return 0.0
    peak = max(tvl_history)
    if peak <= 0:
        return 0.0
    current = tvl_history[-1]
    return round(((peak - current) / peak) * 100, 2)

def build_aae_signal(cfg: Dict, state: Dict, pool: Dict, price: float, in_range: bool,
                     efficiency: float, est_fees: float, apr: float, pool_tvl_drop_pct: float,
                     out_of_range_confirmed: bool = True, oor_duration_minutes: float = 0.0,
                     just_recovered: bool = False) -> AAESignal:
    """Build structured AAE signal from all computed data."""

    eastern = timezone(timedelta(hours=cfg.get("quiet_hours", {}).get("timezone_offset", -4)))
    now = datetime.now(eastern)
    now_str = now.isoformat()

    position = cfg["position"]
    milestones = cfg["milestones"]

    # Calculate splits
    total_position = position["total_usd"]
    token0_value = position["token0_amount"] * price
    token1_value = position["token1_amount"]
    token0_split = round((token0_value / total_position) * 100, 1) if total_position > 0 else 0
    token1_split = round((token1_value / total_position) * 100, 1) if total_position > 0 else 0

    # Progression
    current_idx = get_current_tier(est_fees, milestones)
    next_idx = min(max(current_idx + 1, 0), len(milestones) - 1)
    progress_pct = calc_progress_to_next(est_fees, current_idx, milestones)

    # Handle unranked state
    if current_idx == -1:
        current_tier_label = "Unranked"
        current_tier_num = 0
    else:
        current_tier_label = milestones[current_idx]["label"]
        current_tier_num = current_idx + 1

    # Action triggers
    compound_ready = state["total_fees_earned_usd"] >= cfg["compound_threshold_usd"]
    dca_ready = cfg["dca"]["enabled"] and now.weekday() == cfg["dca"]["day_of_week"]
    milestone_changed = current_idx > state.get("current_milestone_idx", 0)
    
    # Micro-DCA: efficiency-triggered bonus DCA ($10 at threshold_10, $20 at threshold_20)
    micro_dca_cfg = cfg.get("micro_dca", {})
    micro_dca_enabled = micro_dca_cfg.get("enabled", True)
    threshold_10 = micro_dca_cfg.get("threshold_10", 50)
    threshold_20 = micro_dca_cfg.get("threshold_20", 40)
    micro_dca_ready = False
    micro_dca_amount = 0
    if micro_dca_enabled and in_range:
        if efficiency < threshold_10 and efficiency >= threshold_20:
            micro_dca_ready = True
            micro_dca_amount = 10
        elif efficiency < threshold_20:
            micro_dca_ready = True
            micro_dca_amount = 20

    # Severity (AAE Signal Spec: SILENT / LOW / HIGH / CELEBRATE)
    severity = determine_severity(in_range, efficiency, compound_ready, dca_ready, milestone_changed, pool_tvl_drop_pct, micro_dca_ready, cfg,
                                  out_of_range_confirmed=out_of_range_confirmed,
                                  oor_duration_minutes=oor_duration_minutes,
                                  just_recovered=just_recovered)

    # Suggested action
    suggested = get_suggested_action(in_range, efficiency, compound_ready, dca_ready, milestone_changed, current_idx, pool_tvl_drop_pct, micro_dca_ready, micro_dca_amount, cfg,
                               oor_duration_minutes=oor_duration_minutes,
                               just_recovered=just_recovered)

    # Claimable rewards estimate (fees since last compound)
    claimable = round(state["total_fees_earned_usd"], 2)

    signal = AAESignal(
        timestamp=now_str,
        signal_type="POSITION",
        severity=severity,
        pool_address=cfg["pool_address"],
        chain=cfg["chain"],
        token0_symbol=cfg["token0"]["symbol"],
        token1_symbol=cfg["token1"]["symbol"],
        price=round(price, 4),
        price_change_24h=round(pool.get("price_change_24h", 0), 2) if pool.get("price_change_24h") is not None else None,
        range_low=position["range_low"],
        range_high=position["range_high"],
        in_range=in_range,
        fee_efficiency=efficiency,
        shape=position["shape"],
        position_value_usd=round(total_position, 2),
        token0_split_pct=token0_split,
        token1_split_pct=token1_split,
        fees_24h=round(est_fees, 2),
        fees_since_deposit=round(state["total_fees_earned_usd"], 2),
        claimable_rewards_usd=claimable,
        apr=round(apr, 1),
        current_tier=current_tier_num,
        current_tier_label=current_tier_label,
        next_tier=next_idx + 1,
        next_tier_label=milestones[next_idx]["label"],
        progress_to_next_pct=progress_pct,
        days_in_range=round(state["total_days_in_range"], 1),
        compound_ready=compound_ready,
        dca_ready=dca_ready,
        micro_dca_ready=micro_dca_ready,
        micro_dca_amount=micro_dca_amount,
        suggested_action=suggested,
        data_source=pool.get("source", "unknown"),
        squad_id=cfg.get("squad", {}).get("squad_id")
    )

    return signal

# ── Report Formatters ────────────────────────────────────────────────────────────────────────

def format_liquidity_shape(price: float, range_low: float, range_high: float, shape: str, width: int = 20) -> str:
    """Generate ASCII liquidity shape visualization showing price position within range."""
    if range_high <= range_low:
        return ""
    
    # Normalize price position (0.0 = bottom, 1.0 = top)
    pos = (price - range_low) / (range_high - range_low)
    pos = max(0.0, min(1.0, pos))
    
    # Generate shape profile (liquidity density at each point)
    profile = []
    for i in range(width):
        x = i / (width - 1)  # 0.0 to 1.0
        if shape == "spot":
            # Uniform distribution
            density = 1.0
        elif shape == "bidirectional":
            # Higher at edges, lower at center
            density = 0.3 + 0.7 * abs(x - 0.5) * 2
        else:  # curve (default)
            # Bell curve — highest at center
            density = 0.3 + 0.7 * (1 - abs(x - 0.5) * 2)
        profile.append(density)
    
    # Normalize profile to max 4 bars height
    max_d = max(profile) if profile else 1
    bars = [max(1, round((d / max_d) * 4)) for d in profile]
    
    # Find price column
    price_col = int(pos * (width - 1))
    price_col = max(0, min(width - 1, price_col))
    
    # Build visualization (bottom-up, 4 rows)
    rows = []
    for level in range(4, 0, -1):
        row = ""
        for i, bar in enumerate(bars):
            if i == price_col:
                row += "◆"  # Price marker
            elif bar >= level:
                row += "█"  # Liquidity present
            else:
                row += "·"  # No liquidity
        rows.append(row)
    
    # Bottom axis with range labels
    axis = f"${range_low:.2f}" + " " * (width - len(f"${range_low:.2f}") - len(f"${range_high:.2f}")) + f"${range_high:.2f}"
    
    # Shape label and description
    shape_labels = {
        "spot": "SPOT — uniform liquidity across range",
        "bidirectional": "BID-ASK — concentrated at edges, fee-optimized for swings",
        "curve": "CURVE — concentrated at center, fee-optimized for ranging",
    }
    shape_desc = shape_labels.get(shape, f"{shape.upper()} shape")
    
    viz = "\n".join(rows) + "\n" + axis + f"\n◆ = price (${price:.4f})\n{shape_desc}"
    return viz

def format_human_report(signal: AAESignal, cfg: Dict) -> str:
    """Format human-readable Telegram report from AAE signal."""
    
    now_str = datetime.fromisoformat(signal.timestamp).strftime("%I:%M %p EDT")
    
    status_emoji = {
        "SILENT": "😐",
        "LOW": "⚠️",
        "HIGH": "🚨",
        "CELEBRATE": "🎉"
    }.get(signal.severity, "▪️")
    
    range_emoji = "🟩" if signal.in_range else "🟥"
    
    # Liquidity shape visualization
    liq_shape = format_liquidity_shape(
        signal.price, signal.range_low, signal.range_high, signal.shape
    )
    
    lines = [
        f"**{signal.token0_symbol}/{signal.token1_symbol} Squad Treasury** — {now_str}",
        f"",
        f"{status_emoji} **{signal.severity}** | Data: {signal.data_source.upper()}",
        f"",
        f"**Position:**",
        f"• Value: ${signal.position_value_usd} ({signal.token0_symbol} {signal.token0_split_pct}% / {signal.token1_symbol} {signal.token1_split_pct}%)",
        f"• Price: ${signal.price} ({signal.price_change_24h:+.1f}% 24h)" if signal.price_change_24h is not None else f"• Price: ${signal.price}",
        f"• Range: ${signal.range_low:.2f} – ${signal.range_high:.2f} {range_emoji}",
        f"• Efficiency: {signal.fee_efficiency}% ({signal.shape.upper()})",
        f"• APR: {signal.apr}%",
        f"",
        f"**Liquidity Shape:**",
        f"```{liq_shape}```",
        f"",
        f"**Revenue:**",
        f"• 24H Fees: ${signal.fees_24h}",
        f"• Cumulative: ${signal.fees_since_deposit}",
        f"• Claimable: ${signal.claimable_rewards_usd}",
        f"• Days in Range: {signal.days_in_range}",
        f"",
        f"**Progression:**",
        f"• Rank: {signal.current_tier_label} (Tier {signal.current_tier})",
        f"• Next: {signal.next_tier_label} ({signal.progress_to_next_pct}%)",
        f"",
        f"**Action:** {signal.suggested_action}",
    ]
    
    if signal.micro_dca_ready:
        lines.append(f"")
        lines.append(f"📈 **Micro-DCA Trigger:** Efficiency dropped to {signal.fee_efficiency}%")
        lines.append(f"• Deploy ${signal.micro_dca_amount} bonus DCA")
        lines.append(f"• Consider rebalancing range for better positioning")
    
    if signal.squad_id:
        lines.insert(1, f"Squad: `{signal.squad_id}`")
    
    return "\n".join(lines)

# ── Main ─────────────────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    
    # Check quiet hours
    if is_quiet_hours(cfg):
        print(json.dumps({"status": "QUIET_HOURS", "timestamp": datetime.now(timezone.utc).isoformat()}))
        sys.exit(0)
    
    state = load_state()
    position = cfg["position"]
    # Capital injection detection
    current_position_usd = position["total_usd"]
    last_position_usd = state.get("last_position_usd")
    capital_injection_usd = 0.0
    if last_position_usd is not None and current_position_usd > last_position_usd:
        capital_injection_usd = round(current_position_usd - last_position_usd, 2)
    state["last_position_usd"] = current_position_usd

    
    # Fetch data with fallback chain
    birdeye = fetch_birdeye(cfg)
    
    try:
        pool = fetch_dexscreener(cfg)
    except Exception:
        onchain = fetch_onchain(cfg)
        if onchain:
            pool = onchain
        elif birdeye:
            pool = {
                "source": "birdeye",
                "price": birdeye["price"],
                "volume_24h": birdeye["volume_24h"],
                "liquidity_usd": birdeye["liquidity_usd"],
                "price_change_24h": birdeye["price_change_24h"]
            }
        else:
            print(json.dumps({"status": "ERROR", "message": "All data sources failed"}))
            sys.exit(1)
    
    # Use Birdeye price if available (more accurate), else pool price
    price = birdeye["price"] if birdeye else pool["price"]
    
    # Core calculations
    in_range = position["range_low"] <= price <= position["range_high"]
    efficiency = calc_fee_efficiency(price, position["range_low"], position["range_high"], position["shape"])
    apr = calc_apr_from_volume(pool, cfg.get("fee_tier_bps", 5))
    est_fees = estimate_daily_fees(pool, position["total_usd"], cfg.get("fee_tier_bps", 5))

    # Pool health: TVL trend tracking
    liquidity = pool.get("liquidity_usd", 0)
    state["tvl_history"] = (state.get("tvl_history", []) + [liquidity])[-168:]  # 7 days @ hourly
    pool_tvl_drop_pct = calc_pool_tvl_drop(state["tvl_history"])
    tvl_trend_7d = calc_tvl_trend(state["tvl_history"])
    
    # 2-check confirmation for out-of-range (ported from lp-range-monitor.py)
    # Duration-based out-of-range escalation (10min monitor → 5min wait → red)
    was_out = state.get("out_of_range_since") is not None
    out_of_range_duration_minutes = 0.0
    out_of_range_confirmed = False
    if not in_range:
        if state.get("out_of_range_since") is None:
            # First time out of range — note timestamp
            state["out_of_range_since"] = now.isoformat()
            out_of_range_confirmed = False
            out_of_range_duration_minutes = 0.0
        else:
            # Already out of range previously — compute elapsed duration
            try:
                since_dt = datetime.fromisoformat(state["out_of_range_since"])
                delta = now - since_dt
                out_of_range_duration_minutes = delta.total_seconds() / 60.0
                # Cap at red threshold for display purposes
                out_of_range_duration_minutes = min(out_of_range_duration_minutes, OUT_OF_RANGE_RED_MINUTES + 10)
            except Exception:
                out_of_range_duration_minutes = 0.0
            out_of_range_confirmed = out_of_range_duration_minutes >= OUT_OF_RANGE_WARNING_MINUTES
    else:
        # Back in range — clear state
        state["out_of_range_since"] = None
        out_of_range_confirmed = False
        out_of_range_duration_minutes = 0.0
    just_recovered = in_range and was_out
    # Update state
    eastern = timezone(timedelta(hours=cfg.get("quiet_hours", {}).get("timezone_offset", -4)))
    now = datetime.now(eastern)
    
    if state["tracking_started"] is None:
        state["tracking_started"] = now.isoformat()
    
    if in_range:
        state["total_days_in_range"] = round(state["total_days_in_range"] + (1.0/144.0), 4)
        state["total_fees_earned_usd"] = round(state["total_fees_earned_usd"] + (est_fees * (1.0/144.0)), 4)
    
    # Update price history
    state["price_history"] = (state.get("price_history", []) + [price])[-100:]
    
    # Milestone tracking (allow -1 for unranked)
    current_idx = get_current_tier(est_fees, cfg["milestones"])
    milestone_changed = current_idx > state.get("current_milestone_idx", -1)
    state["current_milestone_idx"] = current_idx
    
    # Build AAE signal (with 2-check confirmation)
    signal = build_aae_signal(cfg, state, pool, price, in_range, efficiency, est_fees, apr, pool_tvl_drop_pct,
                              out_of_range_confirmed=out_of_range_confirmed,
                              oor_duration_minutes=out_of_range_duration_minutes,
                              just_recovered=just_recovered)

    # Update alert history (only non-silent alerts)
    if signal.severity != "SILENT":
        state["alert_history"] = (state.get("alert_history", []) + [{
            "timestamp": now.isoformat(),
            "severity": signal.severity,
            "action": signal.suggested_action,
            "tvl_trend_7d": tvl_trend_7d,
            "pool_tvl_drop_pct": pool_tvl_drop_pct
        }])[-50:]
    
    state["last_check"] = now.isoformat()
    state["last_price"] = price
    save_state(state)
    
    # Output structured JSON for AAE ingestion
    human_report = format_human_report(signal, cfg)
    if capital_injection_usd > 0:
        human_report = f"💸 Capital added: ${capital_injection_usd:.2f} — progress recalculated.\n\n" + human_report
    output = {
        "status": signal.severity,
        "signal": signal.to_dict(),
        "human_report": human_report,
        "config_hash": hash(json.dumps(cfg, sort_keys=True)) & 0xFFFFFFFF,
    }
    if capital_injection_usd > 0:
        output["capital_injection_usd"] = capital_injection_usd

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
