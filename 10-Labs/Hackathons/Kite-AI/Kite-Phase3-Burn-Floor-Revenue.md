# Kite Phase 3: Agent NFT Burn Floor & Revenue Share Capture

**Date:** 2026-04-19
**Status:** Engineering-approved — ready for implementation
**Source:** Jordan conversation + Blackhole.xyz research + Dmob engineering review
**Related:** [[AAE - Staking & Revenue Sharing]], [[AAE - Multi-Agent Provider Monetization]]

---

## Problem Statement

Agent NFTs are inherently illiquid. Without a secondary market, users who buy an agent NFT can be trapped if nobody wants to buy it from them. The burn floor mechanism creates a **guaranteed exit** — users are never locked into a dead asset. Auto-burn for inactivity transforms this from a "panic exit" into a **protocol health mechanism** that cleans up zombie agents.

## Core Mechanism: The Burn Floor

### How It Works
1. User buys Agent NFT for `X` $TECH
2. User wants out → burns the NFT
3. Protocol returns `floor(X, revenue_history, reserveHealth)` from the reserve pool
4. NFT supply decreases, remaining NFTs become scarcer

### Dynamic Floor Formula

The burn return is **performance-weighted** and **reserve-health-adjusted**:

```
burnReturn = baseFloor + revenueBonus - inactivityPenalty

Where:
  baseFloor = mintPrice × 0.50  (50% guaranteed minimum)
  revenueBonus = min(revenueGenerated, mintPrice × 0.30)  (up to +30% for proven agents)
  inactivityPenalty = 0  (if active) OR mintPrice × 0.10  (if inactive >6 months)

Final payout = burnReturn × reserveHealthMultiplier

Where reserveHealthMultiplier:
  health >= 80% → 100% of floor
  health >= 50% → 90% of floor
  health >= 20% → 75% of floor
  health <  20% → 50% of floor + 48hr circuit breaker pause
```

### Burn Return Tiers

| Scenario | Burn Return | Rationale |
|----------|-------------|-----------|
| **Minted, never used** | 40-50% | Dead weight, no value proven |
| **Active, consistent fees** | 60-80% | Agent proved value, floor respects that |
| **Revenue exceeded mint cost** | 100%+ | User earned back more than paid |
| **Inactive >6 months** | 40% | Penalty for stagnation |
| **Inactive >12 months (auto-burn)** | 35% | Protocol reclaims zombie agents |

### Auto-Burn Tiered Scale (Sliding)

| Inactivity Period | Return % | Burned % | Action |
|-------------------|----------|----------|--------|
| 0-6 months (active) | 50% base + bonuses | 0% | Normal operation |
| 6-9 months | 45% | 5% penalty | First warning at month 6 |
| 9-12 months | 40% | 10% penalty | Second warning at month 9 |
| 12+ months (auto-burn eligible) | 35% | 15% penalty | Permissionless trigger with 0.5% caller bounty |

---

## Auto-Burn After Inactivity (Pull-Based)

### Inactivity Definition
An agent is **inactive** if it generates **zero fees above minimum threshold (≥0.01 $TECH) for 12 consecutive months**.

### Auto-Burn Flow (Permissionless Trigger)
1. **Month 6**: First warning — "Your agent has been inactive for 6 months. Reactivate or risk auto-burn."
2. **Month 9**: Second warning + 5% floor penalty applied
3. **Month 12**: Agent becomes eligible for auto-burn at 35% floor
4. **Anyone can call `triggerAutoBurn(tokenId)`** after the deadline → NFT destroyed, tokens sent to owner, caller gets 0.5% bounty
5. **User action at any point**: Downgrade to free tier → stops the countdown, keeps the NFT (with reduced features)

### Why Pull-Based > Cron
- **No keeper costs** — the community incentivizes cleanup via caller bounty
- **Scales infinitely** — no O(n) iteration over all NFTs
- **Permissionless** — anyone can trigger, including the protocol itself
- **Gas efficient** — single token burn per call, no batch processing needed

