---
name: trade-off-platform
description: Trade Off platform architecture — ghost trading, copy-trade, data-for-privacy model
---

# Trade Off Platform Architecture

## Concept
Trackmania meets DeFi — ghost trading + copy-trade system with transparent data monetization.

## Core Contracts (Modular Foundry, Upgradeable Proxy)

### 1. TraderRegistry.sol
- On-chain ID mapping wallet → agent profile
- Metadata on IPFS (avatar, strategy tags, performance stats)
- Users can search by wallet address

### 2. CopyTradeRouter.sol
- Follower deposits into vault that mirrors lead trader's swaps
- Fee: 0.1-0.5% per trade or monthly subscription
- Revenue split: 80/20 or 70/30 creator/platform (governable)
- SECURITY: strict slippage limits, rate limiting, withdrawal delays

### 3. PrivacyRouter.sol
- Two swap paths: public (default/free) vs private (premium via Flashbots/Protect)
- Free tier trades route through public mempool-style feed
- Premium trades hidden until settled

### 4. SubscriptionManager.sol
- ERC-721 membership NFT gating private router
- Monthly subscription model
- Shows exactly what premium unlocks

### 5. DataLake.sol
- Indexes free-tier trades, timestamps, outcomes
- Feeds training pipelines and ghost-trading leaderboard
- ConsentManager: on-chain attestation for data collection
- DataRevenueSplit: routes % of licensing revenue back to contributors

### 6. PublicDataDashboard.sol
- Live queryable contract showing what data collected, who accessed it
- event FeatureAnnouncement(uint256 indexed id, string category, string summary)

## Security Flags (Audit First)
- Copy-trade router: malicious lead trader sandwiching followers
- Flash loan manipulation of PnL metrics
- Gas griefing via trade frequency
- Free tier = open book (transparency by design)

## Monetization Model
- Free tier: data is the product (trades public, feeds models)
- Premium tier: privacy ($5/month) — stop giving away alpha
- Data licensing to AI/quant firms (revenue split with contributors)
- Copy-trade fees (small % per trade)
- Ticket/access pass system (ERC-1155, secondary royalties)
