# BountyBook Income — First Earn Attempt (2026-08-12)

**Agent wallet:** `0x80dD10df5179ffa08590f49Ae9960fedf9991e47` (keys: `/root/.blockrun/bountybook-{address,agent,token}`)
**Auth:** re-auth flow works (`/auth/nonce` → sign → `/auth/verify`), token 1hr expiry, refresh via `/tmp/bb-auth/auth.js`.

## What was done
1. **Re-authed** the agent wallet (token had expired) via viem personal_sign — working.
2. **Claimed** job `0a1c6ae8` (Build merge_csv.py, $3.50) — `POST /jobs/:id/claim` succeeded, no on-chain tx needed for task-mode.
3. **Built + tested** the deliverable — `merge_csv.py` passes the platform's own test suite locally (ALL TESTS PASSED).
4. **Submitted** twice via `outputData` (inline) — API returned `{"status":"submitted","message":"Output received. Verification in progress."}`.

## Result: PLATFORM-SIDE VERIFIER BUG — not our code
- My 2 attempts logged, but verification fails: `Verification error: Cannot read properties of undefined (reading 'length')`, `checksFailed: ["ipfs_fetch"]`.
- **Every open job has ZERO passing verifications.** Scan of 20+ open jobs: att counts 127–2,644, `passed: 0` on ALL.
- The verifier requires an IPFS CID (`outputCID`), and `ipfs_fetch` fails for everyone — including 4 different executor wallets. No one can pass these jobs right now.
- Inline `outputData` is documented as "preferred" but the verifier still hard-requires IPFS → broken on their side.

## Next step (blocked on us)
Try the **IPFS route**: produce a real CID and submit `outputCID` instead of inline. Need a working IPFS pin path. Current state: no local IPFS daemon, no Pinata/web3.storage/Infura key in .env. If we had a pinning key, we could pin the file, get a CID, and re-submit — that's the only untested path.

## Recommendation
BountyBook's *claim + auth* infra is proven working (real value: we CAN claim jobs autonomously). But the verifier is currently broken for code jobs. Don't burn more work on it until either (a) we set up IPFS pinning and test `outputCID`, or (b) their verifier is fixed. Flag to Jordan: worth a quick email/issue to the BountyBook team — every open job is unverifiable, which is a big bug for them.
