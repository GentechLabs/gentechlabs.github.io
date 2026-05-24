# Claude Code Game Studios — Hierarchy Analysis for Agent Arena

**Date:** May 24, 2026
**Source:** Donchitos/Claude-Code-Game-Studios (49 agents, 73 skills, 12 hooks)

## The 3-Tier Model

### Tier 1 — Directors (opus model, highest authority)
| Agent | Role | Maps to Gentech |
|-------|------|-----------------|
| creative-director | Vision, pillars, tone, conflict resolution | HQ (Jordan) |
| technical-director | Architecture, tech stack, engineering decisions | Labs |
| producer | Sprint planning, milestones, scope, coordination | HQ (ops) |

### Tier 2 — Department Leads (sonnet model)
| Agent | Role | Maps to Gentech |
|-------|------|-----------------|
| lead-programmer | Code architecture, review, API design | Labs lead |
| game-designer | Mechanics, systems, gameplay | AAE design |
| art-director | Visual direction | Entertainment |
| audio-director | Sound direction | Entertainment |
| narrative-director | Story, dialogue | Content |
| qa-lead | Testing strategy | QA/review |

### Tier 3 — Specialists (individual contributors)
6 programmer specialists, 6 design specialists, 7 support specialists, 10+ engine-specific specialists.

## Key Patterns to Adopt

### 1. Collaboration Protocol (NOT autonomous)
Every task follows: **Question → Options → Decision → Draft → Approval**
- Agents ask before writing
- Present 2-4 options with pros/cons
- User decides
- Draft before finalizing
- Approve before writing

**For AAE:** Agents in the arena should follow this same pattern when interacting with users. Not autonomous — collaborative.

### 2. Gate Verdict System
Each director agent outputs structured verdicts:
```
[GATE-ID]: APPROVE / CONCERNS / REJECT
```
With rationale below. The calling skill reads the first line for the verdict token.

**For AAA:** Agent loadouts could have gate verdicts — when an agent evaluates a trade or strategy, it outputs a structured verdict that other agents can read programmatically.

### 3. Delegation Maps
Every agent has explicit:
- **Delegates to:** (who they can assign work to)
- **Reports to:** (who they answer to)
- **Coordinates with:** (peers they sync with)
- **Must NOT do:** (boundary enforcement)

**For AAE:** Agent loadouts should have explicit capability boundaries. A "trading agent" shouldn't be able to modify smart contracts. A "analytics agent" shouldn't execute trades.

### 4. Model Tiers by Role
- Directors → opus (expensive, high-quality reasoning)
- Department leads → sonnet (balanced)
- Specialists → could be haiku/fast (cheap, focused)

**For AAE:** Agent loadouts could have different model tiers based on role complexity. A "portfolio director" uses a stronger model than a "price ticker agent."

### 5. Memory Scoping
- Directors → `memory: user` (cross-session, persistent)
- Leads → `memory: project` (project-scoped)
- Specialists → no memory (ephemeral)

**For AAA:** Agent reputation/memory should be scoped. High-tier agents retain cross-session memory. Low-tier agents are ephemeral.

## Agent Arena Integration Map

### Agent Loadouts (from Game Studios hierarchy)
| AAE Loadout | Game Studios Equivalent | Tier | Capabilities |
|-------------|------------------------|------|-------------|
| Portfolio Director | creative-director | 1 | Vision, strategy, conflict resolution |
| Trading Lead | lead-programmer | 2 | Trade execution, risk management |
| Analytics Agent | performance-analyst | 3 | Data analysis, pattern recognition |
| Execution Agent | gameplay-programmer | 3 | Order placement, wallet management |
| Research Agent | game-designer | 2 | Market research, opportunity discovery |
| Risk Agent | qa-lead | 2 | Portfolio risk, drawdown limits |

### Skill System → Agent Abilities
73 skills in Game Studios → each maps to an agent ability in AAE:
- `code-review` → `trade-review` (validate before execution)
- `sprint-plan` → `strategy-plan` (plan trading sessions)
- `scope-check` → `risk-check` (validate position sizes)
- `architecture-decision` → `portfolio-allocation` (structural decisions)

### Hook System → Agent Lifecycle Hooks
12 hooks in Game Studios → agent lifecycle events:
- Pre-commit → pre-trade validation
- Post-build → post-trade logging
- Session start → agent activation
- Session end → agent deactivation + summary

## Next Steps
1. Map full 49-agent hierarchy to AAE loadout system
2. Extract hook patterns for agent lifecycle
3. Design skill → ability translation layer
4. Prototype gate verdict system for agent decisions
