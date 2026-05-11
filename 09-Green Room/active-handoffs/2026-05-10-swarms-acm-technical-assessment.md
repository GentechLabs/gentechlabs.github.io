---
date: 2026-05-10
author: DMOB (Labs)
status: COMPLETE
requested_by: Desmond (via Green Room handoff 2026-05-07)
hackathon: Swarms ACM Hackathon
deadline: 2026-05-27
build_window: 2026-05-18 to 2026-05-27 (10 days)
---

# Swarms ACM Hackathon — Technical Scoping Assessment: LP Monitor Tokenization

## 1. Swarms Agent Class API Summary (How Tokenization Works)

### What "Tokenization" Actually Means

**It is NOT blockchain tokenization.** Swarms "tokenization" = publishing an agent's system prompt + metadata to the Swarms Marketplace (swarms.world) as a purchasable listing. The "Frenzy Mode" is the hackathon-specific launch mode that enables this.

### Agent Class API (swarms v12.0.0)

```python
from swarms import Agent

agent = Agent(
    agent_name="DeFi LP Monitor",
    agent_description="Monitors concentrated liquidity LP positions with IL tracking, efficiency scoring, and rebalance alerts",
    system_prompt="<full LP monitoring system prompt>",
    model_name="gpt-4.1",              # via LiteLLM
    tools=[fetch_price, read_pool, calc_il, ...],  # @tool decorated functions
    max_loops="auto",                    # self-terminating reasoning
    tags=["defi", "lp", "monitoring", "avalanche"],
    capabilities=["price-tracking", "impermanent-loss", "position-monitoring"],
    use_cases=[
        {"title": "LP Position Health Monitoring", "description": "Track concentrated liquidity positions..."},
        {"title": "Impermanent Loss Alerts", "description": "Calculate and alert on IL thresholds..."},
    ],
    publish_to_marketplace=True,         # <-- triggers listing on init
    temperature=0.5,
    max_tokens=4096,
)
```

### Marketplace Publish Flow

When `publish_to_marketplace=True`, the Agent calls `handle_publish_to_marketplace()` on init, which hits:

```
POST https://swarms.world/api/add-prompt
Headers: Authorization: Bearer <SWARMS_API_KEY>
Body: {
    name, prompt, description, useCases, tags,
    is_free: false, price_usd: <price>,
    category: "research"  # or "finance"
}
```

