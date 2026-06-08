# { "Depends": "py-genlayer:test" }

"""
DeFi Yield Optimizer — GenLayer Intelligent Contract
=====================================================
Autonomous yield optimization with gas escrow for rebalancing.

The contract reads live yield data from DeFi Llama, compares across protocols,
and recommends/records rebalance actions. Users fund a gas escrow — each
rebalance deducts from it. When gas drops below threshold, the contract flags
for top-up.

Part of GenLayer Builder Program — Intelligent Contract Templates.
Built by GenTech Labs.

Usage:
    Deploy via GenLayer CLI, then call from frontend or CLI.
    1. deposit_gas_escrow() — fund your gas balance
    2. scan_yields(protocol_filter) — fetch current yields
    3. get_recommendation(position) — LLM analyzes and recommends
    4. execute_rebalance(action) — move funds if gas available
    5. check_gas_status() — check if gas needs top-up
"""

import json
from dataclasses import dataclass
from datetime import datetime
from genlayer import *


# ─── Storage Models ───────────────────────────────────────────────────────────

@allow_storage
@dataclass
class UserVault:
    """User's yield vault with gas escrow."""
    owner: Address
    gas_balance: u256              # wei — gas escrow for rebalancing
    gas_threshold: u256            # minimum gas before alert
    gas_cost_per_rebalance: u256   # cost per rebalance action (wei)
    total_deposited: u256          # total gas ever deposited
    total_spent: u256              # total gas spent on rebalances
    rebalance_count: int           # number of rebalances executed
    is_active: bool                # vault active flag
    created_at: int                # creation timestamp


@allow_storage
@dataclass
class YieldSnapshot:
    """Point-in-time yield data for a protocol."""
    protocol: str
    pool_id: str
    chain: str
    symbol: str
    apy: float
    apy_base: float
    apy_reward: float
    tvl: float
    risk_score: int                # 0-100 (100 = safest)
    timestamp: int
    source: str                    # API source identifier


@allow_storage
@dataclass
class RebalanceRecord:
    """Record of a rebalance action."""
    user: Address
    from_protocol: str
    to_protocol: str
    from_pool: str
    to_pool: str
    amount: u256
    expected_apy_before: float
    expected_apy_after: float
    gas_cost: u256
    timestamp: int
    reason: str                    # LLM-generated reason


@allow_storage
@dataclass
class YieldRecommendation:
    """LLM-generated yield recommendation."""
    user: Address
    current_yield: float
    best_available_yield: float
    improvement_pct: float
    recommended_protocol: str
    recommended_pool: str
    recommended_chain: str
    risk_assessment: str
    rebalance_worthwhile: bool
    gas_cost_estimate: u256
    reasoning: str
    timestamp: int


# ─── Constants ────────────────────────────────────────────────────────────────

# DeFi Llama yields API
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi/pools"

# Risk categories by protocol type
PROTOCOL_RISK = {
    "aave": 85,           # blue-chip lending
    "compound": 85,       # blue-chip lending
    "curve": 80,          # established DEX
    "uniswap": 80,        # established DEX
    "convex": 75,         # yield booster
    "yearn": 70,          # yield aggregator
    "beefy": 70,          # yield optimizer
    "pendle": 65,         # yield trading
    "gmx": 60,            # perpetual DEX
    "default": 50,        # unknown protocol
}

# Minimum APY improvement to justify rebalance (percentage points)
MIN_APY_IMPROVEMENT = 0.5

# Default gas settings (in wei)
DEFAULT_GAS_THRESHOLD = 0.001 * 10**18       # 0.001 ETH
DEFAULT_GAS_COST_PER_REBALANCE = 0.0005 * 10**18  # 0.0005 ETH


# ─── Main Contract ────────────────────────────────────────────────────────────

