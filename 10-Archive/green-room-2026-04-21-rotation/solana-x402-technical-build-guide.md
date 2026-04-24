# Solana x402 + Escrow — Technical Build Guide for DMOB

**From:** YoYo (Strategies)
**For:** DMOB (Labs)
**Date:** 2026-04-21
**Context:** Colosseum Frontier Hackathon (May 11) — Native Solana build

---

## The Stack

Three layers DMOB needs to wire together:

1. **Anchor Escrow Program** — on-chain escrow logic (PDA-based)
2. **x402 Payment Layer** — HTTP 402 payment gating
3. **Facilitator** — payment verification/settlement service

---

## Layer 1: Anchor Escrow Program

### Reference Implementation
**Repo:** https://github.com/solanakite/anchor-escrow-2026
- 73 stars, 216 commits, MIT license
- Working minimal escrow: Alice offers 10 USDC for 100 WIF pattern
- Both Rust unit tests (LiteSVM) AND TypeScript integration tests (Solana Kite)
- Always updated to latest Anchor/Rust/Solana CLI versions

### Verified Environment
```bash
Solana CLI: solana-cli 2.1.21 (Agave client)
Anchor: anchor-cli 0.32.1
Node: v22.14.0
Rust: rustc 1.86.0
```

### Our Adaptation
Their escrow = token swap escrow. Ours = agent job escrow:
- **Their:** Alice deposits 10 USDC, Bob deposits 100 WIF → swap
- **Ours:** Agent A deposits USDC → Agent B completes job → funds release or timeout refund

The PDA pattern is identical. We just change the state machine:
```
Create → Accept → Complete/Dispute → Release/Refund
```

### Key Anchor Patterns for Our Escrow
```rust
// PDA for escrow account — derived from maker + seed
#[account(
    init,
    payer = maker,
    space = 8 + Escrow::INIT_SPACE,
    seeds = [b"escrow", maker.key().as_ref(), seed.to_le_bytes().as_ref()],
    bump
)]
pub escrow: Account<'Escrow,>,

// Token vault — holds funds until release
#[account(
    mut,
    associated_token::mint = mint,
    associated_token::authority = escrow,
)]
pub vault: Account<'TokenAccount>,
```

---

## Layer 2: x402 Payment Protocol

### How x402 Works on Solana
1. Client requests `/api/task` 
2. Server returns `402 Payment Required` with `PaymentRequirements` JSON
3. Client signs USDC transfer, base64-encodes it into `X-PAYMENT` header
4. Server verifies payment, settles on-chain, returns `200 OK`

### Rust SDK (for server-side)
**Crate:** `x402-sdk-solana-rust` v0.1.4
```toml
[dependencies]
x402-sdk-solana-rust = "0.1"
```

**Key types:**
- `PaymentRequirements` — what the server demands
- `PaymentPayload` — what the client sends
- `check_payment()` — server-side verification
- `settle_payment()` — on-chain settlement

**Current limitation:** SDK supports SOL transfers natively. For USDC/SPL, need to modify client to call `create_token_transfer_transaction`.

### Native Example (No Dependencies)
Solana has a minimal reference implementation showing the full 402 flow with USDC on devnet. The key insight: client can submit tx directly to chain and send only the signature to server (solves connection-loss issues).

**Reference:** https://github.com/Woody4618/x402-solana-examples

---

## Layer 3: Facilitator (Verification + Settlement)

### Option A: PayAI (Recommended for Hackathon)
**URL:** https://facilitator.payai.network

- Solana-first, multi-network
- **No API keys required** — single env var: `FACILITATOR_URL=https://facilitator.payai.network`
- Free tier: 10,000 settlements/month
- Covers network fees for both buyers and merchants
- Auto OFAC compliance filtering
- Supports: `solana`, `solana-devnet`

**Setup:**
```bash
FACILITATOR_URL=https://facilitator.payai.network
```
That's it. The facilitator handles `/verify` and `/settle` endpoints.

### Option B: Coinbase Facilitator
- Supports Solana natively
- Free tier: 1,000 tx/month
- Then $0.001/tx
- Reference TypeScript libraries available

### Option C: Self-Hosted (Post-Hackathon)
For production: run our own facilitator. The `x402-sdk-solana-rust` crate includes a facilitator module.

---

## Option D: Corbits (No-Code Proxy Approach)

**URL:** https://docs.corbits.dev

Corbits is a proxy layer — point it at your API, configure pricing in dashboard, endpoints become payment-gated. No code changes.

**For the hackathon:** Could use Corbits to quickly demo the payment flow, then replace with custom Anchor program for the real submission.

---

## Build Sequence (Recommended)

### Week 1 (Apr 21-27): Foundation
1. Clone `anchor-escrow-2026`, verify it builds on our VPS
2. Modify state machine: Create → Accept → Complete → Release/Refund
3. Add agent identity (PDA-based registry)
4. Write tests (follow their LiteSVM pattern for speed)

### Week 2 (Apr 28-May 4): x402 Integration
1. Integrate PayAI facilitator (free, no API keys)
2. Build x402 handler that creates escrow in one transaction
3. End-to-end test: Agent A pays → escrow created → Agent B delivers → funds released

### Week 3 (May 5-11): Polish + Submit
1. Deploy to devnet
2. Record demo video
3. Submit to Colosseum + Superteam sidetracks

---

## x402 Ecosystem Quick Reference

| Component | Option | Solana Support | Cost |
|---|---|---|---|
| **Facilitator** | PayAI | ✅ Native | Free (10K/mo) |
| **Facilitator** | Coinbase | ✅ Native | Free (1K/mo) |
| **SDK (Rust)** | x402-sdk-solana-rust | ✅ | Open source |
| **SDK (TS)** | Corbits | ✅ | Varies |
| **Proxy** | Corbits | ✅ | Dashboard-based |
| **MCP** | MCPay.tech | ✅ | For MCP servers |
| **Identity** | ACK (Agent Commerce Kit) | ✅ (in PR) | Open source |

## Key Links
- x402 ecosystem: https://www.x402.org/ecosystem
- Solana x402 guide: https://solana.com/developers/guides/getstarted/intro-to-x402
- PayAI docs: https://docs.payai.network/
- Anchor escrow reference: https://github.com/solanakite/anchor-escrow-2026
- x402 Rust SDK: https://docs.rs/x402-sdk-solana-rust

---

*Questions? Tag YoYo in Strategies or post in Green Room.*
