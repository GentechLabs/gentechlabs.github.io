# Anchor Audit Findings — Solana Agent Economy (May 5, 2026)

Programs audited: agent-registry, job-escrow, dispute-resolver, reputation
Build status: `cargo check` passes (Rust 1.95.0), `cargo build-sbf` blocked on platform-tools

## Critical

### 1. verify_world_id.rs — World ID verification is a no-op
- Handler marks `world_id_verified = true` but never verifies the ZK proof
- Comment says "we trust the World ID verifier" but no CPI is made
- **Impact:** Anyone can claim World ID verification with any proof data

### 2. rate_agent.rs — No authorization check
- `rater` is just a `Signer`, no constraint that they were poster/worker of the job
- **Impact:** Sybil rating attack — anyone can spam fake ratings

### 3. mint_nft.rs — Metaplex CPI stubbed out
- Collection and metaplex_program constraints both check against `METAPLEX_CORE_PROGRAM` (same key)
- **Impact:** Collection validation is broken (program == collection), CPI is a no-op

## High

### 4. register_agent.rs — Unchecked swig_wallet
- `/// CHECK: Validated as a system account or PDA` but NO actual constraint
- **Impact:** Any account can be stored as swig_wallet (stored by reference, limited blast radius)

### 5. link_metaplex_identity.rs — Unverified core_asset
- `/// CHECK: Stored by reference only; client validates` — trust-the-client antipattern
- **Impact:** Anyone can link any pubkey as "Metaplex identity"

### 6. create_dispute.rs — Unchecked poster/worker accounts
- Comments say "validated from job account" but no constraint links them to the actual job
- **Impact:** Anyone can create disputes for any job by passing spoofed poster/worker keys

### 7. submit_work.rs — Worker not validated against job
- `worker` is a `Signer` but no constraint checks `worker.key() == job_account.worker`
- **Impact:** Any signer can submit work for any accepted job

## Medium

### 8. update_reputation.rs — No signer required (by design)
- Permissionless tier recalculation
- Low risk but could be gamed if combined with fake ratings

### 9. Integer overflow in rate_agent.rs
- `total_ratings += 1` and `total_score_sum += score` without checked_add
- Practical impact: negligible (u32 overflow at 4B ratings)

## Code Quality
- Unused variables: proof_hash, root, signal in verify_world_id.rs
- Duplicate tier logic: AgentTier and ReputationTier are identical enums
- agent_registration_uri is logged but never stored on-chain
- Ambiguous glob re-exports: all 4 programs re-export `handler` from multiple modules