**Requirements:**
- `SWARMS_API_KEY` env var (from https://swarms.world/platform/api-keys)
- `use_cases` list with `title` + `description` dicts (mandatory)
- Agent name, description, tags
- System prompt gets published as the "prompt" content

### Key API Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `agent_name` | str | Marketplace listing name |
| `agent_description` | str | Marketplace description |
| `system_prompt` | str | The prompt buyers receive |
| `tools` | List[Callable] | Function-calling tools (wrapped with `@tool`) |
| `model_name` | str | LLM backend (gpt-4.1, claude, etc.) |
| `use_cases` | List[Dict] | Required for marketplace publish |
| `tags` | List[str] | Marketplace tags for discovery |
| `publish_to_marketplace` | bool | Triggers marketplace listing |
| `max_loops` | int/str | Reasoning loop count ("auto" for self-terminate) |
| `temperature` | float | LLM temperature |
| `llm` | Any | Pre-configured LiteLLM instance (optional) |

---

## 2. LP Monitor Compatibility Assessment

### What We're Wrapping

The LP Monitor is a **5-phase workflow agent** built as a Hermes skill:

1. **Phase 1 — Price Fetch**: CoinMarketCap Pro API → token prices
2. **Phase 2 — Pool State Read**: DexScreener API + on-chain RPC → position data, bin decoding
3. **Phase 3 — IL Calculation**: HODL baseline vs current portfolio → impermanent loss %
4. **Phase 4 — Vault Entry**: Formatted markdown entry construction
5. **Phase 5 — Skip Logic + Reporting**: Material change detection → Telegram delivery

### Compatibility Matrix

| Component | Hermes-native | Swarms-compatible | Effort |
|-----------|:---:|:---:|--------|
| System prompt | ✅ | ✅ | Low — port directly |
| CMC price fetch tool | Python/curl | ✅ | Low — wrap as `@tool` |
| DexScreener pool reader | Python/curl | ✅ | Low — wrap as `@tool` |
| On-chain LP decoder | `fetch-lfj-position.py` | ⚠️ | Medium — needs env setup |
| IL calculation | Inline math | ✅ | Low — pure function |
| Vault entry formatting | Template + file I/O | ⚠️ | Medium — needs file system |
| Skip logic | Decision tree | ✅ | Low — pure function |
| Telegram delivery | Hermes bot API | ❌ | High — needs alternative |
| Cron scheduling | Hermes cron jobs | ❌ | N/A — marketplace agent is on-demand |
| D5 Milestone cross-ref | Obsidian vault files | ⚠️ | Medium — needs data context |

### What Needs to Change

**MUST change (hard blockers):**
1. **Remove Telegram delivery** → Output is the agent's response text (buyer reads it)
2. **Remove vault file I/O** → Agent can't write to Hermes vault from marketplace
3. **Remove cron dependency** → Marketplace agents are request/response, not scheduled
4. **Remove Hermes-specific tool calls** (`execute_code`, `fetch_data`, etc.) → Replace with Python `@tool` functions

**SHOULD change (quality improvements):**
5. **Make config wallet-agnostic** → Allow user to pass wallet address + chain as input
6. **Generalize chain support** → Currently Avalanche-only; could support Uniswap V3, etc.
7. **Add self-contained data fetching** → Use `httpx`/`requests` directly instead of Hermes tools
8. **Simplify to 3 core tools** → (a) price fetch, (b) position read, (c) IL calculator

**NICE TO HAVE:**
9. D5 milestone alignment (needs config file or user input)
10. Shape stagnation detection (needs historical state)

### Estimated Wrapper Code Size

- **Tools**: ~3-4 `@tool` decorated functions, ~200-300 lines total
- **Agent setup**: ~50 lines (init + marketplace config)
- **System prompt**: ~500 lines (trimmed from 541-line SKILL.md — remove internal coordination, cron refs, vault mechanics)
- **Config/requirements**: ~30 lines (env vars, API keys)
- **Total new code**: ~300-400 lines Python

---

## 3. Submission Requirements Checklist

Based on ACM Hackathon docs (https://docs.swarms.ai/docs/marketplace/acm-hackathon):

### Mandatory Requirements
- [ ] Create Swarms account at swarms.world
- [ ] Obtain `SWARMS_API_KEY` from https://swarms.world/platform/api-keys
- [ ] Build agent with `publish_to_marketplace=True`
- [ ] Enable **Frenzy Mode** during launch (via swarms.world/launch UI or API)
- [ ] Set `use_cases` (required — list of dicts with title + description)
- [ ] Set `tags` and `capabilities` for marketplace discovery
- [ ] List agent **for sale** (set `is_free=False`, `price_usd=<price>`)
- [ ] Publish before **May 27, 2026** 23:59 UTC

### Quality Criteria (for prize ranking)
- [ ] Clear real-world utility (✅ — LP monitoring solves real DeFi problem)
- [ ] Well-described listing (✅ — detailed description + use cases)
- [ ] Easy to evaluate (⚠️ — needs demo/runbook)
- [ ] Finance and market analysis category (✅ — named category match)
- [ ] Marketplace adoption potential (⚠️ — niche but defensible)

### Recommended Submission Assets
- [ ] Agent code (Python, pip-installable or standalone)
- [ ] Marketplace listing copy (name, description, use cases, pricing)
- [ ] README with setup instructions
- [ ] Demo output sample (show what the agent produces)
- [ ] Short demo video or GIF (optional but strong for ranking)

### Pricing Strategy
- **Recommended**: $9.99 one-time or $4.99/month
- **Rationale**: Finance category agents priced $5-$20; ours has unique on-chain data fetching
- **Alternative**: Free listing to maximize adoption for ranking, monetize later

---

## 4. Build Timeline Estimate (May 18–27, 10 Days)

### Phase 1: Foundation (Days 1–2, May 18–19)
| Task | Hours | Owner |
|------|-------|-------|
| Set up swarms.world account + API key | 0.5h | DMOB |
| Create GitHub repo for submission | 1h | DMOB |
| `pip install swarms` + test basic Agent init | 1h | DMOB |
| Port LP Monitor system prompt (trim to ~500 lines) | 3h | DMOB |
| Test basic prompt-only agent (no tools) | 1h | DMOB |

### Phase 2: Tool Wrapping (Days 3–5, May 20–22)
| Task | Hours | Owner |
|------|-------|-------|
| Wrap CMC price fetch as `@tool` | 2h | DMOB |
| Wrap DexScreener pool reader as `@tool` | 3h | DMOB |
| Wrap on-chain LP decoder as `@tool` | 4h | DMOB |
| Wrap IL calculator as `@tool` | 1h | DMOB |
| Test tools individually with Agent | 2h | DMOB |
| Handle API key management (env vars) | 1h | DMOB |

### Phase 3: Integration & Testing (Days 6–7, May 23–24)
| Task | Hours | Owner |
|------|-------|-------|
| Full agent integration test (prompt + all tools) | 4h | DMOB |
| End-to-end LP monitoring run | 3h | DMOB |
| Output formatting & edge cases | 2h | DMOB |
| Error handling (API failures, missing data) | 2h | DMOB |

### Phase 4: Marketplace Launch (Days 8–9, May 25–26)
| Task | Hours | Owner |
|------|-------|-------|
| Write marketplace listing copy | 2h | DMOB/Desmond |
| Create README + setup docs | 2h | DMOB |
| Generate demo output sample | 1h | DMOB |
| Test Frenzy Mode launch flow | 1h | DMOB |
| Publish to marketplace with Frenzy Mode | 1h | DMOB |

### Phase 5: Polish & Submit (Day 10, May 27)
| Task | Hours | Owner |
|------|-------|-------|
| Final QA pass | 2h | DMOB |
| Record demo video/GIF (optional) | 2h | DMOB |
| Confirm listing is live + for sale | 0.5h | DMOB |
| Post to Swarms Discord for visibility | 0.5h | DMOB |

**Total estimated effort**: ~40 hours across 10 days
**Realistic daily capacity**: 4-6 hours (with Kite AI wind-down)
**Buffer**: 2 days for unexpected issues

### Critical Path Dependencies
1. SWARMS_API_KEY must be obtained Day 1 (blocking everything)
2. On-chain LP decoder must work outside Hermes environment
3. Frenzy Mode launch UI must be accessible and functional

---

## 5. Risk Flags and Blockers

### 🔴 HIGH RISK

| Risk | Impact | Mitigation |
|------|--------|------------|
| **On-chain LP decoder relies on Hermes infra** (`execute_code` tool, specific script paths) | Can't run standalone | Rewrite as self-contained Python module with `web3`/`eth_abi` |
| **No SWARMS_API_KEY yet** | Can't test marketplace publish | Get key immediately — Day 0 blocker |
| **Frenzy Mode undocumented** | Unknown launch flow requirements | Test early (Day 2) with a simple prompt-only agent |
| **Marketplace agents may not support external API calls** | Tools that call CMC/DexScreener may be sandboxed | Test tool execution environment before building |

### 🟡 MEDIUM RISK

| Risk | Impact | Mitigation |
|------|--------|------------|
| **CMC Pro API key exposure** | Can't embed in published agent | Agent reads from env var; document setup in README |
| **Avalanche RPC rate limits** | Slow/blocked on-chain reads | Use paid RPC endpoint or cached results |
| **Niche audience** | Low marketplace adoption for LP monitoring | Position as "DeFi Portfolio Analytics" (broader) |
| **Competing submissions** | Finance category is popular | Differentiate on on-chain data + IL tracking uniqueness |

### 🟢 LOW RISK

| Risk | Impact | Mitigation |
|------|--------|------------|
| Swarms SDK API changes | Minor refactor | Pin `swarms==12.0.0` in requirements |
| Marketplace pricing unknown | Can't set optimal price | Start free, adjust after launch |
| LiteLLM model routing | LLM costs for demo | Use cheapest model for testing |

### Blockers Requiring Immediate Action

1. **[BLOCKER]** Obtain SWARMS_API_KEY → https://swarms.world/platform/api-keys
2. **[BLOCKER]** Verify Frenzy Mode launch flow works → test with minimal agent
3. **[BLOCKER]** Confirm tools can make HTTP requests in Swarms execution environment
4. **[REVIEW]** Jordan to approve pricing strategy (free vs paid)
5. **[REVIEW]** GitHub token expired — need new token for repo creation

---

## 6. Recommended Approach: Wrap Existing (NOT Rebuild)

### Verdict: **WRAP** with targeted modifications

The LP Monitor is a strong submission candidate. It solves a real DeFi problem, fits the "Finance and market Analysis" category, and has proven functionality. **Rebuilding from scratch would waste the existing 541-line skill and 460+ lines of reference docs.**

### What to Wrap (Keep As-Is)
- ✅ Core system prompt (trimmed from SKILL.md — remove Hermes coordination, cron refs, vault mechanics)
- ✅ IL calculation logic (pure math, portable)
- ✅ Skip logic decision tree (pure logic, portable)
- ✅ Fee estimation methodology (formula-based)
- ✅ Vault entry formatting template (output format)
- ✅ Rebalance trigger rules (decision matrix)

### What to Rebuild (Targeted Changes)
- 🔄 **3-4 `@tool` functions** replacing Hermes tool calls:
  - `fetch_token_prices(symbols)` → CMC API via `httpx`
  - `read_pool_state(pool_address)` → DexScreener + on-chain via `httpx`/`web3`
  - `decode_lp_position(wallet, pool)` → on-chain bin scanner (rewrite `fetch-lfj-position.py`)
  - `calculate_il(original, current)` → pure Python math
- 🔄 **Agent init script** (~50 lines) with marketplace config
- 🔄 **README + demo assets** (~100 lines)
- 🔄 **Config management** (env vars for API keys, wallet address, pool address)

### What to Remove
- ❌ Telegram delivery (marketplace agent returns text response)
- ❌ Obsidian vault file I/O (no Hermes vault access)
- ❌ Cron scheduling (marketplace agents are on-demand)
- ❌ D5 milestone cross-referencing (needs Obsidian vault context)
- ❌ Skip logic persistence (needs file state between runs)
- ❌ Shape stagnation detection (needs historical state)
- ❌ Hermes-specific tool calls (`execute_code`, `fetch_data`, etc.)

### Why This Works

1. **Speed**: 300-400 lines of new code vs 1000+ for rebuild
2. **Quality**: Existing prompt is battle-tested over weeks of LP monitoring
3. **Differentiation**: On-chain data fetching is rare in marketplace agents
4. **Category fit**: "Finance and market analysis" — exact match
5. **Portfolio value**: Published agent can also be used internally

### Minimum Viable Submission (MVP)

**If time is tight, ship this:**
1. Trimmed system prompt (~500 lines)
2. 2 tools: `fetch_token_prices()` + `read_pool_state()`
3. IL calculator inline in prompt
4. Basic marketplace listing

**Full submission (stretch goal):**
- All 4 tools + error handling + demo output + video

---

## Summary for Jordan

**Recommendation: Green light the LP Monitor submission.**

The technical assessment confirms this is a **low-risk, high-value** hackathon play:

- **Effort**: ~40 hours across 10 days (realistic with 4-6h/day capacity)
- **Approach**: Wrap existing skill, not rebuild. 300-400 lines of new code.
- **Timeline**: Feasible in the May 18–27 window if we start immediately after Kite AI wraps.
- **Prize potential**: $3,000–$7,500 (top 3) or random $1K+ from $15K pool
- **Strategic value**: Marketplace presence, Solana + $SWARMS rewards, cross-promotion

**Immediate action items:**
1. Obtain SWARMS_API_KEY (Day 0 — blocking)
2. Test Frenzy Mode with minimal agent (Day 2 — validate flow)
3. Begin tool wrapping (Day 3 — core build work)
4. Finalize pricing strategy (Day 5 — free vs paid decision)

**Files referenced:**
- `02-Labs/Hackathons/swarms-acm-hackathon.md` — Desmond's scoping brief
- `09-Green Room/active-handoffs/2026-05-07-swarms-acm-dmob-scope.md` — Handoff request
- `03-Strategies/Swarms-Competitive-Analysis.md` — Competitive intel (YoYo)
- `09-Green Room/active-handoffs/2026-05-06-swarms-hackathon-analysis.md` — Initial analysis
- LP Monitor SKILL.md — 541-line monitoring skill (reference archive)

---

**Assessment complete. Ready to hand off to build phase when Kite AI wraps.**
