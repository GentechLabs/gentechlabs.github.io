# Handoff — KeeperHub: GTA Yield Guard (Aug 4, 2026)

**Item:** Keeperhub Agents Onchain Hackathon — x402 Onchain Agents (queue id 1, deadline Aug 13)

**What was done (verified):**
- Created a real workflow in the KeeperHub org (id `2352bd53-...`):
  - Name: `GTA Yield Guard — Aave Health Factor Auto-Rebalancer (Base)`
  - Workflow ID: `r0nfoic9vk12ik1h3af67`
  - Flow: Schedule `*/15 * * * *` → `aave-v3/get-user-account-data` (Base 8453, wallet 0x53A8…8EA) → Condition `healthFactor < 1.5e18` → `web3/approve-token` (USDC → Aave Pool) → `web3/write-contract` `Pool.supply(USDC, 1e6, wallet, 0)`
  - Wallet integration wired: `7y1vcmw5kds4yf0ij4eoo`
- Test execution launched: exec ID `1momvt8frv3pa97hhaxu9` (org has no debt position, so the write branch does not fire — read/decide path only).
- Schema pitfalls learned: `web3/*` actions use `network` (not `chainId`); `approve-token` needs `tokenConfig` JSON string; `write-contract` requires an inline `abi`.

**What can be continued:**
1. Fund the wallet, open a small Aave position on Base, let the guard fire → capture the real tx hash for the submission (judging requires a live tx link).
2. Record the demo video off the KeeperHub run view.
3. Assemble the submission page (repo `10-Labs/keeperhub-rebalancer/yield_rebalancer.py` + workflow link + tx link).

**Blocked on:** funding (see jordan-items).
**Ping:** Jordan.
