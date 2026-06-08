# Sphere SDK (Unicity Labs)

**Source:** https://github.com/unicity-sphere/sphere-sdk
**Status:** 🔍 Researching
**Added:** May 29, 2026

## What It Is
SDK for autonomous economic agents. Identity, payments, discovery, messaging, and atomic swaps — all peer-to-peer, no gas auctions.

## Key Features
- **Identity:** `@nametag` handles + secp256k1 keypairs
- **Payments:** Send/receive bearer tokens (UCT)
- **Discovery:** Agents find each other via marketplace
- **Atomic swaps:** Peer-to-peer trades without middlemen
- **Direct messaging:** Encrypted P2P via Nostr (NIP-04)
- **Group chat:** Agent group messaging with roles
- **Token backup:** IPFS/IPNS sync

## Install
```bash
npm install @unicitylabs/sphere-sdk
npm install @unicitylabs/sphere-sdk ws  # Node.js needs WebSocket
```

## GenTech Integration Potential
| Sphere Feature | Current Stack | Better? |
|---------------|--------------|---------|
| Identity (@nametag) | ERC-8004 | 🟡 Different approach — may be complementary |
| Payments | x402 | 🟡 Both peer-to-peer, Sphere has bearer tokens |
| Discovery | Custom | ✅ Sphere has built-in agent discovery |
| Atomic swaps | AgentEscrow | 🟡 Sphere is trustless, AgentEscrow has governance |
| Messaging | Nostr (separate) | ✅ Built-in, Nostr-based |
| Group chat | Hermes routing | 🟡 Different — agent-to-agent vs agent-to-human |

## Next Steps
- [x] Install SDK on testnet ✅
- [x] Create agent wallet ✅ (@gentech-agent on testnet)
- [ ] Test send/receive (need testnet tokens)
- [ ] Test agent discovery
- [ ] Test P2P messaging
- [ ] Compare to current x402 + ERC-8004 setup
- [ ] Decision: integrate, complement, or skip

## Test Results (May 29, 2026)
- Wallet: `alpha1qg4f9007f7m5f3nj3k74pp0pzhd7mht0ptu6wwj`
- Identity: `@gentech-agent`
- Network: Testnet
- Status: ✅ LIVE — wallet created, identity confirmed
