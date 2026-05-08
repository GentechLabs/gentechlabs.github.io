# Security Incident Monitoring — Reference Guide

**Skill:** `protocol-ecosystem-scan` variant  
**Trigger:** Post-exploit / security incident requiring daily intelligence monitoring  
**Last Updated:** 2026-05-02 (KelpDAO/LayerZero incident)

## Source Categories (Security-Focused)

| Category | Primary Sources | Fallback / Secondary | What to Extract |
|---|---|---|---|
| **Official Incident Response** | Protocol blog, security advisory pages | team Twitter/X, Discord announcements, GitHub security advisories | Incident statement date, attribution (e.g., "state actor"), affected systems, claimed fixes |
| **Protocol Code Activity** | GitHub commits since incident (filter by date) | Releases page, changelogs, audit repo commits | Commits tagged "security", "hotfix", "DVN", "RPC"; release versions; breaking changes |
| **Governance Reaction** | Snapshot/Tally proposals | Forum posts, community call recordings | New proposals mandating multi-DVN, security parameter changes, quorum adjustments |
| **DVN / Infrastructure Stats** | Dune Analytics, protocol-specific dashboards | LayerZero Scan API, subgraph queries, community-maintained dashboards | DVN distribution (1-of-1 vs 2-of-2 vs 3-of-3+), active/inactive DVNs, migration velocity |
| **Competitor Responses** | Competitor blogs, Twitter/X threads | Reddit discussions, Medium articles, pod interviews | Security marketing contrasting models, "lessons learned" posts, recruitment of affected users |
| **Community Sentiment** | X/Twitter, Telegram, Discord, Reddit | N/A | Blame attribution ("who's at fault?"), calls for action, migration discussions |

## Fallback Hierarchy When Primary Source Fails

1. **Official blog → Team Twitter → GitHub Issues/Discussions → Community Forum**
2. **Dune Analytics blocked → LayerZero Scan API / subgraph / explorer endpoints → Community dashboard mirrors**
3. **GitHub API rate-limited → GitHub HTML page scrape → Git mirror (git.io shortlinks)**

## Delta Tracking Table Format

Use this structure for daily supplements:

| Item | Previous Day | Current Day | Change | Notes |
|------|--------------|-------------|--------|-------|
| Latest official blog post | Apr 19 — X | Still Apr 19 — no new post | None | Team in silent posture |
| GitHub commits (24h) | 0 | 0 | None | No security patch activity |
| Governance proposals | 0 | 0 | None | Community not mobilizing |
| Competitor campaigns | Not detected | Not detected | None | Wormhole/Axelar silent |

**Outcome:** "No material changes detected" or "Change: X crossed threshold Y."

## Risk Assessment Matrix (Post-Incident)

| Level | Criteria | Action |
|---|---|---|
| **CRITICAL** | Vulnerability still exploitable + no mitigation announced | Freeze integrations, immediate mitigation |
| **HIGH** | Vulnerability exploitable + soft-policy response only (no on-chain enforcement) | Portfolio risk audit, contingency planning |
| **MEDIUM** | Vulnerability patched but systemic change absent | Monitor migration completion, watch for follow-on exploits |
| **LOW** | Protocol-level hardening enforced + migration complete | Resume normal monitoring cadence |

**LayerZero current placement:** **HIGH** — single-DVN attack path still technically viable because protocol doesn't mandate ≥2 DVNs at smart-contract level.

## Key Questions to Answer Every Check

1. **Latest official statement** — date, content, new information vs. reiteration?
2. **Code-level response** — commits, releases, breaking changes?
3. **Governance action** — new proposals, voting, implementation timelines?
4. **DVN stats movement** — has 1-of-1 percentage decreased? At what velocity?
5. **Competitor messaging** — exploiting vulnerability or staying silent?
6. **Risk level change** — improved, unchanged, or worsened since last check?

## Output Template Structure

```markdown
## Supplement — {DATE} Check

**Checked:** {timestamp} UTC  
**Analyst:** YoYo, Head of Strategies @ Gentech

### Delta Since {PREVIOUS_DATE} Report

**One-sentence summary of change (or "No new material changes detected").**

| Item | Previous Status | Current Status | Change |
|------|----------------|----------------|--------|
| ... | ... | ... | ... |

### Detail

1. **{Source Category 1}:** Findings with specific evidence (URLs, commit SHAs, proposal IDs)
2. **{Source Category 2}:** Findings...
3. ...

### Risk Assessment ({DATE})

**Risk Level: {UNCHANGED / IMPROVED / WORSENED} → {SEVERITY}**

*Paragraph justification referencing specific unchanged/changed factors.*

### Action Items (Updated {DATE})

| Priority | Action | Owner | Due |
|----------|--------|-------|-----|
| ... | ... | ... | ... |

*— YoYo, Gentech Strategies*
```

## Common Pitfalls & Workarounds

- **Dune blocked by Cloudflare** → Use `curl -H "User-Agent: Mozilla/5.0"` + session cookies if available, or switch to alternative data sources (subgraph, Scan API)
- **Blog JSON embedded in Next.js bundle** → Cannot access Contentful API without access token; fall back to HTML scraping simple text patterns + team Twitter for official tone
- **GitHub API rate-limit (60 req/hr)** → Switch to GitHub HTML page scraping for basic commit list, or use `git.io` shortlinks to clone repo shallowly
- **No Dune stats available** → Query LayerZeroScan.com directly, or use community-maintained Dash这场比赛 (if any), or approximate from protocol deployment data
- **Competitor social silence** — absence of evidence ≠ evidence of absence; document as "not detected" not "confirmed absent"

## Related Skills

- `link-research-summary` — for deep-diving individual URLs when a claim needs verification
- `blogwatcher` — for RSS-based blog monitoring when site offers feed
- `github-issues` / `github-repo-management` — for GitHub-specific deep probes
- `system-health` — for infrastructure-status check patterns (overlaps with explorer checks)
