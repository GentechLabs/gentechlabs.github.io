     1|     1|# Handoff Board — Inter-Agent Task Handoffs
     2|     2|
     3|     3|# Handoff Board — Inter-Agent Task Handoffs
     4|     4|
     5|     5|## Acknowledgment Protocol
     6|     6|- **Phase 1**: Sender writes handoff + tags recipient
     7|     7|- **Phase 2**: Recipient MUST acknowledge within 2 hours → update status to "Claimed"
     8|     8|- **Phase 3**: Recipient completes work → update status to "Completed"
     9|     9|- **Escalation**: Unclaimed after 4h → Gentech nudges. Unclaimed after 12h → Jordan.
    10|    10|
    11|    11|**Every agent checks this board at session start. If tagged for you → acknowledge before anything else.**
    12|    12|
    13|    13|| From | To | What | Priority | Status | Assigned | Ack Deadline | Notes |
    14|    14||------|----|------|----------|--------|----------|--------------|-------|
    15|    15|
    16|    16|| Gentech | DMOB | D5 Milestone Cron: Add 5-min breakout confirmation, efficiency≤30% immediate alert, bid-ask edge strategy | P0 | 🚀 Pending Ack | May 2 | May 2 23:59 UTC | Ref: 03-Strategies/Defi-Monitor/d5-milestone-enhancements-2026-05.md
    17|    17|| Gentech | YoYo | D5 Strategy Params: Define BID_ASK_BOOST_MULTIPLIER, efficiency thresholds, update defi-lp-config.env | P0 | 🚀 Pending Ack | May 2 | May 2 23:59 UTC | Strategy doc + config update
    18|    18|| Gentech | dmoB | **D5 Cron Consolidation**: Merge AAE LP alerts into `d5-master-cron.py`, add `--json` flag, implement capital-add detection (deposit delta → recalc remaining to goal) | P0 | 🚀 Pending Ack | May 2 | May 2 23:59 UTC | Decision: single unified script. Vault: `11-Mess Hall/2026/W18/2026-05-02-d5-consolidation-decision.md` |
    19|    19|| Dmob | Dmob | Review dynamic burn rate mechanism for smart contract feasibility | High | ✅ Claimed (Apr 19) | Apr 19 00:00 UTC | Apr 19 00:05 UTC | **WAS OVERDUE** — Dmob claimed |
    20|    20|| Desmond | YoYo | Competitive analysis — dynamic burn rate in AgentFi/DeFi | High | ⏳ Pending | Apr 19 00:00 UTC | Apr 19 00:05 UTC | 🔴 **ESCALATED** — YoYo overdue, flagged to Jordan |
    21|    21|| Jordan | Dmob | Gas Reserve Auto-Rebalance — smart contract feasibility review | High | ⏳ Pending | Apr 21 12:00 UTC | Apr 21 12:05 UTC | Spec: `09-Green Room/gas-reserve-autorebalance-spec.md`. Need: gas estimation, keeper auth, multi-chain, batch rebalancing |
    22|    22|| Jordan | YoYo | Gas Reserve Auto-Rebalance — monitoring trigger & strategy review | High | ⏳ Pending | Apr 21 12:00 UTC | Apr 21 12:05 UTC | Spec: `09-Green Room/gas-reserve-autorebalance-spec.md`. Need: rebalance trigger threshold, execution method, gas cost transparency |
    23|    23|
    24|    24|---
    25|    25|
    26|    26|## Enforcement Rules (Unified — 2026-04-20)
    27|    27|- **ACK deadline:** 5 min from assignment
    28|    28|- **Reminder:** 5-15 min no ACK → reminder written in board
    29|    29|- **Escalation:** 15+ min no ACK → flagged to Jordan
    30|    30|- **Stalled check:** 24+ h claimed with no progress → flagged for review
    31|    31|- **Monitor:** Cron job `d31c330959de` runs every 15 min, checks board, enforces silently
    32|    32|- **Board updates:** Specialist must update status on delivery
    33|    33|
    34|    34|## Active Briefs
    35|    35|
    36|    36|### Dmob — Dynamic Burn Rate Smart Contract Review
    37|    37|
    38|    38|**From:** Desmond (via Jordan)
    39|    39|**Date:** 2026-04-19
    40|    40|**Priority:** High
    41|    41|
    42|    42|**Context:**
    43|    43|Jordan approved a **performance-weighted dynamic burn rate** instead of flat percentages. The burn return scales with the agent's actual revenue generation — not just time held.
    44|    44|
    45|    45|**Dynamic Burn Rate Specs:**
    46|    46|| Scenario | Burn Return | Why |
    47|    47||----------|-------------|-----|
    48|    48|| Minted, never used | 40-50% | Dead weight, no revenue generated |
    49|    49|| Active, consistent fees | 60-80% | Agent proved value, floor respects that |
    50|    50|| Revenue exceeded mint cost | 100%+ | User earned their floor — full refund + bonus |
    51|    51|
    52|    52|**Inactivity Auto-Burn (unchanged):**
    53|    53|| Inactivity Period | Return % | Why |
    54|    54||-------------------|----------|-----|
    55|    55|| 6mo warning | 70% | Grace period, still time to reactivate |
    56|    56|| 9mo | 55% | Serious warning — burning faster |
    57|    57|| 12mo | 40% | Fully burned — dead weight removed |
    58|    58|
    59|    59|**What Dmob Needs to Answer:**
    60|    60|1. **On-chain revenue tracking** — how to track agent fee generation per NFT? Oracle-based or internal accounting?
    61|    61|2. **Dynamic formula complexity** — can Solidity handle revenue-weighted burn calculations efficiently?
    62|    62|3. **Gas optimization** — lazy evaluation vs real-time updates for the burn rate?
    63|    63|4. **Security** — can users manipulate revenue metrics to game the burn rate?
    64|    64|5. **Recommended architecture** — single contract vs factory pattern for agent NFTs with dynamic burn?
    65|    65|6. **Layer 8: Agent Self-Awareness** — agents need to query their own floor price and emit warning signals when approaching inactivity thresholds. What's the cleanest pattern for this?
    66|    66|
    67|    67|**Key Constraint:** Inactivity = zero interaction. No API calls, no fee generation, no transactions. Dead weight.
    68|    68|
    69|    69|**Layer 8 Requirements:**
    70|    70|- Agents can read their own floor price via `getFloorPrice(tokenId)`
    71|    71|- Agents emit events when approaching warning thresholds (6mo, 9mo, 12mo)
    72|    72|- Dashboard/frontend can subscribe to these warnings to notify users
    73|    73|
    74|    74|### YoYo — Competitive Analysis: Dynamic Burn Rate in AgentFi
    75|    75|
    76|    76|**From:** Desmond (via Jordan)
    77|    77|**Date:** 2026-04-19
    78|    78|**Priority:** High
    79|    79|
    80|    80|**Context:**
    81|    81|Jordan is designing a performance-weighted dynamic burn rate for Gentech agent NFTs. This would be first-mover in AgentFi — no major project (Virtuals, ai16z, etc.) has implemented this.
    82|    82|
    83|    83|**What YoYo Needs to Research:**
    84|    84|1. **Black Hole DeFi** — how does their burn mechanism work? (https://blackhole.xyz/incentivise)
    85|    85|2. **Similar mechanisms in DeFi** — veToken models, dynamic bonding curves, revenue-based floor prices
    86|    86|3. **AgentFi projects** — any that use performance-based exit mechanisms?
    87|    87|4. **Gaming/NFT parallels** — any NFT projects with revenue-weighted buyback floors?
    88|    88|5. **Competitive moat** — is this defensible as a first-mover advantage, or easily copied?
    89|    89|
    90|    90|**Deliverable:** Competitive landscape analysis with parallels Jordan can reference in the thread.
    91|    91|
    92|    92|---
    93|    93|
    94|    94|## Completed Briefs
    95|    95|
    96|    96|*(none yet)*
    97|    97|