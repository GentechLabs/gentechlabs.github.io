---
name: gentech
domain: devops
tags:
- gentech
- class-level
- umbrella
status: active
version: 1.0.0
description: Consolidated umbrella for gentech-* skills.
---
## Included Capabilities

### Orchestrator Pattern (Runtime Behavior)
Gentech operates as the lead orchestrator in ALL Telegram groups. Specialists (YoYo, DMOB, Desmond) are on-demand — they only activate when routed to by Gentech.
- **Full reference:** `multi-agent-telegram-org` skill (sections: Smart Routing Protocol, Context Injection, Token Optimization Tracking)
- **Vault files:** `00-HQ/smart-routing-rules.md`, `03-Strategies/agent-memory/*.md`
- **Tracking:** `references/token-optimization-tracker.md`

### gentech-agent-reactivation
- **Full reference:** `references/gentech-agent-reactivation/SKILL.md`
- **Execution scripts:** `scripts/gentech-agent-reactivation/`

### gentech-agent-health-diagnosis
Systematic diagnostic workflow to determine why Hermes agent gateways are down — distinguishes between stale locks, auth failures, revoked tokens, and config issues before attempting recovery
- **Full reference:** `references/gentech-agent-health-diagnosis/SKILL.md`
- **Execution scripts:** `scripts/gentech-agent-health-diagnosis/`

### pre-work-audit
Before starting ANY work, audit existing state — check GitHub repo (latest commits, branches) AND Obsidian vault (prior work, notes, handoffs). Never assume fresh start. Includes no-idle workflow directive.
- **Full reference:** `skills/gentech/pre-work-audit/SKILL.md`