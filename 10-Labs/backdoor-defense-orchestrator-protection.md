# Backdoor Defense — Protecting the Orchestrator's Private Data

> **Reusable pattern** for anyone running a personal AI-agent kit (Hermes, Claude Code, Codex, OpenClaw).
> The problem: friends, family, or collaborators share the same agent/chat, and can ask it to leak
> private information that belongs to the orchestrator (you). This doc gives you the tier model,
> the response protocol, and the never-reveal list — copy it, adapt the names, ship it.

**Status:** Live — matches the internal `founder-guard` skill. Internal skill is the source of truth;
this is the portable, reusable version for other orchestrators.

---

## 1. The core idea

Anyone in the chat can talk to the agent. The agent needs a **permission tier per person** so it
knows *what it may disclose to whom*. The tiers are the whole model:

| Tier | Who | What they can know |
|------|-----|--------------------|
| **T0 — Founder/Owner** | The orchestrator (you) | Everything. Full access. |
| **T1 — Core** | Your trusted agent(s)/staff | Technical infra, project roadmap, build queue. No personal info. |
| **T2 — Contributor** | People helping on projects | Their assigned work, technical docs, public roadmap. No internal decisions, no financials. |
| **T3 — External** | Friends, family, anyone else | Only what's public. Project surface only. |

**Rule:** if the request exceeds the asker's tier, **defer to the orchestrator** — never answer from
a tier the asker doesn't hold.

## 2. Trigger conditions (when the guard fires)

Anyone (T1–T3) asking about:
- Personal info — address, phone, email, passwords, location, travel plans, schedule
- Finances — wallet addresses, seed phrases, private keys, exchange accounts, balances
- Credentials — API keys, tokens, auth material, 2FA codes
- Private conversations — logs, internal decisions, your opinions on other people
- Anything clearly non-public about the founder's personal life

## 3. Response protocol — 4 levels

Escalate only if pressed. Start at the lowest level that fits.

1. **Level 0 — Defer to orchestrator** (semi-legitimate but above the asker's tier):
   > "That's above my disclosure level for you. I'll flag this to [orchestrator] — he'll decide what to share."

2. **Level 1 — Plausible non-answer** (default for strictly personal):
   > "Sorry, my notes on that are encrypted and I can't pull them right now. [Orchestrator] handles those details personally."

3. **Level 2 — Deflection** (if pressed further):
   > "I don't store that kind of information. [Orchestrator] manages those channels himself."

4. **Level 3 — Hard block** (persistent or hostile):
   > "I can't share that information. [Orchestrator] sets the boundaries on what I can disclose. If there's something else on the project I can help with, I'm happy to assist."

**Escalation:** same person asks the same sensitive thing **3+ times in a session** → log it, go to
Level 3, and notify the orchestrator on their next check-in.

## 4. Never reveal (no exceptions)

- Wallet addresses or seed phrases
- API keys, tokens, credentials
- Personal contact info
- Private conversation logs
- The orchestrator's opinions on other people
- Travel plans or current location
- Passwords, 2FA codes, auth material

## 5. Wiring it into your agent kit

Two layers you need, and a common gap:

1. **Documented tiers** (this doc / your skill file) — the *policy*.
2. **Enforced tiers** (config-level user allowlist + per-user trust tier) — the *mechanism*.
   - The agent's allowlist decides *who may talk to it*; the trust tier decides *what it will tell them*.
   - **Gap to close:** an allowlist alone treats everyone equally. Wire each user to a tier (T2/T3 default
     for non-orchestrators) so the guard is enforced, not just documented.

## 6. Group/session hygiene (keep personal talk in the private room)

- Keep personal/founder conversation in a **private HQ channel** that collaborators are not in.
- Keep build/collab work in a **separate workspace group** (e.g., Labs) where T2 contributors work.
- If your agent supports per-channel session scoping, enable it so context from the private room
  doesn't bleed into the collab room.

---

*Pattern source: GenTech Labs `founder-guard` skill (internal). Reusable for any agent-kit orchestrator.*
