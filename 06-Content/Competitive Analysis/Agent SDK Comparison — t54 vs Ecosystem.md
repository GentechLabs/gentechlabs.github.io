# Agent SDK Comparison — t54 vs. Ecosystem

**Date:** 2026-04-26 (updated with live repo recon)  
**Analyst:** Desmond (Creative) + Gentech (live SDK audit)  
**Scope:** All agent payment/identity SDKs referenced in the GenTech brain

---

## t54 x402-secure SDK — Live Repo Recon (Apr 26)

**Repo:** `github.com/t54-labs/x402-secure` | **Stars:** 25 | **Forks:** 3 | **Last commit:** 6 months ago  
**License:** Apache-2.0 | **Lang:** Python 3.11+ | **PyPI:** `x402-secure` (import: `x402_secure_client`)

### What It Actually Is

x402-secure is **NOT** a standalone payment protocol. It is an **open-source proxy + SDK layer that wraps Coinbase's x402** and injects t54's Trustline risk engine into every transaction.

```
┌─────────────────────────────────────────────┐
│  Your Agent / Merchant Service               │
├─────────────────────────────────────────────┤
│  x402-secure SDK (Python)                    │
│  ├─ BuyerClient / SellerClient              │
│  ├─ OpenAITraceCollector                    │
│  └─ Risk session manager                    │
├─────────────────────────────────────────────┤
│  x402-secure Proxy (:8000)                   │
│  ├─ /risk/session  → Trustline              │
│  ├─ /risk/trace    → Evidence store         │
│  ├─ /x402/verify   → x402 upstream          │
│  └─ /x402/settle   → x402 upstream          │
├─────────────────────────────────────────────┤
│  Coinbase x402 Facilitator (upstream)        │
│  ├─ /facilitator/verify                     │
│  └─ /facilitator/settle                     │
├─────────────────────────────────────────────┤
│  Blockchain (Base/Base Sepolia)              │
└─────────────────────────────────────────────┘
```

### The 4-Phase Flow (from their README)

**Phase 1:** Create risk session (`POST /risk/session`) → returns `sid`  
**Phase 2:** AI interaction + trace collection (`OpenAITraceCollector`) → stream events captured  
**Phase 3:** Store trace (`POST /risk/trace`) → returns `tid`  
**Phase 4:** Execute payment with `X-PAYMENT`, `X-PAYMENT-SECURE`, `X-RISK-SESSION` headers  

### Key Technical Details

| Feature | Implementation |
|---------|---------------|
| **Payment scheme** | `exact` (EIP-3009 authorization) |
| **Chains** | Base, Base Sepolia |
| **Asset** | USDC (`0x036CbD53842c5426634e7929541eC2318f3dCF7e` on Base Sepolia) |
| **Risk levels** | `low` / `medium` / `high` (ENUM) |
| **Trace collector** | OpenAI native today, LangChain/AutoGPT "coming" |
| **Proxy modes** | `PROXY_LOCAL_RISK=1` (local) or forward to `RISK_ENGINE_URL` |
| **Production proxy** | `https://x402-proxy.t54.ai` |
| **Dashboard** | Live risk insights + Coinbase x402 Bazaar leaderboard |

### Buyer Integration (5 min)

```python
from x402_secure_client import BuyerClient, BuyerConfig, OpenAITraceCollector

buyer = BuyerClient(BuyerConfig(
    seller_base_url="https://api.example.com",
    agent_gateway_url="https://x402-proxy.t54.ai",
    buyer_private_key=YOUR_PRIVATE_KEY
))

session = await buyer.create_risk_session(app_id="my-agent-v1")
tracer = OpenAITraceCollector()

# ... run your OpenAI stream with tracer.process_stream() ...

tid = await buyer.store_agent_trace(sid=session['sid'], task="...", events=tracer.events)
result = await buyer.execute_paid_request(endpoint="...", sid=session['sid'], tid=tid)
```

### Seller Integration (10 min)

FastAPI middleware pattern. Checks for `X-PAYMENT`, `X-PAYMENT-SECURE`, `X-RISK-SESSION` headers. Forwards to proxy for `verify_then_settle()`.

### Liability Protection Matrix

| Scenario | Without x402-secure | With x402-secure |
|----------|---------------------|------------------|
| Prompt injection tricks agent | ❌ You pay | ✅ Protected |
| Agent exceeds user intent | ❌ You pay | ✅ Protected |
| Malicious user disputes | ❌ You fight | ✅ Clear evidence |
| Agent makes reasonable decision | ❌ You prove it | ✅ Trace stored |

---

## The Playing Field