```solidity
function triggerAutoBurn(uint256 tokenId) external {
    Agent memory agent = agents[tokenId];
    require(agent.status == STATUS_INACTIVE, "Not inactive");
    require(block.timestamp >= agent.inactiveDeadline, "Deadline not reached");
    require(!isBurned(tokenId), "Already burned");

    uint256 floor = _calculateFloor(agent); // 35% auto-burn rate
    uint256 bounty = floor * 5 / 1000; // 0.5% caller incentive

    _markBurned(tokenId);
    _burn(tokenId);
    reservePool.claim(agent.owner, floor - bounty);
    reservePool.claim(msg.sender, bounty);

    emit AgentAutoBurned(tokenId, floor, block.timestamp, msg.sender);
}
```

### Why Auto-Burn Matters
- Prevents zombie NFTs from cluttering the registry
- Keeps supply healthy and meaningful
- Forces users to either use their agent or release it back to the protocol
- The 35% auto-burn floor is intentionally lower than voluntary burn (40-50%) to incentivize proactive decisions

---

## Free Tier Downgrade Path

### The "Pause Button"
Instead of burning, users can **downgrade their Agent NFT to free tier**:

- Keep the NFT (soulbound, non-transferable — ERC-5192 compliant)
- Lose premium features (custom brain, advanced tools, higher execution limits)
- Stop the auto-burn countdown
- Can upgrade back to paid tier at any time

### Why This Is The Smartest Design
Most users will **downgrade rather than burn** — this keeps them in the ecosystem. The free tier acts as a holding pattern for users who might return later. It's the psychological safety net that prevents panic burns.

---

## Reserve Pool Economics

### Funding Sources

| Source | % | Annual Estimate |
|--------|---|-----------------|
| **Mint Fee Allocation** | 10% of every mint | Primary funding |
| **Protocol Fee Tax** | 2% of all agent fees | Secondary, growing over time |
| **Treasury Backstop** | As needed | Emergency liquidity |

### Pool Mechanics
- The reserve pool is a **separate smart contract** with controlled withdrawals
- Only the burn function can withdraw from it
- Pool balance is **publicly auditable** on-chain
- **Circuit breaker**: if health drops below 10%, pause burns for 48 hours to allow replenishment
- Dynamic fee adjustment: if pool runs low (< 20% health), mint fees increase to 15% until recovery

### Sustainability Model

```
Reserve Health = poolBalance / (totalOutstandingNFTs × avgFloorPrice)

If health < 0.10 → PAUSE burns for 48hr (circuit breaker)
If health < 0.20 → increase mint fee to 15%, burn multiplier = 75%
If health > 0.50 → reduce mint fee to 5%, burn multiplier = 90%
If health > 0.80 → burn multiplier = 100%, excess flows to treasury
```

---

## Smart Contract Architecture (Engineering-Approved)

### Core Contracts

```
AgentNFT (ERC-721Upgradeable, IMMUTABLE after deploy)
├── Ownable / AccessControl
├── Pausable
├── ReentrancyGuard
├── mint(price, agentConfig) → payable, calls ReservePool.fund()
├── burn(tokenId) → destroys NFT, calls ReservePool.claim()
├── downgrade(tokenId) → sets soulbound flag (ERC-5192 locked())
├── triggerAutoBurn(tokenId) → permissionless, caller gets 0.5% bounty
└── transferFrom() → blocked if soulbound (override all transfer paths)

ReservePool (UUPSUpgradeable)
├── AccessControl (only AgentNFT can call claim)
├── Pausable (circuit breaker)
├── fund() → internal, called by AgentNFT.mint()
├── claim(recipient, amount) → only AgentNFT, nonReentrant
├── health() → view, calculates reserve ratio
└── setMintFee() → only governance

AgentRegistry (Library / Pure Storage Contract)
├── mapping(tokenId → AgentData) — packed struct
├── lastFeeTimestamp(tokenId) → for inactivity check
├── cumulativeRevenue(tokenId) → packed storage
├── getStatus(tokenId) → Active / Inactive / Downgraded / Burned
└── recordFee(tokenId, amount) → only FeeDistributor

FeeDistributor
├── distribute() → splits fees: stakers/treasury/team/reserve
├── reserveContribution() → 2% to ReservePool
├── recordFee(tokenId, amount) → updates AgentRegistry
└── claimRewards(staker) → merkle-based distribution
```

