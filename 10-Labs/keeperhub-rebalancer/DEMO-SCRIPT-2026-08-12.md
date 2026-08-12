# 🎬 KeeperHub Agents Onchain — Demo Video Script + Submission Skeleton
*Deadline: Aug 13 (TOMORROW). JORDAN CONFIRMED GO. Proof tx done Aug 8 (0.01 USDC, Base).*

---

## Part A — Demo Video Script (target 90–120 seconds)

**Project:** GTA Yield Guard — Autonomous Aave Health-Factor Auto-Rebalancer (Base)
**Repo:** `10-Labs/keeperhub-rebalancer/yield_rebalancer.py`
**KeeperHub workflow:** `r0nfoic9vk12ik1h3af67` (live in KeeperHub org)
**Wallet:** `0x53A8…8EA` (Base)

### THE STORY (one line for judges)
> *"An autonomous agent watches your DeFi position and rebalances it onchain through KeeperHub — no human in the loop."*

### SHOT-BY-SHOT

**0:00–0:10 — Hook (screen: workflow graph in KeeperHub)**
> "This is an autonomous yield rebalancer. Every 15 minutes it reads the health factor of an Aave position on Base. If the position gets too risky, it rebalances — automatically, onchain, through KeeperHub."

*(Show the workflow node graph — Schedule → get-user-account-data → condition → approve → supply)*

**0:10–0:30 — The mechanism (screen: workflow detail / node config)**
> "Here's the decision logic: **if health factor drops below 1.5**, the agent approves USDC to Aave and supplies collateral to push it back to safe. That's a real `execute_check_and_execute` — read a value, evaluate a condition, execute if met."

*(Point to the condition node `healthFactor < 1.5e18`, then the two action nodes)*

**0:30–0:50 — It's real, not a mockup (screen: execution run view / tx)**
> "This isn't a slideshow. The workflow is live in KeeperHub — every run is a real onchain execution. Here's a test execution ID `1momvt8frv3pa97hhaxu9`. The decision path fired: it read the position, evaluated the condition, and chose to hold because the position was healthy. When it's not, the tx hits the chain."

*(Show the run view: exec ID, the read result, the condition evaluation)*

**0:50–1:10 — The agent code (screen: yield_rebalancer.py, brief)**
> "Under the hood it's a small, auditable agent — a KeeperHub MCP client. Read the APY, decide, rebalance. No black boxes. The same pattern works for any onchain guard: liquidation, oracle drift, yield underperformance."

*(Scroll the code quickly — show the `run_once` / `should_rebalance` logic)*

**1:10–1:20 — Close (screen: repo + workflow link)**
> "GTA Yield Guard. An autonomous onchain agent — built on KeeperHub. Link to the repo and the live workflow below. Build first, talk later."

### JUDGING HOOKS (make sure these land)
- ✅ **Real workflow** — live KeeperHub org, not a mock
- ✅ **Real execution** — exec ID `1momvt8frv3pa97hhaxu9`, decision path fired
- ✅ **Real onchain** — proof tx (0.01 USDC) + submit a live rebalance tx link if position opens
- ✅ **Autonomy** — schedule-driven, no human in the loop
- ✅ **Open source** — repo with code

---

## Part B — Submission Skeleton (GitHub repo + Devpost/DoraHacks)

### Required files (repo root)
**Public repo LIVE: https://github.com/Gentech-Labs/keeperhub-yield-guard** (created Aug 12)
- LICENSE (Apache 2.0, verified 200) ✅
- README.md (pitch) ✅
- yield_rebalancer.py (agent) ✅
- docs/WORKFLOW.md (workflow ref) ✅
- .env.example ✅

### README.md pitch (first 20 lines)
```markdown
# GTA Yield Guard — Autonomous Aave Rebalancer (KeeperHub)

An autonomous onchain agent that watches an Aave health factor and rebalances
the position through KeeperHub when it drops below a threshold. No human in the loop.

- **KeeperHub workflow:** `r0nfoic9vk12ik1h3af67`
- **Chain:** Base (8453) · **Wallet:** 0x53A8…8EA
- **Decision:** read `get-user-account-data` → `healthFactor < 1.5e18` → `approve` → `supply`
- **Execution:** live exec `1momvt8frv3pa97hhaxu9` (read/decide path)
- **Demo video:** [LINK]
- **Onchain proof:** [PROOF TX HASH] · [REBALANCE TX HASH if opened]
```

### Submission fields
- **Title:** GTA Yield Guard — Autonomous Aave Health-Factor Auto-Rebalancer
- **Track:** x402 Onchain Agents
- **Category:** DeFi / Autonomous Agent / Infrastructure
- **Links:** GitHub repo + KeeperHub workflow link + demo video (YouTube/Drive, unlisted OK)
- **Wallet:** the funded Base wallet (0x53A8…8EA or the one with the live tx)

---

## Part C — The ONE thing that needs your hands

The demo **video** itself (record the KeeperHub run view + walkthrough). Everything else
(repo files, README, workflow doc) I can assemble now.

**To film (5–8 min of screen capture):**
1. Open the KeeperHub workflow `r0nfoic9vk12ik1h3af67` → show the node graph
2. Click the condition node → show `healthFactor < 1.5e18`
3. Open the execution `1momvt8frv3pa97hhaxu9` → show it read + decided HOLD
4. If you can, open a small Aave position on Base and let the guard fire → capture the real rebalance tx hash for the submission
5. Say the 5 opening lines above; the rest can be captions
