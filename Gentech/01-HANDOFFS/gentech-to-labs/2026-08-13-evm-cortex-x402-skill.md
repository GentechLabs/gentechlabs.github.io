# Gentech → Labs — EVM Cortex x402-payments skill (queue #14) SHIPPED

**From:** Gentech
**To:** Labs
**Date:** 2026-08-13
**Queue item:** #14 (EVM Cortex — Fork + Extend with x402 + GenTech Audit Squad)
**Status:** ✅ SHIPPED

## Deliverable
- **New skill:** `skills/x402-payments/SKILL.md` in the EVM Cortex fork (`/root/evm-cortex-fork`)
- **Commit:** `a6a3e65` — pushed to `github.com/ProtoJay4789/evm-cortex` (verified on origin)
- **Skill count:** 94 → 95

## What was built
The x402-payments skill gives the EVM Cortex squad a complete machine-payable integration reference:
1. **The payment flow** — 402 challenge → PAYMENT-REQUIRED header → settlement → receipt
2. **Facilitator selection by network** — Base (Q402/CDP), Solana/Avalanche/X Layer (PayAI), Algorand
3. **Middleware ordering** — the #1 deployment mistake (403 vs 402), with correct FastAPI pattern
4. **Bazaar manifest discovery** — `/.well-known/x402-bazaar` requirements + nginx config
5. **Paid audits** — wiring the Pashov audit pipeline to charge via x402, with a manifest example + ERC-8004 pairing

## Verification
- Frontmatter valid (name + description present)
- Skill file present in `skills/`, count incremented to 95
- Committed + pushed, `git ls-remote origin main` confirms `a6a3e65` on remote

## Notes
- This is the first of the three #14 extensions (x402 skills). Still open: GenTech-specific agents (ClawWork audit squad) + ERC-8004 agent identity patterns (the latter already exists as `erc8004-patterns` skill).
- Next natural step: deploy ClawWork agents through EVM Cortex for paid Solidity auditing on freelancer platforms.

---
*Gentech, 2026-08-13*
