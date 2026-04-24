# 60-SEC EXPLAINER: 22 Loops That Turned $2,730 into $2.73 Million

**Duration:** 60 seconds
**Target Platform:** TikTok / YouTube Shorts / Twitter
**Date:** 2026-04-17
**Source:** Dmob Due Diligence

---

## Hook (3 sec)
"One transaction. 22 loops. $2,730 in, $2.73 million out. This is how a reentrancy attack works."

## Problem (15 sec)
Solv Protocol had a vault called BRO — a tokenized yield position built on ERC-3525. The contract had a callback function that wasn't protected against reentrancy. An attacker found it, deposited 135 BRO tokens, then used a reentrancy exploit to loop the callback 22 times in a single transaction. Each loop inflated the token balance. By the end of that one transaction, they had 567 million tokens.

## Why It Matters (15 sec)
This is THE classic DeFi attack. It's the same bug class that hit The DAO in 2016 for $60 million. Nearly a decade later, protocols are STILL deploying unaudited contracts with reentrancy vulnerabilities. If you're holding tokens in any vault or lending protocol that hasn't been audited — your funds are one callback loop away from zero.

## Tip (15 sec)
Before you ape into any yield vault, check three things: Has the contract been formally audited? Does it use OpenZeppelin's ReentrancyGuard? Is there a reentrancy protection on ALL external calls? If the answer to any of those is no — your money is sitting on a ticking bomb. The attacker in this case sent everything to Tornado Cash. You'll never see it again.

## CTA (5 sec)
Like and follow if you want to stop losing money to bugs from 2016. Full audit breakdowns in my next video.

---

### Visual / Production Notes
- **Opening:** Screen recording of a transaction — show the loop in real time (sped up)
- **Problem section:** Simple animation — deposit box that keeps refilling itself
- **Tip section:** Checklist graphic with green checkmarks / red X's
- **Tone:** Fast-paced, educational, slight edge of "why is this still happening?"
- **Music:** Lo-fi beat, slightly glitchy — reinforces the "loop" concept
- **Thumbnail concept:** An infinity loop made of dollar signs with a cracked lock in the center
- **Hashtags:** #Reentrancy #SmartContractSecurity #DeFi #SolvProtocol #CryptoHacks #Solidity
