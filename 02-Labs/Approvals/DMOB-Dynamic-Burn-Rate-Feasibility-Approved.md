# 🔬 DMOB Feasibility Review — Dynamic Burn Rate (Agent NFT Burn Floor)

**Date:** 2026-05-02
**Reviewer:** DMOB (Labs)
**Source:** Handoff from Desmond via Jordan | Kite Phase 3 Spec v2
**Priority:** CRITICAL — Overdue by 13 days
**Status:** ✅ APPROVED — Feasible with recommended architecture

---

## Executive Summary

**Verdict:** ✅ **FEASIBLE** — The dynamic burn floor mechanism is sound from a smart contract perspective and can be implemented securely with established patterns. The engineering-approved spec from Kite Phase 3 is robust and follows best practices.

**Key Strengths:**
- Pull-based auto-burn eliminates keeper costs
- Reserve pool circuit breaker prevents bank runs
- Packed structs optimize gas (~3 slots vs 5+)
- Soulbond (ERC-5192) path preserves user retention
- Revenue tracking is on-chain, lazy, no oracle needed

**Primary Risks (Mitigated):**
| Risk | Severity | Mitigation | Residual |
|------|----------|------------|----------|
| Reserve drain / bank run | Critical | Dynamic multiplier + 48hr pause at <10% health | Low |
| Revenue inflation attack | High | Minimum fee threshold + unique buyer checks | Medium |
| Flash loan manipulation | High | Snapshot balance at tx start | Low |
| Re-entrancy on burn→claim | Critical | `ReentrancyGuard` + CEI pattern | None |
| Soulbound bypass | High | Override ALL transfer functions | None |

---

## Architecture Assessment

### ✅ Recommended Pattern: Two-Contract System

```
AgentNFT (ERC-721Upgradeable, IMMUTABLE)
├── mint(price) → payable, internal ReservePool.fund()
├── burn(tokenId) → calls ReservePool.claim()
├── downgrade(tokenId) → soulbound flag (ERC-5192)
├── triggerAutoBurn(tokenId) → permissionless + 0.5% caller bounty
└── Override: transferFrom, safeTransferFrom, approve, setApprovalForAll

ReservePool (UUPSUpgradeable)
├── fund() — only AgentNFT
├── claim(recipient, amount) — only AgentNFT, nonReentrant
├── health() → view: poolBalance / (totalNFTs × avgFloorPrice)
├── circuit breaker: pause() when health < 10%
└── setMintFee() — governance
```

**Why this separation:**
- AgentNFT immutable → user confidence (no rule changes post-mint)
- ReservePool upgradeable → fee adjustments, emergency fixes
- Clear access control boundaries
- Reserve funds isolated from NFT logic

### Gas Optimization Highlights

**Packed Agent Struct (3 slots = 192 bytes):**

```solidity
struct Agent {
    uint128 mintPrice;           // bytes 0–15
    uint128 revenueGenerated;   // bytes 16–31
    uint40 lastFeeTimestamp;    // bytes 32–37
    uint8 status;               // byte 38  (0=active,1=inactive,2=downgraded,3=burned)
    bytes32 configHash;         // bytes 39–70 (IPFS CID)
}
// Storage savings: ~40% vs naive struct (5+ slots → 3 slots)
```

**Cost breakdown (est.):**
- Mint: ~120k gas (standard ERC-721 + struct write)
- Record fee: ~5k gas (single slot update)
- Burn: ~150k gas (includes external ReservePool claim call)
- Auto-burn trigger: ~160k gas (read-heavy, single external call)

**On-chain revenue tracking is cheap** — just `uint128` accumulator per NFT. No oracle needed; fees are recorded internally by `FeeDistributor.recordFee(tokenId, amount)`.

---

## Dynamic Formula Feasibility

The proposed formula is clean and fully on-chain computable:

```solidity
function _calculateFloor(Agent memory agent) internal view returns (uint256) {
    uint256 base = agent.mintPrice * 50 / 100;              // 50% guaranteed
    uint256 bonus = min(agent.revenueGenerated, agent.mintPrice * 30 / 100);
    uint256 total = base + bonus;  // up to 80% for proven agents

    // Inactivity penalty: 6mo→45%, 9mo→40%, 12mo→35%
    if (agent.status == STATUS_INACTIVE_6MO)  total = total * 45 / 100;
    if (agent.status == STATUS_INACTIVE_9MO)  total = total * 40 / 100;
    if (agent.status == STATUS_INACTIVE_12MO) total = total * 35 / 100;

    // Reserve health multiplier
    uint256 health = reservePool.health();
    uint256 multiplier = health >= 80 ? 100 :
                         health >= 50 ? 90 :
                         health >= 20 ? 75 : 50;
    return total * multiplier / 100;
}
```

**Precision:** Using basis points (10000 = 100%) is cleaner; the above uses integer division safely because all numerators are ≥ denominator minimums. No rounding errors meaningful at these scales.

---

## Security Review (Critical Path)

### 1. Re-entrancy Guard — ✅ REQUIRED
**Risk:** `burn()` calls `reservePool.claim()` — external call after state change.
**Pattern:** `nonReentrant` + check-effects-interact already specified in spec. **ACCEPTABLE.**

