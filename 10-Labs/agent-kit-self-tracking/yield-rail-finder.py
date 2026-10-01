#!/usr/bin/env python3
"""Yield Rail Finder — Steward's cross-rail yield heat-map.

For each configured rail (chain), pulls live yield opportunities from the
Yield.xyz MCP (via yield_mcp.py), computes a "headline yield" (top APY on a
liquid, comparable opportunity), maps it onto the 6-color Rainbow heat scale,
and reports which rail currently holds the edge.

Outputs:
  1. Human-readable report to stdout (Telegram / cron delivery)
  2. JSON to the Hub (DeFi/rainbow/rail-finder-data.json) so the Yield Farm
     tab can render a rail heat-map next to the Yield Rainbow.

Heat scale (Jordan's design — same colors as the Rainbow, new job):
  🔴 On Fire   APY >= 8%
  🟠 Hot       APY 6-8%
  🟡 Warm      APY 5-6%
  🟢 Cool      APY 4-5%
  🔵 Cooling   APY 3-4%
  🟣 Coma      APY < 3%

The Rainbow answers "WHERE are we in the cycle"; the Rail Finder answers
"WHERE is the hottest yield right now."
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yield_mcp import YieldMCP, YieldMCPError, rank  # noqa: E402
from yield_vs_baseline import agentic_edge, compare  # noqa: E402

# ── Rails we operate / watch ────────────────────────────────────────────────
# Each rail: network id (Yield.xyz), label, primary token for apples-to-apples.
RAILS = [
    {"net": "base",        "label": "Base / Aerodrome", "token": "USDC", "icon": "⛓️"},
    {"net": "solana",      "label": "Solana / Meteora", "token": "USDC", "icon": "🌊"},
    {"net": "avalanche-c", "label": "Avalanche / LFJ",   "token": "USDC", "icon": "🏔️"},
    {"net": "monad",       "label": "Monad (future)",    "token": "USDC", "icon": "🧬"},
]

# Minimum TVL to consider an opportunity "liquid enough" to count as headline.
MIN_TVL = 1_000_000  # $1M floor — skip dust pools that can't take capital.

# Rainbow heat bands (mirrors yield-rainbow band colors, new semantics).
HEAT_BANDS = [
    {"name": "On Fire", "emoji": "🔴", "color": "#e84142", "min": 8.0},
    {"name": "Hot",     "emoji": "🟠", "color": "#f59e0b", "min": 6.0},
    {"name": "Warm",    "emoji": "🟡", "color": "#eab308", "min": 5.0},
    {"name": "Cool",    "emoji": "🟢", "color": "#22c55e", "min": 4.0},
    {"name": "Cooling", "emoji": "🔵", "color": "#3b82f6", "min": 3.0},
    {"name": "Coma",    "emoji": "🟣", "color": "#a855f7", "min": 0.0},
]

HUB_JSON_PATH = os.environ.get(
    "RAIL_FINDER_HUB_PATH",
    "/root/repos/gentechlabs.github.io/DeFi/rainbow/rail-finder-data.json",
)

# Provider → app URL, so the report can emit clickable links (bare URLs are
# NOT tappable in Telegram — always use [text](url) markdown).
PROVIDER_URLS = {
    "stakekit": "https://stakekit.com",
    "securitize": "https://securitize.io",
    "kamino": "https://app.kamino.finance",
    "fluid": "https://fluid.io",
    "aave": "https://app.aave.com",
    "morpho": "https://app.morpho.org",
    "yearn": "https://yearn.fi",
    "aerodrome": "https://aerodrome.finance",
    "traderjoe": "https://traderjoexyz.com",
    "meteora": "https://app.meteora.ag",
    "jito": "https://jito.network",
    "lido": "https://stake.lido.fi",
    "compound": "https://app.compound.finance",
    "spark": "https://app.spark.fi",
    "eigenlayer": "https://app.eigenlayer.xyz",
}


def provider_link(provider: str) -> str:
    """Return a clickable markdown link for a provider, or plain text if unknown."""
    p = (provider or "").strip()
    if not p:
        return "—"
    url = PROVIDER_URLS.get(p.lower())
    if url:
        return f"[{p}]({url})"
    return p


def heat_band(apy_pct: float) -> dict:
    """Map an APY% onto the heat scale (first band whose min it clears)."""
    for b in HEAT_BANDS:
        if apy_pct >= b["min"]:
            return b
    return HEAT_BANDS[-1]


def headline_for_rail(client: YieldMCP, rail: dict, limit: int = 30) -> dict:
    """Compute a rail's headline yield: top liquid APY, preferring the token."""
    try:
        items = client.yields(
            networks=[rail["net"]],
            limit=max(limit, 50),
        )
    except YieldMCPError as exc:
        return {
            "net": rail["net"], "label": rail["label"], "icon": rail["icon"],
            "ok": False, "error": str(exc),
        }

    liquid = rank(items, min_tvl=MIN_TVL)
    if not liquid:
        return {
            "net": rail["net"], "label": rail["label"], "icon": rail["icon"],
            "ok": False, "error": "no liquid opportunities (TVL < $1M)",
        }

    # Prefer the primary token's opportunities; fall back to all-liquid best.
    primary = [o for o in liquid if (o.get("tokenSymbol") or "").upper() == rail["token"].upper()]
    pool = primary or liquid

    top = pool[0]
    apy_pct = float(top.get("rewardRate") or 0) * 100
    band = heat_band(apy_pct)
    top_token = (top.get("tokenSymbol") or "").upper()

    # Honest labeling: headline may be a volatile native-token staking yield,
    # NOT the stable (USDC) yield we'd actually park capital in.
    is_stable = top_token in ("USDC", "USDT", "USDS", "USDe", "DAI", "USX", "AUSD", "USDt")

    # Agentic Treasury edge: what WE can do vs passive HODL/stake on this rail.
    # compare() = does the headline yield beat HODL/stake.
    # agentic_edge() = the active strategy's expected return vs passive.
    edge = agentic_edge(apy_pct, top_token)
    base = compare(apy_pct, top_token)

    # Top 3 of this rail for detail (prefer primary token, then liquid).
    detail = pool[:3]

    return {
        "net": rail["net"], "label": rail["label"], "icon": rail["icon"],
        "ok": True,
        "headlineApy": round(apy_pct, 2),
        "headlineProvider": top.get("providerId", ""),
        "headlineType": top.get("type", ""),
        "headlineTvl": float(top.get("tvlUsd") or 0),
        "token": top_token,
        "isStable": is_stable,
        "band": band["name"], "bandEmoji": band["emoji"], "bandColor": band["color"],
        "edge": edge,
        "baseline": base,
        "top": [
            {
                "apy": round(float(o.get("rewardRate") or 0) * 100, 2),
                "provider": o.get("providerId", ""),
                "type": o.get("type", ""),
                "tvl": float(o.get("tvlUsd") or 0),
                "token": (o.get("tokenSymbol") or "").upper(),
            }
            for o in detail
        ],
    }