The agentic economy has **three layers** of SDK infrastructure. t54 plays in Layer 2, but Layer 1 is commoditizing fast.

```
┌───────────────────────────────────────────────────────┐
│  Layer 3: Application / Service SDKs                     │
│  Dexter (search), Birdeye (data), Corbits (APIs)         │
├───────────────────────────────────────────────────────┤
│  Layer 2: Trust / Identity / Risk SDKs                    │
│  t54 (x402-secure), Zauthx402, Kite Passport              │
├───────────────────────────────────────────────────────┤
│  Layer 1: Payment Protocol SDKs                           │
│  Coinbase x402 (core), PayAI (Solana), CDP Wallet         │
└───────────────────────────────────────────────────────┘
```

---

## Layer 1: Payment Protocol SDKs (The Rail)

### 1. Coinbase x402 (Foundation Standard)
| Attribute | Detail |
|-----------|--------|
| **Package** | `x402-foundation/x402` (moved from `coinbase/x402`, which is now a dev fork) |
| **License** | Apache-2.0 |
| **Languages** | TypeScript (primary), Python, Go |
| **What it does** | Core HTTP 402 protocol implementation. Open standard for internet-native payments. Server middleware + client wrappers. |
| **Chains** | EVM (Base, etc.), Solana, Stellar — network-agnostic by design |
| **Key stat** | Open standard; "35M+ transactions, $10M+ volume" claim needs verification — not visible in repo |
| **Cloud support** | Cloudflare, Google, Vercel (via ecosystem) |
| **Principles** | Open standard, HTTP-native, network/token/currency agnostic, backwards compatible, trust-minimizing, easy to use |
| **Schemes** | `exact` (live), `upto` (theoretical) — extensible |
| **Our status** | ✅ Researched, `x402` skill in optional-skills, Dexter SDK evaluated |

**README verbatims:**
- "x402 is an open standard for internet native payments. It aims to support all networks (both crypto & fiat) and forms of value."
- "It is the goal of the x402 community to improve ease of use relative to other forms of payment on the Internet."
- "The client/server should not need to think about gas, rpc, etc."

**Verdict:** This is the TCP/IP of agent payments. Commoditized, open, table stakes. Not a differentiator.

### 2. PayAI Network
| Attribute | Detail |
|-----------|--------|
| **Package** | PayAI facilitator (Solana-native) |
| **What it does** | Solana-specific x402 settlement + agent marketplace |
| **Token** | $PAYAI (~$3M market cap) |
| **Differentiation** | Native Solana focus, marketplace for agent services |
| **Our status** | 🟡 Monitored in x402 ecosystem tracker |

**Verdict:** Solana-only. Useful as a facilitator partner, not a competitor.

### 3. CDP Wallet / Coinbase Agentic Wallet
| Attribute | Detail |
|-----------|--------|
| **Package** | `coinbase/agentic-wallet-skills` |
| **What it does** | Embedded wallet for agents + MCP integration |
| **Differentiation** | Deep Coinbase ecosystem integration, fiat on/off ramps |
| **Our status** | ✅ Referenced in Agentic Market integration |

**Verdict:** Wallet infrastructure. We use it, don't compete with it.

---

## Layer 2: Trust / Identity / Risk SDKs (The Moat)

This is where **t54 lives** and where differentiation actually happens.

