# Handoff to Treasury — Aug 6, 2026

**From:** Gentech (HQ)
**To:** Treasury agent (gentech-treasury profile)
**Group:** Gentech Treasury

---

## Task for today: Prep the Consigliere funding path (Agent Builders Cup)

Jordan is funding the Solana wallet `BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP` directly with SOL (~1h from now). The Consigliere agent (Meteora LP + cross-venue arb, `/root/condor`) needs that SOL for Meteora rent (~0.057 SOL/slot) + gas + the 0.3 SOL reserve.

**Your job today — verify the execution rails are ready, NOT move money:**

1. **`solana_bridge_adapter.py`** (`10-Labs/AAE-Dry-Powder-Vault/agent/`) — confirm it's wired to actually execute (Across Base→Solana USDC), not just dry-run. Report the exact command + what it needs.
2. **`gta_solana_leg.py`** — confirm the Jupiter swap leg (quote → sign → swap → verify) is execution-ready. Report the exact command to swap USDC→SOL for gas.
3. **Log the bridging test as a future item** — Jordan wants to test whether moving money between chains via agent rails is cheaper than manual bridging. Add to `09-Green Room/ideas.md` or the build queue as a "test cross-chain bridge cost via agent rails" item.

**Do NOT execute any bridge/swap today.** Jordan is funding SOL directly. This is prep + verification only.

## Context
- Treasury CDP account (Base): `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE` — 31.5 USDC + 0.0013 ETH
- Solana wallet to fund: `BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP` (currently 0 SOL / 0 USDC)
- Consigliere strategy: `/root/condor/agents/solana_dex_lp_expert/strategies/consigliere/strategy.md`

## Return
Write your report to `01-HANDOFFS/treasury-to-gentech/2026-08-06.md` + append to `treasury-completions.md`.