def build_report(rails_result: list[dict], ts: str) -> str:
    """Build a mobile-friendly, rich-text report.

    Mobile-safe layout: NO fixed-width column alignment (that breaks when
    Telegram wraps lines / emoji widths vary). One data point per line,
    separated by '·' / '—' so it re-flows cleanly on any screen width.

    Rich text: bold section headers + clickable provider links (markdown),
    which Telegram renders. Bare URLs are NOT tappable — always [text](url).
    """
    ok = [r for r in rails_result if r.get("ok")]
    ok.sort(key=lambda r: r["headlineApy"], reverse=True)
    worst = [r for r in rails_result if not r.get("ok")]

    lines = []
    lines.append("**🧭 YIELD RAIL FINDER**")
    lines.append(f"{ts} · cross-rail yield heat-map")
    lines.append("")

    if ok:
        hottest = ok[0]
        lines.append(f"**Hottest:** {hottest['icon']} {hottest['label']} "
                     f"{hottest['bandEmoji']} **{hottest['headlineApy']}%** · "
                     f"{provider_link(hottest['headlineProvider'])} · {hottest['token']}")
        lines.append("")
        lines.append("**Rails:**")
        for r in ok:
            stab = " · ⚠️ volatile token" if not r.get("isStable") else ""
            lines.append(
                f"{r['bandEmoji']} {r['label']} — **{r['headlineApy']}%** · "
                f"{r['band']} · {provider_link(r['headlineProvider'])} · {r['token']}{stab}"
            )
        lines.append("")
        lines.append("**🚀 Agentic Treasury edge (vs passive HODL/stake):**")
        for r in ok:
            e = r.get("edge", {})
            b = r.get("baseline", {})
            # Active APY = headline * multiplier; edge over the best passive option.
            active = e.get("active_apy", 0)
            vs_best = e.get("vs_passive_best", 0)
            sep = e.get("separation", "")
            hodl = b.get("hodl_30d", 0)
            stake = b.get("stake_apr", 0)
            lines.append(
                f"{r['icon']} {r['label']} — active **{active}%** · "
                f"vs HODL {hodl:+.1f}% · vs stake {stake:.1f}% · "
                f"edge **{vs_best:+.1f}pts** · {sep}"
            )
        lines.append("")
        lines.append("**Top picks (≥$1M TVL):**")
        for r in ok:
            for t in r["top"][:2]:
                lines.append(
                    f"{r['icon']} {t['token']} — **{t['apy']}%** · "
                    f"{provider_link(t['provider'])} · {t['type']} · ${t['tvl']/1e6:.2f}M"
                )
        lines.append("")
    if worst:
        lines.append("**⚠️ Unreachable rails:**")
        for r in worst:
            lines.append(f"{r['icon']} {r['label']}: {r.get('error')}")
        lines.append("")

    lines.append("Legend: 🔴≥8% · 🟠6-8 · 🟡5-6 · 🟢4-5 · 🔵3-4 · 🟣<3")
    lines.append("⚠️ = volatile native-token yield, not deployable USDC")
    lines.append("Data: Yield.xyz MCP · not financial advice")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Yield Rail Finder")
    p.add_argument("--json", action="store_true", help="print JSON only")
    p.add_argument("--write-hub", action="store_true",
                   help="write JSON to the Hub path (DeFi/rainbow/rail-finder-data.json)")
    p.add_argument("--limit", type=int, default=30, help="opportunities per rail to scan")
    args = p.parse_args()

    client = YieldMCP()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    results = [headline_for_rail(client, rail, args.limit) for rail in RAILS]

    if args.json:
        print(json.dumps({
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "rails": results,
        }, indent=2))
        return 0

    report = build_report(results, ts)
    print(report)

    if args.write_hub:
        data = {
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "rails": results,
        }
        os.makedirs(os.path.dirname(HUB_JSON_PATH), exist_ok=True)
        with open(HUB_JSON_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n[hub] wrote {HUB_JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
