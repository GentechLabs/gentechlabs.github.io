# Dexter DAO — PR Ready for Submission

## PR: Zod Validation Schemas for x402 v2

**Target repo:** Dexter-DAO/dexter-x402-sdk
**Branch:** feat/zod-validation
**Files:** 3 changed, 229 insertions

### What's in the PR
- `src/validation/schemas.ts` — Zod schemas for all x402 v2 payment types
- `src/validation/index.ts` — module exports
- `package.json` — added `./validation` subpath export
- Also fixes: `coinbase/x402` → `x402-foundation/x402` reference

### How to submit
1. Go to https://github.com/Dexter-DAO/dexter-x402-sdk
2. Click Fork → create fork under ProtoJay4789
3. Go to your fork → Branches → New branch: `feat/zod-validation`
4. Push the code from `/root/dexter-sdk-full/` to that branch
5. Open PR against Dexter-DAO/dexter-x402-sdk main

### Code location
`/root/dexter-sdk-full/` — full clone with branch ready
