"""
AAE Yield Farm — Config-First Deploy Flow
===========================================
Phase 1: Config form template + input validation
Phase 2: Preview card with fee/APR projections

The user fills shape/range/entry → preview card → config written → on-chain reader verifies.
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

# ── Config Schema ──────────────────────────────────────────────────────────

@dataclass
class YieldFarmConfig:
    """User-declared configuration for an AAE yield farm position."""
    shape: str                    # "CURVE" or "BID-ASK"
    range_low: float              # Lower price bound
    range_high: float             # Upper price bound
    entry_price: float            # Price at deployment
    amount_usd: float             # Total USD amount to deploy
    strategy_label: str = ""      # Optional human label
    pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
    chain: str = "avalanche"
    token0: str = "AVAX"
    token1: str = "USDC"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def validate(self) -> list[str]:
        """Return list of validation errors. Empty list = valid."""
        errors = []

        # Shape
        if self.shape.upper() not in ("CURVE", "BID-ASK"):
            errors.append(f"Shape must be CURVE or BID-ASK, got '{self.shape}'")

        # Range
        if self.range_low <= 0:
            errors.append(f"Range low must be > 0, got {self.range_low}")
        if self.range_high <= 0:
            errors.append(f"Range high must be > 0, got {self.range_high}")
        if self.range_low >= self.range_high:
            errors.append(f"Range low ({self.range_low}) must be < range high ({self.range_high})")

        # Entry price
        if self.entry_price <= 0:
            errors.append(f"Entry price must be > 0, got {self.entry_price}")
        if self.entry_price < self.range_low or self.entry_price > self.range_high:
            errors.append(f"Entry price ({self.entry_price}) must be within range [{self.range_low}, {self.range_high}]")

        # Amount
        if self.amount_usd <= 0:
            errors.append(f"Amount must be > 0, got {self.amount_usd}")

        # Pool address (basic hex check)
        if not re.match(r'^0x[a-fA-F0-9]{40}$', self.pool_address):
            errors.append(f"Pool address must be a valid 0x-prefixed 40-char hex string")

        return errors

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "YieldFarmConfig":
        return cls(**data)


# ── Config Form Template ───────────────────────────────────────────────────

CONFIG_FORM_TEMPLATE = """🏦 AAE Yield Farm — New Position

Shape:
  ● CURVE   (default — choppy markets, tight range)
  ○ BID-ASK (macro events, Fed, CPI — wider range)

Range (low):  ${range_low:.2f}
Range (high): ${range_high:.2f}
Entry price:  ${entry_price:.2f} (auto-filled from current market)

Amount: ${amount_usd:.2f} (wallet balance: ${wallet_balance:.2f})

Strategy label: {strategy_label} (optional, e.g. "July chop")