### Packed Agent Struct (Gas Optimized)

```solidity
struct Agent {
    uint128 mintPrice;          // bytes 0-15
    uint128 revenueGenerated;   // bytes 16-31
    uint40 lastFeeTimestamp;    // bytes 32-37
    uint8 status;               // byte 38 (0=active, 1=inactive, 2=downgraded, 3=burned)
    bytes32 configHash;         // bytes 39-70 (IPFS CID hash, 1 slot)
} // Fits in 3 slots instead of 5+
```

### Key Solidity Patterns

```solidity
// Burn function — Check-Effects-Interact pattern
function burn(uint256 tokenId) external nonReentrant {
    require(ownerOf(tokenId) == msg.sender, "Not owner");
    require(!isBurned(tokenId), "Already burned");

    Agent memory agent = agents[tokenId];
    uint256 floor = _calculateFloor(agent);
    uint256 multiplier = _getBurnMultiplier();
    uint256 payout = floor * multiplier / 100;

    require(reservePool.balance() >= payout, "Insufficient reserve");

    _markBurned(tokenId);         // Effects: update state FIRST
    _burn(tokenId);               // Effects: destroy NFT

    reservePool.claim(msg.sender, payout);  // Interact: external call LAST

    emit AgentBurned(tokenId, payout, block.timestamp);
}

// Dynamic burn multiplier tied to reserve health
function _getBurnMultiplier() internal view returns (uint256) {
    uint256 health = _calculateHealth();
    if (health >= 80) return 100;
    if (health >= 50) return 90;
    if (health >= 20) return 75;
    return 50;  // Emergency floor
}

// Soulbound transfer override (ERC-5192)
function transferFrom(address from, address to, uint256 tokenId) public override {
    require(!soulbound[tokenId], "Soulbound: transfer blocked");
    super.transferFrom(from, to, tokenId);
}

// Inactivity tracking — lazy on-chain, no oracle needed
function recordFee(uint256 tokenId, uint256 amount) external onlyFeeDistributor {
    agents[tokenId].revenueGenerated += uint128(amount);
    agents[tokenId].lastFeeTimestamp = uint40(block.timestamp);
}
```

---

## Game Theory & Incentive Alignment

### User Incentives
| Action | User Gets | Protocol Gets |
|--------|-----------|---------------|
| **Mint + use actively** | Revenue + burn floor security | Fees + healthy ecosystem |
| **Mint + downgrade to free** | Free agent, stopped countdown | Retained user, potential re-upgrade |
| **Burn voluntarily** | 40-80% of mint back | Deflationary supply reduction |
| **Hold inactive** | Nothing (auto-burn countdown) | Zombie cleanup via permissionless trigger |

### Flywheel Effects
1. **Burn floor confidence** → more mints → larger reserve pool → stronger floor
2. **Auto-burn** → zombie cleanup → scarcer active agents → higher perceived value
3. **Downgrade path** → user retention → reactivation potential → LTV increase
4. **Deflationary pressure** → burned agents removed → remaining agents appreciate

### Risk Mitigations (Engineering-Reviewed)

| Risk | Mitigation | Severity |
|------|------------|----------|
| **Reserve drain (bank run)** | Dynamic burn multiplier + 48hr circuit breaker at 10% health | Critical |
| **Self-dealing revenue inflation** | Revenue excludes self-referential transactions; minimum unique buyer threshold | High |
| **Flash loan reserve check bypass** | Snapshot-based health check; balance checked at tx start | High |
| **Soulbound bypass via approval** | Override `transferFrom`, `safeTransferFrom`, `approve`, `setApprovalForAll` | High |
| **Re-entrancy on burn→claim** | `ReentrancyGuard` + check-effects-interact pattern | Critical |
| **Mass burn events** | 12-month inactivity threshold prevents panic cascades | Medium |
| **Gas griefing on auto-burn** | Limit to 1 agent per trigger tx; caller bounty incentivizes efficiency | Medium |
| **Inactivity timestamp manipulation** | Minimum fee threshold (≥0.01 $TECH) required to reset clock | Medium |

---

## Comparison: Blackhole vs Kite Burn Models

