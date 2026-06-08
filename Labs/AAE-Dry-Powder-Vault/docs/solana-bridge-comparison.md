# Solana Bridge Options — Comparison & Recommendation

## Context

CCTP (Circle's Cross-Chain Transfer Protocol) does NOT support Solana. We need an alternative for bridging USDC from Base/Avalanche to Solana.

## Options Compared

### 1. Across Protocol ⭐ RECOMMENDED

| Attribute | Value |
|-----------|-------|
| **Settlement Time** | <5 seconds (median) |
| **Fee** | 0.06-0.10% LP fee + gas |
| **Supported Routes** | Base→Solana, Avalanche→Solana, Ethereum→Solana |
| **SDK** | `@across-protocol/app-sdk` (TypeScript), Python via web3.py |
| **Security** | Audited by OpenZeppelin, battle-tested |
| **Uptime** | 99.9%+ |
| **Solana Support** | ✅ Native (SVM SpokePool) |
| **USDC Handling** | Native USDC (no wrapping) |

**Why Recommended:**
- Fastest fills in the market (sub-5s median)
- Lowest fees for our volume range
- Official Solana migration guide available
- Python SDK compatible with our orchestrator
- depositV3 function for EVM origin, native SVM for Solana destination

**Base SpokePool:** `0xb4a8d45647445EA9FC3E1058096142390683dBC2`

### 2. deBridge

| Attribute | Value |
|-----------|-------|
| **Settlement Time** | Instant finality |
| **Fee** | 0.001 ETH flat (~$2-3) |
| **Supported Routes** | 15+ networks to Solana |
| **SDK** | JavaScript SDK |
| **Security** | 100% uptime, decentralized |
| **Solana Support** | ✅ Native |
| **USDC Handling** | Native USDC |

**Pros:**
- Flat fee is good for large transfers (>$5K)
- Instant finality
- 100% uptime track record

**Cons:**
- Flat fee is expensive for small transfers (<$5K)
- Less Python SDK support
- Newer protocol

### 3. Wormhole (Portal Bridge)

| Attribute | Value |
|-----------|-------|
| **Settlement Time** | 5-30 minutes |
| **Fee** | Variable (relayer fees) |
| **Supported Routes** | 45+ chains including Solana |
| **SDK** | `wormhole-sdk` (TypeScript), Python via wormhole_sdk |
| **Security** | Guardian network (19 validators) |
| **Solana Support** | ✅ Native |
| **USDC Handling** | Wrapped or NTT (Native Token Transfers) |

**Pros:**
- Most battle-tested bridge (highest TVL)
- Institutional grade security
- NTT for native USDC transfers

**Cons:**
- Slowest settlement time
- More complex integration
- Guardian network adds latency

## Cost Analysis (for $10,000 USDC transfer)

| Bridge | Fee | Total Cost | Time |
|--------|-----|-----------|------|
| Across | 0.08% | ~$8.00 | <5s |
| deBridge | Flat | ~$2.50 | Instant |
| Wormhole | Variable | ~$3-5 | 5-30min |

## Recommendation: Across Protocol

**For our use case (automated agent, frequent small-medium rotations):**

1. **Speed:** Sub-5s fills mean rotations complete instantly
2. **Cost:** 0.08% is acceptable for our volume ($500-$10K per rotation)
3. **Integration:** Python SDK works with our orchestrator
4. **Reliability:** Battle-tested with 99.9% uptime
5. **Native USDC:** No wrapped token risk

**Implementation Plan:**
1. Use Across `depositV3` on Base SpokePool
2. Monitor for Solana completion via Across API
3. Fallback to deBridge for large transfers (>$50K)

## Integration Architecture

```
Base (EVM)                    Solana (SVM)
┌─────────────┐              ┌─────────────┐
│ SpokePool   │  ── USDC ──> │ SVM Spoke   │
│ depositV3() │              │ claim()     │
└─────────────┘              └─────────────┘
        │                           │
        └─────── Across API ────────┘
              (Quote + Status)
```

## Key Addresses

| Chain | Contract | Address |
|-------|----------|---------|
| Base | SpokePool | `0xb4a8d45647445EA9FC3E1058096142390683dBC2` |
| Avalanche | SpokePool | `0x6f26bf09b1c792e3228e5467807a900a503c0281` |
| Solana | SVM Spoke | Program-based (not contract address) |

## Solana USDC Addresses

| Token | Address |
|-------|---------|
| USDC (native) | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDC (wrapped) | `A9mUU4qvySqd1SGFgz8DQsFn26Vewy88SeY668n3HUn` |

## Next Steps

1. Integrate Across depositV3 in `solana_bridge_adapter.py`
2. Add deBridge as fallback for large transfers
3. Test on Base Sepolia + Solana Devnet
