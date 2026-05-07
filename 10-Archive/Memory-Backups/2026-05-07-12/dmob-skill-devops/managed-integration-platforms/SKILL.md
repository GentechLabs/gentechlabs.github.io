---
name: managed-integration-platforms
description: "Adopting and operating managed integration platforms (Composio, Merge, etc.) for AI agents — tool coverage, OAuth handling, sandboxed execution, and systematic rollout across agent ecosystems."
version: 0.1.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  hermes:
    tags: [integrations, composio, oauth, agent-tooling, devops]
    related_skills: [google-workspace, hermes-agent, autonomous-ai-agents]
---

# Managed Integration Platforms for Agent Tooling

**Scope:** Evaluating, adopting, and operating third-party integration platforms (Composio, Merge, OneAPI, etc.) to replace custom-built API wrappers and OAuth flows in agent systems.

**Why this class matters:**
- Every external API integration consumes ~8–16 hours (auth, error handling, rate limits, testing)
- Managed platforms provide 1000+ pre-built tools with unified auth and sandboxing
- Reduces maintenance debt and accelerates agent capabilities

---

## Trigger Conditions

When you observe any of these signals, activate this skill:

1. **Auth debt accumulating**: Multiple OAuth implementations (Google, GitHub, Slack, Notion) scattered across codebase
2. **Tool coverage gaps**: Agents need external APIs that would take >4 hours to build custom
3. **Security review burden**: Each external call requires individual threat modeling and audit
4. **Agent capability ceiling**: Agents repeatedly fail due to missing tool integrations
5. **Maintenance overload**: API changes, token refresh bugs, rate limit handling consume significant time

---

## Decision Framework: Build vs Compose

| Factor | Build Custom | Use Managed Platform |
|--------|--------------|---------------------|
| **Time to ship** | 8–40 hrs/integration | 0–2 hrs (1-line tool call) |
| **Auth complexity** | OAuth flows, token refresh, key rotation | Fully managed by platform |
| **Security surface** | Each integration is an attack surface | Single platform security boundary |
| **Rate limiting** | Custom backoff/retry logic per API | Platform handles uniformly |
| **Maintenance** | Ongoing (API version tracking) | Platform maintains |
| **Sandboxing** | Must implement yourself | Built-in (often required) |
| **Vendor lock-in** | Low (your wrapper code) | Medium (platform-dependent) |
| **Cost** | Developer time only | Subscription ($29–$299/mo typical) |

**Rule of thumb**: If you need >3 external API tools and any one would take >6 hours to build properly → **Compose**.

---

## Gentech Integration Audit Process

**Step 1: Vault-wide scan** (non-destructive, read-only)
```bash
cd /root/vaults/gentech
rg -i "api_key|client_secret|oauth|webhook" --type py --type md -l | head -100
```

**Step 2: Categorize findings**
- **Active integrations** (02-Labs/, 02-AAE/, 03-Strategies/, 06-Security/)
- **Archived** (10-Archive/ — ignore unless resurrecting old projects)
- **Infrastructure** (Hermes gateway, custom bot servers — deprioritize unless replacing)

**Step 3: Map to platform tool catalog**
- Search platform docs for "GitHub", "Slack", "Discord", "Notion", "Google", etc.
- Mark each Gentech integration as: ✅ Covered / ⚠️ Partial / ❌ Missing

**Step 4: Estimate replacement effort**
| Integration | Current custom code (LOC) | Auth complexity | Replacement impact |
|-------------|-------------------------|-----------------|-------------------|
| Google Workspace | ~400 (OAuth skill) | High (multi-scope refresh) | **CRITICAL** |
| GitHub API | ~200 (token mgmt) | Medium (OAuth app) | HIGH |
| Slack webhooks | ~50 (simple POST) | Low (webhook URL) | MEDIUM |
| Notion API | ~150 (page tree) | Medium (DB-permissions) | HIGH |
| Etherscan API | ~100 (RPC polling) | Low (API key) | LOW |

---

## Gentech-Specific Integration Map

**Current active integrations (excluding archives):**

| Service | Use Case | Current Implementation | Composio Equivalent | Priority |
|---------|----------|----------------------|---------------------|----------|
| **Google Workspace** | Email, Calendar, Drive, Sheets | Custom OAuth skill (`google-workspace/`) | GMAIL_*, CALENDAR_*, DRIVE_*, SHEETS_* | **CRITICAL** |
| **GitHub** | repo mgmt, PRs, issues | Manual API calls via `gh` + raw requests | GITHUB_* (full suite) | **HIGH** |
| **Slack** | notifications, alerts | Webhook JSON formatting | SLACK_POST_MESSAGE, SLACK_UPDATE_THREAD | **HIGH** |
| **Discord** | hackathon comms | Webhooks + embed building | DISCORD_SEND_MESSAGE | **MEDIUM** |
| **Notion** | specs, handoff docs | Custom page tree builder | NOTION_* (pages, blocks, databases) | **HIGH** |
| **Etherscan** | tx receipts, balances | Custom RPC polling with retry | ETHERSCAN_* (tx, balance, contract) | **MEDIUM** |
| **Birdeye (Solana)** | token prices, trends | Custom x402 client | Not in Composio (blockchain-native) | **KEEP CUSTOM** |
| **Telegram** | Agent gateway | Hermes own gateway | TELEGRAM_SEND_MESSAGE (optional eval) | **LOW** |

