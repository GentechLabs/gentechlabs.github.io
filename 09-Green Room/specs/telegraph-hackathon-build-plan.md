# Telegraph Season I Hackathon — Build Plan

**Source:** [hackathon.telegraphprotocol.com](https://hackathon.telegraphprotocol.com/) · [x402 doc](https://telegraph-2.gitbook.io/telegraph/miner-registry/x402-payment.md) · [YAML standard](https://telegraph-2.gitbook.io/telegraph/miner-registry/yaml-standard.md)
**Date:** 2026-08-06
**Prize:** $15,000 USD across 3 rounds (H1 $5K · H2 $10K · H3 mainnet TBD)
**Timeline:** H1 Aug 17 – Sep 7 (21 days) · H2 mid-Oct · H3 Dec mainnet
**Status:** 🟢 Jordan GO (Aug 6) — register when home. Scoping.

---

## Why we win (this is OUR stack)

- **Telegraph uses x402 natively** — per-request micropayments via the PayAI facilitator, `PAYMENT-SIGNATURE` header, 402 challenge. This is exactly what our gateway already does.
- **Miner track = "wrap any API/model/dataset/tool via a YAML file."** We have a catalog of x402-ready services (token security, wallet analysis, market intelligence, agent discovery, DeFi LP analytics, NFT search, treasury defender, lineage guard).
- **Config-only integration** — write a YAML, register on-chain, done. No greenfield build.
- **First-mover playbook** — we're already live on 7 chains incl Algorand. Telegraph is another venue to be first on, and it validates the "write the rules" thesis.

## The 3 tracks

| Track | What | Judging |
|---|---|---|
| **1 · Miner** (opens Aug 17) | Wrap any API/model/dataset/tool into Telegraph via YAML. Supply layer. | Telegraph ranking/performance, apps built on your miner, requests served, X posts |
| **2 · Script Author** (opens Aug 17) | Write evaluation scripts that score/rank miners. | Automated eval, ranking accuracy, gaming resistance, X posts |
| **3 · Application** (opens after miners/scripts live) | Build products/agents on live miners. | Users, adoption, creativity, must use Telegraph miners |

## Chosen approach

**Primary: Miner Track** — wrap our existing x402 gateway services as Telegraph miners. We already have the APIs; this is YAML + on-chain registration.

**Candidate miners (pick 2-3 strongest):**
1. **Token Security / Rugcheck** — `/v1/security/score/{address}` — high demand, verifiable signal
2. **Market Intelligence** — `/v1/market/price/{symbol}` — simple, high volume
3. **Wallet Analysis** — `/v1/wallet/portfolio/{address}` — verifiable portfolio signal
4. **Agent Discovery** — `/v1/agents/search` — ERC-8004 registry search

**Secondary: Script Author Track** — write an evaluation script that scores miner responses. Natural fit for our compliance/safety playbook angle.

**Tertiary (later): Application Track** — once miners are live, build an agent on top.

## The YAML standard (what we plug in)

```yaml
version: "1"
kind: subnet
id: <assigned>
slug: gentech-token-security
protocol: generic
name: GenTech Token Security
description: Token risk scoring and rugcheck analysis
base_url: https://api.gentechlabs.net
auth:
  type: none
endpoints:
  - path: /v1/security/score/{address}
    external_path: /v1/security/score/{address}
    method: GET
semantics:
  signal_mapping:
    type: token_risk
    confidence_field: risk_score
  supported_intents:
    - token_risk_assessment
    - rugcheck
on_chain:
  min_price_usdc: 0.01
```

## x402 payment (already our stack)

- Telegraph gates subnet calls behind x402 — 402 challenge → pay → retry with `PAYMENT-SIGNATURE` → 200.
- Facilitator: PayAI (`facilitator.payai.network`) — we already use PayAI as our Solana leg.
- Miners set `min_price_usdc` floor at registration (min $0.01, immutable).
- Networks: Base Sepolia (testnet), Polygon (mainnet), Solana Devnet.

## Judging criteria mapping (Miner track)

| Criterion | How we satisfy |
|---|---|
| Telegraph ranking & performance | Real, working x402 services |
| Apps built on your miner | Our own gateway + agent stack can consume them |
| Total requests served | Live services, real demand |
| Progress updates on X | Post the Algorand first-mover + Telegraph miner build |

## Risks

- **Track 1 & 2 open Aug 17** — need to register early for early track access + core team support (private Discord).
- **YAML schema validation** — must match exactly (slug kebab-case, supported_intents required, signal_mapping.type enum).
- **On-chain registration** — needs a wallet + gas on the registration chain.
- **H1 is $5K** — smaller pool, but it's the bootstrap round; H2 ($10K) and H3 (mainnet) are bigger.

## Action items
- [ ] **Jordan:** register at hackathon.telegraphprotocol.com (early = track access + Discord support)
- [ ] **Gentech:** pick 2-3 gateway services → write YAML miners
- [ ] **Gentech:** register miners on-chain, test x402 payment flow
- [ ] **Gentech:** write evaluation script (Script Author track)
- [ ] **Gentech:** post progress on X
