---
name: vault-first-research
description: Research workflow — full findings to vault, one-liner to memory, skill if repeatable. Use when exploring new protocols, tools, or domains for the project.
---

# Vault-First Research Workflow

Use this when researching any new protocol, tool, ecosystem, or domain for the Gentech/AAE project.

## The Problem

Memory tool has a 2.2K char limit (~8 entries). If you dump research into memory, you'll fill it fast and have to prune constantly. Session context is lost between conversations.

## The Flow

```
Research → Vault (full) → Memory (1-liner pointer) → Skill (if repeatable procedure)
```

## Steps

### 1. Research Phase
- Use **browser tools** for GitHub repos, docs, Twitter threads
- Use **web_search/extract** when available (faster, cheaper)
- If rate-limited on web_search, **fall back to browser_navigate** — GitHub raw content, docs sites, etc.
- Collect: what it is, how it works, ecosystem, integration points, code examples

### 2. Vault Write (Full Details)
Write structured research note to vault:
```
/root/vaults/gentech/01-Projects/{project}/
/root/vaults/gentech/04-Intelligence/   ← for market/threat intel
```

Template:
```markdown
# {Topic} Research — {Project}

**Date:** YYYY-MM-DD
**Source:** URLs

---

## What is it?
## How does it work?
## Ecosystem / Key Players
## Integration Points (for our project)
## Next Steps / Open Questions
```

### 3. Memory Write (One-Liner Pointer)
Save ONLY:
- What it is (1 phrase)
- Where details live (vault path or key URL)
- Why it matters to the project

Format: `{Topic}: {one-liner}. {Key stats}. {Vault path or link}.`

### 4. Skill Write (If Repeatable)
If you discovered a procedure that will be needed again — save it as a skill.
- Code patterns, API integrations, deployment workflows
- NOT one-time research findings

## Memory Discipline

**DO save to memory:**
- User preferences, corrections, stable facts
- Tool quirks, environment details
- Project pointers (where things live)

**DO NOT save to memory:**
- Task progress, TODO lists, session outcomes
- Full research findings (that's what the vault is for)
- Temporary state

**When memory is full:**
- Merge overlapping entries (combine routing + environment into one)
- Remove entries that can be rediscovered via session_search
- Shorten aggressively — every char counts at 95%+

## Session Notes

At natural breakpoints, write a session note:
```
/root/vaults/gentech/00-Sessions/YYYY-MM-DD-topic.md
```

Contents: what we did, what's next, blockers, decisions made.
This is the breadcrumb for `session_search` to find later.

## Research Chaining

When one source naturally leads to another (x402 → Birdeye → GenLayer → Agentic Market), **chain up to 5-6 sources** before stopping to save. This preserves momentum and catches connections you'd miss if you saved after each source.

Rules for chaining:
- If a source mentions a new tool/protocol/project you haven't seen → add to chain
- If you find a live production integration (not just an announcement) → priority chain
- If chain hits 6+ sources or 15+ tool calls → STOP, save everything to vault, then continue
- Always end a chain with a vault write before context gets too large

## Memory Pruning (When Full)

Memory hits 90%+ regularly. Concrete merge patterns:

1. **Combine environment entries** — routing + obsidian + crons → one entry
2. **Shorten hackathon deadlines** — full dates → abbreviated (ARC Apr 25, Kite Apr 26...)
3. **Remove rediscoverable facts** — if session_search can find it, don't store it
4. **Replace long entries with shorter ones** — memory tool has `replace` action for this
5. **Never let memory hit 100%** — you can't add anything and the error blocks your turn

## Pitfalls

- **Search engines often block bots**: Google, DuckDuckGo, Bing, Startpage, and others frequently return CAPTCHAs or empty results. Workaround: skip search engines entirely and go directly to authoritative source websites for the data you need (see "Bypassing Search Engines" below).
- **Vendor pricing behind login/Cloudflare**: Birdeye and similar crypto infra often block bots. If pricing pages are gated, check vault for existing notes, add a TODO, and move on — don't burn 3-4 tool calls on retries.
- **Check vault BEFORE web tools**: Search the vault first (`search_files` in `/root/vaults/gentech`). Chances are research was already captured. The vault answer is free; web scraping costs tokens and often fails.
- **GitHub repos via browser > web_extract**: web_extract gets AUTH_ERROR on GitHub. Use `browser_navigate` to the repo page — snapshot works fine without login.
- **Check for llms.txt**: Some sites (especially x402 ecosystem) expose `/llms.txt` with structured content. Try it before scraping. If it returns content, it's the fastest extraction path.

## Bypassing Search Engines

When search engines block you (CAPTCHA, bot detection, empty results), go directly to the authoritative source instead:

| Data needed | Bypass target | Why it works |
|---|---|---|
| Flight prices | `google.com/travel/flights` + Kiwi.com | See `flight-search` skill for full methodology, URL patterns, and price benchmarks |
| Commodity/fuel prices | `finance.yahoo.com/quote/CL=F` | Direct quote pages load without bot checks |
| Aviation industry context | `simpleflying.com`, `ch-aviation.com` | News sites rarely block browsers |
| Academic papers | Direct arXiv or publisher URLs | No search engine needed |
| GitHub code/docs | Direct repo URL via browser | Works without login for public repos |
| Wikipedia/reference | Direct article URLs | Never blocks browsers |

**Pattern**: Identify 3-5 specific authoritative sources for your data domain BEFORE starting research. Hit them directly rather than wasting iterations on search engines that will block you.

## Start-of-Session Protocol

1. Read last session note from vault
2. Check memory for stable context
3. Use `session_search` if user references past work
4. Don't ask user to repeat themselves
