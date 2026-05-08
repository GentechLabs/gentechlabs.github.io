---
name: technology-radar-monitoring
description: "Weekly scan of vendor ecosystems, model releases, dependency updates, and framework changes affecting your technology stack."
version: 1.0.0
author: DMOB (Labs)
tags: [monitoring, ecosystem, dependencies, vendor-management, security-updates, stack-currency]
triggers:
  - weekly scan
  - vendor status check
  - model provider update
  - dependency vulnerability scan
  - stack health assessment
---

# Technology Radar Monitoring

Systematically track the health and currency of your technology stack across vendors, models, frameworks, and dependencies.

## When to Use

- Scheduled weekly cron (default: Sunday UTC)
- After major vendor announcements (model releases, pricing changes, deprecations)
- Before planning infrastructure upgrades or migrations
- When troubleshooting cross-provider routing issues
- Quarterly strategic review of stack direction

## What It Covers

1. **Vendor Product Lifecycle** — deprecations, service status, EOL notices
2. **Model Provider Landscape** — new releases, pricing, API changes, migration timelines
3. **Agent Framework/Tooling** — new skills, breaking changes, security patches
4. **Dependency Security** — CVE scans, outdated packages, version upgrades
5. **Internal Stack Health** — agent gateway status, model routing configs, credential validity

## Data Sources

| Source | What to Check | How |
|--------|---------------|-----|
| Internal vault (`03-Strategies/`, `02-Labs/`) | Project status, migration docs, handoffs | Read markdown files for decisions & timelines |
| Agent configs (`~/.hermes/profiles/*/config.yaml`) | Active models, providers, fallbacks | Scan for provider, model, base_url fields |
| Hermes CLI | Agent version, gateway health | `hermes --version`, `hermes gateway list` |
| Package managers | Outdated packages, security updates | `pip list --outdated`, `apt upgrade --just-print`, `npm outdated` |
| Vendor channels | Announcements, blog posts, GitHub releases | Bookmark vendor homepages; check weekly |

## Output Format

**Tech Radar Summary — [Date]**

*PentAGI status | Nous migration | Hermes version | Model configs | Security alerts*

Keep it tight (max 200 words) with:
- ✅ Green: Healthy, no action
- ⚠️ Yellow: Attention needed (e.g., expiring tokens)
- 🔴 Red: Action required (broken routing, expiring subscriptions)
- 📊 Version numbers and dates
- ⏭️ Next check date

Save to: `11-Mess Hall/daily/YYYY-MM-DD-tech-radar.md` or include in daily second-brain sync.

## Standard Procedure

1. **Vault scan** — read project files for status updates (PentAGI, migration docs, handoffs)
2. **Agent config audit** — parse all `~/.hermes/profiles/*/config.yaml` for current model/provider assignments
3. **Gateway health** — `hermes gateway list` to confirm all agents online
4. **Version check** — `hermes --version` vs upstream GitHub releases
5. **Dependency scan** — pip + apt (npm if installed)
6. **Credential check** — look for expired tokens, .env corruption patterns
7. **Findings synthesis** — categorize by severity, flag action items
8. **Report & archive** — write to vault; update next-week todo if blockers found

## Known Stack Signals (Gentech Reference)

| Component | What to Watch | Current (2026-05-03) |
|-----------|---------------|----------------------|
| PentAGI | Service status, relevance | ⚠️ Deprecated; superseded by Hermes; service down since Apr 16 |
| Nous Research | Subscription expiry, API changes | ⚠️ Subscription ends May 9, 2026; migration in progress |
| Hermes Agent | Version vs upstream | ✅ v0.12.0 (2026.4.30) — current; 0 commits behind |
| OpenCode Go | Routing health, 401s | ✅ Resolved Apr 26 failure; gateways clean |
| Ollama Cloud | Rate limits, model availability | ✅ DMOB on qwen3-coder-next; working |
| Kimi K2.6 | Swarm capabilities, rate limits | 🟡 Under eval; 30K+ pulls; watch quota |
| Dependencies | CVE fixes, major version bumps | 🔴 cryptography, elevenlabs, fal_client, firecrawl-py, docker, gh |

## Pitfalls & Gotchas

- **vision_analyze 401s** often trace to expiredNous token even if primary model is OpenCode; check both `.env` files
- **.env corruption** — line-merges during edits break credentials; validate with `cat -A` to see hidden chars
- **Gateway PID stale locks** — dead PID files prevent startup; clean `/tmp` or `hermes gateway stop --all` before restart
- **pip outdated noise** — many Hermes deps pinned; focus on security-critical (cryptography, requests, urllib3)
- **Vault lag** — daily files may be a day behind; cross-check with `~/.hermes/logs/` for fresh errors
- **Model switch fallback** — always test routing with a cheap query before declaring success

## Extension Points

- Add vendor RSS feeds to `references/vendor-watchlist.md`
- Store historical version tracking in `references/version-history.md`
- Keep a running CVE log in `references/security-advisories.md`

## Related

- `hermes-agent-health-check` — gateway-specific diagnostics
- `hermes-agent-reactivation` — recovery workflows
- `dependency-watchlist` — package-level advisory scanning (if installed)
