# Xona Labs — PR Ready for Submission

## PR: feat/validation-fixes — 3 issues in 1 PR

**Target repo:** xona-labs/xona
**Branch:** feat/validation-fixes
**Files:** 3 changed, 167 insertions, 42 deletions

### What's in the PR

| Issue | Fix | File |
|-------|-----|------|
| **#5** — Zod validation | New `src/validation.ts` with schemas for x402 v1/v2 challenges, payment requirements, settlement. Re-exported from types/index.ts for backwards compat | `src/validation.ts`, `src/types/index.ts` |
| **#2** — tweetnacl 64-byte key | Changed `keypair.secretKey.slice(0, 32)` → `keypair.secretKey` (full 64 bytes) | `src/signer.ts` |
| **#3** — Fail closed on network | Removed silent `accepts[0]` fallback. Throws with available networks listed | `src/signer.ts` |

### How to submit
1. Go to https://github.com/xona-labs/xona
2. Click Fork → create fork under ProtoJay4789
3. Go to your fork → Branches → New branch: `feat/validation-fixes`
4. Push the code from `/root/xona-sdk/` to that branch
5. Open PR against xona-labs/xona main

### Code location
`/root/xona-sdk/` — full clone with branch ready