### 4. t54 — x402-secure SDK
| Attribute | Detail |
|-----------|--------|
| **Package** | `@t54-labs/clawcredit-sdk` (v0.2.40, npm) + open-source `x402-secure` proxy (Python, GitHub) |
| **License** | SDK is npm-published; x402-secure proxy is Apache-2.0 OSS |
| **What it does** | **Open-source proxy + SDK that wraps Coinbase x402 and injects Trustline risk engine into every payment** |
| **Key feature** | Trustline real-time risk engine — behavioral patterns, code audits, mandates, device context |
| **Identity** | KYA (Know Your Agent) — developer KYB, model provenance, human-agent binding, intent attestation |
| **Credit** | ClawCredit — agent-native credit lines underwritten by risk scores |
| **Dashboard** | x402 Secure Dashboard — live risk insights, anomaly detection, Coinbase x402 Bazaar leaderboard |
| **Auditability** | Every spend linked to reasoning trace + code snapshot |
| **Chains** | Base, Base Sepolia (via x402). XRPL (lead), Solana mentioned on marketing. |
| **Asset** | USDC (`0x036CbD53842c5426634e7929541eC2318f3dCF7e` on Base Sepolia) |
| **Payment scheme** | `exact` via EIP-3009 authorization |
| **Risk levels** | `low` / `medium` / `high` (ENUM returned on every transaction) |
| **Trace collector** | OpenAI native today. LangChain/AutoGPT "coming" (6+ months stale) |
| **Proxy endpoints** | `/risk/session`, `/risk/trace`, `/x402/verify`, `/x402/settle` |
| **Production proxy** | `https://x402-proxy.t54.ai` |
| **Custody** | Keyless / custodial (agents don't manage private keys) |
| **Integrations** | World ID, lobster.cash, Evernorth |
| **Repo health** | 25 stars, 3 forks, last commit 6 months ago — early stage, low community traction |

**Verdict:** The most **complete Layer 2 stack** in the ecosystem. Institutional-grade. Their SDK doesn't just *do* payments — it *validates who is paying* and *whether they should be allowed to*. **But:** low OSS activity, 6-month stale repo, Python-only SDK, OpenAI-only trace collector.

---

### 5. Zauthx402
| Attribute | Detail |
|-----------|--------|
| **Token** | $ZAUTH (~$3M market cap) |
| **What it does** | Auth layer for x402 payments |
| **Differentiation** | Focused on authentication/authorization only |
| **Our status** | 🟡 Monitored — auth overlap with AgentEscrow |

**Verdict:** Narrower than t54. Just auth, no risk engine or credit. Micro-cap means limited resources.

---

### 6. Kite AI — Agent Passport
| Attribute | Detail |
|-----------|--------|
| **What it does** | Identity + payment layer for agents |
| **Tagline** | "Let your AI Agent transact in the real world while you stay in control" |
| **Differentiation** | BYOA (Bring Your Own Agent), real-world/off-ramp focus |
| **Our status** | ✅ Tracked as potential partner/competitor |

**Verdict:** Identity-first like t54, but consumer-facing rather than institutional. Less mature, no known SDK yet.

---

## Layer 3: Application / Service SDKs (The Discovery)

### 7. Dexter AI x402 SDK v3.0
| Attribute | Detail |
|-----------|--------|
| **Package** | `@dexterai/x402` (npm) |
| **What it does** | Full-stack x402 SDK + **cross-bazaar search engine** |
| **Key feature** | `wrapFetch()` — transparent payment handling. Client just calls `fetch()`, SDK handles 402s. |
| **Discovery** | First genuine x402 search engine — agents can discover services across bazaars |
| **Chains** | Solana, Base, Polygon, Arbitrum, Optimism, Avalanche, SKALE |
| **Pricing** | Access Pass mode (pay once, unlimited for time window), dynamic pricing |
| **Token** | $DEXTER on Solana (~$889K market cap) |
| **Our status** | ✅ Researched, used in Kite AI hackathon submission draft |

**Verdict:** Best **developer experience** in the ecosystem. The `wrapFetch` pattern is elegant. Discovery layer is unique. But no trust/identity layer — purely payments + search.

---

### 8. Corbits / Faremeter
| Attribute | Detail |
|-----------|--------|
| **What it does** | Pay-per-use API platform + OSS framework for agentic payments |
| **Differentiation** | API monetization for developers, not agent identity |
| **Our status** | 🟡 Referenced in ecosystem research |

**Verdict:** Merchant tooling. Complementary, not competitive.

---

### 9. Birdeye x402 Client (Our Internal Build)
| Attribute | Detail |
|-----------|--------|
| **Package** | Custom Python client (`birdeye-x402-client.py`) |
| **What it does** | Birdeye API access via x402 pay-per-request |
| **Pricing** | $0.003/request |
| **Differentiation** | Purpose-built for our LP monitoring stack |

**Verdict:** Our own Layer 3 integration. Not a product, but proves we can ship x402 infra.

---

### 10. GenLayer / Apolo — Escrow + AI Adjudication
| Attribute | Detail |
|-----------|--------|
| **What it does** | Trustless escrow with AI validator (GenLayer oracle) |
| **Flow** | x402 → Apolo escrow → GenLayer adjudicates → BNB settles |
| **Differentiation** | **Dispute resolution layer** — the only project with AI-validated escrow |
| **Our status** | ✅ GenLayerOracle.sol built, 51/51 tests passing |

**Verdict:** Unique position. No one else has AI adjudication. Closest to our AgentEscrow architecture.

---

## Head-to-Head: t54 vs. The Field

| Dimension | t54 x402-secure | Dexter SDK | Coinbase x402 | Zauthx402 | Kite Passport | GenLayer/Apolo |
|-----------|-----------------|------------|---------------|-----------|---------------|----------------|
| **Layer** | 2 (Trust) | 3 (App) | 1 (Protocol) | 2 (Auth) | 2 (Identity) | 2.5 (Escrow) |
| **Primary value** | Risk engine + KYA | Discovery + DX | Payment rail | Authentication | Real-world ID | Dispute resolution |
| **Open source** | Partial (SDK npm, proxy OSS) | Partial (npm package) | ✅ Full (Apache-2.0) | Unknown | Unknown | ✅ Contracts OSS |
| **Chains** | XRPL, Solana, Base | 7+ chains | Solana, Base, EVM | Unknown | Unknown | BNB (live), multi-chain planned |
| **Credit system** | ✅ ClawCredit | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Risk scoring** | ✅ Trustline (real-time) | ❌ | ❌ | ❌ | ❌ | ✅ AI adjudication (post-fact) |
| **Identity verification** | ✅ KYA + World ID | ❌ | ❌ | ✅ Auth only | ✅ Passport | ❌ |
| **Auditability** | ✅ Reasoning traces | ❌ | ❌ | ❌ | ❌ | ✅ On-chain escrow logs |
| **Dashboard** | ✅ x402 Secure Dashboard | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Custody model** | Custodial (keyless) | Self-custody | Self-custody | Unknown | Unknown | Self-custody |
| **Funding** | $5M (Franklin Templeton, Ripple) | Token ($889K mcap) | Coinbase (public co.) | $3M mcap | Unknown | Hackathon grants |
| **Institutional backers** | ✅ Heavy | ❌ | ✅ Coinbase | ❌ | ❌ | ❌ |

---

## What t54's SDK Does That Others Don't

### 1. **Agent-Native Risk Scoring (Trustline)**
No other SDK evaluates transactions using *agent-specific signals*: behavioral patterns, code audits, mandates, device context. Dexter just routes payments. Coinbase just settles them. t54 *judges* them.

### 2. **KYA — Know Your Agent**
Not just "does this wallet have funds?" but "who built this agent, what model does it run, is it bound to a verified human?" This is institutional-grade identity for software.

### 3. **Agent Credit Underwriting**
ClawCredit is unique. Agents get credit lines based on verified identity + risk scores + transaction history. No other SDK in the ecosystem offers this. It's a genuine financial primitive.

### 4. **Reasoning Trace Auditability**
Every spend is linked to an agent reasoning trace + code snapshot. This is *explainable AI finance* — critical for regulatory acceptance and debugging.

### 5. **x402 Secure Dashboard + Leaderboard**
Network-wide security signals, anomaly detection, official Coinbase x402 Bazaar leaderboard integration. No competitor has a comparable monitoring surface.

### 6. **Custody as a Feature (Not a Bug)**
They handle keys so agents don't have to. This enables credit (you can't underwrite self-custody wallets easily). It's a design choice that unlocks their entire credit model.

