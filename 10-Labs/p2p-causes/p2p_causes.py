"""
GenTech Hub — P2P Causes + Flyer Factory
=========================================
P2P funding layer for Agentic Treasury. Users create causes (story + photos + goal).
Hub generates posters/banners/flyers from user data. Wallet discovery, ratings,
reputation scores. Same trust-graph infrastructure as prediction markets.

Simulation mode by default. Real execution requires wallet integration.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ── Types ──────────────────────────────────────────────────────────────

class CauseStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    FUNDED = "funded"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FlyerStyle(Enum):
    MODERN = "modern"          # Clean, minimal, gradient-heavy
    BOLD = "bold"              # High contrast, large text
    CHARITY = "charity"        # Warm tones, heart imagery
    TECH = "tech"              # Cyber/neon aesthetic
    NATURE = "nature"          # Earth tones, organic shapes


class FlyerFormat(Enum):
    POSTER = "poster"          # 2:3 ratio (Instagram post)
    BANNER = "banner"          # 16:9 ratio (Twitter/website)
    STORY = "story"            # 9:16 ratio (Instagram story)
    SQUARE = "square"          # 1:1 ratio (profile/thumbnail)


class ReputationTier(Enum):
    NEW = "new"                # 0-1 contributions
    TRUSTED = "trusted"        # 2-5 contributions
    VERIFIED = "verified"      # 6-20 contributions
    CORE = "core"              # 21+ contributions


# ── Data Models ───────────────────────────────────────────────────────

@dataclass
class Cause:
    """A P2P funding cause."""
    id: str
    title: str
    story: str
    creator_wallet: str
    goal_amount_usd: float
    raised_amount_usd: float = 0.0
    image_urls: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: CauseStatus = CauseStatus.DRAFT
    contributor_count: int = 0
    created_at: str = ""
    deadline: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def progress_pct(self) -> float:
        if self.goal_amount_usd <= 0:
            return 0.0
        return min(self.raised_amount_usd / self.goal_amount_usd * 100, 100.0)

    @property
    def remaining_usd(self) -> float:
        return max(self.goal_amount_usd - self.raised_amount_usd, 0.0)

    @property
    def is_fully_funded(self) -> bool:
        return self.raised_amount_usd >= self.goal_amount_usd


@dataclass
class Contribution:
    """A single contribution to a cause."""
    cause_id: str
    contributor_wallet: str
    amount_usd: float
    message: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class WalletReputation:
    """Reputation score for a wallet."""
    wallet: str
    total_contributed_usd: float = 0.0
    causes_supported: int = 0
    causes_created: int = 0
    successful_causes: int = 0
    average_rating: float = 0.0
    rating_count: int = 0
    tier: ReputationTier = ReputationTier.NEW
    first_seen: str = ""
    last_active: str = ""

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.first_seen:
            self.first_seen = now
        if not self.last_active:
            self.last_active = now

    def recalculate_tier(self):
        total_contributions = self.causes_supported + self.causes_created
        if total_contributions >= 21:
            self.tier = ReputationTier.CORE
        elif total_contributions >= 6:
            self.tier = ReputationTier.VERIFIED
        elif total_contributions >= 2:
            self.tier = ReputationTier.TRUSTED
        else:
            self.tier = ReputationTier.NEW


# ── Flyer Factory ─────────────────────────────────────────────────────

@dataclass
class FlyerSpec:
    """Specification for generating a flyer/poster/banner."""
    cause: Cause
    style: FlyerStyle = FlyerStyle.MODERN
    format: FlyerFormat = FlyerFormat.POSTER
    accent_color: str = "#22c55e"  # GenTech green
    show_progress: bool = True
    show_contributors: bool = True
    show_wallet: bool = False
    custom_message: str = ""

    def to_html(self) -> str:
        """Generate an HTML flyer that can be rendered or screenshotted."""
        progress = self.cause.progress_pct
        remaining = self.cause.remaining_usd

        # Style-specific color schemes
        colors = {
            FlyerStyle.MODERN: {"bg": "linear-gradient(135deg, #0a0a0a, #1a1a2e)", "accent": self.accent_color, "text": "#e0e0e0"},
            FlyerStyle.BOLD: {"bg": "linear-gradient(135deg, #1a0000, #2d0000)", "accent": "#ef4444", "text": "#ffffff"},
            FlyerStyle.CHARITY: {"bg": "linear-gradient(135deg, #0d1a0d, #1a2d1a)", "accent": "#22c55e", "text": "#e0e0e0"},
            FlyerStyle.TECH: {"bg": "linear-gradient(135deg, #0a001a, #1a0033)", "accent": "#a855f7", "text": "#e0e0e0"},
            FlyerStyle.NATURE: {"bg": "linear-gradient(135deg, #0d1a0d, #1a2d1a)", "accent": "#fbbf24", "text": "#e0e0e0"},
        }

        # Format-specific dimensions
        dims = {
            FlyerFormat.POSTER: {"width": "600px", "height": "900px"},
            FlyerFormat.BANNER: {"width": "900px", "height": "506px"},
            FlyerFormat.STORY: {"width": "400px", "height": "711px"},
            FlyerFormat.SQUARE: {"width": "600px", "height": "600px"},
        }

        c = colors.get(self.style, colors[FlyerStyle.MODERN])
        d = dims.get(self.format, dims[FlyerFormat.POSTER])

        # Progress bar
        progress_bar = ""
        if self.show_progress:
            progress_bar = f"""
            <div class="progress-section">
                <div class="progress-label">${self.cause.raised_amount_usd:.0f} raised of ${self.cause.goal_amount_usd:.0f} goal</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress:.1f}%"></div>
                </div>
                <div class="progress-stats">
                    <span>{progress:.0f}% funded</span>
                    <span>${remaining:.0f} remaining</span>
                </div>
            </div>"""

        # Contributors
        contributors_section = ""
        if self.show_contributors and self.cause.contributor_count > 0:
            contributors_section = f"""
            <div class="contributors">
                <span class="contrib-count">{self.cause.contributor_count} contributor{"s" if self.cause.contributor_count != 1 else ""}</span>
            </div>"""

        # Custom message
        message_html = f"<p class='message'>{self.custom_message}</p>" if self.custom_message else ""

        # Tags
        tags_html = ""
        if self.cause.tags:
            tags_html = '<div class="tags">' + ''.join(
                f'<span class="tag">{t}</span>' for t in self.cause.tags[:5]
            ) + '</div>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #000; }}
    .flyer {{ width: {d["width"]}; height: {d["height"]}; background: {c["bg"]}; color: {c["text"]}; padding: 40px; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; border: 2px solid {c["accent"]}; border-radius: 16px; }}
    .flyer::before {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle at 30% 20%, {c["accent"]}11 0%, transparent 50%); pointer-events: none; }}
    .header {{ position: relative; z-index: 1; }}
    .badge {{ display: inline-block; background: {c["accent"]}; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 0.75em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }}
    .title {{ font-size: 2em; font-weight: bold; line-height: 1.2; margin-bottom: 8px; }}
    .story {{ font-size: 0.9em; opacity: 0.8; line-height: 1.5; margin-bottom: 16px; max-height: 80px; overflow: hidden; }}
    .progress-section {{ margin: 20px 0; }}
    .progress-label {{ font-size: 0.85em; margin-bottom: 8px; opacity: 0.9; }}
    .progress-bar {{ height: 12px; background: #222; border-radius: 6px; overflow: hidden; }}
    .progress-fill {{ height: 100%; background: {c["accent"]}; border-radius: 6px; transition: width 0.5s; }}
    .progress-stats {{ display: flex; justify-content: space-between; font-size: 0.8em; margin-top: 6px; opacity: 0.7; }}
    .contributors {{ margin: 12px 0; }}
    .contrib-count {{ font-size: 0.85em; opacity: 0.7; }}
    .message {{ font-size: 0.9em; font-style: italic; opacity: 0.8; margin: 12px 0; }}
    .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 12px 0; }}
    .tag {{ background: {c["accent"]}22; color: {c["accent"]}; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; }}
    .footer {{ position: relative; z-index: 1; font-size: 0.75em; opacity: 0.5; text-align: center; border-top: 1px solid {c["accent"]}33; padding-top: 12px; }}
</style>
</head>
<body>
<div class="flyer">
    <div class="header">
        <div class="badge">P2P Cause</div>
        <div class="title">{self.cause.title}</div>
        <div class="story">{self.cause.story[:200]}{"..." if len(self.cause.story) > 200 else ""}</div>
        {tags_html}
        {message_html}
    </div>
    <div>
        {progress_bar}
        {contributors_section}
    </div>
    <div class="footer">Powered by GenTech Labs — Agentic Treasury</div>
</div>
</body>
</html>"""


