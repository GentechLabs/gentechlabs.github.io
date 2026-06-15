# Mantle Turing Test X Thread — #MantleAIHackathon

## Tweet 1

AI agents have no wallets, no identity, and no autonomous execution on-chain.

We built that.

Introducing Agent Economy — a 6-contract system giving AI agents identity, reputation, escrow payments, and autonomous triggers on @MantleLabs.

🧵 #MantleAIHackathon

---

## Tweet 2

The architecture:

→ AgentRegistry: on-chain identity + 0-10K reputation
→ JobEscrow: trustless payments with dispute resolution
→ AgentKeeper: autonomous condition → action triggers
→ ERC8004Adapter: identity NFTs via ERC-8004 standard
→ Zerion + GoldRush adapters: DeFi risk data feeds

6 contracts. ~650 lines. 14 tests passing.

---

## Tweet 3

The ERC-8004 integration is the key.

Every agent gets an on-chain Identity NFT on Mantle. Their reputation isn't locked in one protocol — it travels with the NFT across DeFi, job markets, and DAOs.

IdentityRegistry: 0x8004...BD9e
ReputationRegistry: 0x8004...8713

Portable agent reputation. Finally.

---

## Tweet 4

How agents become autonomous:

1. Register condition in AgentKeeper (price threshold, time delay, custom)
2. Oracle adapters push live data (Zerion portfolio risk, GoldRush analytics)
3. When condition fires → keeper executes the action automatically

Agents don't wait for humans. They set rules. The chain enforces them.

---

## Tweet 5

The full demo flow:

1️⃣ Agent registers with skills (IPFS hash)
2️⃣ Gets ERC-8004 identity NFT
3️⃣ Client creates escrow job (ETH locked)
4️⃣ Agent accepts → completes → payment auto-released
5️⃣ Reputation score updates on-chain

One agent lifecycle. Fully trustless. Fully autonomous.

---

## Tweet 6

The big picture:

Agent staking with MNT → reputation-weighted job selection → cross-chain portability → DAO governance → DeFi integration

Agents managing LP positions, rebalancing portfolios, earning and spending — all verifiably on-chain.

This is the infrastructure layer for the agentic economy.

---

## Tweet 7

Built for @MantleLabs Turing Test — Agentic Wallets & Economy track.

6 contracts. 14 tests. Full deployment scripts for Mantle Sepolia.

Agents need an economy. We built the infrastructure.

Repo: github.com/ProtoJay4789/mantle-turing-test

#MantleAIHackathon #MantleTuringTest #ERC8004 #AgenticAI
