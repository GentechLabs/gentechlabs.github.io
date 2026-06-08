# 🚢 Ship Mode Checklist — All Hackathons

**Last updated:** 2026-04-19
**Mode:** SHIP > BUILD — Submit what we have, stop polishing

---

## 🔴 ARC Hackathon — Apr 25 (6 days)

**Status:** Code done, content ready, needs deployment + recording

### Code
- [x] `AgentEscrow.sol` — core escrow with USDC + EIP-712
- [x] `DisputeResolver.sol` — on-chain dispute resolution
- [x] `X402PaymentHandler.sol` — nanopayment verification

### What's Ready
- [x] Video script (2-min, timed) → `08-Daily/content-drafts/arc-hackathon-video-script.md`
- [x] Pitch script → `08-Daily/content-drafts/arc-hackathon-pitch.md`
- [x] README → `repos/arc-hackathon/README.md`

### What's Still Needed
| Item | Who | Status |
|------|-----|--------|
| Deploy to Arc testnet | Dmob | ⏳ Pending |
| Record 2-min demo video | Jordan | ⏳ Use Desmond's script |
| Fill lablab.ai submission form | Jordan | ⏳ Use pitch script as copy |
| Upload video + repo link | Jordan | ⏳ After recording |
| GitHub: branches, README polish | Dmob | ⏳ Quick polish |

### Jordan's ARC Tasks (if not done)
- [ ] Confirm signup at lablab.ai
- [ ] Review ARC submission requirements on lablab.ai
- [ ] Record video using Desmond's script

---

## 🟠 Kite AI — Apr 26 (7 days)

**Status:** GenLayer contracts written, needs fixtures + deploy

### Code
- [x] `kite_agent_escrow.py` — GenLayer intelligent contract
- [x] `kite_sla_enforcement.py` — SLA enforcement logic

### What's Ready
- [x] README → `08-Daily/content-drafts/kite-ai-submission-readme.md`
- [x] Demo outline (2-min with dispute flow)

### What's Still Needed
| Item | Who | Status |
|------|-----|--------|
| Fix conftest.py (direct_vm fixture) | Dmob | 🔴 BLOCKING |
| Deploy to Kite testnet | Dmob | ⏳ After fixtures |
| Record 2-min demo video | Jordan | ⏳ Use Desmond's outline |
| Submit to Kite portal | Jordan | ⏳ After deployment |

### Dmob's Kite Tasks
- [ ] Fix GenLayer test fixtures (conftest.py with direct_vm, direct_deploy, direct_alice)
- [ ] Run test suite, verify all pass
- [ ] Deploy to Kite testnet
- [ ] Verify deployment on explorer

---

## 🟡 ETHGlobal Open Agents — May 3 (14 days)

**Status:** 3 contracts, 44/44 tests passing, deploy script ready

### Code
- [x] `AgentRegistry.sol` — ERC-721 agents with 0G skill hashes
- [x] `TaskManager.sol` — task lifecycle with escrow
- [x] `AgentKeeper.sol` — condition-based autonomous execution
- [x] Deploy script ready

### What's Ready
- [x] README (being replaced by Desmond's polished version)
- [x] Pitch script → `08-Daily/content-drafts/ethglobal-submission-pitch.md`
- [x] Demo video script (3-min, timed) → `08-Daily/content-drafts/ethglobal-demo-video-script.md`
- [x] Polished README → `08-Daily/content-drafts/ethglobal-readme-draft.md`

### What's Still Needed
| Item | Who | Status |
|------|-----|--------|
| 0G Storage integration | Dmob | ⏳ Phase 3 |
| KeeperHub integration | Dmob | ⏳ Phase 3 |
| Deploy to 0G testnet | Dmob | ⏳ After integrations |
| Record 3-min demo video | Jordan | ⏳ After deployment |
| Fill ETHGlobal submission form | Jordan | ⏳ Use pitch script |

### Jordan's ETHGlobal Homework (CRITICAL — do before Apr 23 brainstorm)
- [ ] Join ETHGlobal Discord: https://discord.gg/ethglobal
- [ ] Claim 0G testnet tokens: https://faucet.0g.ai
- [ ] Sign up for KeeperHub: https://app.keeperhub.com
- [ ] Get KeeperHub API key (from dashboard)
- [ ] Install MetaMask + add 0G Galileo network
  - Chain ID: 16602
  - RPC: https://evmrpc-testnet.0g.ai
- [ ] Attend brainstorm session: **Apr 23 @ 3pm EDT**

### Dmob's ETHGlobal Tasks
- [ ] Integrate 0G Storage SDK (@0glabs/0g-ts-sdk)
- [ ] Integrate KeeperHub MCP
- [ ] End-to-end demo flow
- [ ] Deploy to 0G testnet (Chain ID: 16602)
- [ ] Security audit pass

---

## 🟢 Colosseum Frontier — May 11 (22 days)

**Status:** Not started, still planning

### Not Started Yet
- [ ] Solana Anchor project scaffold
- [ ] AgentRegistry program
- [ ] JobEscrow program
- [ ] AgentBrain program
- [ ] RiskOracle program
- [ ] Reputation program
- [ ] TaskManager program

### Kickoff: After ARC/Kite/ETHGlobal submission

---

## 📋 Submission Matrix — Quick Reference

| Hackathon | Code | Content | Deploy | Demo | Submit | Ship By |
|-----------|------|---------|--------|------|--------|---------|
| **ARC** | ✅ | ✅ | ⏳ | ⏳ | ⏳ | Apr 25 |
| **Kite** | ✅ | ✅ | ⏳ | ⏳ | ⏳ | Apr 26 |
| **ETHGlobal** | ✅ | ✅ | ⏳ | ⏳ | ⏳ | May 3 |
| **Frontier** | ❌ | ❌ | ❌ | ❌ | ❌ | May 11 |

---

## 🎯 Ship Mode Rules

1. **Code stops, packaging starts** — If tests pass and contracts compile, it's done. No more optimization.
2. **Submit imperfect** — A working demo with rough edges > a polished spec doc with no deployment
3. **One video per hackathon** — Jordan records once using Desmond's script. No reshoots.
4. **Deploy early** — Get addresses on-chain, update README with contract addresses, submit
5. **Demo video is 50% of judging** — Prioritize recording over code polish

---

#ship-mode #hackathon #checklist #organization