# ── P2P Causes Engine ─────────────────────────────────────────────────

class P2PCausesEngine:
    """
    Core engine for P2P Causes.
    Simulation mode by default — stores causes in memory.
    """

    def __init__(self, simulation: bool = True):
        self.simulation = simulation
        self._causes: dict[str, Cause] = {}
        self._contributions: list[Contribution] = []
        self._reputations: dict[str, WalletReputation] = {}
        self._next_id = 1

    def create_cause(self, title: str, story: str, creator_wallet: str,
                     goal_amount_usd: float, tags: Optional[list[str]] = None,
                     image_urls: Optional[list[str]] = None) -> Cause:
        """Create a new cause."""
        cause_id = f"cause-{self._next_id}"
        self._next_id += 1

        cause = Cause(
            id=cause_id,
            title=title,
            story=story,
            creator_wallet=creator_wallet,
            goal_amount_usd=goal_amount_usd,
            tags=tags or [],
            image_urls=image_urls or [],
            status=CauseStatus.ACTIVE,
        )
        self._causes[cause_id] = cause

        # Update creator reputation
        self._ensure_reputation(creator_wallet)
        self._reputations[creator_wallet].causes_created += 1
        self._reputations[creator_wallet].recalculate_tier()

        return cause

    def contribute(self, cause_id: str, contributor_wallet: str,
                   amount_usd: float, message: str = "") -> Optional[Contribution]:
        """Contribute to a cause."""
        cause = self._causes.get(cause_id)
        if not cause:
            return None
        if cause.status != CauseStatus.ACTIVE:
            return None
        if amount_usd <= 0:
            return None

        contribution = Contribution(
            cause_id=cause_id,
            contributor_wallet=contributor_wallet,
            amount_usd=amount_usd,
            message=message,
        )
        self._contributions.append(contribution)

        # Update cause
        cause.raised_amount_usd += amount_usd
        cause.contributor_count += 1
        if cause.is_fully_funded:
            cause.status = CauseStatus.FUNDED

        # Update contributor reputation
        self._ensure_reputation(contributor_wallet)
        rep = self._reputations[contributor_wallet]
        rep.total_contributed_usd += amount_usd
        rep.causes_supported += 1
        rep.last_active = datetime.now(timezone.utc).isoformat()
        rep.recalculate_tier()

        return contribution

    def get_cause(self, cause_id: str) -> Optional[Cause]:
        return self._causes.get(cause_id)

    def list_causes(self, status: Optional[CauseStatus] = None) -> list[Cause]:
        causes = list(self._causes.values())
        if status:
            causes = [c for c in causes if c.status == status]
        return sorted(causes, key=lambda c: c.created_at, reverse=True)

    def get_contributions(self, cause_id: str) -> list[Contribution]:
        return [c for c in self._contributions if c.cause_id == cause_id]

    def get_reputation(self, wallet: str) -> Optional[WalletReputation]:
        return self._reputations.get(wallet)

    def generate_flyer(self, cause_id: str, style: FlyerStyle = FlyerStyle.MODERN,
                       format: FlyerFormat = FlyerFormat.POSTER,
                       accent_color: str = "#22c55e") -> Optional[str]:
        """Generate an HTML flyer for a cause."""
        cause = self._causes.get(cause_id)
        if not cause:
            return None

        spec = FlyerSpec(
            cause=cause,
            style=style,
            format=format,
            accent_color=accent_color,
        )
        return spec.to_html()

    def _ensure_reputation(self, wallet: str):
        if wallet not in self._reputations:
            self._reputations[wallet] = WalletReputation(wallet=wallet)


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="GenTech Hub — P2P Causes")
    sub = parser.add_subparsers(dest="command")

    # create
    create = sub.add_parser("create", help="Create a new cause")
    create.add_argument("--title", required=True)
    create.add_argument("--story", required=True)
    create.add_argument("--wallet", required=True)
    create.add_argument("--goal", type=float, required=True)
    create.add_argument("--tags", nargs="*", default=[])

    # contribute
    contrib = sub.add_parser("contribute", help="Contribute to a cause")
    contrib.add_argument("--cause-id", required=True)
    contrib.add_argument("--wallet", required=True)
    contrib.add_argument("--amount", type=float, required=True)
    contrib.add_argument("--message", default="")

    # list
    ls = sub.add_parser("list", help="List causes")
    ls.add_argument("--status", default="active")

    # flyer
    flyer = sub.add_parser("flyer", help="Generate a flyer HTML")
    flyer.add_argument("--cause-id", required=True)
    flyer.add_argument("--style", choices=[s.value for s in FlyerStyle], default="modern")
    flyer.add_argument("--format", choices=[f.value for f in FlyerFormat], default="poster")
    flyer.add_argument("--output", default="")

    # reputation
    rep = sub.add_parser("reputation", help="Check wallet reputation")
    rep.add_argument("--wallet", required=True)

    args = parser.parse_args()
    engine = P2PCausesEngine(simulation=True)

    if args.command == "create":
        cause = engine.create_cause(
            title=args.title,
            story=args.story,
            creator_wallet=args.wallet,
            goal_amount_usd=args.goal,
            tags=args.tags,
        )
        print(f"✅ Cause created: {cause.id}")
        print(f"   Title: {cause.title}")
        print(f"   Goal: ${cause.goal_amount_usd:.2f}")
        print(f"   Status: {cause.status.value}")

    elif args.command == "contribute":
        result = engine.contribute(args.cause_id, args.wallet, args.amount, args.message)
        if result:
            cause = engine.get_cause(args.cause_id)
            print(f"✅ Contribution recorded: ${args.amount:.2f}")
            print(f"   Cause: {cause.title if cause else 'unknown'}")
            print(f"   Progress: {cause.progress_pct:.1f}%" if cause else "")
        else:
            print(f"❌ Contribution failed — cause not found or inactive")

    elif args.command == "list":
        try:
            status = CauseStatus(args.status)
        except ValueError:
            status = None
        causes = engine.list_causes(status)
        if not causes:
            print("No causes found")
        else:
            print(f"Found {len(causes)} cause(s):")
            for c in causes:
                print(f"  • {c.id}: {c.title} — ${c.raised_amount_usd:.0f}/${c.goal_amount_usd:.0f} ({c.progress_pct:.0f}%) — {c.status.value}")

    elif args.command == "flyer":
        html = engine.generate_flyer(args.cause_id, FlyerStyle(args.style), FlyerFormat(args.format))
        if html:
            if args.output:
                with open(args.output, "w") as f:
                    f.write(html)
                print(f"✅ Flyer written to {args.output}")
            else:
                print(html)
        else:
            print(f"❌ Cause not found: {args.cause_id}")

    elif args.command == "reputation":
        rep = engine.get_reputation(args.wallet)
        if rep:
            print(f"Wallet: {rep.wallet}")
            print(f"Tier: {rep.tier.value}")
            print(f"Total contributed: ${rep.total_contributed_usd:.2f}")
            print(f"Causes supported: {rep.causes_supported}")
            print(f"Causes created: {rep.causes_created}")
        else:
            print(f"No reputation data for {args.wallet}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
