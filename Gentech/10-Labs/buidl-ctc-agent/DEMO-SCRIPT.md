# BUIDL CTC 2026 Fall — Demo Video Script
**GenTech Verified Agent — The Oracle-Free Machine-Money Loop**

Target: ~3 minutes. Screen-record the terminal + a browser showing the CC3 explorer.

---

## [0:00–0:20] Hook — the problem
**Voiceover:**
> "Most DeFi agents make decisions on data they can't prove. They trust centralized
> oracles. When an autonomous agent moves money on unverifiable data, that's a trust
> hole. We built an agent that only acts on cryptographically verified cross-chain
> data — no oracle anywhere."

**Screen:** title card "GenTech Verified Agent — Oracle-Free Machine-Money Loop"

## [0:20–0:50] The loop — architecture
**Voiceover:**
> "Here's the loop. A USDC transfer happens on Sepolia. The Attestcoin Protocol
> generates a Merkle inclusion proof. Creditcoin verifies that proof on-chain. Only
> then does the AI decide — and trigger an action on Creditcoin."

**Screen:** the architecture diagram (from DECK.md), animated flow.

## [0:50–1:30] Live proof — Attestcoin integration
**Voiceover:**
> "First, the agent queries which chains Creditcoin attests. Live on testnet, it
> returns Ethereum and Sepolia. Then it generates a proof for a real transaction and
> verifies it on-chain."

**Screen:** run `node src/agent.mjs <txHash>` — show `getSupportedChains` output,
then `On-chain verification: SUCCESS ✓`.

## [1:30–2:10] The contract — trust enforced
**Voiceover:**
> "The action contract enforces the trust model. It refuses unverified events. Only
> cryptographically confirmed data gets recorded — and if it clears the threshold, it
> triggers a rebalance. Here are the tests proving it."

**Screen:** `npx hardhat test` — show 4/4 passing, highlight the "refuses unverified"
test.

## [2:10–2:40] The on-chain trigger
**Voiceover:**
> "When a verified event clears the threshold, the agent records it on Creditcoin and
> triggers the rebalance. The evidence lineage — chain, block, tx hash — is stored
> on-chain, so every decision is replayable and auditable."

**Screen:** the deployed contract on the CC3 explorer, showing `recordVerifiedEvent`
tx + `RebalanceTriggered` event.

## [2:40–3:00] Close
**Voiceover:**
> "GenTech Verified Agent — autonomous decisions you can prove. Built on the
> Attestcoin Protocol, on Creditcoin. No oracle. No trust hole. Just verified
> machine money."

**Screen:** GenTech Labs logo + "genTechlabs.net"

---

## Recording checklist
- [ ] Deploy contract to CC3 testnet (needs funded key)
- [ ] Run agent against a real Sepolia USDC tx
- [ ] Capture CC3 explorer showing the trigger event
- [ ] Record ~3 min, upload to YouTube/Vimeo, public
- [ ] Add URL to DoraHacks submission
