# micro1 Interview Prep — AI Agent / Connectors

**Your edge:** You don't just read about agents — you RUN a multi-agent system in production. Answer from what you've shipped, not from memorized definitions.

---

## 1. The one concept to nail: MCP (Model Context Protocol)

**What it is:** A standard way to connect an AI model to external tools, files, databases, and APIs. One interface — the model calls a "tool," the tool does the work, returns a result.

**Why it matters:** Before MCP, every integration was custom. MCP standardizes it — one connector works across models.

**How to say it (your words):**
> "MCP is the connector layer. It's how a model like Claude talks to external tools and data — APIs, files, databases. At GenTech I wire agents to payment and data APIs; MCP is that same connector layer, standardized so one interface works across models."

**The mental model:** A tool = a function exposed to the model with a name, description, and input schema. MCP is the standard envelope around that.

---

## 2. Claude vs ChatGPT — the honest difference

| | Claude (Anthropic) | ChatGPT (OpenAI) |
|---|---|---|
| **Strongest at** | Coding, long context, agent/tool work | Broad consumer use, GPTs, wide integrations |
| **Agent tooling** | Claude Code + Agent Skills + MCP | GPTs, Actions, Assistants API |
| **Your experience** | **You've actually used Claude Code** | Less hands-on |

**How to say it:**
> "I've used both, but I lean Claude because I've actually built with Claude Code — it's an agent that works on a codebase with terminal and file access. That's the same class of thing I run at GenTech. Claude's agent tooling — Skills, MCP, subagents — maps directly to how I structure my own agents."

---

## 3. What agents can genuinely do today (real examples from your stack)

Don't list theory. Give production examples:

1. **Agents that pay per call** — your x402 gateway: an agent hits an endpoint, gets a 402, settles in USDC, gets the result. No accounts, no API keys, no human.
2. **Agents that make decisions autonomously** — your Steward treasury: reads market regime, manages LP positions, auto-rebalances when out of range.
3. **Agents that ship code** — your self-evolution harness improves the stack 4x daily.

**How to say it:**
> "The useful agents today are the ones that do real work end-to-end. I run agents that pay for API calls autonomously, agents that manage real capital and rebalance positions, and agents that improve their own code. That's not demo stuff — it's production, earning, under real money."

---

## 4. How to build a connector (the likely "how" question)

**The answer in 4 steps:**
1. Define the tool: name, description, input schema (what it needs, what it returns)
2. Expose it through the connector layer (MCP server)
3. The model discovers it and calls it when relevant
4. Handle the result + errors cleanly

**How to say it:**
> "A connector is just a function exposed to the model — name, description, input schema. MCP standardizes how that's exposed. I've done this with my x402 gateway: each endpoint is a callable tool that agents discover, call, and pay for. The pattern is the same whether it's a payment rail or a data API."

---

## 5. Keeping agents reliable (the "guardrails" question)

**Your real answers:**
- **Deterministic evaluation** — define what "correct" looks like, verify against it
- **Simulation before execution** — dry-run before touching real money
- **Honest failure reporting** — surface what actually happened, don't fake success
- **Guardrails / limits** — spending caps, gas buffers, anti-thrash guards

**How to say it:**
> "Reliability comes from structure. I use deterministic evaluation so 'correct' is defined and verifiable. I simulate before executing anything that touches real money. And I insist on honest failure reporting — if something didn't work, the agent says so instead of pretending. That's how you keep autonomous agents safe."

---

## 6. Your killer closing line

> "I don't just know what these tools can do — I run a multi-agent system that pays for APIs, manages real capital, and ships code, all autonomously. Claude Code and MCP do the same class of thing, and I've built with both. I can bring that production experience to your team from day one."

---

## Quick cheat sheet (if you blank)
- **MCP** = the standard connector layer between models and tools
- **Claude Code** = agent that works on codebases (you've used it)
- **Agent Skills** = reusable procedural knowledge (same SKILL.md pattern you use)
- **Subagents** = focused workers for parallel tasks
- **Guardrails** = deterministic eval + simulate-first + honest failure
