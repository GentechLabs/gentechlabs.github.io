# KeeperHub Proof Transfer — LIVE TX CONFIRMED ✅

**Date:** 2026-08-10
**Status:** Proof transfer executed and confirmed on Base mainnet.

## The fix — root cause
The KeeperHub proof transfer kept failing with "Invalid token address" / "Invalid contract
address" on the canonical Base USDC address `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913`.

**Root cause:** the address had a **bad EIP-55 checksum**. We were sending
`0x833589...bDA02913` (uppercase `DA`), but the correct checksummed form is
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (uppercase `bdA`). One character. KeeperHub's
validation rejected the wrong-checksum address at the token/contract resolution layer.

**Fix:** use `eth_utils.to_checksum_address()` to derive the correct address, then call
`execute_contract_call` directly with `chain_id`, `contract_address`, `function_name`,
`function_args`, and `abi` (bypassing the broken plugin wrappers that send wrong param names).

## The live transaction (judging requirement)
- **TX hash:** `0xf3d953ad7035e9e4f92904e0cfb61eaf7d9efa1effbd650cf247943702655b90`
- **Link:** https://base.blockscout.com/tx/0xf3d953ad7035e9e4f92904e0cfb61eaf7d9efa1effbd650cf247943702655b90
- **Status:** `success` (confirmed Base mainnet)
- **Timestamp:** 2026-08-10 22:56:45 UTC
- **From:** `0x53A8DFA431D03A36499f9DB70AAFbb00C28308EA` (KeeperHub wallet)
- **To:** `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE`
- **Amount:** 10,000 units = **0.01 USDC**
- **Method:** execute (USDC.transfer)

## Submission assets (KeeperHub Agents Onchain, deadline Aug 13)
1. ✅ Live tx link (above) — the non-negotiable requirement
2. ✅ GitHub repo: `github.com/Gentech-Labs/programmable-money-x402` (or agent-economy-solana)
3. ⏳ Demo video — record the real on-chain transfer
4. ⏳ Assemble submission on DoraHacks

## Scripts (working, bypass plugin wrappers)
- `/tmp/kh_contract.py` — direct execute_contract_call with correct params
- Use `eth_utils.to_checksum_address()` on ANY contract address before sending to KeeperHub.