| Aspect | Blackhole (Supermassive veNFT) | Kite (Agent Burn Floor) |
|--------|-------------------------------|------------------------|
| **Burn Action** | Burn $BLACK → permanent veNFT | Burn Agent NFT → token refund |
| **Supply Effect** | Deflationary (tokens destroyed) | Deflationary (NFTs destroyed) |
| **User Benefit** | Permanent voting power + 10% boost | Guaranteed exit + revenue bonus |
| **Protocol Benefit** | No team sell pressure | Healthy NFT registry, retained users |
| **Key Innovation** | Burn = upgrade | Burn = insurance policy |
| **Auto-Burn** | None | Permissionless trigger with caller bounty |
| **Reserve Health** | N/A | Dynamic multiplier + circuit breaker |

---

## Implementation Priority (Dmob-Approved)

| Phase | What | Why First |
|-------|------|-----------|
| **3.1** | ReservePool contract — funding, claim, health check, pausable | Foundation — everything else depends on this. Deploy & audit first. |
| **3.2** | AgentNFT core — mint, flat 50% burn, soulbound flag, re-entrancy guard | Core functionality, simplest formula first |
| **3.3** | Revenue tracking — `recordFee()`, `lastFeeTimestamp`, packed struct | Enables dynamic floor calculation |
| **3.4** | Dynamic floor — full formula + reserve health multiplier + inactivity penalty | Adds complexity on top of working base |
| **3.5** | Auto-burn — `triggerAutoBurn()` with caller bounty | Pull model, can be added last |
| **3.6** | Dynamic fees — health-based mint fee adjustment | Optimization, not core functionality |

**Do NOT build in parallel.** The reserve pool must be deployed, tested, and audited before the NFT contract references it.

---

## Recommended Standards & Libraries

| Pattern | Library | Why |
|---------|---------|-----|
| **ERC-721** | `@openzeppelin/contracts-upgradeable/token/ERC721/ERC721Upgradeable.sol` | Standard, upgradeable, well-audited |
| **Access Control** | `@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol` | Role-based, granular permissions |
| **Reentrancy Guard** | `@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol` | Non-negotiable for burn→claim |
| **Pause** | `@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol` | Emergency circuit breaker |
| **Safe ERC-20** | `@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol` | Safe transfers for $TECH |
| **UUPS Proxy** | `@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol` | Cheaper proxy for ReservePool |
| **ERC-5192** | Custom `locked()` view implementation | Soulbound standard compliance |
| **Fixed-point math** | `@openzeppelin/contracts/utils/math/Math.sol` or `solady/Math` | Safe percentage calculations |

**Avoid Solmate** for this project. It's gas-optimized but less battle-tested than OpenZeppelin for financial contracts handling treasury funds. The gas savings (~10-20%) aren't worth the audit risk when you're holding a reserve pool.

---

## Config Storage

Burned agent configs preserved via **IPFS hash on-chain** (1 slot, 32 bytes):
- Full config lives off-chain on IPFS
- Hash stored on-chain for tamper resistance
- Re-minting the same config: caller provides IPFS CID, contract verifies hash matches a previously burned agent's config
- Can apply a re-mint discount for recycled configs

---

## Tech Stack Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **AgentNFT** | Immutable after deploy | Users need confidence their NFT rules won't change. ERC-721 standard is stable. |
| **ReservePool** | UUPS Upgradeable | Burn formula may need adjustment. Fee parameters will change. Emergency fixes may be needed. |
| **AgentRegistry** | Library / Pure Storage | Avoid cross-contract call overhead. Logic belongs in AgentNFT and ReservePool. |
| **Inactivity Tracking** | On-chain, lazy | ~5k gas per fee event. No oracle needed. Internal protocol state only. |
| **Soulbound** | Same contract + flag | No need to migrate NFTs between contracts. Simpler UX, lower cost, easier audit. |

---

## Open Questions for Jordan

1. What's the target mint price range for agents? ($100, $500, $1000+)
2. Auto-burn warnings: Telegram notification, email, or on-chain event only?
3. Should there be a grace period after auto-burn where users can recover their NFT? (Dmob recommends against — creates uncertainty around burn finality)
4. Re-mint discount for recycled configs? (Suggested: 10% off mint price if config matches a burned agent)
