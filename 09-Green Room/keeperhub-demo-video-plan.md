# KeeperHub Demo Video — Shot List & Ideas (for tomorrow, Aug 11)

**Context:** KeeperHub proof transfer is LIVE and confirmed (see keeperhub-proof-transfer-live.md).
The demo video is the last submission piece before the DoraHacks form (deadline Aug 13).

## The one-sentence pitch
Lineage through the GTA arb executor wiring a real USDC transfer through KeeperHub's
onchain execution — live, verifiable, done.

## Story arc (under 2 min — judges weight working execution over polish)
1. **Hook (0:00–0:15)** — "This is an agent executing a real transaction through KeeperHub."
   Show the wallet, the 10 USDC balance.
2. **The wiring (0:15–0:40)** — agent (GTA arb executor) calls KeeperHub MCP with a
   USDC.transfer instruction. Explain x402/MPP dual-routing + gas handling (judging criteria).
3. **The execution (0:40–1:10)** — live tx fires, show it landing on Base mainnet.
   Paste the confirmed tx link into the frame.
4. **Proof + verification (1:10–1:45)** — pull up the blockscout tx, show `success`,
   wallet balance dropped 10.0 → 9.98. That IS the deliverable.
5. **Close (1:45–2:00)** — "Working execution, real onchain proof." Repo + link.

## What I need from you (or can produce)
- Screen recording of the actual tx (blockscout page + wallet). I can draft the narration
  script + shot list; you record on desktop or I can render.
- Repo link to feature: `github.com/Gentech-Labs/programmable-money-x402`

## Next
- Draft narration script (I'll write it)
- Decide recording method (desktop OBS vs me rendering a screenflow)
- Assemble DoraHacks submission (video + repo + tx link) by Aug 13