[Deploy]  [Cancel]
"""


# ── Preview Card Generator ─────────────────────────────────────────────────

@dataclass
class FeeProjection:
    daily_fees_usd: float = 0.0
    estimated_apr_pct: float = 0.0
    daily_volume_usd: float = 0.0
    pool_liquidity_usd: float = 0.0
    position_share_pct: float = 0.0
    fee_tier_bps: int = 5

    @classmethod
    def estimate(cls, config: YieldFarmConfig, pool_volume_24h: float,
                 pool_liquidity: float, current_price: float) -> "FeeProjection":
        """Estimate daily fees and APR based on pool data."""
        position_share = config.amount_usd / pool_liquidity if pool_liquidity > 0 else 0
        fee_tier = 0.0005  # 5 bps

        # In-range fee estimate: position's share of volume × fee tier
        # Out-of-range earns $0
        in_range = config.range_low <= current_price <= config.range_high
        if in_range and pool_volume_24h > 0:
            daily_fees = pool_volume_24h * position_share * fee_tier
        else:
            daily_fees = 0.0

        # APR: (daily_fees × 365) / position_value
        apr = (daily_fees * 365 / config.amount_usd * 100) if config.amount_usd > 0 else 0.0

        return cls(
            daily_fees_usd=round(daily_fees, 4),
            estimated_apr_pct=round(apr, 1),
            daily_volume_usd=round(pool_volume_24h, 2),
            pool_liquidity_usd=round(pool_liquidity, 2),
            position_share_pct=round(position_share * 100, 3),
            fee_tier_bps=int(fee_tier * 10000),
        )


def render_preview_card(config: YieldFarmConfig, fees: FeeProjection,
                        wallet_balance: float) -> str:
    """Render a terminal-friendly preview card."""
    in_range = config.range_low <= fees.daily_volume_usd / max(fees.pool_liquidity_usd, 1) * config.amount_usd <= config.range_high

    lines = [
        "┌─────────────────────────────────────┐",
        f"│  ✅ Confirm Deployment{' ' * 27}│",
        "│                                     │",
        f"│  Shape:  {config.shape.upper():<30}│",
        f"│  Range:  ${config.range_low:.2f}  →  ${config.range_high:.2f}{' ' * 12}│",
        f"│  Entry:  ${config.entry_price:.2f}{' ' * 28}│",
        f"│  Amount: ${config.amount_usd:.2f}{' ' * 27}│",
        "│                                     │",
        f"│  Projected fees: ~${fees.daily_fees_usd:.4f}/day{' ' * 11}│",
        f"│  Est. APR: ~{fees.estimated_apr_pct:.1f}% at current volume{' ' * 5}│",
        f"│  Position share: {fees.position_share_pct:.3f}% of pool{' ' * 8}│",
        "│                                     │",
        "│  [✓ Looks good — deploy on LFJ]     │",
        "│  [✗ Cancel — fix something]         │",
        "└─────────────────────────────────────┘",
    ]
    return "\n".join(lines)


# ── Config File I/O ────────────────────────────────────────────────────────

def write_config(config: YieldFarmConfig, path: str) -> str:
    """Write config to JSON file. Returns the path."""
    data = config.to_dict()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def read_config(path: str) -> Optional[YieldFarmConfig]:
    """Read config from JSON file. Returns None if file doesn't exist or is invalid."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return YieldFarmConfig.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


# ── Verification Gate (Phase 3) ───────────────────────────────────────────

@dataclass
class VerificationResult:
    passed: bool
    mismatches: list[str] = field(default_factory=list)
    config: Optional[dict] = None
    onchain: Optional[dict] = None

    def __bool__(self):
        return self.passed


def verify_position(config: YieldFarmConfig, onchain_data: dict,
                    tolerance_pct: float = 1.0) -> VerificationResult:
    """
    Compare config against on-chain position data.
    tolerance_pct: allowed deviation (e.g. 1.0 = 1% tolerance on amounts).
    """
    mismatches = []

    # Shape check
    config_shape = config.shape.upper()
    onchain_shape = onchain_data.get("shape", "").upper()
    shape_map = {"CURVE": "CURVE", "BID-ASK": "BID-ASK", "BIDIRECTIONAL": "BID-ASK"}
    if shape_map.get(onchain_shape, onchain_shape) != config_shape:
        mismatches.append(
            f"Shape mismatch: config says {config_shape}, on-chain shows {onchain_shape}"
        )

    # Range check
    onchain_low = onchain_data.get("range_low") or onchain_data.get("range", {}).get("low")
    onchain_high = onchain_data.get("range_high") or onchain_data.get("range", {}).get("high")

    if onchain_low and abs(onchain_low - config.range_low) / config.range_low * 100 > tolerance_pct:
        mismatches.append(
            f"Range low mismatch: config ${config.range_low:.4f}, on-chain ${onchain_low:.4f} "
            f"({abs(onchain_low - config.range_low) / config.range_low * 100:.1f}% off)"
        )
    if onchain_high and abs(onchain_high - config.range_high) / config.range_high * 100 > tolerance_pct:
        mismatches.append(
            f"Range high mismatch: config ${config.range_high:.4f}, on-chain ${onchain_high:.4f} "
            f"({abs(onchain_high - config.range_high) / config.range_high * 100:.1f}% off)"
        )

    # Total value check
    onchain_total = onchain_data.get("totalValue") or onchain_data.get("totalValueUSD")
    if onchain_total and abs(onchain_total - config.amount_usd) / config.amount_usd * 100 > tolerance_pct * 2:
        mismatches.append(
            f"Amount mismatch: config ${config.amount_usd:.2f}, on-chain ${onchain_total:.2f}"
        )

    return VerificationResult(
        passed=len(mismatches) == 0,
        mismatches=mismatches,
        config=config.to_dict(),
        onchain=onchain_data,
    )


