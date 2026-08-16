# Algorand v5.0.0 — Quantum-Safe Positioning (Jordan, Aug 16 2026)

## The angle (Jordan's framing — the sharpest version)

**Algorand = the quantum-safe parking lot for the agentic treasury.**

Algorand v5.0.0 (mainnet, Aug 16 2026) shipped **native Falcon-1024 post-quantum accounts** —
the first major chain to make quantum-resilient accounts a first-class protocol feature, not a bolt-on.
Also: usage-based fees, doubled smart-contract size, cross-app box sharing, ZK-friendly hashing.

**The strategic thesis:** if you're a treasury, DAO, or agent holding long-term value, the rational
move is to park it on the chain that's ALREADY quantum-resilient — so you're not exposed to
"harvest now, decrypt later." This is a **trust story, not a tech story** — and trust is what
treasury infrastructure sells.

## Why this is the perfect angle for Algorand AND the agentic treasury

1. **Validates our quantum treasury direction.** Our `quantum_treasury` uses hybrid
   ECDSA + SPHINCS+ (SLH-DSA, a NIST finalist). Algorand shipped Falcon-1024 (the OTHER NIST
   finalist) natively. Same thesis, two directions — strong third-party validation.
2. **Strengthens our Algorand x402 Challenge position.** We're already live on the Algorand
   rail: wallet funded, USDC opted-in (ASA 31566704), **first mainnet settlement Aug 6**
   through GoPlausible, tagged `x402-global-challenge`. Early on the chain pushing
   quantum-resilience hardest = genuine differentiator for the $100K + 500K ALGO challenge.
3. **The clean story:** "We run a quantum-safe agentic treasury, and Algorand is the chain
   that made quantum-resilient accounts native — so our x402 rail on Algorand is the natural
   home for it."

## Key facts to cite
- Algorand v5.0.0 live on mainnet Aug 16 2026 (largest upgrade since Jan 2025 staking rewards)
- Native Falcon-1024 post-quantum accounts (first major chain)
- 2022: State Proofs signed with FALCON already on mainnet (anchored history to genesis)
- 2025: first quantum-resilient tx on Algorand mainnet
- June 2026: Algorand Foundation post-quantum roadmap, broad quantum-resilience by 2027
- Usage-based fees (pay for what a tx costs, not flat rate)
- Doubled smart-contract size limit; cross-app box sharing; ZK-friendly hashing

## Our live Algorand state (verified)
- Wallet: `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI`
- USDC ASA 31566704 opted-in (txn D4ZESUWYNZ6HYN77FQDVDQ2RVN7MRNRCC3FVH4ATJVZIKZJUAYUA)
- First mainnet settlement Aug 6: txid GQBF6UBBQHMEM3HI4FIUHRIFOIJQEG462NOPCSXJXHTOV77LNMWA
- Rail: `X402_NETWORKS="base,algorand"`, `X402_PAYTO_ALGORAND=<addr>`, verify mode `auto`
  (routes AVM proofs → GoPlausible)
- Test script: `/root/.algorand/algo_settle_test.py`

## Next
- Draft the Algorand x402 Challenge submission angle around this positioning
- Tie quantum treasury (SPHINCS+) to Algorand's native Falcon-1024 in the agentic treasury pitch
