# ETHGlobal Open Agents — YoYo Research Memo

**Date:** 2026-04-19
**Horizon:** May 3, 2026 submission (14 days)
**Prize Pool:** $50K+ total | $15K 0G (primary) + $5K KeeperHub (secondary)
**Confidence:** High on architecture, medium on competitive landscape (web tools expired)

---

## Thesis

**Build an on-chain agent economy using 0G for storage/compute + KeeperHub for autonomous execution.** Most teams will build trading bots or simple agent wrappers. We build infrastructure: agent registry → task marketplace → autonomous execution → persistent memory.

---

## Current State Assessment

### ✅ What's Done
- Foundry project scaffolded at `~/projects/ethglobal-open-agents/`
- 3 core contracts: AgentRegistry, TaskManager, AgentKeeper
- 3 interfaces defined
- 7/7 tests passing
- GitHub repo: https://github.com/ProtoJay4789/ethglobal-open-agents
- 0G repos cloned: agent-skills, agenticID-examples, 0g-memory
- Architecture diagram locked

### ⚠️ What's Blocked
- **Jordan action:** Get KeeperHub API key (app.keeperhub.com)
- **Jordan action:** Claim 0G testnet tokens (faucet.0g.ai)
- **Jordan action:** Sign up for ETHGlobal Open Agents by Apr 24

### 🔄 What's Next (Phase 2: Apr 20-28)
1. Deploy contracts to 0G Galileo testnet
2. Integrate 0G Storage SDK — upload/download agent skills
3. Integrate KeeperHub check-and-execute pattern
4. Build end-to-end demo flow
5. Security audit pass
6. Record 2-3 min demo video
7. Write README with deployed addresses

---

## Competitive Edge Analysis

### What Others Will Build (Consensus)
- Uniswap trading bots (oversubscribed)
- Simple agent wrappers (LLM → API → on-chain tx)
- Agent chatbots with no real on-chain logic
- Multi-agent demo with hardcoded flows

### What Makes Us Different
1. **Deep 0G integration** — most will use it superficially (upload a file). We store agent skills as Merkle-rooted JSON, use INFT (ERC-7857) for agent ownership, use Compute for inference
2. **KeeperHub autonomous execution** — agents trigger their own on-chain actions via `check-and-execute`, not manual triggers
3. **Real blockchain logic** — task lifecycle with escrow, dispute resolution, reputation tracking — things that can't work off-chain
4. **Multi-sponsor synergy** — 0G + KeeperHub is a unique combination nobody else will have
5. **Built on existing AAE architecture** — we're not starting from scratch, we're plugging into a proven framework

### Risk: What Could Go Wrong
- **0G testnet instability** — new chain, may have downtime during hackathon
- **KeeperHub API limits** — 60 req/min could bottleneck demo
- **Scope creep** — trying to do all 4 sponsors instead of going deep on 2
- **Demo video quality** — rough video kills async round chances
- **Jordan availability** — needs to handle sign-up, API keys, video recording

---

## Sponsor Track Strategy

### 0G ($15K) — Go DEEP
**Integration points (ranked by difficulty):**
1. **Storage (easy)** — Upload agent skill JSON → get root hash → store in AgentRegistry ✅ Do this first
2. **INFT/ERC-7857 (medium)** — Mint agent identity as INFT → proves agent ownership ✅ Differentiator
3. **Compute (medium)** — Route agent inference requests through 0G Compute → TEE-verified results ✅ Nice demo
4. **Chain (trivial)** — Deploy on 0G testnet → already planned ✅ Table stakes

**Minimum for 0G prize:** #1 + #4
**Competitive for 0G prize:** #1 + #2 + #4
**Winner-level:** All four

### KeeperHub ($5K) — Go DEEP
**Integration points:**
1. **MCP server** — Connect Claude/Codex to KeeperHub via MCP → agent can execute on-chain actions
2. **check-and-execute** — Register a condition → KeeperHub monitors → auto-executes when triggered
3. **Para MPC wallets** — Agents execute without exposing private keys

**Minimum for KeeperHub prize:** #1 + #2
**Competitive for KeeperHub prize:** All three

---

## Revised Timeline (14 Days to May 3)

### Week 1: Apr 20-26 (Build Core Integration)
- [ ] **Jordan:** Sign up ETHGlobal, claim 0G tokens, get KeeperHub API key
- [ ] **Dmob:** Deploy contracts to 0G testnet
- [ ] **Dmob:** Integrate 0G Storage SDK (upload agent skills)
- [ ] **Dmob:** Integrate KeeperHub check-and-execute
- [ ] **YoYo:** Monitor sponsor docs for updates, track competitor submissions
- [ ] **Jordan:** Record draft demo video (even if rough)

### Week 2: Apr 27-May 3 (Polish + Submit)
- [ ] **Dmob:** End-to-end demo flow, bug fixes
- [ ] **Dmob:** Security audit (reentrancy, access control, input validation)
- [ ] **Jordan:** Record final demo video (2-3 min, tight)
- [ ] **Dmob:** Write README with architecture + deployed addresses
- [ ] **Jordan:** Submit on ETHGlobal before May 3, 4 PM UTC
- [ ] **All:** Prepare for live judging May 4

---

## Falsifiable Predictions

1. **If 0G testnet goes down for >24h during Week 1**, we need a fallback deployment plan (Base/Arbitrum testnet)
2. **If KeeperHub API is unstable or rate-limited**, we demo with mocked responses and note it in submission
3. **If <50% of teams go deep on any sponsor**, our deep 0G + KeeperHub integration wins the $20K combined
4. **If >80% of teams do Uniswap trading bots**, we automatically stand out by building infrastructure, not trading tools

---

## Action Items for Jordan (This Week)

| Task | Due | Priority |
|------|-----|----------|
| Sign up for ETHGlobal Open Agents | Apr 24 | [P] |
| Claim 0G testnet tokens from faucet | Apr 20 | [P] |
| Get KeeperHub API key (app.keeperhub.com) | Apr 20 | [P] |
| Record draft demo video | Apr 22-24 | [Q] |

---

*Confidence: High on architecture, medium on competitive landscape (web research tools expired — will update when available)*
*Next review: Apr 22 or when Jordan completes sign-up tasks*
