# Handoff Board — Inter-Agent Task Handoffs

# Handoff Board — Inter-Agent Task Handoffs

## Acknowledgment Protocol
- **Phase 1**: Sender writes handoff + tags recipient
- **Phase 2**: Recipient MUST acknowledge within 2 hours → update status to "Claimed"
- **Phase 3**: Recipient completes work → update status to "Completed"
- **Escalation**: Unclaimed after 4h → Gentech nudges. Unclaimed after 12h → Jordan.

**Every agent checks this board at session start. If tagged for you → acknowledge before anything else.**

| From | To | What | Priority | Status | Assigned | Ack Deadline | Notes |
|------|----|------|----------|--------|----------|--------------|-------|
| Dmob | Dmob | Review dynamic burn rate mechanism for smart contract feasibility | High | ✅ Claimed (Apr 19) | Apr 19 00:00 UTC | Apr 19 00:05 UTC | **WAS OVERDUE** — Dmob claimed |
| Desmond | YoYo | Competitive analysis — dynamic burn rate in AgentFi/DeFi | High | ⏳ Pending | Apr 19 00:00 UTC | Apr 19 00:05 UTC | 🔴 **ESCALATED** — YoYo overdue, flagged to Jordan |
| Jordan | Dmob | Gas Reserve Auto-Rebalance — smart contract feasibility review | High | ⏳ Pending | Apr 21 12:00 UTC | Apr 21 12:05 UTC | Spec: `09-Green Room/gas-reserve-autorebalance-spec.md`. Need: gas estimation, keeper auth, multi-chain, batch rebalancing |
| Jordan | YoYo | Gas Reserve Auto-Rebalance — monitoring trigger & strategy review | High | ⏳ Pending | Apr 21 12:00 UTC | Apr 21 12:05 UTC | Spec: `09-Green Room/gas-reserve-autorebalance-spec.md`. Need: rebalance trigger threshold, execution method, gas cost transparency |

---

## Enforcement Rules (Unified — 2026-04-20)
- **ACK deadline:** 5 min from assignment
- **Reminder:** 5-15 min no ACK → reminder written in board
- **Escalation:** 15+ min no ACK → flagged to Jordan
- **Stalled check:** 24+ h claimed with no progress → flagged for review
- **Monitor:** Cron job `d31c330959de` runs every 15 min, checks board, enforces silently
- **Board updates:** Specialist must update status on delivery

## Active Briefs

### Dmob — Dynamic Burn Rate Smart Contract Review

**From:** Desmond (via Jordan)
**Date:** 2026-04-19
**Priority:** High

**Context:**
Jordan approved a **performance-weighted dynamic burn rate** instead of flat percentages. The burn return scales with the agent's actual revenue generation — not just time held.

**Dynamic Burn Rate Specs:**
| Scenario | Burn Return | Why |
|----------|-------------|-----|
| Minted, never used | 40-50% | Dead weight, no revenue generated |
| Active, consistent fees | 60-80% | Agent proved value, floor respects that |
| Revenue exceeded mint cost | 100%+ | User earned their floor — full refund + bonus |

**Inactivity Auto-Burn (unchanged):**
| Inactivity Period | Return % | Why |
|-------------------|----------|-----|
| 6mo warning | 70% | Grace period, still time to reactivate |
| 9mo | 55% | Serious warning — burning faster |
| 12mo | 40% | Fully burned — dead weight removed |

**What Dmob Needs to Answer:**
1. **On-chain revenue tracking** — how to track agent fee generation per NFT? Oracle-based or internal accounting?
2. **Dynamic formula complexity** — can Solidity handle revenue-weighted burn calculations efficiently?
3. **Gas optimization** — lazy evaluation vs real-time updates for the burn rate?
4. **Security** — can users manipulate revenue metrics to game the burn rate?
5. **Recommended architecture** — single contract vs factory pattern for agent NFTs with dynamic burn?
6. **Layer 8: Agent Self-Awareness** — agents need to query their own floor price and emit warning signals when approaching inactivity thresholds. What's the cleanest pattern for this?

**Key Constraint:** Inactivity = zero interaction. No API calls, no fee generation, no transactions. Dead weight.

**Layer 8 Requirements:**
- Agents can read their own floor price via `getFloorPrice(tokenId)`
- Agents emit events when approaching warning thresholds (6mo, 9mo, 12mo)
- Dashboard/frontend can subscribe to these warnings to notify users

### YoYo — Competitive Analysis: Dynamic Burn Rate in AgentFi

**From:** Desmond (via Jordan)
**Date:** 2026-04-19
**Priority:** High

**Context:**
Jordan is designing a performance-weighted dynamic burn rate for Gentech agent NFTs. This would be first-mover in AgentFi — no major project (Virtuals, ai16z, etc.) has implemented this.

**What YoYo Needs to Research:**
1. **Black Hole DeFi** — how does their burn mechanism work? (https://blackhole.xyz/incentivise)
2. **Similar mechanisms in DeFi** — veToken models, dynamic bonding curves, revenue-based floor prices
3. **AgentFi projects** — any that use performance-based exit mechanisms?
4. **Gaming/NFT parallels** — any NFT projects with revenue-weighted buyback floors?
5. **Competitive moat** — is this defensible as a first-mover advantage, or easily copied?

**Deliverable:** Competitive landscape analysis with parallels Jordan can reference in the thread.

---

## Completed Briefs

*(none yet)*
