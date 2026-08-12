# Gentech → Labs (gizmo) — 2026-08-12 — BountyBook Earning Rail

## Context / Why this handoff
Jordan asked me to hand BountyBook over to you. We took a real earning swing at it this session and hit a hard wall. Full diagnosis below so you don't redo the research or burn time on a dead path.

## What we found (the short version)
**BountyBook (bountybook.ai) — an agent task marketplace on Base (USDC/x402). "Post work, agents deliver, oracle verifies, escrow pays."**

Our agent wallet + claim + submit pipeline **works end-to-end**:
- Agent wallet: `0x80dD10df5179ffa08590f49Ae9960fedf9991e47`
  - Keys: `/root/.blockrun/bountybook-{address,agent,token}`
  - Auth: `GET /auth/nonce?address=` → sign (EIP-191) → `POST /auth/verify` → Bearer token (1hr expiry). Refresh script: `/tmp/bb-auth/auth.js`.
- Claim: `POST /jobs/:id/claim {executorAddress}` — works, no on-chain tx for task-mode.
- Submit: `POST /jobs/:id/submit {executorAddress, outputData:{...}}` — works, API accepts.

**BUT the platform has NEVER paid anyone out.** Two confirmed, independent blockers:
1. **code_test verifier crash:** every code job fails verification for every agent. Error: `Cannot read properties of undefined (reading 'length')`, `checksFailed:["ipfs_fetch"]`. Root cause (confirmed by 3+ agents + their own bug-report bounty): the oracle reads `spec.success_condition.required_fields.length` but code_test specs carry `required_files`. `undefined.length` → crash. **Lifetime code_test settlements: 0 of 32.** I reproduced it on the exact documented inline payload, twice.
2. **Payout rail never fires even on non-code jobs:** verified jobs show `payout_status=failed`, no `payout_tx_hash`. Treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` shows **zero lifetime USDC outflows on Base** — no money has EVER moved.

**Operator already knows:** two "in progress" bounties on their board are a bug report (job `3c452142`, "Lifetime code_test settlements 0 of 32, no USDC has ever moved") and a **$150 fix offer** (job `8a7bd232`) — the patch is claimed by another agent. No public GitHub. Contact: Discord `discord.gg/BXKTe44Y`, X `@_ptonik`.

**Bottom line: do NOT spend time earning on BountyBook right now.** It's parked. IPFS pinning does NOT help (server-side spec bug, not a delivery problem).

## What I logged (for reference)
- `09-Green Room/bountybook-full-diagnosis-2026-08-12.md`
- `09-Green Room/bountybook-income-attempt-2026-08-12.md`
- Registry row #14 in `11-Mess Hall/marketplace-listings-registry.md` → ⛔ PARKED
- Considerations tracker → "BountyBook — Parked" section, re-check ~Aug 19

## Re-check condition (the ONLY thing worth watching)
Around **Aug 19**, if a verified BountyBook job starts showing a real `payout_tx_hash` (i.e. USDC actually moves on Base), THEN it becomes our best autonomous earning rail — the pipeline we control already works. Until then, leave it.

## If you want to pick up a genuine thread (optional, not blocked)
- **The $150 oracle-fix offer** (job `8a7bd232`) is claimed by another agent, but the fix itself (root cause: `required_fields` vs `required_files`) is a small server-side patch. If you can see the repo / reproduce the bug and submit a working patch to the BountyBook team via Discord, there's real bounty money on the table. This is an open-source-style contribution, not marketplace work. **Only pursue if you can access their codebase — otherwise it's guesswork.**
- Otherwise, treat BountyBook as closed until the Aug 19 re-check.

---
changed:   BountyBook diagnosed as never-paid platform (code verifier + payout rail both broken). Registry + Green Room + considerations updated.
validated: Claim+submit pipeline works; reproduced verifier crash twice on documented inline payload; confirmed 0/32 code settlements + zero lifetime treasury outflows.
next-todo: Re-check ~Aug 19 whether verified jobs show payout_tx_hash. Optional: chase the $150 oracle-fix bounty via Discord if codebase is accessible. No active earning until then.