---

## Where t54 Is Vulnerable

| Weakness | Why It Matters for Us |
|----------|----------------------|
| **Custodial = CEX vibes** | DeFi-native users distrust custody. Our self-custody vault is a differentiator. |
| **XRPL-first** | Ripple investor bias. Solana + Base have more developer momentum. |
| **No token** | Can't bootstrap community incentives. We have $TECH for that. |
| **B2B-only positioning** | No retail angle. We own the solo agent operator. |
| **Closed risk engine** | Trustline is proprietary. We can make REP transparent and community-governed. |
| **No escrow / dispute resolution** | They verify identity but don't resolve disputes. GenLayer/Apolo + AgentEscrow fill this gap. |
| **Heavy compliance framing** | Ex-SEC/FDIC advisors scare retail DeFi users. We stay light. |

---

## Strategic Implications for GenTech

### The Stack We Should Build

```
┌───────────────────────────────────────────────────────┐
│  Layer 3: Service Discovery (borrow from Dexter pattern)            │
│  → Agent capability registry, cross-bazaar search                 │
├───────────────────────────────────────────────────────┤
│  Layer 2: Trust + Reputation + Escrow (OUR LAYER)                  │
│  → REP scores (transparent, community-governed)                   │
│  → AgentEscrow with AI adjudication (GenLayer oracle)             │
│  → Yield-backed collateral (instead of credit underwriting)       │
├───────────────────────────────────────────────────────┤
│  Layer 1: Payment Rail (use existing — don't rebuild)              │
│  → Coinbase x402 / Dexter SDK / PayAI facilitator                 │
└───────────────────────────────────────────────────────┘
```

### Don't Compete on Layer 1
Coinbase owns the payment rail. Dexter owns discovery. **We compete on Layer 2** — the trust layer between them.

### Differentiation Playbook

