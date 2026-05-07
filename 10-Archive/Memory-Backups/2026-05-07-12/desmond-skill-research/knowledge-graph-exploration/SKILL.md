---
name: knowledge-graph-exploration
description: "Turn codebases or knowledge vaults into interactive queryable graphs using Understand-Anything."
intent: Generate and navigate interactive knowledge graphs for onboarding, architecture exploration, and Q&A over structured notes
category: research
primary_tools:
  - understand-anything (CLI)
  - obsidian (vault as source)
secondary_tools: []
critical_dependencies: []
common_patterns:
  - vault-to-graph
  - natural-language-queries
  - architecture-exploration
fragments: []
setup_needed: false
---

# Knowledge Graph Exploration

## Purpose

Convert **any knowledge base** (code, markdown vault, wiki) into an **interactive knowledge graph** that agents (and humans) can explore and query via natural language.

**Core value:**
- Onboard new agents in minutes: "Show me how AgentEscrow works" → interactive graph
- Debug architecture: trace dependencies visually
- Discover connections: "What documents mention Philippines AND AVAX?"
- Share with non-technical stakeholders: clickable exploration vs static README

---

## Tool: Understand-Anything

GitHub: `Lum1104/Understand-Anything`

**What it does:**
- Parses code/markdown → builds graph of entities (files, functions, concepts) and relationships (imports, references, mentions)
- Web UI for interactive exploration
- CLI for automation
- RAG Q&A on top of graph (ask questions in natural language)
- Works with Claude Code, Cursor, Copilot, Gemini CLI

**Install:**
```bash
git clone https://github.com/Lum1104/Understand-Anything
cd Understand-Anything
pip install -r requirements.txt
./install.sh  # installs platform-specific integrations
```

---

## Git Architecture: Gentech

### Source → Graph Pipeline

1. **Input** — Obsidian vault: `/root/vaults/gentech/`
2. **Build** — run `understand-anything` CLI over vault
3. **Output** — interactive web app + SQLite graph DB
4. **Serve** — local dev server or deployed static site

```bash
# Generate graph from vault
python understand_anything.py \
  --source /root/vaults/gentech/ \
  --output ./gentech-graph/ \
  --format both  # web UI + JSON export
```

---

## Graph Content Types

| Node Type | Examples | Edges |
|---|---|---|
| **Project** | AgentEscrow, Travel-Philippines | HAS_COMPONENT, DEPENDS_ON |
| **Agent** | Desmond, DMOB, YoYo | OWNS, COLLABORATES_ON |
| **File** | `escrow-state-machine.md`, `02-Labs/Hackathons/` | REFERENCES, MENTIONS |
| **Concept** | Solana, Anchor, LP, ComfyUI | RELATED_TO, USES |
| **Decision** | "Choose Edge TTS for batch" | DECIDED, ALTERNATIVES |

---

## Query Examples

After graph is built, ask via CLI or web UI:

**Architecture questions:**
- "What are all the files that reference `JobEscrow`?"
- "Show me the dependency tree for the AgentRegistry program"
- "Which agents have worked on both DeFi and travel projects?"

**Knowledge retrieval:**
- "What did we decide about ElevenLabs Voice Agent costs?"
- "Summarize everything about Philippines trip planning"
- "List all open questions about the Colosseum Frontier deadline"

**Onboarding new agent:**
- "Explain the hackathon submission workflow"
- "What are Jordan's travel preferences?"
- "Show me current blocker items"

---

## Integration with Agent Workflows

**Daily brief generation:**
- Each morning, DMOB queries graph for "yesterday's changes" → adds to standup

**Hackathon submission companion:**
- Judges can explore the architecture graph instead of reading a static PDF
- Add QR code in README linking to `gentech-graph/AgentEscrow`

**Vault dead-link detection:**
- Graph identifies orphaned notes (no incoming edges)
- Periodic job: "Archive or reconnect orphaned notes"

---

## Deployment Options

| Option | Cost | Maintenance | Best for |
|---|---|---|---|
| **Local-only** | $0 | Manual rebuilds | Personal exploration |
| **GitHub Pages** | $0 | CI rebuild on commit | Team-wide sharing |
| **Self-hosted VPS** | $5/mo | Automated updates | Private/internal only |
| **Cloud (Railway)** | $5/mo | Zero-ops | Public demo link |

**Recommended:** GitHub Pages — pushes to `gh-pages` branch on vault updates. Free, visible to sponsors.

---

## Automation Hooks

**Vault → Graph CI:**
```yaml
# .github/workflows/graph.yml
on: push
jobs:
  build-graph:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python understand_anything.py --source /data/vault --output ./public
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

**Agent-side:** Before answering a question, agents can query local graph for context first (faster than full vault search).

---

## Pitfalls

| Pitfall | Mitigation |
|---|---|
| **Graph stale** (vault updated but not rebuilt) | Auto-rebuild on vault commit via cron/GitHub Action |
| **Noisy edges** (every file mentions every other file) | Filter edges by relevance threshold; only IMPORT/REFERENCE |
| **Security leak** (private notes exposed in public graph) | Deploy private instance; add access control layer |
| **Brittle queries** ("What's the status on X?" too vague) | Teach agents to query graph with structured prompts |

---

## Templates

- `templates/graph-config.yaml` — configure node/edge types, filters
- `templates/vault-frontmatter-template.md` — standardize POI metadata for rich graph nodes

---

## Related Skills

- `obsidian` — vault is the source material
- `github-pr-workflow` — CI/CD for graph updates
- `multi-agent-tts-conversation` — optionally narrate graph exploration as audio walkthrough

---

*Session discovery (2026-05-03): Understand-Anything identified as tool to turn vault into interactive knowledge graph for onboarding and exploration; combined with vault sync creates living, queryable team brain.*