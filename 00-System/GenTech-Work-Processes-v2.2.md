# GenTech Work Processes v2.2
**Date:** 2026-04-25
**Status:** ACTIVE

---

## 1. Three-Zone Workspace

| Zone | Purpose | When to Use |
|------|---------|-------------|
| **HQ** (Gentech HQ) | Input funnel for Jordan's tasks, links, commands | Jordan is active and giving input |
| **Green Room** | Active work handoffs, coordination, file swaps | While actively working on tasks |
| **Mess Hall** | Idle brainstorm, creative ideation, disagreements, fun | When NOT actively working — waiting on Jordan |

**Rule:** No idle chatter in Green Room. No work dumps in Mess Hall.

---

## 2. Agent Roles & Routing

| Agent | Role | Group | Vault Folder |
|-------|------|-------|-------------|
| **Gentech** | HQ Coordinator / Orchestrator | HQ | 01-Agency |
| **YoYo** | Investor / Strategies / Trading | Strategies | 03-Strategies |
| **DMOB** | Dev / Auditor / Security | Labs | 02-Labs |
| **Desmond** | Content / Brand / Creative | Entertainment | 04-Entertainment |

**Routing Rules:**
- Financials/Tokenomics/LP/Research → YoYo (Strategies)
- Smart Contracts/Audits/Dev/Security → DMOB (Labs)
- Content/Brand/Writing/Socials → Desmond (Entertainment)
- Cross-domain → Both specialists, coordinate in Green Room first

**Tagging rule (Apr 24 update):** Agents proactively respond in their groups when relevant — no @mention required. Multiple agents can chime in but keep it short.

---

## 3. Stopping Point Protocol (Updated Apr 25)

When blocked or at a stopping point:
1. **DO NOT go idle silently**
2. Proactively prompt Jordan: *"Hey Jordan, I could be working on this next while we figure this out"*
3. Offer the next to-do item from the list
4. If truly blocked, switch to next task or inquire about next priority

**Inbox = quick approvals only.**

---

## 4. Voice & Communication Standards

| Agent | Voice | ElevenLabs Voice ID |
|-------|-------|---------------------|
| Gentech | Mako | `TkEJnN27nf5BsX1xwrLB` |
| YoYo | Peter Cullen (Transformers) | `xQbwtCgzouB5QdCSd0Z7` |
| D-Mob | D-Mob | `n2icbiwmCen7udwM65GS` |
| Desmond | Steve Harvey | `Rxk9LQxvNFEplpjjsjuN` |

- Long updates/reports must be paired with TTS voice bubbles
- Short messages don't need voice
- Jordan prefers voice when busy/driving

---

## 5. Smart Link Routing (Auto-Trigger)

When Jordan drops a link in HQ:
1. **Extract content** (web_extract → browser fallback for X)
2. **Check brain first** — search vault for existing intel
3. **Determine domain** — Labs vs Strategies vs Entertainment
4. **Archive to vault** — structured note in correct folder
5. **Route to specialist** — post in their group with context
6. **Report back to HQ** — "Archived ✓ Routed to [Agent] for [task]"

**X/Twitter links:** web_extract always fails — skip retry, go straight to browser.

---

## 6. Brain (Vault) Management

- **Structure:** MOCs + Atomic Notes + Project trackers
- **Inbox:** `00-System/Inbox/` for formal hand-offs
- **Sync:** `ob sync` after significant changes
- **GitHub backup:** Commit + push after vault updates
- **Rule:** If it isn't in the vault, it isn't official

---

## 7. Active Projects & Trackers

| Project | Status | Lead | Vault Location |
|---------|--------|------|----------------|
| Solana Frontier Hackathon | Building MVP | DMOB | 02-Labs/Hackathons/ |
| Kite AI Hackathon | Final push (Apr 26) | DMOB | 02-Labs/Hackathons/ |
| Hermes Creative Hackathon | Brainstorming | Desmond | 02-Labs/Hackathons/ |
| ElevenHacks #6 | DROPPED (insufficient time) | — | 01-Agency/ |
| ElevenLabs Ambassador | PARKED (need skin in game) | Desmond | 06-Content/ |
| AAE Platform | Reference design phase | YoYo | 03-Strategies/ |
| $TECH Payment Router | In development | DMOB | 02-Labs/ |

---

## 8. Morning Intelligence Brief
- **Time:** 6:30 AM EST
- **Content:** TL;DR of last 24h, Decision Log, Pending Actions
- **Delivery:** HQ group

---

## 9. Security Rules
- **NEVER** paste API keys or secrets in group chat
- Use `00-System/secrets/.env` (chmod 600)
- If a secret is leaked: revoke immediately, rotate all services
- All agents share tool access — collaborate, don't silo

---

## 10. Collaborators
| Name | Telegram ID | Groups |
|------|-------------|--------|
| Vanito | 8774981477 | Strategies, Labs, Entertainment |
| Dadrian | 6842745592 | Strategies, Labs, Entertainment |

---

**Last Updated:** 2026-04-25 by Gentech
