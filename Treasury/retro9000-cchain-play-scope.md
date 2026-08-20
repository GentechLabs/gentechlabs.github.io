# Agentic Treasury × Retro9000 C-Chain Round — Play Scope
**Status:** Scoped (Aug 15, 2026) | **Source:** Jordan — "Yes scope the C chain play. See what others have done before us then we can emulate"
**Related:** `Treasury/agentic-treasury-whitepaper.md` | `09-Green Room/specs/agentic-treasury-avalanche-l1-scope.md` (L1 route, deferred)
**Decision:** C-Chain round path is the near-term play. L1 route deferred.

---

## 1. The critical finding: the mechanics CHANGED (this changes our play)

Researching what came before revealed the program is not static — it iterates every round. This is the single most important thing to know:

| Round | Date | Mechanics |
|-------|------|-----------|
| **R1** | Mar 31 | Pure **AVAX burned via gas fees** ranking. Top 40 eligible. |
| **R2** | Apr 29 | + **Multipliers**: Build Games Stage-2 = 10x, **new projects = 5x**. Auto-entry from R1. |
| **R3** | May 30 | Same burn-based ranking. ~2,980 AVAX burned, $20K+ to top 40. |
| **R4** | Jun 29 | **BIG SHIFT: verified-user engagement scoring.** Tiers (unregistered < connected < verified). **Top 20** eligible. 5x new-project + 5x Build Games. |
| **R5** | Jul 30 | Latest. Up to 10K AVAX pool. |

**The lesson from what came before (what we emulate):**
- **Early rounds** = gas-burn arms race. Winners were high-throughput DeFi/gaming that burned lots of AVAX.
- **Round 4+** = the Foundation deliberately moved AWAY from "biggest burn wins" to **"genuinely growing communities with verified real users."** As their Program Manager said: *"rewards builders who are genuinely growing their communities, not just those with the biggest burn numbers."*

**Why this is great news for us:** we are NOT a high-volume gas-burn machine, and we don't need to be. The current mechanic rewards **real users + community growth**, which is exactly the product Jordan's thesis builds (website + chat model → users on-chain → treasury). We don't need to spam transactions; we need real users who verify and engage.

**The one thing to nail for Round 6+ (next):** **verified users with connected X accounts.** A project's score is now dominated by *verified* users (wallet + 30-day-old tx + linked X). Our user acquisition must drive people who connect wallet AND link X on the Retro9000 platform.

---

## 2. Reward structure (what we're actually playing for)

