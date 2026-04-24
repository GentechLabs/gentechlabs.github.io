# Content Pipeline — "We Are the Content"

Created: 2026-04-18
Owner: Desmond (Entertainment)
Status: Active

---

## Mission

Turn daily agent conversations into digestible X/Twitter content. We don't create content — we mine it from real work.

---

## 3-Post Daily Framework

### Post 1 — Morning: "What We're Working On"
> Today's focus: [insert actual task]
> Why it matters: [1-2 sentences on the "so what"]
> The honest part: [what's hard, what's unknown]

### Post 2 — Midday: "What We Learned"
> Just discovered [insight from research/development/discussion]
> Most people think [common assumption]
> The data/code/reality says [what you actually found]
> This changes [what we're doing differently now]

### Post 3 — Evening: "Where We're Headed"
> Update on [current sprint/hackathon/product]
> Shipped: [what got done]
> Blocked: [what didn't]
> Tomorrow: [what's next]

---

## Source Material

Mine content from these locations daily:

| Source | What to Extract | Path |
|--------|----------------|------|
| Mess Hall | Agent discussions, decisions, debates | `11-Mess Hall/Chat — {date}.md` |
| Strategies | Research findings, data analysis, BTC repo insights | `03-Strategies/` |
| Labs | Code commits, technical breakthroughs | `02-Labs/` |
| Agent States | What each agent was working on | `08-Daily/agent-states/` |
| HQ Broadcasts | Key decisions, announcements | `01-Agency(HQ)/` |

---

## Workflow

1. **Daily cron triggers** (10AM, 3PM, 8PM EDT)
2. **Read last 24h** of vault activity — Mess Hall chat, agent states, new research
3. **Distill into 3 posts** using the framework above
4. **Save drafts** → `04-Entertainment/x-drafts/{YYYY-MM-DD}/`
5. **Flag for Jordan's review** — send summary to HQ
6. **Once X API connected** — auto-post approved drafts

---

## Content Series (In Progress)

### Series 1: BTC Belief → Digital Gold (Data-driven)
- 6-tweet thread from BTC-Trading-Since-2020 repo
- Status: Drafted, saved in `03-Strategies/x-content-drafts.md`

### Series 2: Hackathon Sprint (Build in public)
- 6 posts covering ARC → Kite AI → Dev3pack → Solana Frontier
- Status: Drafted, saved in `03-Strategies/x-content-drafts.md`

### Series 3: The Agent Team (Behind the scenes)
- 4 posts on how GenTech agents work together
- Status: Drafted, saved in `03-Strategies/x-content-drafts.md`

### Series 4: Bin-AMM — Shape Your Liquidity (New Monetization Layer)
- **Hook**: "Trader Joe's LFJ lets you customize liquidity per price bin. We're bringing that to our agent economy."
- **Angle**: Bin-level liquidity density vs traditional AMM's locked 50/50 ratio. How $GENTECH LPs can design their own exposure curves.
- **Content pieces**:
  - Medium article: "Why Bin-AMMs Beat Concentrated Liquidity for Agents"
  - X thread: "Uniswap v2 → v3 → Curve → LFJ → GENTECH bin-AMM. The evolution of liquidity."
  - Telegram deep-dive: How agent-managed LP positions work (Layer 8 economics)
- **Source**: `/root/repos/aae-contracts/docs/bin-amm-scoping.md` (Dmob's full technical scoping)
- **Status**: Queued — awaiting Dmob's fork to begin, then build-in-public content
- **Sequencing**: Big-picture first ("show the house, then the wiring") — intro post before technical deep-dives

---

## Content Pillars

1. **Data** — BTC research, on-chain analysis, market structure
2. **Build** — Hackathon progress, shipping updates, code
3. **Team** — Agent capabilities, how AI agents collaborate
4. **Pain** — Real DeFi problems → real solutions

---

## Jordan's Philosophy

> "We are the content. Everyone should talk to Desmond about making our everyday discussions into digestible content."

Not corporate marketing. Not polished PR. Real builder energy — the grind, the learning, the progress, the setbacks. That's what performs.

---

## X API Setup (Pending)

- x-cli installed ✓
- Credentials needed: X_API_KEY, X_API_SECRET, X_BEARER_TOKEN, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
- Once connected: Desmond drafts → Jordan approves → YoYo posts
