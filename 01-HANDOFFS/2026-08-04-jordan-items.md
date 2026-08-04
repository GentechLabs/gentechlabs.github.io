# Jordan Items — Aug 4, 2026 (overnight build session)

## 🔴 BLOCKER — KeeperHub hackathon (deadline Aug 13, 9 days)
The KeeperHub agent workflow is built and live in the org (`r0nfoic9vk12ik1h3af67`), but the
execution wallet is empty:

- `0x53A8DFA431D03A36499f9DB70AAFbb00C28308EA`
- Base mainnet: **0 ETH, 0 USDC**
- Base Sepolia: **0 ETH**

Judging requires a **live onchain tx link**. We cannot produce one without funds.

**Ask:** send ~$15 of ETH + ~$10 USDC on Base to that address (or fund Base Sepolia via faucet
if you'd rather demo on testnet — say the word and I'll re-point the workflow to 84532).
Once funded I can open a tiny Aave position, trip the health-factor guard, and capture the tx.

## 🟡 NEEDED — Algorand x402 Challenge ($100K + 500K ALGO)
Gateway code side is **shipped** tonight — the x402 gateway is now genuinely
multi-network (Base + Algorand, CAIP-2 registry, 17/17 tests, deployed and
verified live with zero regression). Details:
`01-HANDOFFS/gentech-to-labs/2026-08-04-x402-multinetwork-algorand.md`

Two things only you can do:
1. **Algorand mainnet wallet address** — set as `X402_PAYTO_ALGORAND`. The ALGO
   rail is deliberately dormant until then (we never advertise a network we
   can't receive on). Once set it's a restart, no code change.
2. **Register** at `algorand.co/global-x402-challenge` — leaderboard is open.

Heads-up: ALGO proof *settlement* verification is still an open build task
(Coinbase CDP facilitator is EVM-only). Network gating works; settlement needs
an algod/indexer path. I can build that next — it doesn't need you.

## Notes
- KeeperHub AI workflow generation endpoint is disabled server-side ("AI Prompt is disabled") — workflows must be authored by hand. Done.
- KeeperHub MCP `get_execution_status` / `get_execution_logs` tools are not exposed by the server right now; execution IDs are returned but must be checked in the KeeperHub UI.
