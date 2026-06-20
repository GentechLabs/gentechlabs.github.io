# Sana API Research — Earn → Store → Spend Loop

**Date:** June 20, 2026
**Status:** Research Complete
**Priority:** High (completes the full agent economy loop)

---

## What Is Sana?

**Sana Company** (formerly Sanafi Onchain) builds the "money layer of the agentic economy" — a self-custody Solana wallet with Visa Signature card, a neobank API for AI agents, and an onchain perpetuals DEX.

- **Website:** [sana.company](https://sana.company) / [sana.bot](https://sana.bot)
- **Team:** Ex-Coinbase, Meta, KyberSwap, StraitsX, AstraTech, Fasset
- **Status:** 12 months bootstrapped, live on iOS, Android, Solana Seeker
- **Chain:** Solana (Sana Chain coming soon)
- **Native asset:** USDC (via Circle partnership)
- **Token:** $SANA (Solana + Sana Chain)

---

## Product Suite

### 1. Sana Money App (sana.money)
Neobank for humans — iOS/Android/Seeker. Self-custody wallet + Visa card + DeFi yield.

### 2. Sana Bot API (sana.bot)
Developer-facing agent banking API. This is what we'd integrate.

**Seven Agent Skills:**

| # | Skill | Status | Description |
|---|-------|--------|-------------|
| 1 | **Visa Signature Card** | ✅ LIVE | Self-custody card issued by Rain (Visa Principal Member) |
| 2 | **Self-Custody Wallet** | ✅ LIVE | Agent-held keys, A2A transfers, signing |
| 3 | **On/Off-Ramp** | ✅ LIVE | Fiat ↔ stablecoin via integrated partners |
| 4 | **Payments & Privacy** | ✅ LIVE | x402 + MPP protocol support |
| 5 | **Trading** | ✅ LIVE | Onchain spot & perps execution |
| 6 | **Prediction Markets** | ✅ LIVE | Autonomous position taking |
| 7 | **Yield & Investment** | ✅ LIVE | Idle stablecoin yield strategies |

### 3. Sana Perps Trade
Onchain perpetuals DEX.

---

## Agent Integration (sana.bot)

### Supported Interfaces
- Sana App
- **Hermes** ✅ (listed as supported)
- Claude Code
- Codex
- Openclaw
- Cursor

### Supported Protocols
- Jupiter (swaps)
- Meteora (liquidity)
- Sanctum (staking)

### Natural Language Commands
```
sana.swap     — "Swap 500 USDC to SOL and stake on Sanctum"
sana.transfer — "Send 150 USDC to vendor@example.com"
sana.set_controls — "Set $25/day budget, $5 per-tx limit, 3 approved domains"
```

### Flow
```
Machine earns onchain (T+0s) → Sana routes (T+2s) → Human spends via Visa (T+5s)
```

---

## Partners & Infrastructure

| Partner | Role |
|---------|------|
| **Solana** | Base chain |
| **Circle** | USDC issuer |
| **Rain** | Visa Principal Member (card issuance) |
| **Privy** | Wallet infrastructure |
| **Bridge** | Payment rails |
| **Jupiter** | DEX aggregation |
| **Meteora** | Liquidity |
| **Sanctum** | Staking |

---

## Licensing & Compliance

- **Card issuance:** Via Rain, a Visa Principal Member — Sana doesn't need its own Visa license
- **KYC:** Handled by Sana's compliance layer (agents can't pass KYC themselves — Sana acts as the compliance wrapper)
- **Regulatory:** Bootstrapped 12 months, targeting SEA/MENA/LATAM markets
- **Self-custody:** Keys held by agent/human, not Sana

---

## Pricing & Fees

| Item | Cost |
|------|------|
| **ARPA (Avg Revenue/Agent)** | ~$100/yr per agent |
| **Developer overhead (today vs Sana)** | ~$1,000/yr → ~$100/yr (10x cheaper) |
| **API fees** | Micro-fees on A2A routing + execution |
| **Card interchange** | Standard Visa interchange on real-world spend |
| **Yield spread** | Spread on idle stablecoins via integrated DeFi |

**Note:** Specific API pricing tiers not yet public. The pitch deck targets $100M ARR at 1M agents.

---

## Integration Path for GenTech

### The Loop
```
DeFi Yield (LP fees, staking) → Sana Wallet (USDC storage) → Visa Card (real-world spend)
```

### Integration Options

**Option A: Hermes Skill (Recommended)**
- Sana already lists Hermes as a supported interface
- Install their SKILL.md → get sana.swap, sana.transfer, sana.set_controls
- Zero custom code — just install and configure

**Option B: API Integration**
- Build custom Sana API client into Agent Kit
- More control, but more maintenance
- Wait for public API docs (currently gated)

**Option C: x402 Native**
- Sana supports x402 + MPP payments natively
- Could route GenTech agent payments through Sana's rails
- Natural fit with our existing x402 stack

### What We Need to Do
1. **Create a Sana account** (sana.bot/gateway) — email signup
2. **Get API credentials** — client_id + client_secret
3. **Install Hermes skill** (if available) or build API client
4. **Test flow:** Earn USDC via DeFi → Store in Sana wallet → Spend via Visa card
5. **Configure spend controls** — budget limits, approved merchants

### Blockers
- [ ] Sana account creation (needs Jordan's email)
- [ ] API key provisioning (may require approval/application)
- [ ] Card availability check (Visa Signature may be geo-restricted to SEA)
- [ ] Fee structure clarity (public pricing not yet available)

---

## Competitive Landscape

| Platform | Card | Agent API | Self-Custody | x402 | Yield |
|----------|------|-----------|--------------|------|-------|
| **Sana** | ✅ Visa Signature | ✅ Native | ✅ | ✅ | ✅ |
| Jupiter Card | ✅ Visa | ❌ | ✅ | ❌ | ❌ |
| Phantom | ❌ | ❌ | ✅ | ❌ | ❌ |
| Slash | ✅ Visa | ✅ | ❌ | ❌ | ✅ |
| Coinbase | ✅ Visa | ❌ | ❌ | ❌ | ✅ |

**Sana's edge:** Only platform with native agent API + self-custody + Visa card + x402 support.

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| **Geo-restriction** | Medium | Card may be SEA-first; US availability unclear |
| **Regulatory** | Medium | Bootstrapped, not yet Series A; regulatory posture TBD |
| **Dependency** | Low | Self-custody means we can exit; keys are ours |
| **Card issuance** | Low | Rain is Visa Principal Member; infrastructure is solid |
| **API maturity** | Medium | Still actively developing; may have breaking changes |

---

## Recommendation

**Integrate via Hermes skill first.** Sana already supports Hermes, has a live Visa card, and the flow (earn → store → spend) is exactly what GenTech needs. The 10x cost reduction vs. self-managed agent wallets makes this a no-brainer.

**Next step:** Jordan creates a Sana account, we get API credentials, and I install the Hermes skill. Test with a small USDC amount to validate the full loop.

---

*Research compiled by Gentech | June 20, 2026*
