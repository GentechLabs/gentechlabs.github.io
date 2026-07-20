"""
Stablecoin Transfer Portal — Core Engine
=========================================
Universal on-ramp: any stablecoin (USDT, DAI, PYUSD, algorithmic) from any chain
→ USDC on ARC. Agent swaps with slippage protection, lands funds in Agentic Treasury.

Architecture:
  Source Chain (any) → Bridge → ARC Chain → Jupiter Swap → USDC → Agentic Treasury

All operations run in simulation mode by default. Real execution requires
Jordan's wallet + API keys.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ── Types ──────────────────────────────────────────────────────────────

class Chain(Enum):
    ETHEREUM = "ethereum"
    BASE = "base"
    SOLANA = "solana"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    BSC = "bsc"
    ARC = "arc"  # Target chain


class Stablecoin(Enum):
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    PYUSD = "PYUSD"
    FRAX = "FRAX"
    LUSD = "LUSD"
    USDG = "USDG"


class BridgeProtocol(Enum):
    CCTP = "cctp"          # Circle CCTP (USDC native)
    WORMHOLE = "wormhole"  # Wormhole bridge
    ACROSS = "across"      # Across Protocol
    STARGATE = "stargate"  # Stargate / LayerZero
    HYPHEN = "hyphen"      # Biconomy Hyphen
    NATIVE = "native"      # Same-chain swap (no bridge needed)


class SwapProtocol(Enum):
    JUPITER = "jupiter"    # Jupiter on Solana/ARC
    UNISWAP = "uniswap"    # Uniswap on EVM chains
    CURVE = "curve"        # Curve stablecoin pools
    ONE_INCH = "one-inch"  # 1inch aggregator
    ORCA = "orca"          # Orca on Solana


class RouteStatus(Enum):
    PENDING = "pending"
    SIMULATED = "simulated"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SLIPPAGE_EXCEEDED = "slippage_exceeded"


# ── Data Models ───────────────────────────────────────────────────────

@dataclass
class SwapRoute:
    """A single hop in the swap chain."""
    protocol: SwapProtocol
    from_token: Stablecoin
    to_token: Stablecoin
    from_amount: float
    expected_to_amount: float
    min_to_amount: float  # After slippage
    price_impact_pct: float = 0.0
    fee_pct: float = 0.0
    pool: str = ""


@dataclass
class BridgeRoute:
    """A bridge hop between chains."""
    protocol: BridgeProtocol
    from_chain: Chain
    to_chain: Chain
    token: Stablecoin
    amount: float
    estimated_time_minutes: int = 0
    fee_usd: float = 0.0


@dataclass
class TransferPlan:
    """Complete plan for a stablecoin transfer."""
    source_chain: Chain
    source_token: Stablecoin
    source_amount: float
    target_chain: Chain = Chain.ARC
    target_token: Stablecoin = Stablecoin.USDC
    slippage_tolerance_pct: float = 0.5
    bridges: list[BridgeRoute] = field(default_factory=list)
    swaps: list[SwapRoute] = field(default_factory=list)
    estimated_total_fee_usd: float = 0.0
    estimated_time_minutes: int = 0
    expected_output: float = 0.0
    min_output: float = 0.0
    status: RouteStatus = RouteStatus.PENDING
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def is_same_chain(self) -> bool:
        return self.source_chain == self.target_chain

    @property
    def is_same_token(self) -> bool:
        return self.source_token == self.target_token

    @property
    def needs_bridge(self) -> bool:
        return not self.is_same_chain

    @property
    def needs_swap(self) -> bool:
        return not self.is_same_token


# ── Slippage Protection ───────────────────────────────────────────────

@dataclass
class SlippageConfig:
    """Slippage tolerance configuration."""
    default_pct: float = 0.5       # 0.5% default
    max_pct: float = 3.0            # Hard cap
    min_pct: float = 0.1            # Minimum (tight)
    aggressive_pct: float = 1.0     # For volatile pairs
    conservative_pct: float = 0.3  # For stable-stable pairs

    def validate(self, pct: float) -> float:
        """Clamp slippage to allowed range."""
        return max(self.min_pct, min(pct, self.max_pct))


def apply_slippage(amount: float, slippage_pct: float) -> float:
    """Calculate minimum output after slippage."""
    return amount * (1 - slippage_pct / 100)


# ── Route Planner ─────────────────────────────────────────────────────

class RoutePlanner:
    """
    Plans the optimal route for a stablecoin transfer.
    Simulation mode by default — returns estimated routes without real execution.
    """

    # Supported bridge paths
    BRIDGE_PATHS: dict[tuple[Chain, Chain], list[BridgeProtocol]] = {
        (Chain.ETHEREUM, Chain.ARC): [BridgeProtocol.CCTP, BridgeProtocol.WORMHOLE],
        (Chain.BASE, Chain.ARC): [BridgeProtocol.CCTP],
        (Chain.SOLANA, Chain.ARC): [BridgeProtocol.WORMHOLE, BridgeProtocol.CCTP],
        (Chain.ARBITRUM, Chain.ARC): [BridgeProtocol.CCTP, BridgeProtocol.ACROSS],
        (Chain.OPTIMISM, Chain.ARC): [BridgeProtocol.CCTP],
        (Chain.POLYGON, Chain.ARC): [BridgeProtocol.CCTP, BridgeProtocol.HYPHEN],
        (Chain.AVALANCHE, Chain.ARC): [BridgeProtocol.CCTP],
        (Chain.BSC, Chain.ARC): [BridgeProtocol.STARGATE, BridgeProtocol.WORMHOLE],
    }

    # Swap protocols by chain
    SWAP_PROTOCOLS: dict[Chain, list[SwapProtocol]] = {
        Chain.ARC: [SwapProtocol.JUPITER],
        Chain.SOLANA: [SwapProtocol.JUPITER, SwapProtocol.ORCA],
        Chain.ETHEREUM: [SwapProtocol.UNISWAP, SwapProtocol.CURVE, SwapProtocol.ONE_INCH],
        Chain.BASE: [SwapProtocol.UNISWAP, SwapProtocol.CURVE],
        Chain.AVALANCHE: [SwapProtocol.CURVE, SwapProtocol.UNISWAP],
    }

    # Estimated bridge times (minutes)
    BRIDGE_TIMES: dict[BridgeProtocol, int] = {
        BridgeProtocol.CCTP: 15,
        BridgeProtocol.WORMHOLE: 10,
        BridgeProtocol.ACROSS: 5,
        BridgeProtocol.STARGATE: 20,
        BridgeProtocol.HYPHEN: 3,
        BridgeProtocol.NATIVE: 0,
    }

    # Bridge fees (USD, estimated)
    BRIDGE_FEES: dict[BridgeProtocol, float] = {
        BridgeProtocol.CCTP: 0.50,
        BridgeProtocol.WORMHOLE: 0.30,
        BridgeProtocol.ACROSS: 0.40,
        BridgeProtocol.STARGATE: 0.60,
        BridgeProtocol.HYPHEN: 0.25,
        BridgeProtocol.NATIVE: 0.0,
    }

    # Swap fees (percentage)
    SWAP_FEES: dict[SwapProtocol, float] = {
        SwapProtocol.JUPITER: 0.01,     # 0.01% (Jupiter aggregator)
        SwapProtocol.UNISWAP: 0.30,     # 0.30% (Uniswap V3)
        SwapProtocol.CURVE: 0.04,      # 0.04% (Curve stable pools)
        SwapProtocol.ONE_INCH: 0.10,   # 0.10% (1inch)
        SwapProtocol.ORCA: 0.05,       # 0.05% (Orca)
    }

    # Stablecoin-stablecoin price impact (very low for stable pairs)
    STABLE_SWAP_IMPACT: dict[tuple[Stablecoin, Stablecoin], float] = {
        (Stablecoin.USDC, Stablecoin.USDT): 0.01,
        (Stablecoin.USDT, Stablecoin.USDC): 0.01,
        (Stablecoin.USDC, Stablecoin.DAI): 0.02,
        (Stablecoin.DAI, Stablecoin.USDC): 0.02,
        (Stablecoin.USDC, Stablecoin.FRAX): 0.03,
        (Stablecoin.FRAX, Stablecoin.USDC): 0.03,
        (Stablecoin.USDC, Stablecoin.PYUSD): 0.05,
        (Stablecoin.PYUSD, Stablecoin.USDC): 0.05,
        (Stablecoin.USDC, Stablecoin.LUSD): 0.10,
        (Stablecoin.LUSD, Stablecoin.USDC): 0.10,
    }

    def __init__(self, simulation: bool = True):
        self.simulation = simulation

    def plan(self, source_chain: Chain, source_token: Stablecoin,
             source_amount: float, target_chain: Chain = Chain.ARC,
             target_token: Stablecoin = Stablecoin.USDC,
             slippage_pct: Optional[float] = None) -> TransferPlan:
        """
        Plan the optimal route for a stablecoin transfer.
        
        Returns a TransferPlan with estimated routes, fees, and timing.
        No real funds are moved.
        """
        plan = TransferPlan(
            source_chain=source_chain,
            source_token=source_token,
            source_amount=source_amount,
            target_chain=target_chain,
            target_token=target_token,
            slippage_tolerance_pct=slippage_pct or 0.5,
        )

        remaining = source_amount
        total_fee = 0.0
        total_time = 0

        # Step 1: If same chain but different token → swap only
        if plan.is_same_chain and not plan.is_same_token:
            swap = self._plan_swap(source_chain, source_token, target_token, remaining)
            plan.swaps.append(swap)
            remaining = swap.expected_to_amount
            total_fee += swap.expected_to_amount * swap.fee_pct / 100

        # Step 2: If different chain → bridge then swap
        elif plan.needs_bridge:
            # Bridge the source token to target chain
            bridge = self._plan_bridge(source_chain, target_chain, source_token, remaining)
            plan.bridges.append(bridge)
            remaining -= bridge.fee_usd
            total_fee += bridge.fee_usd
            total_time += bridge.estimated_time_minutes

            # If bridged token ≠ target token, swap
            if source_token != target_token:
                swap = self._plan_swap(target_chain, source_token, target_token, remaining)
                plan.swaps.append(swap)
                remaining = swap.expected_to_amount
                total_fee += remaining * swap.fee_pct / 100

        # Step 3: Same chain, same token → no-op (just deposit)
        # (already handled — remaining stays as-is)

        plan.expected_output = round(remaining, 6)
        plan.min_output = round(apply_slippage(remaining, plan.slippage_tolerance_pct), 6)
        plan.estimated_total_fee_usd = round(total_fee, 4)
        plan.estimated_time_minutes = total_time
        plan.status = RouteStatus.SIMULATED

        return plan

    def _plan_bridge(self, from_chain: Chain, to_chain: Chain,
                     token: Stablecoin, amount: float) -> BridgeRoute:
        """Plan a bridge hop."""
        protocols = self.BRIDGE_PATHS.get((from_chain, to_chain), [BridgeProtocol.NATIVE])
        best = protocols[0]  # Pick first (best) protocol

        return BridgeRoute(
            protocol=best,
            from_chain=from_chain,
            to_chain=to_chain,
            token=token,
            amount=amount,
            estimated_time_minutes=self.BRIDGE_TIMES.get(best, 15),
            fee_usd=self.BRIDGE_FEES.get(best, 0.50),
        )

    def _plan_swap(self, chain: Chain, from_token: Stablecoin,
                   to_token: Stablecoin, amount: float) -> SwapRoute:
        """Plan a swap hop."""
        protocols = self.SWAP_PROTOCOLS.get(chain, [SwapProtocol.JUPITER])
        best = protocols[0]

        # Estimate price impact
        impact = self.STABLE_SWAP_IMPACT.get(
            (from_token, to_token), 0.05
        )

        fee_pct = self.SWAP_FEES.get(best, 0.10)
        fee = amount * fee_pct / 100
        impact_cost = amount * impact / 100
        expected = amount - fee - impact_cost

        return SwapRoute(
            protocol=best,
            from_token=from_token,
            to_token=to_token,
            from_amount=amount,
            expected_to_amount=round(expected, 6),
            min_to_amount=round(apply_slippage(expected, 0.5), 6),
            price_impact_pct=impact,
            fee_pct=fee_pct,
            pool=f"{from_token.value}/{to_token.value} on {chain.value}",
        )


# ── Transfer Executor ─────────────────────────────────────────────────

class TransferExecutor:
    """
    Executes a TransferPlan.
    Simulation mode by default — logs what would happen without moving funds.
    """

    def __init__(self, simulation: bool = True):
        self.simulation = simulation

    def execute(self, plan: TransferPlan) -> TransferPlan:
        """
        Execute a transfer plan.
        
        In simulation mode, marks the plan as SIMULATED and returns it.
        In real mode, would execute bridges and swaps on-chain.
        """
        if self.simulation:
            plan.status = RouteStatus.SIMULATED
            return plan

        # Real execution path (requires wallet + API keys)
        # TODO: Implement when Jordan provides wallet access
        plan.status = RouteStatus.FAILED
        return plan


# ── Portal Engine ─────────────────────────────────────────────────────

@dataclass
class TransferResult:
    """Result of a transfer request."""
    plan: TransferPlan
    success: bool
    message: str
    tx_hashes: list[str] = field(default_factory=list)


class StablecoinPortal:
    """
    Main entry point for the Stablecoin Transfer Portal.
    
    Usage:
        portal = StablecoinPortal(simulation=True)
        result = portal.transfer(
            source_chain=Chain.ETHEREUM,
            source_token=Stablecoin.USDT,
            source_amount=100.0,
        )
        print(result.plan.expected_output)  # ~99.xx USDC on ARC
    """

    def __init__(self, simulation: bool = True):
        self.planner = RoutePlanner(simulation=simulation)
        self.executor = TransferExecutor(simulation=simulation)
        self.slippage = SlippageConfig()

    def transfer(self, source_chain: Chain, source_token: Stablecoin,
                 source_amount: float, target_chain: Chain = Chain.ARC,
                 target_token: Stablecoin = Stablecoin.USDC,
                 slippage_pct: Optional[float] = None) -> TransferResult:
        """
        Plan and execute a stablecoin transfer.
        
        In simulation mode, plans the route and returns estimated output.
        No real funds are moved.
        """
        # Validate
        if source_amount <= 0:
            return TransferResult(
                plan=TransferPlan(source_chain=source_chain, source_token=source_token,
                                  source_amount=source_amount),
                success=False,
                message="Amount must be > 0",
            )

        slippage = self.slippage.validate(slippage_pct or self.slippage.default_pct)

        # Plan
        plan = self.planner.plan(
            source_chain=source_chain,
            source_token=source_token,
            source_amount=source_amount,
            target_chain=target_chain,
            target_token=target_token,
            slippage_pct=slippage,
        )

        # Execute
        plan = self.executor.execute(plan)

        return TransferResult(
            plan=plan,
            success=plan.status == RouteStatus.SIMULATED,
            message=self._format_summary(plan),
        )

    def _format_summary(self, plan: TransferPlan) -> str:
        """Format a human-readable transfer summary."""
        parts = [
            f"Transfer {plan.source_amount} {plan.source_token.value} on {plan.source_chain.value}",
            f"→ {plan.expected_output} {plan.target_token.value} on {plan.target_chain.value}",
        ]

        if plan.bridges:
            for b in plan.bridges:
                parts.append(f"  Bridge: {b.protocol.value} ({b.estimated_time_minutes} min, ${b.fee_usd:.2f})")

        if plan.swaps:
            for s in plan.swaps:
                parts.append(f"  Swap: {s.protocol.value} via {s.pool} (impact: {s.price_impact_pct}%)")

        parts.append(f"  Min output: {plan.min_output} (slippage: {plan.slippage_tolerance_pct}%)")
        parts.append(f"  Est. fee: ${plan.estimated_total_fee_usd:.4f}")
        parts.append(f"  Est. time: {plan.estimated_time_minutes} min")
        parts.append(f"  Status: {plan.status.value}")

        return "\n".join(parts)


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Stablecoin Transfer Portal")
    sub = parser.add_subparsers(dest="command")

    # transfer
    tx = sub.add_parser("transfer", help="Plan a stablecoin transfer")
    tx.add_argument("--from-chain", choices=[c.value for c in Chain], required=True)
    tx.add_argument("--from-token", choices=[s.value for s in Stablecoin], required=True)
    tx.add_argument("--amount", type=float, required=True)
    tx.add_argument("--to-chain", default="arc")
    tx.add_argument("--to-token", default="USDC")
    tx.add_argument("--slippage", type=float, default=0.5)

    # list
    ls = sub.add_parser("list", help="List supported chains and tokens")

    args = parser.parse_args()

    if args.command == "transfer":
        portal = StablecoinPortal(simulation=True)
        source_chain = Chain(args.from_chain)
        source_token = Stablecoin(args.from_token)
        target_chain = Chain(args.to_chain)
        target_token = Stablecoin(args.to_token)

        result = portal.transfer(
            source_chain=source_chain,
            source_token=source_token,
            source_amount=args.amount,
            target_chain=target_chain,
            target_token=target_token,
            slippage_pct=args.slippage,
        )

        if result.success:
            print("✅ Transfer Planned Successfully")
            print()
            print(result.message)
        else:
            print(f"❌ {result.message}")

    elif args.command == "list":
        print("Supported Source Chains:")
        for c in Chain:
            print(f"  • {c.value}")
        print()
        print("Supported Stablecoins:")
        for s in Stablecoin:
            print(f"  • {s.value}")
        print()
        print("Bridge Protocols:")
        for b in BridgeProtocol:
            print(f"  • {b.value}")
        print()
        print("Swap Protocols:")
        for s in SwapProtocol:
            print(f"  • {s.value}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
