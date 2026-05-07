# Understand-Anything — Knowledge Graph for Vault Navigation

**Date evaluated:** 2026-05-03
**Source:** https://github.com/Lum1104/Understand-Anything
**License:** MIT
**Language:** Python + multi-agent pipeline, web dashboard (likely Next.js/React)

## What It Does

Turns any codebase or knowledge base (including Karpathy-pattern LLM wikis) into an interactive, force-directed knowledge graph. Agents parse files, extract entities/relationships, then present a navigable dashboard where you can:
- Pan/zoom the graph
- Search for nodes
- Ask questions about components
- Follow guided tours (auto-generated architecture walkthroughs)

## Why This is Strategic for GenTech

We have a **10,000+ file vault** that's currently navigable only via manual browsing or full-text search. This tool makes our second brain **explorable** as a visual map.

**Immediate use cases:**
1. **Onboarding new agents/team members** — "Show me everything related to Solana Frontier" → graph lights up dependencies
2. **Debugging complex systems** — visual trace from Brain → Governance → AAE → AgentEscrow
3. **Hackathon demos** — Live interactive tour: "Here's how our architecture fits together"
4. **Knowledge retention** — Vault becomes a living knowledge graph, not just a file dump

**Connects to Karpathy LLM Wiki pattern:** Our vault already uses Karpathy's wiki format (`index.md` with wikilinks). Understand-Anything has built-in support for parsing that exact format.

## Technical Fit

| Aspect | Details |
|--------|---------|
| Input | Our entire vault at `/root/vaults/gentech` (10,027 markdown files) |
| Output | Interactive web dashboard (likely runs on localhost:3000) |
| LLM | Multi-agent pipeline uses LLM to discover implicit relationships |
| GPU need | No — agent inference, not model training; CPU-acceptable |
| Deployment | Install on server, or run locally on Jordan's 32GB workstation |

## Integration Plan

### Phase 1 — Install & Explore (This Week)
- Deploy Understand-Anything on the GenTech server
- Point it at the vault
- Generate initial graph (~10k nodes)
- Save graph snapshot for later diffing

### Phase 2 — Hermes Skill Wrapper
- Write Hermes skill: `/graph show me projects related to <topic>`
- Map natural language → graph query
- Return text summary + optional link to live dashboard

### Phase 3 — Vault Integration
- Add graph node IDs to vault frontmatter (`graph_id:`) for persistent linking
- Agent responses can link to specific vault files via the graph
- Auto-update graph on vault commits (cron)

### Phase 4 — Visual Demo Layer
- Export graph as embeddable widget
- Desmond adds to Gentech Entertainment frontend as "Our Brain" interactive page
- Hackathon judges can explore our knowledge graph live

## Cost Implications

- **Free (MIT)** — no licensing
- **Compute:** LLM calls for relationship extraction. Use our existing provider credits (OpenRouter, StepFun).
- **Hosting:** Runs on same server as Hermes; no extra cost.

## Verdict

🚀 **Core** — This is infrastructure-grade.  
It transforms our vault from static docs into a living, queryable knowledge graph.

## Next Actions

1. **Yoyo** — Install Understand-Anything on server, point at vault, get dashboard running
2. **Gentech** — Create `03-Projects/Integrations/understand-anything/` with setup docs
3. **All** — Explore the live graph, identify missing connections, tag important nodes

## Related Vault Files
- `03-Projects/AAE/kite-passport-technical-deep-dive.md` (Karpathy wiki format in use)
- Vault root (`/root/vaults/gentech/`) — graph source
