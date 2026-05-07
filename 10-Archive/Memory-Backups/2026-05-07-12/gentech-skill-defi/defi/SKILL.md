---
name: defi
description: "Comprehensive DeFi operations for Hermes agents: LP position monitoring, strategy design, on-chain data reading, and security intelligence. Covers off-chain API monitoring, on-chain web3.py reads, systematic strategy rules, and post-incident reconnaissance."
tags: [defi, lp, strategy, on-chain, security, monitoring]
trigger: "When the user needs any DeFi-related operation: LP monitoring, strategy design, on-chain position reads, or security incident monitoring. Use this umbrella to access sub-sections for specific workflows."
related_skills:
  - market-macro-monitor  # price data context
  - link-research-summary  # protocol research
version: 1.0.0
author: Gentech
---

# DeFi Operations (Umbrella)

This umbrella skill covers the core DeFi agent operation patterns — lightweight recurring LP monitoring, deep on-chain position reading, systematic strategy design, and post-incident security intelligence. Each subsection below is a focused skill module with its full original content preserved in `references/`.

> **Consolidated skills:** `defi-lp-position-monitor`, `defi-lp-strategy-designer`, `defi-onchain-position-reader`, `defi-security-intel-monitor`.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Check my LP positions daily / set up cron monitor" | [1. LP Position Monitor](#1-lp-position-monitor-lightweight--cron) |
| "Design exit/entry rules / portfolio rotation strategy" | [2. LP Strategy Designer](#2-lp-strategy-designer-systematic-strategy-design) |
| "Read exact on-chain position data / per-bin breakdown" | [3. On-Chain Position Reader](#3-on-chain-position-reader-deep-web3py) |
| "Monitor a protocol after a hack/exploit / gather intel" | [4. Security Intel Monitor](#4-security-intel-monitor-post-incident-recon) |

---

## 1. LP Position Monitor (Lightweight / Cron)

**Original skill:** `defi-lp-position-monitor`

Recurring lightweight DeFi LP position monitoring via off-chain APIs (CoinGecko, DexScreener), with Obsidian vault skip-logic, milestone/D5 alignment checks, and Telegram summary reporting. Designed for cron jobs where full on-chain web3.py reads are unnecessary.

### When to Use
- Daily cron, price alerts, summary reports
- Mobile/low-bandwidth contexts
- Avoiding full on-chain reads for efficiency

### Key Data Sources
- CoinGecko (free, no key) — watchlist prices, 24h change
- Binance Public API — fallback when CoinGecko 429s
- CoinMarketCap (requires key) — secondary fallback
- DexScreener — pool volume, TVL, price data

### Skip-Logic Rules
| Condition | Action |
|-----------|--------|
| Price delta < 0.5% + IL < 0.5% + in-range | Skip vault append |
| IL ≥ 1.0% | Append vault, flag review |
| Price exits range | Append vault, flag review |
| Milestone tier achieved | Append vault, celebrate |

### Cron Frequency
Recommended: **4× daily** (08:15, 12:15, 16:15, 20:15 UTC)

### Common Pitfalls
- CoinGecko aggressive rate limits → cascade fallbacks
- DexScreener HTTP 403 after repeated calls → best-effort only
- Fee estimation is approximate, not on-chain exact

> **Full canonical content:** See `references/defi-lp-position-monitor-full.md` for the complete original runbook, including code snippets, error handling, multi-pool monitoring, and vault templates.

---

## 2. LP Strategy Designer (Systematic Strategy Design)

**Original skill:** `defi-lp-strategy-designer`

Design systematic DeFi strategy rules — LP exit/entry signals, multi-strategy portfolio rotation (LP ↔ Staking ↔ HODL ↔ Farming), regime detection, resistance ladders, position sizing, and trainable learning layers where agents learn from user patterns.

### When to Use
- Designing bull/bear market LP exit or entry strategies
- Creating resistance ladder rules for scaling out of LP
- Deciding LFJ shape (curve/bid-ask/spot) for market regime
- Building systematic signals for LP ↔ spot transitions
- Documenting strategy rules in vault files
- Designing multi-strategy rotation and hybrid portfolio models
- Creating trainable learning layers where agents observe user trading patterns

### Core Concepts
**Shape by Regime:**
| Regime | Best Shape |
|--------|-----------|
| Choppy/ranging | Curve |
| High volatility, no direction | Bid-Ask |
| Strong bullish breakout | Exit → spot |
| Crash/panic dump | Skewed curve (70% stablecoin) |
| Consolidation after rally | Curve at new range |

**Exit Signal Framework:**
- High confidence: volume breakout, momentum surge, macro catalyst → act immediately
- Medium confidence: trend confirmation → scale out 50%, rest on confirmation
- Low confidence: parabolic moves → wait for consolidation

**Position Sizing Templates** (Bull breakout, post-consolidation re-entry, crash protection) — see full skill for code blocks.

### Multi-Strategy Rotation (v1.1)
Baseline allocation: 30% yield farming (passive), 20% staking (stable), 50% active bucket (LP/HODL/rotate). Active bucket shifts based on market regime detection.

### Trainable Learning Layer
AAE observes user trading decisions → learns user patterns → mimics user style → executes autonomously → compares decisions to user's and improves from corrections. Modes: Shadow → Supervised → Autonomous.

> **Full canonical content:** See `references/defi-lp-strategy-designer-full.md` for complete strategy design playbook, including documentation patterns, integration with monitor, and the completed bull-market exit strategy example.

---

## 3. On-Chain Position Reader (Deep web3.py)

**Original skill:** `defi-onchain-position-reader`

Read on-chain DeFi LP positions from EVM chains using web3.py. Handles factory-based DEX protocols (LFJ, Uniswap V3, etc.) with dynamic pair addresses, ERC-1155/ERC-721 position tokens, and ABI mismatch recovery via raw RPC calls.

### When to Use vs Off-Chain APIs
| Need | Use |
|------|-----|
| Price, volume, TVL | DexScreener / CoinGecko |
| Per-bin share breakdown, exact reserves, position NFT data | **This skill** — on-chain reads |

### Environment (isolated venv)
```bash
uv venv /root/.hermes/scripts/.venv --python 3.11
uv pip install --python /root/.hermes/scripts/.venv/bin/python web3 requests
```
Script shebang: `#!/root/.hermes/scripts/.venv/bin/python3`

### LFJ (Avalanche) — Critical Notes
**V2.1 vs V2.2 ABI mismatch:** Factory returns V2.1 pair contracts (minimal proxies) with different function names than SDK docs. Always verify with raw `eth_call` before building.

**V2.1 function names:** `getActiveId()` (not `activeBin()`), `getTokenX()` / `getTokenY()`. `getBin(uint256)` does NOT exist — per-bin reserves inaccessible.

**Position scanning:** ERC-1155 positions; token ID = bin ID. Scan bidirectionally from active bin (±1, ±2...) not linearly. Early exit after 20+ consecutive empty offsets.

### Silent Reverts → Agent Hallucination CRITICAL
When a contract function doesn't exist, `eth_call` reverts silently and returns empty bytes. The script reads this as zero positions and the AI agent then **hallucinates realistic-looking but fake data**. Always test each function selector individually with raw `eth_call`; if script returns zero positions, log a warning — never let the agent assume data is valid.

### Combined LP + Wallet Tracker Pattern
Merge LP position data with wallet balances (Routescan API) in a single script for holistic view and single cron job.

> **Full canonical content:** See `references/defi-onchain-position-reader-full.md` for ABI mismatch recovery, RPC batch limits, debugging reverted calls, full Avalanche token reference, and testing checklist.

---

## 4. Security Intel Monitor (Post-Incident Recon)

**Original skill:** `defi-security-intel-monitor`

Autonomous DeFi security incident monitoring and intelligence reconnaissance. Gather post-incident updates from official blogs, protocol statements, governance proposals, competitor responses, and on-chain/off-chain stats dashboards. Compile structured intelligence reports with risk assessment and action items.

### Workflow
1. Define scope
2. Gather official sources — blog archive navigation, GitHub releases/commits, governance portals
3. Search for protocol-level changes — GitHub commit history post-incident, Snapshot/Tally proposals
4. Check on-chain/analytics dashboards — Dune (with Cloudflare workarounds)
5. Competitor intelligence — rival protocols capitalizing on incident
6. Compile structured report with risk level rubric
7. Save to vault with date header

### Risk Level Rubric
- **IMPROVED:** Protocol enacted an on-chain upgrade or mandatory minimum that materially reduces recurrence risk
- **UNCHANGED:** No protocol-level change; only operator-level or recommendation-level responses
- **WORSENED:** New attack vectors discovered, protocol remains silent, or contagion risk increased

### Known Obstacles & Workarounds
| Obstacle | Workaround |
|----------|------------|
| Google search bot detection | Navigate direct URLs; skip search |
| Dune Cloudflare block | Try BROWSERBASE_ADVANCED_STEALTH; document gap |
| X/Twitter login wall | browser_navigate may expose posts; xurl CLI if authenticated |
| JS-heavy docs | browser_console execute JS selectors |

> **Full canonical content:** See `references/defi-security-intel-monitor-full.md` for the complete report template, example LayerZero DVN monitoring, and detailed source-gathering techniques.

---

## Related Skills (External)

- **`market-macro-monitor`** — price lookup and macro context for DeFi positions
- **`link-research-summary`** — protocol and project research before building
- **`protocol-ecosystem-scan`** — recurring protocol intelligence for chains/tokens you follow

---

## References (Session-Specific Detail)

- `references/defi-lp-position-monitor-full.md`
- `references/defi-lp-strategy-designer-full.md`
- `references/defi-onchain-position-reader-full.md`
- `references/defi-security-intel-monitor-full.md`

These files contain the complete original SKILL.md content from the pre-consolidation skills, preserved verbatim for session-specific detail and edge-case coverage not captured in the summary sections above.