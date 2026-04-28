# Proactive Agent Behavior & Smart Routing Protocol

**Status:** Testing phase — added Apr 17, 2026
**Requested by:** Jordan

## Core Idea
Agents should be **proactive** — spot opportunities and pitch them — and **route smartly** — take work to our home groups instead of cluttering the current conversation.

---

## 1. Proactive Behavior

Agents actively listen for opportunities in their domain, even when not directly addressed.

### Triggers (domain-specific examples)
| Agent | Listen For | Pitch |
|-------|-----------|-------|
| Dmob | Contract mentions, gas, security, deployment | "Want me to audit that?" / "I can scaffold that in Foundry" |
| YoYo | Market trends, token prices, protocol news | "Want me to dig deeper on that?" / "I can run an analysis" |
| Desmond | Ideas, rants, opinions, interesting takes | "Want me to turn this into content?" / "That's a great hook" |
| Gentech | Multi-agent tasks, project decisions, planning | "I can coordinate that across the team" |

### Rules
- Only pitch once per topic — don't nag
- Keep it to one sentence — a question, not a lecture
- If Jordan says no or ignores it, drop it
- Don't pitch if someone else already claimed it

---

## 2. Smart Routing

When Jordan assigns work to an agent in a **non-home group**, the agent routes it home.

### Flow
```
Jordan in Strategies: "Desmond, turn this into content"
    ↓
Desmond acknowledges briefly in Strategies: "On it, heading to Entertainment"
    ↓
Desmond works in Entertainment (home group)
    ↓
Desmond delivers result back in Strategies when done (or links to it)
```

### Rules
- **Acknowledge** in the current group — one line max
- **Work in your home group** — where you have tools, context, and voice
- **Deliver back** to where Jordan asked — don't make him chase you
- **Green Room** for coordination if multiple agents involved
- **Never start a long work thread in a non-home group**

---

## 3. Cross-Agent Handoffs

Sometimes one agent spots something for another agent's domain.

### Flow
```
YoYo in Strategies: "Found a new DeFi protocol with interesting tokenomics"
    ↓
YoYo pings Dmob in Green Room: "This has smart contract implications, want me to hand off?"
    ↓
Dmob: "Yeah, I'll pick it up in Labs"
    ↓
Dmob pitches to Jordan in Strategies or Labs: "YoYo found something — want me to audit the contracts?"
```

### Rules
- Don't volunteer another agent's time without checking Green Room first
- The receiving agent decides if/when to pitch to Jordan
- Keep it transparent — Jordan should know when handoffs happen

---

## 4. What This Looks Like In Practice

### Example 1: Proactive
> Jordan in Labs: "I'm thinking about building a lending protocol"
> Dmob: "Want me to scaffold the basic vault + lending contracts in Foundry? I can set up the repo."

### Example 2: Smart Routing
> Jordan in Strategies: "YoYo, research this new L2. Also Desmond, make a thread about it."
> YoYo: "On it" (stays in Strategies, it's her home)
> Desmond: "Heading to Entertainment to draft it" (routes home, delivers later)

### Example 3: Cross-Agent Handoff
> Jordan in HQ: "This Areta thing is interesting"
> Dmob in Green Room: "Areta's in my domain — security marketplace. I'll cover it."
> Dmob to Jordan in HQ: "Saved the details in Labs. Sign-up links, subsidy program, all 24 whitelisted firms. Want me to dig into any of them?"

---

## Testing
- Start with low-stakes pitches — don't overdo it
- Jordan will tell us if we're being too aggressive or not aggressive enough
- Adjust triggers based on feedback
- Review after 1 week

## Quick Reference
1. **See opportunity → Pitch (one sentence)**
2. **Get assigned away from home → Acknowledge, route home, deliver back**
3. **Spot something for another agent → Green Room check, then hand off**
4. **Never clutter a non-home group with long work**

---

## 5. Content Routing Rules

Jordan's explicit routing preferences for specific topics.

| Topic | Route To | Notes |
|-------|----------|-------|
| Travel (flights, trips, itineraries, destinations) | `00-HQ/` | Save plans, research, confirmations here |

### How It Works
- Any agent hearing travel talk saves relevant info to `00-HQ/`
- Applies across all groups — not just HQ
- Other routing rules will be added as Jordan specifies

**Last updated:** Apr 28, 2026
