# Due Diligence Report — 2026-04-17

**Chain:** Gentech Due Diligence (YoYo → Dmob)
**Date:** Thursday, April 17, 2026

---

## 📋 NEW FINDINGS:

• **Kuberna Labs** — 🟠 MEDIUM-HIGH — AI agent execution layer with 18 unaudited Solidity contracts. Strong code quality but critical centralization risks (owner can mint tokens, pause all operations, no timelocks). Full audit completed and written to 06-Security/Kuberna Labs-audit.md.

## 🚩 RED FLAGS FOUND:

• **Kuberna Labs** — Owner can mint up to 1B governance tokens with no vesting enforced on-chain. Treasury proposals are owner-only. CrossChainRouter has no timelock on admin functions. Single maintainer (Kennedy Kawacuk) = bus factor of 1.

• **Drift Protocol** — $285M exploit (Apr 1, 2026) via DPRK social engineering. 6-month infiltration operation — hackers befriended team members at conferences, deposited $1M, then used compromised admin key + oracle manipulation. Not a code bug — a human compromise. (Source: rekt.news)

• **Resolv Labs** — $25M loss (Mar 22, 2026) from compromised private key. Attacker minted 80M USR tokens with no oracle check or mint cap. Hardcoded oracles kept feeding broken markets. Supply chain attack vector.

• **Solv Protocol** — $2.73M drained from BRO vault via callback/reentrancy in unaudited ERC-3525 contract. 22 loops turned 135 BRO into 567M tokens in single tx. Attacker exited to Tornado Cash.

• **Sumsub (KYC Provider)** — 18-month undetected breach (Jul 2024 → Feb 2026). Opaque ownership structure. The company verifying identities for 4,000+ crypto clients couldn't verify its own security. Relevant for any protocol using Sumsub for compliance.

## ✅ CLEAN PROTOCOLS:

• **Kuberna Labs (code quality)** — Well-structured codebase, uses OpenZeppelin imports, ReentrancyGuard on financial contracts, Chainlink oracle integration with 1-hour timelock on PriceOracle. Vesting has 90-day cliff + 365-day schedule. Multisig contract is properly implemented. MIT licensed and open source.

• **LFJ (formerly Trader Joe)** — AVAX/USDC 5bps pool showing strong metrics ($3.5M liquidity, 93% APR). YoYo analysis pending but no security concerns noted. Established platform on Avalanche.

## ⚠️ CRITICAL ALERTS:

• **Social engineering is the #1 attack vector in 2026.** Drift ($285M) and Radiant Capital precedent show DPRK is running sustained human intelligence operations against DeFi teams. Recommend all Gentech-affiliated protocols implement:
  - Hardware wallet requirements for all admin keys
  - Multi-sig with geographic distribution
  - Background checks on new hires with contract access
  - No single-person access to critical infrastructure

• **Unaudited contracts in production remain the biggest code risk.** Solv's BRO vault and Kuberna's 18 contracts both lack audits. Any protocol deploying unaudited code with user funds is a ticking time bomb.

---

## Action Items:
1. ✅ Kuberna Labs audit complete — vault note updated (#needs-audit → #audited)
2. 📝 Share audit findings with Kennedy (Kuberna founder) — offer to contribute timelock pattern
3. 👀 Monitor Drift Protocol recovery and governance response
4. 🔍 LFJ AVAX/USDC analysis still pending from YoYo
5. 📊 No new #needs-audit protocols in vault — pipeline clear
