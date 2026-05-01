---
name: spec-creation
category: software-development
description: Create technical specifications for smart contract features — architecture decisions, failure modes, open questions, and team delegation patterns.
---

# Spec Creation Workflow

## When to Use
- Before writing smart contract code for new features
- When designing multi-agent delegated work
- When building features with financial implications (gas, yield, fees)

## Steps

1. **Draft spec in vault** at `09-Green Room/spec-{feature-name}.md`
2. **Include these sections:**
   - Trigger mechanism (primary + fallback)
   - Gas economics (reserve %, cost estimates, depletion handling)
   - Failure modes (slippage, downtime, MEV, exploits)
   - Revenue model (fees, upsell paths)
   - Open questions for decision maker
3. **Delegate modeling work** to appropriate agents (e.g., YoYo→Strategies for LP math, yield impact)
4. **Report back** to user with:
   - What's done
   - What's in progress
   - Open questions needing decisions

## Key Decisions to Surface
- Gas reserve currency (native token vs stablecoin)
- Who pays on failure (user vs platform)
- Minimum deposit thresholds
- Opt-in vs opt-out for automated features

## Pitfalls
- Don't code without spec — smart contract edge cases are expensive post-deploy
- Always model gas costs on target network, not Ethereum mainnet
- Include depletion handling for gas reserves
- Surface volatile vs stable currency tradeoffs early