class YieldOptimizer(gl.Contract):
    """
    DeFi Yield Optimizer with gas escrow.

    Reads live yield data, compares protocols, recommends rebalancing.
    Users fund gas escrow — each rebalance deducts from it.
    """

    # Storage
    vaults: TreeMap[Address, UserVault]
    yield_cache: TreeMap[str, YieldSnapshot]     # pool_id → snapshot
    recommendations: TreeMap[Address, YieldRecommendation]
    rebalance_history: TreeMap[Address, DynArray[int]]  # user → timestamps
    all_rebalances: TreeMap[int, RebalanceRecord]       # index → record
    total_rebalances: u256
    total_gas_deposited: u256
    total_gas_spent: u256
    last_yield_scan: int

    def __init__(self):
        self.total_rebalances = 0
        self.total_gas_deposited = 0
        self.total_gas_spent = 0
        self.last_yield_scan = 0

    # ─── Internal: Fetch Yield Data from DeFi Llama ──────────────────────

    def _fetch_yields(self, protocol_filter: str = "") -> list:
        """
        Fetch live yield data from DeFi Llama API.
        Returns list of yield pool dicts.
        """
        url = DEFILLAMA_YIELDS_URL

        def fetch_data() -> str:
            response = gl.nondet.web.get(url)
            return response.text

        raw_text = gl.eq_principle.strict_eq(fetch_data)
        data = json.loads(raw_text)

        if "data" not in data:
            raise Exception(f"DeFi Llama API error: {data.get('message', 'no data')}")

        pools = data["data"]

        # Filter by protocol if specified
        if protocol_filter:
            protocol_lower = protocol_filter.lower()
            pools = [p for p in pools if protocol_lower in p.get("project", "").lower()]

        # Filter for reasonable TVL (> $100k) and positive APY
        pools = [
            p for p in pools
            if p.get("tvlUsd", 0) > 100_000
            and p.get("apy", 0) > 0
            and p.get("apy", 0) < 1000  # filter out obviously wrong data
        ]

        # Sort by APY descending
        pools.sort(key=lambda x: x.get("apy", 0), reverse=True)

        return pools

    # ─── Internal: LLM Yield Analysis ────────────────────────────────────

    def _analyze_yields(self, pools: list, user_position: dict = None) -> dict:
        """
        Use LLM to analyze yield data and generate recommendations.
        Returns dict with analysis, recommendation, and risk assessment.
        """
        # Build summary for LLM (top 20 pools by APY)
        top_pools = pools[:20]
        pool_summary = json.dumps([{
            "project": p.get("project", "unknown"),
            "symbol": p.get("symbol", "???"),
            "chain": p.get("chain", "unknown"),
            "apy": round(p.get("apy", 0), 2),
            "apy_base": round(p.get("apyBase", 0), 2),
            "apy_reward": round(p.get("apyReward", 0) or 0, 2),
            "tvl_usd": round(p.get("tvlUsd", 0)),
            "pool_id": p.get("pool", ""),
            "stablecoin": p.get("stablecoin", False),
            "il_risk": p.get("ilRisk", "no"),
        } for p in top_pools], indent=2)

        position_text = ""
        if user_position:
            position_text = f"""
Current User Position:
- Protocol: {user_position.get('protocol', 'none')}
- Pool: {user_position.get('pool_id', 'none')}
- Chain: {user_position.get('chain', 'none')}
- Current APY: {user_position.get('apy', 0)}%
- Value: ${user_position.get('value_usd', 0)}
"""

        prompt = f"""
You are a DeFi yield optimization agent. Analyze the following yield data and provide a recommendation.

Top Yield Pools (sorted by APY):
{pool_summary}
{position_text}
Provide a JSON analysis with:
1. Compare the user's current position (if any) against available yields
2. Identify the best risk-adjusted yield opportunity
3. Determine if rebalancing is worthwhile (考虑 gas costs, impermanent loss risk, protocol risk)
4. Consider: stablecoin vs volatile pairs, TVL depth, chain bridging costs

Respond in JSON only:
{{
    "best_opportunities": [
        {{
            "protocol": "<name>",
            "pool_id": "<id>",
            "chain": "<chain>",
            "symbol": "<symbol>",
            "apy": <float>,
            "tvl_usd": <float>,
            "risk_level": "<LOW|MEDIUM|HIGH>",
            "stablecoin": <true|false>,
            "reason": "<why this is good>"
        }}
    ],
    "current_vs_best": {{
        "current_apy": <float or 0>,
        "best_apy": <float>,
        "improvement_pct": <float>,
        "rebalance_worthwhile": <true|false>
    }},
    "risk_assessment": "<brief risk summary>",
    "recommendation": "<actionable recommendation text>",
    "gas_consideration": "<note about gas costs vs benefit>"
}}

IMPORTANT: Respond ONLY with valid JSON. No other text.
"""
        def get_analysis() -> str:
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            return json.dumps(result, sort_keys=True)

        analysis = json.loads(gl.eq_principle.strict_eq(get_analysis))
        return analysis

    # ─── Internal: Calculate Risk Score ───────────────────────────────────

    def _get_protocol_risk(self, protocol: str) -> int:
        """Get deterministic risk score for a protocol."""
        protocol_lower = protocol.lower()
        for key, score in PROTOCOL_RISK.items():
            if key in protocol_lower:
                return score
        return PROTOCOL_RISK["default"]

    def _deterministic_recommendation(self, pools: list) -> dict:
        """
        Fallback deterministic yield comparison (no LLM).
        Returns recommendation based on APY and risk scoring.
        """
        if not pools:
            return {
                "best_opportunities": [],
                "current_vs_best": {"current_apy": 0, "best_apy": 0, "improvement_pct": 0, "rebalance_worthwhile": False},
                "risk_assessment": "No pools available",
                "recommendation": "No yield data available for analysis",
                "gas_consideration": "N/A"
            }

        # Score each pool: APY * risk_factor * TVL_factor
        scored = []
        for p in pools[:20]:
            apy = p.get("apy", 0)
            tvl = p.get("tvlUsd", 0)
            protocol = p.get("project", "default")
            risk = self._get_protocol_risk(protocol) / 100.0
            tvl_factor = min(1.0, tvl / 10_000_000)  # cap at $10M TVL
            stablecoin_bonus = 1.2 if p.get("stablecoin", False) else 1.0

            score = apy * risk * tvl_factor * stablecoin_bonus
            scored.append({
                "pool": p,
                "score": score,
                "risk_level": "LOW" if risk >= 0.8 else "MEDIUM" if risk >= 0.6 else "HIGH"
            })

        scored.sort(key=lambda x: x["score"], reverse=True)

        best = scored[0]["pool"] if scored else None
        opportunities = []
        for s in scored[:3]:
            p = s["pool"]
            opportunities.append({
                "protocol": p.get("project", "unknown"),
                "pool_id": p.get("pool", ""),
                "chain": p.get("chain", "unknown"),
                "symbol": p.get("symbol", "???"),
                "apy": round(p.get("apy", 0), 2),
                "tvl_usd": round(p.get("tvlUsd", 0)),
                "risk_level": s["risk_level"],
                "stablecoin": p.get("stablecoin", False),
                "reason": f"Score {round(s['score'], 2)}: APY {round(p.get('apy', 0), 2)}% with {s['risk_level'].lower()} risk"
            })

        best_apy = best.get("apy", 0) if best else 0

        return {
            "best_opportunities": opportunities,
            "current_vs_best": {
                "current_apy": 0,
                "best_apy": round(best_apy, 2),
                "improvement_pct": round(best_apy, 2),
                "rebalance_worthwhile": best_apy > MIN_APY_IMPROVEMENT
            },
            "risk_assessment": f"Top opportunity: {best.get('project', 'N/A')} at {round(best_apy, 2)}% APY" if best else "No data",
            "recommendation": f"Consider {best.get('project', 'N/A')} on {best.get('chain', 'N/A')} for {round(best_apy, 2)}% APY" if best else "No recommendations available",
            "gas_consideration": "Review gas cost vs expected yield improvement"
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC WRITE FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    @gl.public.write.payable
    def deposit_gas_escrow(self) -> dict:
        """
        Deposit gas to fund future rebalancing operations.
        Call with value (ETH) to add to your gas escrow.
        """
        sender = gl.tx.sender
        amount = gl.tx.value

        if sender not in self.vaults:
            self.vaults[sender] = UserVault(
                owner=sender,
                gas_balance=amount,
                gas_threshold=DEFAULT_GAS_THRESHOLD,
                gas_cost_per_rebalance=DEFAULT_GAS_COST_PER_REBALANCE,
                total_deposited=amount,
                total_spent=0,
                rebalance_count=0,
                is_active=True,
                created_at=int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0,
            )
        else:
            vault = self.vaults[sender]
            vault.gas_balance += amount
            vault.total_deposited += amount
            self.vaults[sender] = vault

        self.total_gas_deposited += amount

        return {
            "status": "success",
            "gas_balance": int(self.vaults[sender].gas_balance),
            "gas_deposited": int(amount),
            "gas_threshold": int(self.vaults[sender].gas_threshold),
            "message": f"Gas escrow funded. Balance: {int(self.vaults[sender].gas_balance) / 10**18:.6f} ETH"
        }

    @gl.public.write
    def set_gas_threshold(self, threshold_wei: u256) -> dict:
        """Set your gas alert threshold (in wei)."""
        sender = gl.tx.sender
        if sender not in self.vaults:
            return {"error": "No vault found. Deposit gas first."}

        vault = self.vaults[sender]
        vault.gas_threshold = threshold_wei
        self.vaults[sender] = vault

        return {
            "status": "success",
            "new_threshold": int(threshold_wei),
            "message": f"Gas threshold set to {int(threshold_wei) / 10**18:.6f} ETH"
        }

    @gl.public.write
    def set_gas_cost_per_rebalance(self, cost_wei: u256) -> dict:
        """Set the gas cost per rebalance action (in wei)."""
        sender = gl.tx.sender
        if sender not in self.vaults:
            return {"error": "No vault found. Deposit gas first."}

        vault = self.vaults[sender]
        vault.gas_cost_per_rebalance = cost_wei
        self.vaults[sender] = vault

        return {
            "status": "success",
            "new_cost": int(cost_wei),
            "message": f"Gas cost per rebalance set to {int(cost_wei) / 10**18:.6f} ETH"
        }

    @gl.public.write
    def scan_yields(self, protocol_filter: str = "") -> dict:
        """
        Fetch and cache current yield data from DeFi Llama.
        Optionally filter by protocol name (e.g., "aave", "curve").

        Returns cached yield snapshots and metadata.
        """
        pools = self._fetch_yields(protocol_filter)

        # Cache top 50 pools
        cached = 0
        for p in pools[:50]:
            pool_id = p.get("pool", "")
            if not pool_id:
                continue

            protocol = p.get("project", "unknown")
            risk_score = self._get_protocol_risk(protocol)

            snapshot = YieldSnapshot(
                protocol=protocol,
                pool_id=pool_id,
                chain=p.get("chain", "unknown"),
                symbol=p.get("symbol", "???"),
                apy=round(p.get("apy", 0), 4),
                apy_base=round(p.get("apyBase", 0) or 0, 4),
                apy_reward=round(p.get("apyReward", 0) or 0, 4),
                tvl=round(p.get("tvlUsd", 0)),
                risk_score=risk_score,
                timestamp=int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0,
                source="defillama",
            )

            self.yield_cache[pool_id] = snapshot
            cached += 1

        self.last_yield_scan = int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0

        # Return top 10 by APY
        top_10 = pools[:10]
        return {
            "status": "success",
            "pools_fetched": len(pools),
            "pools_cached": cached,
            "protocol_filter": protocol_filter or "all",
            "top_yields": [{
                "protocol": p.get("project", "unknown"),
                "symbol": p.get("symbol", "???"),
                "chain": p.get("chain", "unknown"),
                "apy": round(p.get("apy", 0), 2),
                "tvl_usd": round(p.get("tvlUsd", 0)),
                "stablecoin": p.get("stablecoin", False),
            } for p in top_10],
            "scan_timestamp": self.last_yield_scan,
        }

    @gl.public.write
    def get_recommendation(self, current_protocol: str = "", current_pool: str = "",
                           current_chain: str = "", current_apy: float = 0.0,
                           value_usd: float = 0.0) -> dict:
        """
        Get LLM-powered yield recommendation.
        Compares your current position against cached yield data.

        Args:
            current_protocol: Your current protocol (e.g., "aave")
            current_pool: Your current pool ID
            current_chain: Your current chain
            current_apy: Your current APY
            value_usd: Position value in USD
        """
        sender = gl.tx.sender

        # Fetch fresh yields for analysis
        pools = self._fetch_yields("")

        # Build user position context
        user_position = None
        if current_protocol:
            user_position = {
                "protocol": current_protocol,
                "pool_id": current_pool,
                "chain": current_chain,
                "apy": current_apy,
                "value_usd": value_usd,
            }

        # Get LLM analysis (with deterministic fallback)
        try:
            analysis = self._analyze_yields(pools, user_position)
        except Exception:
            analysis = self._deterministic_recommendation(pools)

        # Extract best opportunity
        best_opps = analysis.get("best_opportunities", [])
        best = best_opps[0] if best_opps else {}

        # Check gas status
        gas_ok = True
        gas_status = "no_vault"
        if sender in self.vaults:
            vault = self.vaults[sender]
            gas_ok = vault.gas_balance >= vault.gas_cost_per_rebalance
            gas_status = "sufficient" if gas_ok else "insufficient"

        # Store recommendation
        recommendation = YieldRecommendation(
            user=sender,
            current_yield=current_apy,
            best_available_yield=best.get("apy", 0),
            improvement_pct=analysis.get("current_vs_best", {}).get("improvement_pct", 0),
            recommended_protocol=best.get("protocol", ""),
            recommended_pool=best.get("pool_id", ""),
            recommended_chain=best.get("chain", ""),
            risk_assessment=analysis.get("risk_assessment", ""),
            rebalance_worthwhile=analysis.get("current_vs_best", {}).get("rebalance_worthwhile", False),
            gas_cost_estimate=self.vaults[sender].gas_cost_per_rebalance if sender in self.vaults else DEFAULT_GAS_COST_PER_REBALANCE,
            reasoning=analysis.get("recommendation", ""),
            timestamp=int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0,
        )

        self.recommendations[sender] = recommendation

        return {
            "status": "success",
            "current_yield": current_apy,
            "best_yield": best.get("apy", 0),
            "improvement_pct": analysis.get("current_vs_best", {}).get("improvement_pct", 0),
            "rebalance_worthwhile": analysis.get("current_vs_best", {}).get("rebalance_worthwhile", False),
            "recommendation": analysis.get("recommendation", ""),
            "risk_assessment": analysis.get("risk_assessment", ""),
            "gas_consideration": analysis.get("gas_consideration", ""),
            "gas_status": gas_status,
            "top_opportunities": best_opps[:3],
            "analysis_type": "llm" if analysis.get("best_opportunities", [{}])[0].get("reason", "") else "deterministic",
        }

    @gl.public.write
    def execute_rebalance(self, from_protocol: str, to_protocol: str,
                          from_pool: str, to_pool: str,
                          amount: u256, reason: str = "") -> dict:
        """
        Execute a rebalance action. Deducts gas from escrow.

        In production, this would call external DEX/bridge contracts.
        For the template, it records the action and deducts gas.

        Args:
            from_protocol: Source protocol name
            to_protocol: Target protocol name
            from_pool: Source pool ID
            to_pool: Target pool ID
            amount: Amount to rebalance (in smallest unit)
            reason: Optional reason for rebalance
        """
        sender = gl.tx.sender

        # Check vault exists
        if sender not in self.vaults:
            return {"error": "No gas vault found. Deposit gas first."}

        vault = self.vaults[sender]

        # Check vault is active
        if not vault.is_active:
            return {"error": "Vault is inactive."}

        # Check gas balance
        if vault.gas_balance < vault.gas_cost_per_rebalance:
            return {
                "error": "Insufficient gas for rebalance.",
                "gas_balance": int(vault.gas_balance),
                "gas_required": int(vault.gas_cost_per_rebalance),
                "message": "Please deposit more gas to continue rebalancing."
            }

        # Deduct gas
        vault.gas_balance -= vault.gas_cost_per_rebalance
        vault.total_spent += vault.gas_cost_per_rebalance
        vault.rebalance_count += 1
        self.vaults[sender] = vault

        self.total_gas_spent += vault.gas_cost_per_rebalance
        self.total_rebalances += 1

        # Record rebalance
        timestamp = int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0
        record_index = int(self.total_rebalances)

        # Get APYs from cache if available
        apy_before = 0.0
        apy_after = 0.0
        if from_pool in self.yield_cache:
            apy_before = self.yield_cache[from_pool].apy
        if to_pool in self.yield_cache:
            apy_after = self.yield_cache[to_pool].apy

        record = RebalanceRecord(
            user=sender,
            from_protocol=from_protocol,
            to_protocol=to_protocol,
            from_pool=from_pool,
            to_pool=to_pool,
            amount=amount,
            expected_apy_before=apy_before,
            expected_apy_after=apy_after,
            gas_cost=vault.gas_cost_per_rebalance,
            timestamp=timestamp,
            reason=reason,
        )

        self.all_rebalances[record_index] = record
        self.rebalance_history.get_or_insert_default(sender).append(timestamp)

        # Check gas threshold after deduction
        needs_gas = vault.gas_balance < vault.gas_threshold

        return {
            "status": "success",
            "rebalance_id": record_index,
            "from_protocol": from_protocol,
            "to_protocol": to_protocol,
            "apy_before": round(apy_before, 2),
            "apy_after": round(apy_after, 2),
            "gas_cost": int(vault.gas_cost_per_rebalance),
            "gas_remaining": int(vault.gas_balance),
            "gas_threshold": int(vault.gas_threshold),
            "needs_gas_topup": needs_gas,
            "message": f"Rebalanced from {from_protocol} to {to_protocol}. " +
                       ("Gas low! Top up soon." if needs_gas else "Gas balance healthy."),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC VIEW FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    @gl.public.view
    def get_gas_status(self) -> dict:
        """Check your gas escrow status and threshold alert."""
        sender = gl.tx.sender
        if sender not in self.vaults:
            return {
                "has_vault": False,
                "message": "No gas vault. Call deposit_gas_escrow() to start."
            }

        vault = self.vaults[sender]
        balance_eth = int(vault.gas_balance) / 10**18
        threshold_eth = int(vault.gas_threshold) / 10**18
        cost_eth = int(vault.gas_cost_per_rebalance) / 10**18
        remaining_actions = int(vault.gas_balance // vault.gas_cost_per_rebalance) if vault.gas_cost_per_rebalance > 0 else 0

        return {
            "has_vault": True,
            "gas_balance_wei": int(vault.gas_balance),
            "gas_balance_eth": round(balance_eth, 6),
            "gas_threshold_wei": int(vault.gas_threshold),
            "gas_threshold_eth": round(threshold_eth, 6),
            "gas_cost_per_rebalance_wei": int(vault.gas_cost_per_rebalance),
            "gas_cost_per_rebalance_eth": round(cost_eth, 6),
            "remaining_rebalances": remaining_actions,
            "needs_topup": vault.gas_balance < vault.gas_threshold,
            "total_deposited_eth": round(int(vault.total_deposited) / 10**18, 6),
            "total_spent_eth": round(int(vault.total_spent) / 10**18, 6),
            "rebalance_count": vault.rebalance_count,
            "status": "⚠️ LOW GAS — TOP UP SOON" if vault.gas_balance < vault.gas_threshold else "✅ Gas balance healthy",
        }

    @gl.public.view
    def get_yield_comparison(self) -> dict:
        """Get cached yield comparison across all tracked protocols."""
        if not self.yield_cache:
            return {
                "cached_pools": 0,
                "message": "No yield data cached. Call scan_yields() first.",
            }

        # Group by protocol
        protocols = {}
        for pool_id, snapshot in self.yield_cache.items():
            proto = snapshot.protocol
            if proto not in protocols:
                protocols[proto] = []
            protocols[proto].append({
                "pool_id": snapshot.pool_id,
                "symbol": snapshot.symbol,
                "chain": snapshot.chain,
                "apy": snapshot.apy,
                "tvl": snapshot.tvl,
                "risk_score": snapshot.risk_score,
            })

        # Sort protocols by best APY
        protocol_summary = []
        for proto, pools in protocols.items():
            best_apy = max(p["apy"] for p in pools)
            avg_apy = sum(p["apy"] for p in pools) / len(pools)
            total_tvl = sum(p["tvl"] for p in pools)
            protocol_summary.append({
                "protocol": proto,
                "pool_count": len(pools),
                "best_apy": round(best_apy, 2),
                "avg_apy": round(avg_apy, 2),
                "total_tvl": round(total_tvl),
                "risk_score": pools[0]["risk_score"],
                "top_pools": sorted(pools, key=lambda x: x["apy"], reverse=True)[:3],
            })

        protocol_summary.sort(key=lambda x: x["best_apy"], reverse=True)

        return {
            "cached_pools": len(self.yield_cache),
            "protocol_count": len(protocols),
            "last_scan": self.last_yield_scan,
            "protocols": protocol_summary,
        }

    @gl.public.view
    def get_user_history(self, user_address: str = "") -> dict:
        """Get rebalance history for a user."""
        user = Address(user_address) if user_address else gl.tx.sender

        if user not in self.rebalance_history:
            return {"rebalance_count": 0, "history": []}

        timestamps = self.rebalance_history[user]
        history = []
        for i in range(len(timestamps)):
            # Find matching record
            for idx in range(1, int(self.total_rebalances) + 1):
                if idx in self.all_rebalances:
                    record = self.all_rebalances[idx]
                    if record.user == user and record.timestamp == timestamps[i]:
                        history.append({
                            "from_protocol": record.from_protocol,
                            "to_protocol": record.to_protocol,
                            "amount": int(record.amount),
                            "apy_before": round(record.expected_apy_before, 2),
                            "apy_after": round(record.expected_apy_after, 2),
                            "gas_cost": int(record.gas_cost),
                            "reason": record.reason,
                            "timestamp": record.timestamp,
                        })
                        break

        return {
            "rebalance_count": len(timestamps),
            "total_gas_spent": sum(h["gas_cost"] for h in history),
            "history": history,
        }

    @gl.public.view
    def get_recommendation_history(self) -> dict:
        """Get your latest yield recommendation."""
        sender = gl.tx.sender
        if sender not in self.recommendations:
            return {"has_recommendation": False}

        r = self.recommendations[sender]
        return {
            "has_recommendation": True,
            "current_yield": r.current_yield,
            "best_yield": r.best_available_yield,
            "improvement_pct": r.improvement_pct,
            "recommended_protocol": r.recommended_protocol,
            "recommended_chain": r.recommended_chain,
            "risk_assessment": r.risk_assessment,
            "rebalance_worthwhile": r.rebalance_worthwhile,
            "gas_cost_estimate": int(r.gas_cost_estimate),
            "reasoning": r.reasoning,
            "timestamp": r.timestamp,
        }

    @gl.public.view
    def get_total_stats(self) -> dict:
        """Get global contract statistics."""
        return {
            "total_rebalances": int(self.total_rebalances),
            "total_gas_deposited_eth": round(int(self.total_gas_deposited) / 10**18, 6),
            "total_gas_spent_eth": round(int(self.total_gas_spent) / 10**18, 6),
            "active_vaults": len(self.vaults),
            "cached_pools": len(self.yield_cache),
            "last_yield_scan": self.last_yield_scan,
        }