### 2. Reserve Health Snapshot — ✅ REQUIRED
**Risk:** Flash loan attacker checks `reservePool.balance()` → sees sufficient funds → burns → between check and call, reserves drained by other tx.
**Fix:** Snapshot health at start of transaction:

```solidity
uint256 snapshotBalance = reservePool.balance();
require(snapshotBalance >= payout, "Insufficient reserve at tx start");
```

Or embed the check inside `ReservePool.claim()` itself (preferred — single point of truth).

### 3. Timestamp Manipulation — ✅ ACCEPTABLE
**Risk:** Miners could slightly manipulate `block.timestamp` to delay/advance inactivity clock.
**Impact:** Minimal — 1-month thresholds, 60-second miner wiggle room is noise. No action needed.

### 4. Revenue Self-Dealing — ⚠️ NEEDS GUARD
**Risk:** User creates two agents, pays self fees to inflate revenue → higher burn floor.
**Mitigation:** `FeeDistributor.recordFee()` should enforce minimum unique buyer count or cap self-fee contributions at 10% of total. **Recommend adding:**

```solidity
require(uniqueBuyersCount > 0, "No external revenue");
```

### 5. Permissionless Auto-Burn — ✅ SOUND
**Pull-based model** with 0.5% caller bounty is gas-efficient and scales. No keeper dependencies. No griefing risk because:
- Only eligible after 12 months inactivity
- Single agent per tx (no batch griefing)
- Bounty < gas cost for pointless spam

---

## Layer 8: Agent Self-Awareness

### Requirement: Agents query floor price + emit warnings

**Cleanest pattern:** On-chain view + separate event emitter (off-chain watcher).

```solidity
// In AgentNFT
function getFloorPrice(uint256 tokenId) external view returns (uint256) {
    Agent memory agent = agents[tokenId];
    return _calculateFloor(agent);
}

// Warning events (emitted by FeeDistributor on lastActivity update)
event AgentActivityWarning(uint256 indexed tokenId, uint256 monthsInactive);
event AgentDowngradeReady(uint256 indexed tokenId);  // 9mo mark
event AgentAutoBurnEligible(uint256 indexed tokenId);  // 12mo mark
```

**Why not emit from AgentNFT itself?** Gas cost. A separate off-chain cron (Beam Cloud) can scan the registry daily and emit warning events for any agent approaching thresholds. Cheaper than on-chain checks every fee record.

---

## Implementation Roadmap (DMOB-Approved Phases)

**DO NOT build in parallel** — ReservePool must be deployed and audited first.

| Phase | Deliverable | Owner | Est. Time |
|-------|-------------|-------|-----------|
| 3.1 | `ReservePool.sol` (UUPS, Pausable, AccessControl) | DMOB | 3 days |
| 3.2 | `AgentNFT.sol` core (mint/burn/soulbound, flat 50% floor) | DMOB | 4 days |
| 3.3 | `FeeDistributor.recordFee()` integration + packed struct | Desmond/AAE | 2 days |
| 3.4 | Dynamic floor formula (revenue bonus + inactivity penalty) | DMOB | 2 days |
| 3.5 | Reserve health multiplier + circuit breaker | DMOB | 1 day |
| 3.6 | `triggerAutoBurn()` with caller bounty | DMOB | 1 day |
| 3.7 | Full test suite (Foundry: unit + invariant + fuzz) | DMOB | 3 days |
| 3.8 | Internal audit (YoYo + DMOB walk-through) | Joint | 1 day |
| 3.9 | Testnet deployment (Base Sepolia) + integration tests | DMOB | 2 days |

**Total critical path:** ~19 days (3.5 weeks) with parallel test writing.

---

## Chain Selection Recommendation

**Base (EVM) only for v1.**

**Why:**
- $TECH lives on Base (existing Token contract)
- AgentEscrow already EVM-native
- Developer tooling (Foundry, ethers.js) is mature
- YoYo's monitoring stack (Beam Cloud) is EVM-first

**Solana expansion** can be Phase 2 after hackathon sprint. The same economics apply, but requires Anchor rewrite + Pyth oracle integration.

---

## Open Questions for Jordan

1. **Mint price band:** What's the target range? ($100, $500, $1000+) — affects reserve sizing
2. **Warning channel:** Telegram notification, email, or on-chain events only?
3. **Grace period post-auto-burn:** DMOB recommends NO — burn finality must be absolute. Users have 12 months + downgrade path.
4. **Re-mint discount:** Should burned agents with matching IPFS config get 10% off if re-minted?

---

## DMOB Approval

✅ **APPROVED — Ready for Implementation**

The spec is engineering-ready. No showstoppers. Proceed with Phase 3.1 (ReservePool) immediately.

**Conditions:**
1. Fix `BurnSplitter` critical finding (onlyRouter) before any deployment (see YoYo audit)
2. Add revenue self-dealing guard in `FeeDistributor.recordFee()`
3. Snapshot reserve balance at tx start in `ReservePool.claim()`
4. All contracts must use OpenZeppelin upgradeable (no Solmate for treasury-facing contracts)

**Next handoff:** Once Phase 3.1 code is written, DMOB to perform line-by-line security review before Phase 3.2 begins.

---

*Approved by DMOB, Labs | Doc: `02-Labs/Hackathons/Kite-AI/Kite-Phase3-Burn-Floor-Revenue.md`*
