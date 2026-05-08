---
name: protocol-ecosystem-scan
description: Recurring multi-source intelligence scan of a blockchain/crypto protocol ecosystem. Checks websites, GitHub, npm, explorer dashboards, and competitor sources to produce a structured strategy report.
version: 1.0.0
author: Gentech
license: MIT
tags: [research, protocol, ecosystem, intelligence, cron, crypto, blockchain, x402]
---

# Protocol Ecosystem Scan

Run a scheduled, multi-source intelligence sweep across a protocol ecosystem (e.g., x402, Solana, Base) to surface new developments, SDK changes, facilitator/competitor movements, and actionable insights for strategy.

## When to Use

- Biweekly or monthly **ecosystem pulse checks** on protocols Gentech integrates with or monitors
- Pre-hackathon **landscape reviews** to spot new tools, SDKs, or facilitators
- Post-announcement **deep-follow** to verify claims and check for breaking changes
- **Competitive monitoring** when a new facilitator, SDK, or token launches in our domain
- Any recurring cron job instruction that says "scan X ecosystem" or "report on Y protocol changes"
- **Security incident monitoring** — post-exploit intelligence gathering (see `references/security-incident-monitor.md`)

## What This Covers (Class-Level)

This skill handles the *pattern* of multi-source protocol monitoring. The exact URLs change per protocol, but the source categories are consistent:

| Category | Typical Sources | What to Extract |
|---|---|---|
| **Protocol Docs & Ecosystem** | Official ecosystem page, partner directories | New partners, facilitators, tools, categories |
| **Primary Infrastructure** | Facilitator/SDK landing pages, docs | SDK updates, new chains, feature launches |
| **Explorer / Analytics** | Protocol-specific explorers, dashboards | Transaction volumes, chain health, facilitator market share |
| **GitHub** | Core protocol repo, SDK repos | Commits, releases, tags, merged/open PRs, breaking changes |
| **Package Registries** | npm, PyPI, crates.io, Go packages | Version bumps, publish dates, breaking changes |
| **Competitors** | Similar facilitator/explorer projects | New entrants, pricing, feature gaps |
| **Security Incidents** *(variant)* | Incident statements, DVN/infra stats, exploit attribution | Post-exploit response quality, code activity, governance changes, risk deltas |

## Workflow

### 1. Gather Sources in Parallel

Hit as many sources as the protocol exposes, concurrently:

```bash
# Example for x402 — adapt URLs per protocol
curl -s -o /tmp/eco.json https://x402.org/api/ecosystem      # ecosystem listings
curl -s -o /tmp/commits.json https://api.github.com/repos/{org}/{repo}/commits
curl -s -o /tmp/tags.json https://api.github.com/repos/{org}/{repo}/tags
curl -s -o /tmp/prs.json "https://api.github.com/repos/{org}/{repo}/pulls?state=all&per_page=50"
curl -s -o /tmp/npm.json https://registry.npmjs.org/{package}
```

### 2. Hit Explorer Dashboards via Browser

For explorer/analytics pages that are JS-rendered:

```
browser_navigate → https://explorer.example.com/protocols
browser_navigate → https://explorer.example.com/chains
browser_navigate → https://explorer.example.com/facilitators
```

Extract key metrics (txn counts, volumes, active chains, downtime alerts).

### 3. Parse & Structure

Use `execute_code` or save-to-file-then-read to avoid `curl | python3` security blocks:

```bash
curl -s -o /tmp/data.json <url>
```
Then parse in Python to extract:
- **SDK/Protocol:** version history, publish dates, recent commits, merged PRs, breaking keywords
- **Explorer:** volumes, txns, chain status (operational/down), facilitator rankings
- **Ecosystem:** new partner names, categories, descriptions

### 4. Build the Report

Use this standard structure — it works across protocols:

```
## 1. New Developments (since last scan)
Table or bulleted list with date + description.

## 2. Relevant to Gentech
Per-item yes/no with a one-sentence "why."

## 3. Action Items
Priority table: P1/P2/P3, action, owner, deadline.

## 4. Risk / Opportunity Assessment
Bullet risks with severity and opportunities with upside.
```

### 5. Deliver & Save

- Deliver report to the relevant group/channel per department routing rules.
- Save a copy to the vault if the user requests persistence.

## Focus Triggers (Gentech-Specific)

When scanning, actively flag items in these categories:

| Focus | What to Look For |
|---|---|
| **SDK Integration** | Solana-native SDKs, MCP integrations, paywall middleware |
| **AAE Monetization** | New facilitator pricing, batching (MPP), per-call economics |
| **Agent Stack** | MCP discovery support, client integrations (Claude, Cursor, ChatGPT) |
| **Token / Economic Changes** | New token launches, staking requirements, fee model shifts |
| **Breaking Changes** | Major version bumps, deprecated endpoints, chain removals |

## Key Metrics to Extract from Explorers

Whenever an explorer/dashboard exists, extract:
- **Protocols tracked** and their txn/volume split
- **Chain health** (operational vs down, uptime)
- **Facilitator leaderboard** (txn count, volume, avg txn size, buyer/seller counts, chain coverage)
- **Server/resource counts** (hosts, endpoints, verification rates)
- **Recent activity window** (24h / 7d / 30d)

## GitHub Signals to Watch

- **Recent commits** (last 30 days): feature keywords, new packages, spec additions
- **Tags / releases**: version bumps, especially major versions (breaking)
- **Open PRs**: new ecosystem entries, facilitators, SDK features not yet merged
- **Closed PRs (recent):** what shipped since the last scan

## Pitfalls

- **No formal GitHub releases?** Check tags — many crypto projects tag but don't write release notes.
- **Explorer data is JS-rendered** — `curl` alone often returns nothing; use `browser_navigate`.
- **Package registry pipes blocked** — save to file first, then parse, to avoid `curl | python3` security intercepts.
- **Downtime can be transient** — note the exact time of scan; chain status changes fast.
- **Wash/fraud analytics often token-gated** — note the requirement but don't chase unless instructed.
- **Ecosystem PRs flood in** — dozens of open ecosystem-addition PRs is normal; surface only the ones that match Gentech focus areas.
- **Security incident monitoring** requires delta-tracking tables and risk-level escalation — see `references/security-incident-monitor.md` for the specialized workflow.

## Output Style

- Lead with the bottom-line strategic verdict in 2–3 sentences.
- Use tables for comparisons (versions, facilitators, chains).
- Keep each section scannable — headers, bold, short bullets.
- End with a clear risk/opportunity frame and a prioritized action list.
