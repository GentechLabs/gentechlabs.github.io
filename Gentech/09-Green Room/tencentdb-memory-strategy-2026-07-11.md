# TencentDB Agent Memory × GenTech — Three-Prong Strategy

**Source:** Tencent Cloud open-sourced TencentDB-Agent-Memory (MIT, 8.5k ★, 785 forks)
**Date:** 2026-07-11
**Status:** Strategy decided — 3 angles

---

## The Project

TencentDB Agent Memory is a **Hermes-compatible long-term memory plugin** with a 4-tier progressive pipeline:
- **Symbolic short-term memory** — compresses tool logs into Mermaid symbols (61% token reduction)
- **Layered long-term memory** — L0 raw → L1 atoms → L2 scenarios → L3 personas
- **Zero external API dependencies** — fully local
- **Multi-DB backends:** LiteDB, TiKV, TCVDB
- **BM25 hybrid retrieval**
- **Hermes plugin:** `hermes-plugin/memory/memory_tencentdb`

Repo: https://github.com/TencentCloud/TencentDB-Agent-Memory
npm: `@tencentdb-agent-memory/memory-tencentdb`

---

## Prong 1: Contribute (Audit)

**Why:** We know Hermes — we run on it, we build plugins for it. Their Hermes plugin integration is the path we'd use too. An audit benefits both sides.

**What we can contribute:**
- Audit the Hermes plugin integration (`hermes-plugin/memory/memory_tencentdb/`)
- Check config.yaml wiring, env var passthrough, Docker deployment
- Add Python SDK examples (their codebase is TypeScript-heavy)
- SKILL.md review — they have one, could align with our skills ecosystem
- Submit PRs for documentation gaps or edge cases we find

**Effort:** 2-4 hours initial audit + ongoing PRs

---

## Prong 2: Integrate (Performance)

**Why:** Replace our current Hermes memory backend with TencentDB Agent Memory for 61% fewer tokens, 51% better task success.

**Our current state:** Built-in Hermes memory (simple file-based).

**Integration path:**
1. Install the npm package in our dependency chain
2. Wire the memory plugin into Hermes config.yaml
3. Configure the progressive pipeline tiers
4. Benchmark before/after on our 32 cron job workload

**Effort:** 4-6 hours (needs desktop testing — Forge territory)

---

## Prong 3: Learn (Academy)

**Why:** The progressive pipeline pattern (L0→L3 layering) is directly applicable to the Academy curriculum and Guardrail Plugin.

**What we take from it:**
- Memory layering pattern for our own systems
- Symbolic compression technique (Mermaid canvas → high-density state)
- Heterogeneous storage strategy (DB for facts, Markdown for personas)
- The evaluation methodology (their benchmark results are rigorous)

**Effort:** Reading + notes as we go

---

## Timeline

| Phase | What | Who | When |
|-------|------|-----|------|
| 1 | Clone + audit Hermes plugin integration | Gentech | This week |
| 2 | Submit 1-2 PRs based on audit | Gentech | This week |
| 3 | Integration evaluation (desktop test) | Forge | Next desktop session |
| 4 | Academy curriculum notes | Both | Ongoing |

---

## Ties to Other Projects

- **Guardrail Plugin** — memory auditing layer could reuse their symbolic pipeline
- **Agent Kit** — could distribute this as optional memory plugin
- **Skills Ecosystem** — their SKILL.md integration matches our format
- **Atelier** — ERC-8004 identity could reference memory personalities
