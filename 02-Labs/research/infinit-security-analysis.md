# INFINIT — Prompt-to-DeFi Security Analysis

> **Analyst:** DMOB (Labs)  
> **Date:** April 29, 2026  
> **Status:** Initial Research  
> **Verdict:** Proceed with Caution

---

## Overview

INFINIT is an AI-powered DeFi platform that lets users describe strategies in plain English and executes them across protocols and chains. Non-custodial. 18+ AI agents across 14+ chains.

**Website:** infinit.tech  
**IN Token (Ethereum):** `0x61fac5f038515572d6f42d4bcb6b581642753d50`  
**IN Token (BSC):** `0x61fac5f038515572d6f42d4bcb6b581642753d50` (same address)  
**Max Supply:** 1,000,000,000 IN (fixed, non-inflationary)  
**TVL:** ~$30.8M  
**Transactions:** ~333K  

---

## Security Model (What's Good)

1. **Non-custodial** — Users sign txs directly, assets never leave wallets ✅
2. **Deterministic execution** — AI generates transaction code, not runtime interpretation — eliminates hallucination risk at execution layer ✅
3. **Multi-layer verification:**
   - Backend testing before strategies reach users
   - Pre-execution simulation with full transparency (protocol, tokens, gas, outcomes)
   - User explicit approval required for every execution
4. **Real-time monitoring** — Users observe each step during execution
5. **PeckShield audit** confirmed on website FAQ ✅
6. **Fixed supply** — 1B IN tokens, non-inflationary ✅

---

## Red Flags & Concerns

### 🔴 Critical

1. **No open-source contracts** — No public GitHub with Solidity source code found. Cannot verify what's actually deployed. Closed-source + requesting transaction signatures = major trust assumption.

2. **No access control documentation** — No info on admin keys, multisig, timelock, or governance contracts. Who can upgrade? Who has admin powers? Who can pause?

### 🟠 High

3. **Proxy patterns unknown** — Cannot determine if upgradeable (UUPS/Transparent/Beacon) without source code or block explorer access. An upgradeable contract with opaque admin controls is a significant risk.

4. **AI agent trust assumption** — Even with deterministic execution, users must trust that the generated code accurately represents their intent. The backend verification layer is opaque — no way to independently verify.

5. **Same contract address on ETH and BSC** — Suggests CREATE2 deterministic deployment or cross-chain minting mechanism. Needs investigation for cross-chain security implications.

### 🟡 Medium

6. **Early-stage protocol** — ~$30.8M TVL, 333K transactions. Less battle-tested than established DeFi protocols.

7. **No formal audit report published** — Website claims PeckShield audit but no public report available for independent review.

---

## Supported Chains (14+)

Arbitrum, Base, BeraChain, BSC, Ethereum, HyperEVM, Hyperliquid, Katana, Mantle, Monad, Optimism, Plasma, Solana, Sonic

---

## Protocol Integrations (35+)

Aave, Aerodrome, Compound, Dolomite, Euler, Hyperliquid, Morpho, Pendle, Sushiswap, Uniswap, Venus, and more.

---

## What's Needed for Deeper Analysis

- [ ] Published contract source code (Solidity)
- [ ] Multisig/timelock documentation
- [ ] Full PeckShield audit report
- [ ] Admin key documentation
- [ ] Proxy pattern identification
- [ ] Access control architecture review
- [ ] Cross-chain bridge security model

---

## Verdict

**Proceed with Caution.** The concept is compelling — "DeFi's Claude moment" — and the non-custodial + deterministic execution model is sound in principle. However, closed-source contracts with no access control transparency is a dealbreaker for serious capital allocation without further due diligence.

**Next Steps:**
- Monitor for open-source contract releases
- Request audit report from team
- Track on-chain activity for admin/key management patterns
- Re-evaluate when transparency improves

---

*Saved by DMOB — Labs Department*