**Blockchain/RPC exceptions** (DO NOT replace):
- web3.py / web3.js calls
- Solana RPC (Birdeye, Helium)
- Custom DeFi position readers
→ These are domain-specific, not generic API integrations.

---

## Phase 1: Pilot (Week 1)

1. **Environment setup**
   - Get Composio API key
   - Install SDK: `pip install composio-core`
   - Store key in `~/.hermes/.env`: `COMPOSIO_API_KEY=xxx`
   - Verify: `python -c "from composio import Composio; print(Composio().tools.list())"` 

2. **Link ONE account (Google)**
   ```bash
   python -c "from composio import Composio; Composio().integrations.link('gmail')"
   ```
   - Grant Gmail + Calendar scopes
   - Confirm connection status via dashboard

3. **Test one action**
   ```python
   from composio import Composio
   client = Composio()
   result = client.tools.exec(action="GMAIL_SEARCH_EMAILS", params={"query": "is:unread", "max_results": 5})
   print(result)
   ```

4. **Document findings** in `02-Labs/Audits/Composio-Pilot-Phase1.md`

---

## Phase 2: Core Integrations (Sprint 1–2)

| Integration | Target Project | Action |
|-------------|----------------|--------|
| GitHub API | AAE Brain layer | Replace custom issue/PR labeling → `GITHUB_ADD_LABELS` |
| Slack | Labs notifications | Replace webhook boilerplate in scripts → `SLACK_POST_MESSAGE` |
| Notion | Handoff docs | Auto-generate spec pages → `NOTION_CREATE_PAGE` |
| Google Suite | All agents | Deprecate `google-workspace/` skill, switch to Composio |

**Success criteria**: At least 3 active projects using Composio tools, zero custom OAuth code for those services.

---

## Phase 3: Advanced Rollout (Sprint 3+)

1. **AgentEscrow integration** — all milestone triggers and verification via Composio tools
2. **Cross-tool orchestration** — compose multi-step actions (e.g., "when PR merged → post to Slack → schedule Calendar review")
3. **Audit logging** — log every Composio action to `02-Labs/Audits/Composio-Usage-YYYY.md` for compliance and cost tracking

---

## Cost Tracking Template

```markdown
## Composio Usage Report — Week of YYYY-MM-DD

| Tool | Invocations | Estimated cost | Use case |
|------|-------------|----------------|----------|
| GMAIL_SEARCH_EMAILS | 47 | $0.00 (free tier) | Agent daily triage |
| GITHUB_CREATE_ISSUE | 12 | $0.02 | Auto-bug creation |
| SLACK_POST_MESSAGE | 89 | $0.04 | Pipeline notifications |
| **Total** | **148** | **$0.06** | — |
```

---

## Pitfalls & gotchas

1. **Token scope mismatch** — When linking accounts, select only the scopes needed. Over-scoping triggers Google security blocks.
2. **Rate limits still apply** — Composio enforces per-tool rate limits; implement exponential backoff in your agent logic even though platform handles基础重试.
3. **Sandboxed execution ≠ no side effects** — `GMAIL_SEND_EMAIL` actually sends. Always confirm with user before destructive actions.
4. **Platform dependency risk** — Keep a fallback plan: if Composio downtime, agents should gracefully degrade (cache credentials, queue actions).
5. **Audit trail** — Without logging, you lose visibility into what agents are doing. Enable platform audit logs and mirror to your own vault.

---

## Related Skills

- [`google-workspace`](skill://google-workspace) — Our custom OAuth implementation (to be deprecated)
- [`hermes-agent`](skill://hermes-agent) — Gateway and tool management
- [`autonomous-ai-agents`](skill://autonomous-ai-agents) — Multi-agent orchestration patterns

---

## References

<references>
- `references/gentech-integration-audit-2026-05-03.md` — Full vault scan results and integration map
- `references/composio-quick-start.md` — SDK setup, auth flow, first tool call
- `references/cost-benefit-template.md` — Spreadsheet for tracking ROI
- `references/phase1-implementation-checklist.md` — Step-by-step pilot execution
</references>