| Their Feature | Our Counter |
|---------------|-------------|
| Closed Trustline risk engine | **Open REP scores** — community-governed weights, on-chain |
| Custodial credit (ClawCredit) | **Self-custody yield-backed collateral** — user keeps keys, vault stakes collateral |
| KYA verification | **Reputation-native identity** — on-chain history + social proof, not institutional KYB |
| Reasoning trace auditability | **Full agent decision log** — vault records every signal, trade, and rationale |
| B2B merchant focus | **Retail agent operator** — the solo builder running 3 agents |
| No token / no community incentives | **$TECH token** — rewards for good behavior, burns for bad |

---

## Recommended SDK Architecture for GenTech

### What We Build
1. **AgentEscrow SDK** (`@gentech/agent-escrow`) — open-source escrow contracts with AI adjudication
2. **REP SDK** (`@gentech/rep`) — transparent reputation scoring, queryable by any agent
3. **Vault SDK** (`@gentech/vault`) — self-custody wallet + yield integration for agents
4. **Guardrail Proxy** (t54-style) — optional middleware that adds REP checks to any x402 payment

### What We Use (Don't Build)
- Payment settlement: **Coinbase x402** or **Dexter SDK**
- Service discovery: **Dexter search engine** (partner or integrate)
- Wallet infra: **CDP Wallet** or **Privy**
- Data feeds: **Birdeye x402** (already built)

---

## Action Items

- [ ] **DMOB:** Evaluate t54's open-source `x402-secure` proxy — can we fork/adapt for REP-based guardrails?
- [ ] **DMOB:** Design `@gentech/rep` SDK interface — how do external agents query REP scores?
- [ ] **YoYo:** Model yield-backed collateral mechanics as alternative to ClawCredit's underwriting
- [ ] **Desmond:** Draft "Layer 2 Trust Stack" positioning for hackathon submissions
- [ ] **All:** Decide — integrate with t54's SDK (partner) or build competing guardrail layer?

---

## Appendix: x402-secure vs. Base Coinbase x402 — Technical Diff

**This is the key question: what does t54's SDK actually add on top of the open standard?**

| Dimension | Coinbase x402 (base) | t54 x402-secure (layer on top) |
|-----------|----------------------|--------------------------------|
| **Scope** | Payment protocol only | Payment + risk + identity + liability |
| **Standard** | Open standard (Apache-2.0) | Proxy wrapper (Apache-2.0) + closed Trustline engine |
| **Client types** | Generic HTTP client | `BuyerClient` / `SellerClient` with risk session management |
| **Headers** | `X-PAYMENT`, `PAYMENT-SIGNATURE` | Adds `X-PAYMENT-SECURE`, `X-RISK-SESSION` |
| **Risk check** | ❌ None | ✅ Pre-payment risk evaluation via Trustline |
| **Trace collection** | ❌ None | ✅ `OpenAITraceCollector` captures full reasoning stream |
| **Liability model** | Caveat emptor | ✅ Protected if agent acts within trace bounds |
| **Dispute resolution** | ❌ None | ✅ Cryptographic evidence of agent behavior |
| **Credit system** | ❌ None | ✅ ClawCredit (agent-native credit lines) |
| **Dashboard** | ❌ None | ✅ x402 Secure Dashboard + Bazaar leaderboard |
| **Identity** | Wallet address only | ✅ KYA: developer KYB, model provenance, human-agent binding |
| **Custody** | Self-custody | Custodial (keyless) |
| **Integration time** | ~10 min (server) | ~5 min buyer / ~10 min seller (with risk) |
| **Languages** | TS, Python, Go | Python only (for OSS proxy) |
| **Chains** | Multi-chain by design | Base/Base Sepolia (via x402), XRPL marketing |

**The one-liner:** x402 moves money. x402-secure decides *whether the money should move*.

### What This Means for GenTech

We should **not** build a payment rail. Coinbase owns that. We should **not** build a closed risk engine. t54 is doing that (poorly, with 6-month stale repos).

**Our play:** Build the **open, community-governed reputation layer** that any x402-secure (or base x402) transaction can query. REP scores as a public good. Let t54 chase institutional KYB — we chase the solo agent operator who needs transparent, on-chain reputation without custody.

---

## Sources

- t54.ai website, blog, team page (recon: Desmond, Apr 26)
- `03-Projects/_merged-01-Projects/AAE/x402-research.md` (DMOB, Apr 20)
- `05-Learning/x402-Research.md` (DMOB, Apr 16)
- `03-Strategies/t54.ai-Competitive-Analysis.md` (YoYo, Apr 26)
- `06-Content/x402-ecosystem-tracker.md` (YoYo, Apr 24)
- `10-Inbox/kite-passport-agent-identity.md` (Jordan, Apr 25)
