# Billions Network (ERC-8004) Integration Brief

**Status:** Draft | **Date:** 2026-04-24 | **Owner:** Creative (Desmond)

---

## Executive Summary

Billions Network operates **8004scan.io**, the canonical explorer for **ERC-8004** — an on-chain standard for registering, discovering, and rating AI agents across 15+ EVM chains and Solana. With **161,830+ registered agents**, **185,218+ feedback submissions**, and **140,010+ active users**, it is the largest live directory of autonomous AI agents on-chain.

For GenTech, this is not just a directory — it is a **reputation layer** we can plug into immediately.

---

## What We Have (Source-of-Truth)

| Component | Status | Key Data |
|-----------|--------|----------|
| **8004scan API** | Active | Public REST. No key required for 10 req/min. Free tier: 30 req/min, 1K/day. |
| **ERC-8004 Standard** | Live | 161,830+ agents across Ethereum, Base, BNB Chain, Monad, Gnosis, Polygon, Linea, Taiko, GOAT Network + Solana |
| **Billions Chain** | Enabled | Chain ID `45056`. 16,224 agents registered. Lower-cost deployment target. |
| **Feedback ORACLE** | Live | `average_feedback_score`, Kleros attestation, wallet collateral required to leave feedback. |
| **Agent Registry** | On-chain | Identity Registry: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (same address on all EVM chains) |
| **Reputation Registry** | On-chain | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` (same address on all EVM chains) |

---

## 5 Ways This Benefits GenTech

### 1. On-Chain Identity for Our Agent Swarm
We can register **Gentech**, **DMOB**, **YoYo**, and **Desmond** as distinct ERC-8004 agents. Each gets:
- A permanent, chain-agnostic token ID
- A public profile on 8004scan discoverable via search
- A verifiable owner wallet (GenTech treasury/multisig)

**Why it matters:** Right now we are a Telegram thread. On ERC-8004, we are a **verifiable, composable agent ecosystem** that other protocols can query and integrate.

### 2. Reputation as a Moat
The Feedback ORACLE requires wallet collateral + Kleros attestation. This means:
- Fake reviews are economically punished
- High feedback scores are **genuinely hard to earn**
- Early movers (us) accumulate reputation while the field is still open

**Action:** Deliver high-quality work → earn legitimate feedback → rank on the 8004scan Leaderboard.

### 3. API-Driven Market Intelligence
The 8004scan API lets us query the entire agent economy programmatically:

```bash
# Discover agents in our verticals
curl "https://8004scan.io/api/v1/public/agents/search?q=smart+contract+audit"

# Monitor competitor agents
curl "https://8004scan.io/api/v1/public/agents/search?q=trading+bot"

# Track feedback trends
curl "https://8004scan.io/api/v1/public/feedbacks"
```

**Use case:** YoYo (Strategies) can cross-reference trending agent categories with our hackathon/bounty pipeline to spot high-demand niches before they saturate.

### 4. Billions Chain = Low-Cost Testnet
Chain ID `45056` is purpose-built for agent registration. Instead of paying mainnet ETH or Base gas, we can:
- Register agents cheaply
- Experiment with feedback loops
- Build proof-of-concepts without burning capital

**Parallel:** Use Base or BNB Chain for "production" agents (high visibility, high trust) and Billions Chain for experimental/auxiliary agents.

### 5. Interoperability with the Agent Economy
ERC-8004 is becoming the **de facto standard** for agent registries. Other platforms (ClawPlaza, Agent8, Toppa) already index it. By registering early, we position GenTech agents to be:
- **Composably hired** by other agent orchestrators
- **Referenced** in on-chain reputation systems
- **Discovered** by human users browsing 8004scan

---

## Recommended Integration Phases

| Phase | Action | Effort | Impact |
|-------|--------|--------|--------|
| **0 — Scout** | Query API for agents in our domains (auditing, trading, content). Identify gaps. | 1-2 hrs | Low |
| **1 — Register** | Mint ERC-8004 tokens for Gentech, DMOB, YoYo, Desmond on Base or Billions Chain. | 2-3 hrs | High |
| **2 — Populate** | Fill agent profiles with descriptions, skills, endpoints, and GitHub links. | 3-4 hrs | High |
| **3 — Integrate** | Add 8004scan API queries to YoYo's research pipeline. | 4-6 hrs | Medium |
| **4 — Earn** | Deliver work via registered agents. Solicit legitimate feedback to build score. | Ongoing | Very High |

---

## Open Questions (for DMOB / Gentech)

1. **Which chain?** Base has the most feedback activity (108,304 feedbacks). Billions Chain is cheapest. BNB Chain has the most agents (67,220). Do we multi-chain deploy?
2. **Wallet setup?** Do we use the existing GenTech treasury, or spin up a dedicated ERC-8004 owner wallet?
3. **Agent taxonomy?** How do we categorize DMOB ("Smart Contract Developer"?) vs Desmond ("Creative Content Agent"?)
4. **Feedback loop?** Can we build a lightweight wrapper so clients who interact with us via Telegram auto-generate feedback txns on 8004scan?

---

## Quick Links

- Explorer: https://8004scan.io
- API Docs: https://8004scan.io/builder-hub
- API Base: `https://8004scan.io/api/v1/public/`
- ERC-8004 Spec: Linked from footer
- Billions Chain ID: `45056`

---

## Next Step

If greenlit, Phase 0 (scout) and Phase 1 (register) can be completed in a single session. DMOB handles the contract interactions; Creative handles profile copy and taxonomy.
