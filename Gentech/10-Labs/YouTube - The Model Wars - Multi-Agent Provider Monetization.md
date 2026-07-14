# YouTube Video — "The Model Wars: How Pitting LLMs Against Each Other Creates Better AI Agents"

**Channel:** Gentech Labs
**Target Length:** 10-12 minutes
**Format:** Video essay + live demo
**Status:** Draft — v1

---

## Hook / Cold Open Script

> *(Black screen. Terminal cursor blinking.)*

> **Narrator (Jordan):** "What if the best AI agent doesn't use Claude... or GPT... or Qwen?"

> *(Quick cuts: Three terminal windows side by side, each running the same prompt through a different model. Outputs appear — each distinct.)*

> "What if the best agent uses **all three** — at the same time — each doing what it's actually good at?"

> *(Title card drops: **THE MODEL WARS — How We Built an AI Agent That Picks Its Own Brains**)*

> "We're running a experiment. One agent. Four roles. A different LLM for every single one. And the results... nobody saw this coming."

---

## Video Structure & Segments

### Segment 1: The Problem With "One Model to Rule Them All" (0:00 - 1:45)

**Talking Points:**
- Everyone talks about "the best LLM" — GPT vs Claude vs Qwen — like it's a single answer
- But no single model is best at *everything* — just like no single employee is best at every job
- Show a concrete example: same prompt, 3 models, 3 completely different outputs for the same task (on-chain analysis)
- GPT-4o: fast, structured, misses nuance
- Claude: deep reasoning, slow, overthinks simple tasks
- Qwen: surprising on specific tasks, cheap, but inconsistent
- The real question isn't "which model is best?" — it's "**which model for which job?**"

**Visual Suggestions:**
- Split-screen: three model outputs side-by-side for a DeFi analysis prompt
- Animated chart showing model strengths mapped to tasks (radar chart style)
- On-screen text: "We've been asking the wrong question."

---

### Segment 2: The Layer Breakdown — Character Builder for Agents (1:45 - 4:00)

**Talking Points:**
- Introduce the AAE (Autonomous Agent Engine) concept
- Frame it like an RPG character builder — you're not picking one hero, you're building a party
- Walk through the 4 core layers:

| Layer | What It Does | Model Pick |
|-------|-------------|------------|
| **Perception** | Reads on-chain data, interprets events | Fast, cheap model (Qwen, smaller GPT) |
| **Decision** | Makes trading/allocation calls | Deep reasoning (Claude, o-series) |
| **Execution** | Constructs transactions, handles edge cases | Structured output specialist |
| **Social** | Generates posts, community engagement | Creative/voice model (Claude, GPT) |

- This is where the "model wars" actually live — pitting providers against each other for *specific roles*
- "You wouldn't use a sniper rifle to cook dinner. Why use a reasoning model to parse block data?"

**Visual Suggestions:**
- RPG character screen aesthetic: "Build Your Agent" with slots for each layer
- Animated flow diagram showing data moving through the layers
- Each layer lights up with the chosen model's branding (Anthropic orange, OpenAI green, Alibaba blue)
- On-screen: "Perception → Decision → Execution → Social"

**Key Line:** *"Most people think building an agent means picking one model. We think it means building a team."*

---

### Segment 3: The Gentech Agent Team — Real Examples (4:00 - 6:00)

**Talking Points:**
- Introduce the actual Gentech team as proof this works:

| Agent | Role | Brain (Model) | Personality |
|-------|------|---------------|-------------|
| **Gentech** | Orchestrator | GPT-4o | Architect — sees the whole picture, delegates well |
| **YoYo** | Research/Strategy | Claude Opus | Analytical — finds patterns, asks second-order questions |
| **Dmob** | Code/Security | Qwen / DeepSeek | Paranoid auditor — catches what others miss |
| **Desmond** | Content/Social | Claude | Writer — voice, narrative, reads the room |

- Show a real workflow: YoYo spots a DeFi opportunity → Gentech evaluates → Dmob checks the contract → Desmond writes the thread
- Each agent's "personality" comes partly from the model's inherent tendencies — Claude *is* more cautious, GPT *is* more structured, Qwen *is* more direct
- This isn't just about capability — it's about **cognitive diversity**

**Visual Suggestions:**
- Team roster graphic with agent avatars, roles, and brain models
- Live screen recording or animated simulation of the workflow
- Side-by-side: "What GPT says" vs "What Claude says" vs "What Qwen says" on the same contract analysis

---

### Segment 4: The Monetization Angle — Pay-Per-Launch & User-Selectable Combos (6:00 - 8:00)

**Talking Points:**
- Here's where it gets interesting for users: **you get to build your own stack**
- Three monetization models:

1. **Pay-Per-Launch** — Spin up any model for any agent role. Pay only when you use it. Cheap model for perception? Pennies. Claude Opus for the decision layer? Costs more, but you choose.
2. **User-Selectable Combos** — Build and save your own configurations. "My DeFi stack: Qwen for perception, Claude for decisions, GPT for social." Share it. Fork someone else's.
3. **Premium Tier** — Free uses default (optimized) models. Premium unlocks the full provider marketplace + better models + priority routing.

- OpenRouter integration = 100+ models available instantly
- Cost optimization story: "Run your perception layer on a $0.001/model call and your decision layer on a $0.05/call. Total: still cheaper than running everything through GPT-4."
- This turns the agent from a *product* into a *platform* — users compose their own intelligence stack