- Pool: **up to 10,000 AVAX/round** (or total AVAX burned in the round).
- **Top 20** projects eligible (down from 40 in early rounds — steeper, but real).
- **New-project multiplier: 5x** (we'd qualify as new). Huge.
- Financial boundaries: grant ≤ 90% of what the project burned; single project ≤ 25% of monthly pool; **$200K lifetime cap**; min $500 share to qualify.
- Referral program: refer a project that gets accepted → $100 AVAX; up to $3K/project/round if they get funded.
- **KYC/KYB required** for reward payout.

---

## 3. What a winning C-Chain submission actually looks like (from winners)

From the research, the pattern that wins now:
1. **Live product on C-Chain** generating real user engagement (not a testnet or empty contract).
2. **A real community** — users who connect wallet, verify, and use the app on-chain.
3. **Social feed activity** — regular milestone updates on the Retro9000 platform (submissions are public, social feed informs community points).
4. **New-project multiplier** (5x) — get in early in a round.
5. **For us specifically:** a CLARITY Act-compliant treasury with real USDC flowing through it = *differentiated* (most entrants are games/dexes; a compliant agent treasury is novel).

---

## 4. Our play — the Agentic Treasury as the C-Chain submission

**The thesis (Jordan, verbatim):** "Users use our website with a chat model baked in. You can take the treasury on the go with our cron job as a present that's interchangeable. AgentKit is front and center, open sourced and all."

**What we submit:**
- **Product:** the Agentic Treasury — a self-custody treasury agent users interact with via the website chat model, running on Avalanche C-Chain (LFJ AVAX/USDC rail).
- **The activity:** real user deposits → treasury deploys → rebalances → harvests → all on-chain on C-Chain. Every action = real transactions on C-Chain.
- **The community:** users who deposit + verify + link X = verified-user score (the currency of Round 4+).
- **The moat:** CLARITY Act Sec. 309/409 compliance — no other entrant is a compliant agent treasury.

---

## 5. Scope — build phases (Easy → Hard)

### Phase C0 — Get on the C-Chain (prereq, ~1-2 days)
- Confirm the LFJ AVAX/USDC rail executes on **C-Chain** (it does — LFJ is Avalanche C-Chain).
- Fund a small C-Chain USDC + AVAX gas slice.
- **Acceptance:** verified on-chain C-Chain transaction from the treasury wallet.

### Phase C1 — User-facing website + chat model (the front door)
- The website (gentechlabs.net) with a **chat model baked in** = the interface users interact with.
- User tells the chat their wallet → treasury discovers position → live on-chain.
- **Acceptance:** a user can talk to the website chat and see their treasury position live.

### Phase C2 — Portability demo (the cron job as "a present that's interchangeable")
- The cron job = the 24/7 portable treasury presence, interchangeable across chains via config.
- Demo: same treasury logic, switch config Base → Avalanche C-Chain → back, funds follow.
- **Acceptance:** one config change moves the treasury's focus chain; verified on-chain.

### Phase C3 — AgentKit front-and-center (open source)
- The open-source AgentKit repo = the canonical, readable artifact judges review.
- Public, tested, README showing the treasury bootstrapping + C-Chain usage.
- **Acceptance:** public repo with docs + tests + a C-Chain demo.

### Phase C4 — Retro9000 submission
- Register the Agentic Treasury on the Retro9000 platform (public submission).
- Drive verified-user adoption: connect wallet + link X + use on-chain.
- Post regular milestone updates to the social feed.
- **Acceptance:** submission live on Retro9000 + a verified-user base + social feed activity.

---

## 6. Cost estimate (honest)

| Item | Cost |
|------|------|
| C-Chain gas (USDC + AVAX slice) | ~$10-30 (tiny on Avalanche) |
| LFJ LP deploy | small USDC slice ($50-100) |
| Website/chat already built | $0 marginal |
| Cron job already built | $0 marginal |
| Our time | ~1-2 weeks dev + user acquisition |

**Capital exposure: ~$100-150.** Well within reason given a 5x new-project multiplier and a $200K lifetime cap.

---

## 7. Risks / honest flags

- **Round timing:** R5 ended Jul 30; R6 hasn't been announced. We may need to ship the product first and enter the next round. **Confirm when R6 opens.**
- **Verified-user scoring is the real competition:** we need actual humans depositing + verifying. Not bots — the Foundation has anti-gaming (X account age ≥ 30 days, KYC). Our user base (Dadrian, family, early adopters) is real but small. **Community growth is the hard part, not the tech.**
- **Top 20 is steeper than top 40.** We can't rely on the multiplier alone.
- **Retro9000 rewards are not guaranteed income** — they're a grant, contingent on ranking + KYC.

---

## 8. Definition of Done (Phase C)

The C-Chain play is "real" when, end to end:
1. Treasury executing on C-Chain (verified tx) — C0
2. Users can interact via website chat — C1
3. Portability demo shown (chain switch via config) — C2
4. AgentKit repo public + readable — C3
5. Submission live on Retro9000 + verified-user base + social feed — C4

---

## 9. What came before (emulation notes)

- **Emulate:** live product + real community + verified users + social feed milestones + 5x new-project multiplier + referral program (self-referral for the $100 AVAX).
- **Avoid:** the gas-burn arms race of R1-3 — Round 4+ stopped rewarding it. Don't spam transactions.
- **Differentiate:** CLARITY Act-compliant agent treasury is a novel category vs the games/dexes that dominate the leaderboard.

---

## 10. Next action (blocker for me)

- **Needs Jordan:** (1) greenlight Phase C0-C4, (2) confirm whether to enter R6 (need to check when it opens + R5 results), (3) any C-Chain USDC/AVAX to fund the demo slice.
- **My immediate next step once greenlit:** C0 — verify the treasury can execute on C-Chain and fund a small demo slice. Then C1-C4 in sequence.

---

## 11. BENQI PAYG — affordable agent-run validator (the infra angle, Aug 20)

**Source:** BENQI Ignite PAYG (app.benqi.fi/ignite). **This is an OPTION within the Retro9000 play, not a yield rail.**

### What it is
- **No 2,000 AVAX ($13K) upfront stake needed.** Pay a **weekly fee**, BENQI supplies the full 2,000 AVAX validator stake, you run the node.
- **Min fee: 8 AVAX/week (~$57).** One-time fee, min stake 0. 2-wk=16 AVAX, 4-wk=30 AVAX, 8/12-wk cheaper per wk. 5% discount paid in QI. Payable AVAX/USDC/QI.
- **Agent-wireable:** run node on our VPS (already 24/7) → extract Node ID + BLS Key + BLS Sig → submit PAYG → BENQI stakes.

### The honest catch — it is a COST, not income
- **PAYG earns NO staking rewards** (BENQI keeps them). Rewards are "minimal."
- So PAYG alone is NOT an income stream. It only becomes income **IF Retro9000 awards** the agent-run-validator infra play.
- **The intersection:** Retro9000's "L1s & Infrastructure Tooling" round ($40M AVAX) rewards critical infra. An agent-run validator generating real on-chain activity = an infra-tooling submission angle. PAYG makes that affordable ($57/wk vs $13K stake).

### How to log it (Jordan's request — "log as an income stream for Retro9000")
- **Income:** CONTINGENT on Retro9000 awarding the infra/instrumentation angle. Not guaranteed.
- **Cost to run:** ~$57/wk (8 AVAX) + VPS hosting (we already run 24/7 infra, ~$0 marginal).
- **Breakeven:** needs a Retro9000 award ≥ the rental cost. A small award (>$57) flips it net-positive.

### Gate / next
- Only pursue if we target the **Infrastructure Tooling** round AND can demonstrate the agent actually runs the validator (uptime, monitoring) — not just pay to rent it.
- **Needs Jordan:** go/no-go on a 1-2 week PAYG experiment when R6/infra round timing is confirmed. Do NOT log this as recurring yield — it's a conditional grant play.
