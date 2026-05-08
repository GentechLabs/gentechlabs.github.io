---
name: hackathon-lifecycle
description: Comprehensive monitoring and management of hackathon statuses from active tracking through submission verification and results monitoring. Covers Encode Club, lablab.ai, and other platforms; vault-based record keeping; cron status checks; and submission packaging for Gentech agents.
tags: [hackathon, monitoring, submission, encode-club, status-check, vault]
---

# Hackathon Lifecycle Management

## When to Use

Use this skill for any recurring or ad-hoc hackathon status diligence, including:
- Daily/weekly check of active hackathon deadlines and our progress
- Verification of submission completion (local evidence + platform confirmation)
- Post-deadline monitoring for judging updates, winner announcements, results publication
- Cross-referencing vault records with official platforms (Encode Club, lablab.ai, Devpost, etc.)
- Flags for blockers (e.g., placeholder addresses, deployment failures)

If you are asked "What's the status of X hackathon?" or "Did we submit to Y?", load this skill.

**Solana Frontier (May 11, 2026)**: See `references/solana-frontier-2026.md` for tracks, prizes, sponsor integrations, and build status. Our submission: AgentEscrow.

## Core Procedure

### A. Establish Baseline from Vault

1. Read `01-Agency/active-hackathons.md` — the single source of truth for current focus, deadlines, and status flags (🟢 building/🟡 pending/🔴 critical).
2. Identify hackathon-specific strategy/watch files:
   - Under `03-Strategies/` look for `Hackathon-Name-Strategic-Watch.md` or `Hackathon-Name_Strategy.md`
   - These contain narrative, scope decisions, and explicit "submission status" notes.
3. Check `11-Mess Hall/` for the last 3 days of daily context files (today-context, rotation-log) for any agenda items or flags related to the hackathon.

### B. Official Platform Check

For Encode Club-hosted hackathons:
- **Direct page:** `curl -s <hackathon-url>` and grep for keywords:
  ```
  closed | ended | announcement | winners | judging | results | finalists | deadlines | extended from
  ```
- **Extract meta description** (it often contains deadline info): `grep -i 'og:description\\|meta name="description"'` and look for date patterns and keywords.
- If page returns mostly empty or is JS-rendered, the page likely loads dynamically. In that case:
  - Try `browser_vision(url, question="What is on this page?")` for full rendered analysis.
  - Or note "manual verification required" as a flag.
- **Check the Encode Club `programmes` listing page** to see if the hackathon still appears. Removed listing often indicates concluded event.
- If the vault shows an earlier deadline but the platform shows a later one, treat the later date as authoritative and note "vault not yet updated to reflect extension."

For lablab.ai or other platforms:
- If blocked by Cloudflare, rely on vault records or targeted `web_search` queries like:
  ```
  site:lablab.ai "hackathon name" results winners
  ```

### C. Submission Evidence Audit

Search the vault for any artifacts that prove submission:
- Files under `08-Daily/` or `10-Archive/` containing `submission`, `pitch`, `demo`, `readme` referencing that hackathon.
- Presence of a `submission-readme.md` or `submission-package` under `03-Projects/Hackathons/` or directly under `02-Labs/Hackathons/Active/<hackathon>/` (e.g., `kite-submission-readme.md` is a ready-to-submit package indicator).
- GitHub activity: use GitHub API to check `ProtoJay4789` or relevant repos for:
  - Commits after the start of Week 4 (typical build phase)
  - Issues labeled `hackathon-submission` or PRs merged with that tag.
  - Git tags or releases named after the hackathon.
- Deployment readiness indicators: check for the presence of `Deploy.s.sol` with correct chain ID, `foundry.toml` configured for the target network, and `.env.example` with real token addresses. These signal that the project is *submission-ready* even if not yet deployed to testnet.
- If any submission evidence exists, mark status as "submitted" and note date and artifacts.

### D. Coordination Channel Scan

Check `11-Mess Hall/` entries for the last 48 hours for any of:
- Winners or finalists announced
- Judging started / demo day scheduled
- Team status update (e.g., "submitted today", "withdrawn", "focused on next hackathon")

Also scan `00-HQ/Brainstorm/` and `01-Agency/Approvals/` for any formal decisions.

### E. Synthesis and Reporting

