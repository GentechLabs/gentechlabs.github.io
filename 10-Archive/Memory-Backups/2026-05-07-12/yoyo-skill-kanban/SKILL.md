---
name: kanban
domain: devops
tags:
- class-level
- umbrella
- kanban
status: active
version: 1.0.0
description: Consolidated umbrella for kanban-* skills.
---
## Included Capabilities

### kanban-worker
Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from agent/prompt_builder.py); this skill is what you load when you want deeper detail on specific scenarios.
- **Full reference:** `references/kanban-worker/SKILL.md`
- **Execution scripts:** `scripts/kanban-worker/`

### kanban-orchestrator
Decomposition playbook + specialist-roster conventions + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.
- **Full reference:** `references/kanban-orchestrator/SKILL.md`
- **Execution scripts:** `scripts/kanban-orchestrator/`