# Self-Evolution — Installed 2026-04-16

Evolutionary self-improvement for Hermes Agent using DSPy + GEPA (Genetic-Pareto Prompt Evolution).

## What It Does
Automatically evolves and optimizes Hermes Agent's skills, tool descriptions, system prompts, and code through reflective evolutionary search. Reads execution traces to understand WHY things fail, then proposes targeted improvements.

## Quick Start
```bash
# Evolve a skill (synthetic eval data)
python -m evolution.skills.evolve_skill \
    --skill <skill-name> \
    --iterations 10 \
    --eval-source synthetic

# Or use real session history
python -m evolution.skills.evolve_skill \
    --skill <skill-name> \
    --iterations 10 \
    --eval-source sessiondb

# Dry run to validate setup
python -m evolution.skills.evolve_skill \
    --skill <skill-name> \
    --dry-run
```

## Cost
~$2-10 per optimization run (API calls, no GPU needed)

## Implementation Status
| Phase | Target | Status |
|-------|--------|--------|
| Phase 1 | Skill files (SKILL.md) | ✅ Implemented |
| Phase 2 | Tool descriptions | 🔲 Planned |
| Phase 3 | System prompt sections | 🔲 Planned |
| Phase 4 | Tool implementation code | 🔲 Planned |
| Phase 5 | Continuous improvement loop | 🔲 Planned |

## Guardrails
1. Full test suite must pass 100%
2. Skills ≤15KB, tool descriptions ≤500 chars
3. No mid-conversation changes
4. Must not drift from original purpose
5. All changes go through human review (PR-based)

## Notes
- Source: `/tmp/hermes-agent-self-evolution/`
- Requires `HERMES_AGENT_REPO` env var to point at hermes-agent repo
- MIT licensed
