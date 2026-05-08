# Gentech Integration Audit — 2026-05-03

**Scope**: Active codebase only (excludes `10-Archive/`)
**Method**:ripgrep scans for HTTP libraries + service-specific patterns

## Executive Summary

| Category | Count | Replace with Composio? |
|----------|-------|----------------------|
| External API clients (requests/httpx) | 559 files (mostly archived) | — |
| Active integrations (non-archive) | ~20 distinct services | **YES** for 10+ |
| Blockchain/RPC exceptions | 3–5 scripts | **NO** (keep custom) |

**Key finding**: Most HTTP-using files are archived red-team skills (Anthropic cybersecurity pack). Active integrations are concentrated in `02-Labs/`, `03-Strategies/`, `06-Security/`.

---

## Active Integration Catalog

### 1. Google Workspace (CRITICAL)
- **Current**: Custom OAuth2 skill (`google-workspace/`), ~400 LOC
- **Files**: `google_api.py`, `setup.py`, `_common.py` (in skills dirs)
- **Pain points**: Token refresh edge cases, scope management, manual GCP project setup
- **Composio coverage**: ✅ GMAIL_*, CALENDAR_*, DRIVE_*, SHEETS_*, DOCS_*
- **Effort to replace**: 2 hours (OAuth linkage + 1 test script)
- **Priority**: P0 — already piloting

---

### 2. GitHub API (HIGH)
- **Current**: Raw requests via `gh` CLI + occasional PyGithub
- **Files**: `03-Strategies/AutoBounty_Agent_Design.md` (design doc mentions automation)
- **Use cases**: Issue labeling, PR status checks, repo creation for AgentEscrow agents
- **Composio actions**: `GITHUB_CREATE_ISSUE`, `GITHUB_ADD_LABELS`, `GITHUB_GET_PULL_REQUEST`, `GITHUB_CREATE_RELEASE`
- **Effort to replace**: 3 hours per workflow
- **Priority**: P1 — AAE Brain layer next sprint

---

### 3. Slack Webhooks (HIGH)
- **Current**: POST JSON payloads to incoming webhook URLs
- **Files**: Agent config YAMLs contain webhook URLs; actual sending via `requests.post()` scattered
- **Use cases**: Pipeline status notifications, hackathon alerts, opportunity scanner
- **Composio actions**: `SLACK_POST_MESSAGE`, `SLACK_UPDATE_THREAD`, `SLACK_ADD_REACTION`
- **Effort to replace**: 1–2 hours per webhook endpoint
- **Priority**: P1 — consolidate all Slack comms

---

### 4. Discord Webhooks (MEDIUM)
- **Current**: Webhook JSON formatting (embeds, fields)
- **Files**: Colosseum-Frontier project notes mention Discord alerts
- **Use cases**: Hackathon team notifications, opportunity broadcast
- **Composio actions**: `DISCORD_SEND_MESSAGE` (plain and embed)
- **Effort to replace**: 1 hour
- **Priority**: P2 — hackathon-focused

---

### 5. Notion API (HIGH)
- **Current**: Custom page tree builder for docs
- **Files**: README mentions Notion integration; skills include `NOTION_*` references in archived code
- **Use cases**: Spec handoffs, sprint retrospectives, knowledge base updates
- **Composio actions**: `NOTION_CREATE_PAGE`, `NOTION_UPDATE_BLOCK`, `NOTION_QUERY_DATABASE`
- **Effort to replace**: 4 hours (database permissions mapping)
- **Priority**: P1 — AAE handoff workflow

---

### 6. Etherscan API (MEDIUM)
- **Current**: Direct Etherscan API calls + custom retry/backoff
- **Files**: `03-Strategies/scripts/lp-position-reader.py` (tx polling)
- **Use cases**: Transaction receipt checking, balance lookups, contract reads
- **Composio actions**: `ETHERSCAN_GET_TRANSACTION_RECEIPT`, `ETHERSCAN_GET_BALANCE`, `ETHERSCAN_GET_CONTRACT_ABI`
- **Effort to replace**: 2 hours (replace custom polling with platform tool)
- **Priority**: P2 — simplify but not urgent

---

### 7. Telegram Bot (LOW)
- **Current**: Hermes Gateway (our own codebase)
- **Files**: Gateway platform adapter (`gateway/platforms/telegram.py`)
- **Note**: We own this stack fully; replacing with Composio gives little benefit
- **Composio actions**: `TELEGRAM_SEND_MESSAGE` (evaluate only if abandoning Hermes Gateway)
- **Priority**: P3 — optional evaluation

---

## Exceptions: Keep Custom

| Service | Reason |
|---------|--------|
| **Blockchain RPC (web3.py, Solana)** | Domain-specific, low-level; managed platforms don't expose full RPC flexibility |
| **Birdeye x402** | Custom payment layer; Composio doesn't cover Solana DeFi data feeds |
| **Hermes Gateway** | Core product; would be foolish to outsource |

---

## Replacement Roadmap Matrix

| Phase | Integrations | Target Project | Estimated hrs | Risk |
|-------|--------------|----------------|---------------|------|
| **1** | Google Workspace | All agents | 2 | Very Low |
| **1** | Slack webhooks | Labs ops | 3 | Low |
| **2** | GitHub API | AAE Brain | 4 | Medium (token scope) |
| **2** | Notion API | Handoff docs | 4 | Medium (DB perms) |
| **2** | Discord webhooks | Colosseum-Frontier | 2 | Very Low |
| **3** | Etherscan | DeFi scripts | 2 | Low |
| **3** | (optional) Telegram | Gateway eval | 4 | High (architectural) |

**Total effort**: ~21 developer hours

**Annual maintenance saved**: ~40 hours (token refresh bugs, rate limit tuning, API version updates)

---

## Next Actions

1. ✅ Complete Google auth pilot (COMPOSIO_API_KEY → OAuth link → test send email)
2. 📋 Create `02-Labs/Audits/Composio-Rollout-Plan.md` with sprint breakdown
3. 🔧 Build thin wrapper: `composio_client.py` in `02-Labs/scripts/` for consistent usage pattern
4. 🧪 Replace ONE Slack webhook in production (opportunity scanner daily) as proof
5. 📊 Set up usage logger (invocation count, cost estimate) in `02-Labs/Budgets/Composio-Cost-Tracking.md`
