# Smart Routing Rules — Gentech Single-Agent

**Version**: 2.0
**Updated**: 2026-06-10
**Purpose**: Single-agent operation with topic-based channel routing
**Model**: Gentech handles everything. Telegram groups are topic channels, not agent-specific.

---

## Architecture

```
Gentech (single brain, all tasks)
├── HQ (-1003863540828) — coordination, decisions, blockers
├── Labs (-1003872552815) — code, contracts, technical work
├── Strategies (-1002916759037) — DeFi, finance, research
└── Entertainment (-1003893562036) — content, social, demos
```

**How it works:**
- Jordan drops messages in the right group by topic
- Gentech reads all groups, handles everything directly
- No agent-to-agent delegation (single brain)
- Work outputs go back to the originating group
- Multi-agent mode reserved for future projects/integrations

---

## Topic Routing

### 🏢 HQ (Coordination)
**Handle here:**
- Status updates and check-ins
- Priority decisions
- Blockers and escalations
- Team status requests
- Project approvals
- Emergency items

### 🔧 Labs (Technical)
**Handle here:**
- Smart contracts (Solidity, Rust, Odra)
- Deployment and testing
- Code review and audits
- Technical architecture
- SDK integration
- GitHub repos and CI/CD
- Hackathon builds

### 📊 Strategies (Finance)
**Handle here:**
- Token prices and market analysis
- Portfolio management
- LP positions and yield
- DeFi protocols
- Grant applications
- Competitive research

### 📢 Entertainment (Content)
**Handle here:**
- Social media content
- Demo videos
- Hackathon submissions
- Community engagement
- Brand voice and tone
- Articles and blog posts

---

## Cron Job Routing

**All cron jobs run under Gentech profile.**

| Job Type | Deliver To | Rationale |
|----------|------------|-----------|
| Finance monitoring | Strategies | DeFi data belongs in finance channel |
| Code/deploy status | Labs | Technical work belongs in labs channel |
| Content/social | Entertainment | Content belongs in entertainment channel |
| Status updates | HQ | Coordination belongs in HQ |
| Cross-cutting | HQ | Multi-topic items go to HQ |

---

## Delegation Rules

**When Jordan asks for work:**
1. Assess the topic → route to correct channel
2. Do the work directly (no agent delegation)
3. Report results in the originating channel
4. If work spans multiple topics → report in HQ

**When cron jobs complete:**
1. Deliver results to the designated channel
2. If action needed → tag Jordan in HQ
3. If informational → deliver silently

---

## Escalation

**Escalate to Jordan (HQ) when:**
- Blocked for >2 hours
- Conflicting priorities
- Security incident
- Budget decisions
- Multi-topic coordination needed

---

## Future: Multi-Agent Mode

When scaling to multiple projects or integrations:
- Re-enable YoYo (Strategies), DMOB (Labs), Desmond (Entertainment)
- Each gets own Hermes profile + cron jobs
- Smart routing reverts to agent-tagging mode
- Brain/vault stays shared (Obsidian sync)

**Trigger conditions:**
- 10+ concurrent hackathons
- Revenue-generating products needing dedicated agents
- External team members needing agent access
- Complex multi-chain operations requiring parallel execution