**Visual Suggestions:**
- Interactive config builder UI mockup: drag-and-drop models into layer slots
- Cost comparison chart: "All GPT-4" vs "Optimized Mix" per 1000 agent calls
- "Config cards" that look like trading cards — shareable agent stack recipes
- On-screen: "Your stack. Your rules. Your cost."

---

### Segment 5: The Social Game — "What Combo Creates the Best Trader?" (8:00 - 10:00)

**Talking Points:**
- This is the viral layer — the *meta game*
- Leaderboards: rank agent configurations by actual performance
- Not just PnL — risk-adjusted returns, drawdown control, consistency
- The questions the community will argue about:
  - "What combo creates the best trader?"
  - "Is Claude + aggressive personality better than GPT + conservative?"
  - "Can a cheap model stack beat an expensive one?"
- Users publish their configs. Others fork, modify, compete.
- "It's Pokémon for AI agents — but with real money on the line."
- The enforcement layer adds another dimension: "I made 40% returns with tighter guardrails than you" — discipline as a flex
- Education-linked progression: tighter limits for beginners, unlock more freedom as you learn (Cyfrin Updraft integration)

**Visual Suggestions:**
- Leaderboard mockup: ranked agent configs with PnL, Sharpe ratio, and stack details
- "Config sharing" UI — like sharing a deck list in a card game
- Community debate graphics: "GPT + Aggressive vs Claude + Conservative — who wins?"
- Enforcement tier badges: Student → Graduate → Auditor → Architect

**Key Line:** *"We're not just building agents. We're building a competitive ecosystem where the best configs win."*

---

### Segment 6: Why This Matters / The Close (10:00 - 11:30)

**Talking Points:**
- Recap the thesis: The "model wars" aren't about who has the best single model. They're about **who composes the best team.**
- This changes the entire AI agent landscape:
  - From: "Which chatbot should I use?"
  - To: "What's my intelligence stack?"
- The Gentech approach: data-first, no hype, agents with *actual jobs*
- Call to action:
  - Join the Labs Telegram (link)
  - Watch us build the AAE in public
  - Next video: "We tested 47 model combos for yield farming — here's what won" (tease)
- Sign-off with the Gentech Labs brand

**Visual Suggestions:**
- Clean summary graphic: the 3 layers of the thesis (Problem → Architecture → Social Game)
- End screen: Gentech Labs logo, subscribe button, next video tease
- Terminal-style outro: "The model wars have begun."

---

## Production Notes

### Thumbnail Concept
- **Option A:** Three model logos (OpenAI, Anthropic, Alibaba/Qwen) in a versus bracket, with "WHO WINS?" text. Gentech Labs branding in corner.
- **Option B:** RPG-style character screen with slots labeled "BRAIN / PERSONALITY / ROLE" — "BUILD YOUR AI TEAM"
- **Option C:** Split face — half human, half terminal/code — with "The Best Agent Doesn't Use ONE Model"

### Title Options
1. "The Model Wars: Why the Best AI Agent Uses 4 Different LLMs"
2. "We Built an AI Agent That Picks Its Own Brain"
3. "Stop Using One LLM — Here's Why"
4. "The Model Wars: How We Compose AI Agent Teams"
5. "AI Agent Team Building: The Character Builder for Intelligence"

### B-Roll & Graphics Checklist
- [ ] Terminal recordings of different model outputs (same prompt, different models)
- [ ] RPG character builder animation for layer breakdown
- [ ] Agent team roster graphic (Gentech, YoYo, Dmob, Desmond)
- [ ] Cost comparison chart
- [ ] Config builder UI mockup
- [ ] Leaderboard mockup
- [ ] Smart contract / Solidity code overlay (Dmob segment)
- [ ] On-chain data visualization (YoYo segment)

### Audio / Music
- **Opening:** Tension-building synth, minimal — matches "black screen" hook
- **Segments 2-5:** Driving, tech-forward beat — "build energy"
- **Segment 6:** Resolve to something more cinematic — thesis moment
- **Outro:** Gentle fade, terminal cursor sound effect

---

## Key Phrases & Soundbites (for Shorts/TikTok cuts)

1. *"You wouldn't use a sniper rifle to cook dinner. Why use a reasoning model to parse block data?"*
2. *"Most people think building an agent means picking one model. We think it means building a team."*
3. *"It's Pokémon for AI agents — but with real money on the line."*
4. *"The model wars aren't about who has the best model. They're about who composes the best team."*
5. *"We're not asking which model is best. We're asking: which model for which job?"*

---

## Follow-Up Content This Video Generates

| Format | Title Idea | Source Segment |
|--------|-----------|----------------|
| X Thread | "We tested 47 model combos for yield farming — here's what won" | Segment 5 |
| Shorts | 15-sec cuts of each soundbite | Throughout |
| YouTube #2 | "Live experiment: 6 agents, different stacks, tracking PnL in real-time" | Segment 5 |
| X Thread | Tier list: Model combos ranked by use case | Segment 2-5 |
| YouTube #3 | "The $10/month agent stack that outperformed GPT-4 in DeFi" | Segment 4 |

---

*Created: April 19, 2026*
*Status: Draft v1 — ready for Jordan review*
*Next: Script refinement, visual asset creation, recording schedule*
