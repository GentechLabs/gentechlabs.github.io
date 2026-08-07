# Graft → Persistent Repo-Context Graph — Borrowed Primitives

**Source:** [github.com/NanoNets/Graft](https://github.com/NanoNets/Graft)
**Date:** 2026-08-04
**Author:** NanoNets (anirudhkumar-nanonets et al.) · MIT · v0.8.2
**Tags:** #context-graph #codebase-orientation #agent-context #tree-sitter #blast-radius

---

## TL;DR

Graft is an open-source **context layer for coding agents** (Claude Code, Cursor,
Codex, Gemini). It solves the "agent re-onboards the repo from zero every session"
problem: instead of re-grepping, re-opening files, and re-following imports each run,
it builds the codebase map **once** into a `graft/` folder of linked markdown files,
then rides along on every prompt. Verified **it runs** (installed `graft 0.8.2` on the
VPS, clean). We are **not adopting it as a dependency** (NanoNets-owned control plane,
npm install surface, 33-day-old project). We **borrow 3 primitives** into our own
self-orientation design: persistent repo graph, staleness-aware auto-refresh, and
blast-radius-on-edit. *Eat the meat, spit out the bones.*

---

## What Graft Is

832★ / 77 forks / MIT / TypeScript / 244 commits (last 19h — very active). Two-pass build:

1. **Tier-1 tree-sitter** — every function/class/call-edge extracted deterministically.
   **No model, no key, $0.** Output: `graft/.graph/wiring.json` + per-file cards.
2. **LLM pass (optional, `--deep`)** — groups files into readable "nodes" with
   plain-English summaries + crux logic lines, under your own provider key.

### The mechanism it implements (the meat)

| Mechanism | What it does |
|---|---|
| **Persistent repo map** | Builds understanding *once*, writes it to the repo as linked markdown. Agents stop re-exploring from zero every session. |
| **Node = meaning, not address** | Each node has Summary (what), Crux (the few lines carrying logic), Sources (content-hash tracked), Links (`[[wikilinks]]`: `depends_on`, `part_of`, `uses`, `implements`, `produces`), Notes (preserved across regens). Agent reads the answer inline, skips the source-open. |
| **Staleness-aware refresh** | Every query stats the tree (~3ms), rebuilds only if something moved — uncommitted/staged/unsaved edits included. Structural, `$0`, never calls the LLM. `graft check` fails loudly on drift. |
| **Blast-radius on edit** | Post-edit hook prints "who depends on this" inline + auto-resyncs the graph. |
| **Vendor-neutral LLM** | Any OpenAI-compatible endpoint (OpenRouter/Fireworks/Groq/LiteLLM/local) or native Anthropic, your key. |

### The benchmark (162-run controlled, same agent, only context differs)

- Tool calls: **46% fewer** · Tokens: **42% fewer** · Time: **60% less** · Correctness: **equal**
- Real-repo sweep: PocketBase, ollama, Excalidraw — up to 4× cheaper / 3× faster.

---

## Primitive-by-Primitive vs. Our Stack

| # | Graft primitive | We already have | Gap? |
|---|---|---|---|
| 1 | **Persistent repo map** (build once, agent reuses) | `codebase-architecture-analysis`, `code-wiki` (generate docs on demand) | 🔴 **REAL GAP** — we regenerate or cold-start orientation each build; nothing persists the "onboard once" map into context |
| 2 | Node = meaning inline (summary + crux, skip the source-open) | `code-wiki` + `deep-code-audit` (produce docs) | 🟡 We produce docs but don't auto-inject the map into agent prompts |
| 3 | **Staleness-aware refresh** ($0, structural, drift-fails) | `source-of-truth-verification`, `pre-work-audit` (manual/on-demand) | 🔴 **REAL GAP** — our line-number/crux references drift silently; no cheap structural freshness check |
| 4 | **Blast-radius on edit** (who depends on this) | `agent-handoff-enforcement`, `codebase-architecture-analysis` | 🟡 We reason about impact manually; they automate it inline |
| 5 | Typed links (`[[wikilinks]]` graph) | Vault cross-links, `code-wiki` Mermaid diagrams | 🟡 Same idea, different medium |
| 6 | Vendor-neutral LLM summarization | Model routing V3 (flash/k2.7/k3) | ✅ We already have this |

---

## BORROW (the meat)

### 1. 🟢 Persistent repo graph — "onboard once, not every time"
**From Graft:** build the codebase map once, reuse it every session; node = meaning
(summary + crux + sources + links), not just a symbol list.
**Our current flaw:** before most builds we cold-start orientation — grep, open files,
re-follow imports — burning tool calls and tokens to rediscover a codebase we mapped
hours ago. `code-wiki`/`codebase-architecture-analysis` generate docs on demand but
don't persist a graph the agent reads by default.
**The mechanism to adopt:** for each repo we work in repeatedly, generate a **compact
repo-context markdown map** (per-subsystem: what it does + the 3-5 crux lines + who it
depends on / who depends on it) and commit it into the repo (gitignored graph) or the
vault. Load it into context at session start instead of re-exploring.

**Wire into:** `gentech-context-management`, `codebase-architecture-analysis`, `pre-work-audit`.

### 2. 🟢 Staleness-aware refresh — "describe the code as it is right now"
**From Graft:** every query stats the tree (~3ms); if anything moved (uncommitted
edits included) it refreshes before answering; `graft check` fails loudly on drift.
**Our current flaw:** crux line numbers and file references silently drift; our
"source of truth" checks are manual and on-demand, not cheap/structural.
**The mechanism to adopt:** before acting on a repo, run a **cheap structural freshness
check** (file mtimes/content hashes vs the last map's fingerprint). If drifted, re-gen
the crux/references before proceeding. Fail loudly (like `graft check`) rather than
acting on a stale map.

**Wire into:** `source-of-truth-verification`, `pre-work-audit`, `cron-truth-layer`.

### 3. 🟢 Blast-radius on edit — "who depends on this"
**From Graft:** post-edit hook prints the dependents inline + auto-resyncs.
**Our current flaw:** we reason about blast radius manually before multi-file changes;
the impact mapping isn't surfaced automatically at the moment of edit.
**The mechanism to adopt:** when we're about to edit a shared symbol/file, resolve its
callers/imports/dependents (via the graph, or a quick `callers`-style query) and print
the blast radius before the change — same nudge Graft gives.

**Wire into:** `agent-handoff-enforcement`, `codebase-architecture-analysis`, `git-conflict-resolution`.

---

## SPIT OUT (the bones)

- ❌ **Don't adopt Graft as a dependency** — NanoNets-owned control plane, global npm
  install, writes into `~/.codex/`, `.claude/`, `.cursor/` machine-wide. Same lesson
  as LoopX: borrow the mechanism, port the ~200-line core into our own design.
- ❌ **Don't install the CLI on the VPS for ongoing use** — verified it runs (0.8.2),
  but we don't want their hooks/statusline owning our agent wiring.
- ❌ **Skip the LLM `--deep` pass as a requirement** — the tree-sitter structural core
  is the real value and it's `$0`; LLM summaries are nice-to-have under our own key.
- ⚠️ **Vendor-neutral but still their graph format** — if we adopt `[[wikilinks]]`
  node shape, use it as a convention in our own maps, not as their schema dependency.

---

## Verdict

**Borrow the 3 mechanisms** (persistent repo graph, staleness-aware refresh,
blast-radius-on-edit) into our own self-orientation + handoff design. They're small,
philosophically aligned with our "vault is the memory, don't cold-start" stance, and
wire cleanly into skills we already run. **Spit out the tool as a dependency.**

## Action Items
- [ ] Add build-queue item: "Repo-context graph — persistent map + staleness check + blast-radius (borrow from Graft)" (id 35, see build_queue.json)
- [ ] Patch `codebase-architecture-analysis` / `pre-work-audit` with the persistent-repo-map + freshness-check pattern
- [ ] Trial on one repo we work in repeatedly (e.g. gold-402 / iagent-x402) — build a compact repo-context markdown map and load it into the next build's context
