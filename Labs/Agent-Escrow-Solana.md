# Agent Escrow — Solana Native (Anchor)

**Repo**: https://github.com/ProtoJay4789/agent-escrow-solana
**Status**: ✅ Compiles, tests pass, BPF .so builds
**Framework**: Anchor 1.0
**Target**: Colosseum/Frontier Hackathon (May 11)

## Architecture

### Program Structure
```
programs/agent-escrow-solana/src/
├── lib.rs              # 7 instructions
├── state.rs            # EscrowConfig + Escrow + EscrowStatus
├── error.rs            # 12 custom errors
├── constants.rs        # PDA seeds
└── instructions/
    ├── initialize.rs          # Deploy config (admin, validator, USDC mint)
    ├── create_escrow.rs       # Buyer deposits USDC → PDA vault
    ├── validate_work.rs       # Direct or Ed25519 precompile signature
    ├── release_funds.rs       # Release to seller after validation
    ├── refund_buyer.rs        # Admin refunds if validation fails
    └── update_validator.rs    # Admin updates AI validator pubkey
```

### State (PDAs)
- **EscrowConfig** `[CONFIG_SEED]` — global: admin, ai_validator, usdc_mint, escrow_count
- **Escrow** `[ESCROW_SEED, id]` — per-escrow: buyer, seller, amount, status, vault
- **Vault** `[ESCROW_SEED, id, b"vault"]` — SPL token account, authority = escrow PDA

### Key Differences from EVM Version
| Solidity | Solana |
|---|---|
| Sequential `_nextEscrowId` | Config PDA `escrow_count` |
| `mapping(id => Escrow)` | One PDA per escrow |
| USDC via `transferFrom` | SPL token CPI transfer |
| EIP-712 signatures | Ed25519 precompile |
| `msg.sender` checks | Anchor `Signer` + constraint checks |

### Ed25519 Precompile Flow
1. Validator signs `(escrow_id + timestamp)` off-chain with Ed25519 key
2. Client builds tx: `[Ed25519PrecompileIx, validate_with_signature(timestamp)]`
3. Solana runtime verifies precompile before program executes
4. Program trusts the precompile verification → applies validation

## Dev Environment Installed
- Rust 1.95.0
- Solana CLI 3.1.13
- Anchor 1.0.0 (via AVM)
- Node/Yarn for TypeScript tests

## Next Steps
- [ ] Write LiteSVM integration tests (initialize → create → validate → release flow)
- [ ] Deploy to Solana devnet
- [ ] Build TypeScript client with `@coral-xyz/anchor`
- [ ] x402 payment middleware integration
- [ ] Security audit pass
