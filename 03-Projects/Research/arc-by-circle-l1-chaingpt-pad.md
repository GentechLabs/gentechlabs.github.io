# Arc by Circle — Stablecoin L1 & ChainGPT Pad

**Source:** [ChainGPT Pad on X](https://x.com/ChainGPT_Pad/status/2084243802366365748) — Mon Aug 03 2026
**Date:** 2026-08-04
**Author:** ChainGPT Pad (@ChainGPT_Pad)
**Tags:** #arc #circle #usdc #launchpad #l1 #stablecoin #hackathon

---

## TL;DR
Arc is Circle's EVM-compatible Layer-1 purpose-built for stablecoin finance: USDC is the **native gas token**, sub-second finality (Malachite consensus), opt-in privacy. Testnet live now (chain ID 5042002); mainnet targets Summer 2026. ChainGPT Pad is the first launchpad committed to it. This directly feeds our **Arc Programmable Money Hackathon** (deadline Aug 9).

---

## Confirmed Network Details (from ChainGPT Pad)

### Arc Testnet — LIVE NOW
| Param | Value |
|---|---|
| Network name | Arc Testnet |
| Chain ID | `5042002` |
| Chain ID (hex) | `0x4CEF52` |
| RPC URL | `https://rpc.testnet.arc.network` |
| Currency | USDC |
| Explorer | `https://testnet.arcscan.app` |
| Faucet | `faucet.circle.com` (test USDC) |

### Arc Mainnet — Summer 2026
- Chain ID / RPC / explorer: **published by Circle at launch**
- Currency: USDC (native gas)

⚠️ **Decimals — VERIFIED from live testnet (Aug 4):** The ChainGPT Pad FAQ claims Arc native USDC is **18 decimals**. On-chain probe of `decimals()` at `0x3600...0000` on the live testnet returns **6** (symbol/name `USDC`). Our `ArcAgentWallet.sol` correctly uses 6-decimal units. **Recheck at mainnet launch** — Circle may ship 18-decimal native USDC on mainnet, which would require amount scaling changes in the deploy.

---

## What Arc Is
- Open, EVM-compatible L1 built by **Circle** (issuer of USDC)
- USDC = native gas → dollar-denominated, predictable fees
- **Malachite consensus** → sub-second finality
- Opt-in privacy for institutional use
- EVM toolchain unchanged: Foundry, Hardhat, MetaMask all work

## Institutional Backing
- 100+ companies on testnet incl. **BlackRock, Visa, Goldman Sachs**
- Public testnet processed **244M+ transactions** in first 7 months (by May 2026)
- ARC token: whitepaper outlines 10B supply, **60% earmarked for ecosystem development** — but Circle CEO calls launch "still exploratory." **Any sale claiming ARC today is a red flag.**

---

## ChainGPT Pad Angle
- First launchpad committed to Arc (independent — NOT affiliated with Circle)
- Full stack: tiered IDOs, public sales (KYC/refunds/on-chain), Buzz campaigns, private rounds
- 100+ projects, 20+ chains, $20M+ raised so far
- Application: pad.chaingpt.org/contact-us — builders can apply now
- Users: KYC + $CGPT staking now = ready for day-one allocations

---

## GenTech Relevance

### 🔥 Directly serves Arc Programmable Money Hackathon (#2, deadline Aug 9)
The tweet/page gives us the **confirmed testnet params** our deploy needs:
- chain ID `5042002`, RPC `https://rpc.testnet.arc.network`, explorer `testnet.arcscan.app`
- Test USDC from `faucet.circle.com` (the exact step Jordan is queued to do)
- **18-decimal native USDC** — our x402/AgentWallet deploy must account for this

### Strategic read
- **Arc is Circle's own chain** → the *strongest* validation of our x402/agent-treasury thesis yet. Stablecoin-native rails ARE the direction of travel. A working x402 deploy on Arc = first-mover on a chain with BlackRock/Visa/Goldman at the table.
- **Robinhood Chain parallel** — we already track Robinhood's stablecoin L1 (perps leg pending). Arc is the same play from Circle. Both validate "stablecoin-native L1" as the emerging settlement layer. Keep both on the radar; x402 rail is chain-agnostic and ports to either.
- **Launchpad opportunity** — ChainGPT Pad listing GenTech's x402 gateway or a demo token on Arc could be marketing channel (Jordan's lens: open-source/hackathon exposure = marketing for our APIs).

## Action Items
- [ ] **Hackathon:** Jordan gets test USDC from `faucet.circle.com` (already queued in 08-03 handoff #2)
- [ ] Verify our `foundry.toml` arc_testnet RPC + chain ID match `5042002` / `rpc.testnet.arc.network` (confirm repo location)
- [ ] Confirm 18-decimal USDC handling in x402/ArcAgentWallet deploy script before testnet deploy
- [ ] (Optional) Add Arc testnet to MetaMask for manual verification: chain 5042002, RPC `rpc.testnet.arc.network`, USDC
- [ ] (Watch) ChainGPT Pad as potential marketing/launch channel on Arc

## Sources
- https://x.com/ChainGPT_Pad/status/2084243802366365748
- http://pad.chaingpt.org/arc