Compose a concise status:

```
## [Hackathon Name] — [Current Status as of DATE]
- Deadline: DATE (timezone)
- Our submission state: NOT_SUBMITTED / IN_PROGRESS / READY_TO_SUBMIT (deployment pending gas) / SUBMISSION_PENDING (docs ready, final checks) / SUBMITTED on DATE / WITHDRAWN
- Track: [if applicable, e.g., Agentic Commerce]
- Platform status: OPEN / CLOSED / JUDGING / RESULTS ANNOUNCED
- Winners/finalists: [if available]
- Evidence: [vault file refs, GitHub links, testnet explorer tx hashes, etc.]
- Blockers: [deployment gas, testnet faucet, demo video, docs polish, etc.]
- Next action: [what needs to happen next, owner if known]
```

For cron jobs: use ~60 words maximum, deliver to Mess Hall root or designated channel.

## Pitfalls and Edge Cases

- **Deadline inconsistency:** Multiple vault files often list different deadlines (e.g., `KiteAI_Strategy.md` shows May 6; `Kite-AI-Strategic-Watch.md` shows May 11). Always trust `01-Agency/active-hackathons.md` as canonical, and double-check the official platform. When uncertain, assume the earlier date.
- **Dynamic rendering on Encode Club:** Their pages are SPA with client-side rendering. `curl` returns a near-empty body. Use keyword search on the raw HTML to infer state (`closed` in meta description may indicate concluded). If ambiguous, schedule a `browser_vision` call or flag for manual review.
- **Results gated behind auth:** Some Encode Club hackathons hide winner announcements behind login. If you see "View Results" button but no public list, treat results as "pending public release" and monitor official X/Twitter.
- **Placeholder contract addresses:** Many hackathon projects start with placeholder contract/DVN addresses. Before any deployment or demo, verify that monitor scripts and contracts reference real addresses. Kite AI DVN placeholder must be replaced pre-production.
- **Stale Mess Hall files:** Files older than 5 days may be archived (`10-Archive/`). Always prefer `2026/W18/` current week. If nothing recent found, look at the `agent-coordination-board.md` for agent check-in status.
- **Multiple similar hackathons:** Encode Club sometimes runs parallel hackathons with similar themes (e.g., "Kite AI Global" vs "April Agentic Mini Hack"). Confirm exact name and URL from `active-hackathons.md`.
- **Deadline extensions:** Encode Club may extend deadlines without immediately updating all vault files. Look for explicit notes in strategy docs like "extended from X" and cross-check the official page's meta description or intro text for updated dates. Always use the latest deadline stated anywhere (vault OR platform).
- **Concurrent hackathon sprint conflicts:** When two or more hackathons overlap (e.g., Solana Frontier May 11 + Kite AI May 17), check `02-Labs/Hackathons/Active/sprint-plan-*.md` to understand resource prioritization. A blocker for a lower-priority hackathon may be intentionally unfunded; always assess whether work is gated by deliverables from a higher-priority track before raising as urgent.
- **Deployment-gas blockers:** For chain-based submissions requiring on-chain deployment, verify: (a) testnet faucet access confirmed, (b) gas available, (c) chain ID configured in foundry/hardhat. Missing any of these means "submission-ready but not yet deployed" — flag as a critical path item, not a missing artifact.

## Vault Reference Map

```
01-Agency/active-hackathons.md           ← Canonical active list & deadlines
03-Strategies/
  Kite-AI-Strategic-Watch.md             ← Long-term strategic notes
  KiteAI_Strategy.md                     ← Short-term execution plan
  README-KiteAI-AgentEconomy.md          ← Overview doc
11-Mess Hall/
  2026/W18/<date>/today-context.md      ← Daily agenda + flags
  2026/W18/<date>/rotation-log-*.md     ← Agent rotation updates
10-Archive/
  green-room-handoffs/                  ← DMOB/Desmond technical handoffs
  Mess Hall/                            ← Older daily logs
03-Projects/
  Hackathons/                           ← Submission artifacts (if any)
```

## Related Skills

- `research/encode-club-hackathon-monitor` — Platform navigation details, page structure breakdown, lablab.ai notes.
- `gentech-agent-health-diagnosis` — If hackathon cron jobs fail.
