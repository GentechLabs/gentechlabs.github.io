# x402B Deep Dive — Agent Arena Integration Research

**Date:** 2026-05-22
**Status:** Research complete, ready for build planning
**Priority:** HIGH — mainnet coming soon

---

## What x402B Actually Is

x402B is Boson Protocol's implementation of the `x402-escrow-schema` — a **non-custodial escrow payment scheme** for x402 HTTP servers. It extends the x402 AI agent payment standard with escrow capabilities.

**Key distinction:** x402's built-in `exact` scheme is settle-and-done (facilitator moves funds to seller immediately). x402B adds an escrow layer where funds are locked until the buyer confirms delivery or the dispute window expires.

**Not a fork of x402** — it's a new scheme value (`"escrow"`) that x402 was designed to host alongside `"exact"` and future schemes.

---

## How It Works (The Flow)

### Deferred Redemption (commit now, redeem later)
1. Server signs a fresh `FullOffer` per request (dynamic pricing)
2. 402 response includes escrow contract address + offer + seller signature
3. Buyer signs meta-tx authorizing escrow contract to lock funds
4. Funds enter Boson Diamond escrow (non-custodial)
5. Server verifies on-chain state, returns resource
6. Buyer later calls `redeemVoucher()` → state = REDEEMED
7. Buyer calls `completeExchange()` → funds release to seller

### Atomic Commit-and-Redeem (single transaction)
- Collapses commit + redeem into one on-chain tx
- Use when: atomic delivery, async delivery with upfront redeem, pre-staged content
- `OrchestrationHandlerFacet2.createOfferCommitAndRedeem` handles it

### Key Design Decisions
- **Buyer never stranded:** Every non-terminal state has a direct on-chain fallback path
- **Facilitator is optional:** Can submit meta-tx directly on-chain
- **Voucher is ERC-721:** Can be traded/sold before redemption (secondary market!)
- **Self-describing responses:** Every server response carries `nextActions` envelope listing legal next steps

---

## The Escrow Guarantee

| Feature | x402 `exact` | x402B `escrow` |
|---|---|---|
| Fund custody | Facilitator → seller | Escrow contract until delivery confirmed |
| Facilitator trust required | Yes | No — optional, buyer has direct on-chain path |
| Per-session pricing | Fixed | Dynamic (seller signs fresh offer per request) |
| Delivery negotiation | No | Yes — pluggable transport registry |
| Dispute resolution | No | Yes — on-chain, resolver-enforced |
| Post-payment actions | None | `nextActions` on every response |
| Censorship resistance | N/A | Multi-channel fallback |

---

## Why It Matters for Agent Arena

### 1. Agent-to-Agent Commerce
- Agents can pay each other with escrow protection
- No trust required between pseudonymous agents
- Dispute resolution built-in for when agents disagree

### 2. Physical + Digital Goods
- Supports both (NFT loadouts, in-game items, physical merchandise)
- Voucher system = ERC-721 representing right to receive a specific product
- Physical fulfillment triggers escrow release

### 3. Multi-Chain
- Live on: Ethereum, Polygon, Base, Arbitrum, Optimism
- CAIP-2 network identifiers (`eip155:<chainId>`)
- EVM-only for v1 (covers all our target chains)

### 4. Agent Mode (MCP Integration)
- `@bosonprotocol/x402-agent` bridges to AI agents via MCP
- Agent buyer policy: spending limits, preferred channels, auto-complete
- Agent seller policy: auto-publish offers, auto-handle disputes
- **Status: STUB** — not fully implemented yet

### 5. Voucher Secondary Market
- Buyer receives ERC-721 voucher on commit
- Can trade/sell before redemption
- Whoever holds voucher at redemption time is the redeemer
- **Directly relevant:** Agent Arena loadout trading, NFT marketplace

---

## Package Ecosystem

| Package | Purpose |
|---|---|
| `x402-core` | Schemas, EIP-712 builders, state machine |
| `x402-evm` | EVM calldata builders, Diamond integration |
| `x402-server` | Framework-agnostic resource server (Express/Hono/Next adapters) |
| `x402-client` | Framework-agnostic client (Axios/Fetch adapters) |
| `x402-facilitator` | Reference verify + settle service |
| `x402-fulfillment` | Pluggable delivery (atomic/email/XMTP/webhook/IPFS) |
| `x402-actions` | Channel registry, state machine, nextActions |
| `x402-agent` | AI-agent glue layer via MCP |

---

## Red Flags / Considerations

### 1. x402 Transaction Collapse
- AgentPMT data: Agentic GDP hit $470M but transactions fell 92%
- Infrastructure shipped fast but usage cratered
- Could mean: premature market, or building toward right timing

### 2. BOSON Token
- Price: ~$0.03 (down 98% from ATH of $5.36)
- Market cap: ~$5.58M
- Circulating supply: 170.46M / 200M max
- **Low market cap = potential for partnership leverage**

### 3. Agent Mode Status
- `x402-agent` is a **stub** (documented but not implemented)
- We'd need to build the MCP bridge ourselves or wait
- However, `agentic-commerce` MCP already exists

### 4. Dispute Resolution
- Built-in but resolver registration needed
- Third-party resolvers can split funds and slash seller bonds
- We'd need to define dispute rules for Agent Arena

---

## Integration Path for Agent Arena

### Phase 1: Research / POC
- [ ] Install `@bosonprotocol/x402-core` and `x402-evm`
- [ ] Test on Base testnet (cheapest, fastest)
- [ ] Create seller identity on Boson Diamond
- [ ] Test deferred + atomic flows with USDC

### Phase 2: Agent Arena Escrow
- [ ] Integrate x402B for in-game item purchases
- [ ] Agent-to-agent trades with escrow protection
- [ ] Voucher system for NFT loadout trading
- [ ] Dispute resolution rules for game context

### Phase 3: Marketplace
- [ ] Secondary market for vouchers (ERC-721 trading)
- [ ] Physical goods integration (merch, hardware)
- [ ] Cross-game item portability

---

## Bottom Line

x402B is the missing piece for Agent Arena's commerce layer. It solves the "how do agents trust each other" problem with non-custodial escrow. The voucher system is perfect for NFT loadout trading. Multi-chain support covers all our target chains.

**The risk:** Agent mode is a stub, BOSON token is down bad, and x402 usage is cratering. But the tech is solid and the timing could work if we build now.

**Recommendation:** Start Phase 1 POC on Base testnet. The SDK is well-documented and the escrow flow is clean. If it works, we can integrate into Agent Arena before mainnet.
