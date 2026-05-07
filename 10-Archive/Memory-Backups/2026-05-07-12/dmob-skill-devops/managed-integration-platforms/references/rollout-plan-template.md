# Phase 2–3 Rollout Plan Template

Use this template after Phase 1 success to structure the full deployment across Gentech projects.

---

## Phase 2: Core Integrations (Sprints 1–2)

### Sprint 1 — GitHub + Slack (Week 1–2)

| Task | Owner | Deliverable | Est. hrs |
|------|-------|-------------|----------|
| Link GitHub org account | DMOB | OAuth connection active | 1 |
| Integrate into AAE Brain layer | AAE Team | Auto-label issues on signal | 3 |
| Replace Labs op scanner Slack webhook | Labs | `opportunity_scanner_daily.py` uses Composio | 2 |
| Centralize Slack channel config | Labs | `02-Labs/Config/slack-channels.yaml` mapping | 1 |
| **Sprint total** | | | **7** |

**Acceptance criteria**:
- [ ] New GitHub issues auto-labeled `agentescrow` + severity
- [ ] Opportunity scanner posts to `#opportunities` via Composio
- [ ] No legacy webhook URLs remain in active code

---

### Sprint 2 — Notion + Calendar (Week 3–4)

| Task | Owner | Deliverable | Est. hrs |
|------|-------|-------------|----------|
| Link Notion workspace | DMOB | DB permissions confirmed | 1 |
| Connect Google Calendar (full) | DMOB | Read/write scopes | 1 |
| Build Notion handoff generator | Labs | Auto-create spec pages from template | 4 |
| Add milestone deadline syncing | AAE | Calendar events from Brain decisions | 3 |
| **Sprint total** | | | **9** |

**Acceptance criteria**:
- [ ] New agent handoff creates Notion page automatically
- [ ] Milestone due dates appear on team Calendar
- [ ] Zero manual doc creation required for new agents

---

## Phase 3: Advanced Orchestration (Sprint 3+)

| Epic | Stories | Owner | Value |
|------|---------|-------|-------|
| **AgentEscrow milestone triggers** | On PR merge → post to Slack + schedule review | Escrow Team | Automated oversight |
| **Cross-tool workflows** | Etherscan tx confirmed → Notion update → Slack ping | Labs | Reduced polling |
| **Audit logging pipeline** | Mirror all Composio calls to vault | Security | Compliance trail |
| **Fallback & resilience** | Queue actions during downtime, replay | Infra | Uptime guarantee |
| **Cost guardrails** | Auto-alert at 80% monthly quota | Finance | Budget control |

---

## Rollout Checklist per Integration

For each new service addition:

- [ ] Service linked in Composio dashboard
- [ ] Scopes verified minimum necessary
- [ ] Wrapper client tested locally (read + write)
- [ ] One production script migrated
- [ ] Audit log entry created
- [ ] Cost tracked for 7 days
- [ ] Old credentials (webhook URLs, API keys) rotated/revoked
- [ ] Documentation updated (this skill + project READMEs)

---

## Cutover Criteria

Before deprecating a custom integration:

1. **Functional parity** — All use cases covered by platform tools
2. **Stability window** — 7 days of zero errors in pilot
3. **Cost validated** — Actual spend < projected budget
4. **Fallback ready** — Old code archived, not deleted (1-week rollback window)
5. **Team trained** — At least 2 agents familiar with new tool calling pattern

---

## Post-Rollout Retrospective Template

```markdown
# Integration Retrospective — <Service>

**Pilot start**: YYYY-MM-DD
**Cutover date**: YYYY-MM-DD
**Invocations (first 30d)**: XXX
**Cost (first 30d)**: $X.XX

### What went well
- Item

### Issues encountered
- Issue → fix applied

### Lessons for next integration
- Lesson
```

Store retro at `02-Labs/Audits/Integrations/<service>-retrospective-YYYY-MM.md`.

---

## Phase 3+ Roadmap

Beyond initial rollout:

1. **Agent personal accounts**: Each agent gets own Composio connection (isolation)
2. **Tool composition macros**: Bundle multi-step actions as single tool call
3. **Platform evaluation**: Benchmark against Merge.dev, OneAPI for specific domains
4. **Custom tool development**: If Composio lacks critical API, build our own tool and submit upstream

---

**Approve rollout**: Labs head signature + date once Phase 2 plan greenlit.