# ── CLI Entry Point ────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="AAE Yield Farm — Config-First Deploy")
    sub = parser.add_subparsers(dest="command")

    # config
    config_cmd = sub.add_parser("config", help="Create a new config")
    config_cmd.add_argument("--shape", choices=["CURVE", "BID-ASK"], default="CURVE")
    config_cmd.add_argument("--range-low", type=float, required=True)
    config_cmd.add_argument("--range-high", type=float, required=True)
    config_cmd.add_argument("--entry-price", type=float, required=True)
    config_cmd.add_argument("--amount", type=float, required=True)
    config_cmd.add_argument("--label", default="")
    config_cmd.add_argument("--output", default="aae-deploy-config.json")

    # preview
    preview_cmd = sub.add_parser("preview", help="Show preview card")
    preview_cmd.add_argument("--config", default="aae-deploy-config.json")
    preview_cmd.add_argument("--volume", type=float, default=918000.0)
    preview_cmd.add_argument("--liquidity", type=float, default=397000.0)
    preview_cmd.add_argument("--price", type=float, default=6.56)

    # verify
    verify_cmd = sub.add_parser("verify", help="Verify config against on-chain data")
    verify_cmd.add_argument("--config", default="aae-deploy-config.json")
    verify_cmd.add_argument("--onchain", default="")

    args = parser.parse_args()

    if args.command == "config":
        cfg = YieldFarmConfig(
            shape=args.shape,
            range_low=args.range_low,
            range_high=args.range_high,
            entry_price=args.entry_price,
            amount_usd=args.amount,
            strategy_label=args.label,
        )
        errors = cfg.validate()
        if errors:
            print("❌ Validation errors:")
            for e in errors:
                print(f"   • {e}")
            return

        write_config(cfg, args.output)
        print(f"✅ Config written to {args.output}")
        print(f"   Shape: {cfg.shape} | Range: ${cfg.range_low:.2f}–${cfg.range_high:.2f} | Amount: ${cfg.amount_usd:.2f}")

    elif args.command == "preview":
        cfg = read_config(args.config)
        if not cfg:
            print(f"❌ Config not found or invalid: {args.config}")
            return

        fees = FeeProjection.estimate(cfg, args.volume, args.liquidity, args.price)
        print(render_preview_card(cfg, fees, wallet_balance=cfg.amount_usd * 1.5))

    elif args.command == "verify":
        cfg = read_config(args.config)
        if not cfg:
            print(f"❌ Config not found or invalid: {args.config}")
            return

        if args.onchain:
            with open(args.onchain) as f:
                onchain = json.load(f)
        else:
            # Try default on-chain data path
            default_path = os.path.join(
                os.path.dirname(args.config), "..", "DeFi", "defi-data.json"
            )
            if os.path.exists(default_path):
                with open(default_path) as f:
                    onchain = json.load(f)
                onchain = onchain.get("lpPosition", onchain)
            else:
                print("❌ No on-chain data file specified and default not found")
                return

        result = verify_position(cfg, onchain)
        if result.passed:
            print("✅ Verification passed — config matches on-chain position")
        else:
            print("⚠️  Config Mismatch Detected")
            for m in result.mismatches:
                print(f"   • {m}")
            print("\n   └─ Did you deploy with the wrong settings? [Fix on LFJ] [Update config]")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
