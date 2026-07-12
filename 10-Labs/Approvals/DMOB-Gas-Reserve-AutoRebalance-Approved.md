# 💰 DMOB Feasibility Review — Gas Reserve Auto-Rebalance

**Date:** 2026-05-02
**Reviewer:** DMOB (Labs)
**From:** Jordan (spec originator)
**Priority:** HIGH — Pending
**Status:** ✅ APPROVED — Feasible with recommended architecture refinements

---

## Executive Summary

**Verdict:** ✅ **FEASIBLE** — The gas abstraction + auto-rebalance pattern is sound and implementable with standard DeFi patterns. The spec requires modest refinement around keeper authentication, gas estimation accuracy, and multi-chain abstraction but has no architectural blockers.

**Core Insight:** This is a **subscription-tier escrow pattern** — user deposits once, platform manages gas internally. The value is convenience + intelligence, not gas arbitrage. **Jordan's principle holds:** "Gas at cost, margin on agent services."

**Primary Risks (Mitigated):**
| Risk | Severity | Mitigation | Residual |
|------|----------|------------|----------|
| Gas estimation overdraw | High | Conservative buffer (30%) + snapshot-based checks | Low |
| Keeper unauthorized rebalance | Critical | `onlyOperator` + timelock owner override | None |
| Reserve drain from spam | Medium | `maxGasPercentPositionValue` guard (1-5%) | Low |
| Multi-chain oracle manipulation | High | Chain-specific price feeds (Pyth/Chainlink) | Medium |
| User withdraw during rebalance | Medium | Reentrancy guard + reserve snapshot | Low |

---

## Architecture Assessment

### ✅ Recommended Contract Skeleton

```solidity
contract GasReserveAutoRebalance is ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Immutables
    IERC20 public immutable usdc;          // Base: USDC, Avalanche: USDC.E
    address public immutable operator;     // Gentech agent wallet
    address public immutable lpManager;    // Uniswap/LFJ pool manager adapter
    uint256 public immutable maxGasPct;    // 300 = 3% max gas/position value

    // Per-user state
    mapping(address => uint256) public gasReserveBalance;
    mapping(address => uint256) public lpPositionId;  // NFT position ID

    // Events
    event Deposited(address indexed user, uint256 amount, uint256 gasReserve, uint256 lpAmount);
    event Rebalanced(address indexed user, uint256 tokenId, uint256 gasCost, uint256 newLower, uint256 newUpper);
    event GasToppedUp(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 gasAmount, uint256 lpAmount);

    // ─── Core Functions ──
    function deposit(uint256 amount) external nonReentrant;
    function rebalance(uint256 tokenId, int24 newLower, int24 newUpper) external onlyOperator;
    function topUpGas() external payable;
    function withdraw() external nonReentrant;
    function getGasReserve(address user) external view returns (uint256);
    function estimateRebalanceGas(uint256 tokenId) external view returns (uint256 gasEstimate);
}
```

**Key patterns:**
1. **ReentrancyGuard** on all state-changing functions (CEI enforced)
2. **Immutable references** — `operator`, `usdc`, `lpManager` set at deploy
3. **Pull-over-push** — user `withdraw()` pulls funds; no forced transfers
4. **Conservative gas estimation** — `estimateRebalanceGas()` returns high-end estimate + 30% buffer

---

## Multi-Chain Strategy

### Chain-Specific Adapters

Each chain needs an `LpManager` adapter contract that abstracts the LP protocol:

```solidity
interface ILpManager {
    function increaseLiquidity(address token0, address token1, int24 tickLower, int24 tickUpper, uint256 amount0, uint256 amount1) external returns (uint128 liquidity, uint256 actualAmount0, uint256 actualAmount1);
    function decreaseLiquidity(uint256 tokenId, uint128 liquidity) external returns (uint256 amount0, uint256 amount1);
    function collect(address token0, address token1, address receiver) external returns (uint256 amount0Collected, uint256 amount1Collected);
    function getPosition(uint256 tokenId) external view returns (uint96 liquidity, int24 tickLower, int24 tickUpper);
}
```

**Adapters:**
- **Base/Ethereum:** `UniswapV3Manager.sol` — wraps Uniswap V3 NonfungiblePositionManager
- **Avalanche:** `LFJManager.sol` — wraps LFJ pool manager (TraderJoe/Vector?)
- **Solana:** Separate Anchor program in `/programs/gas-reserve/` — Jupiter + Orca SDK

**Configuration per chain:**

```solidity
struct ChainConfig {
    address lpManager;
    address priceFeed;      // Chainlink or Pyth
    uint256 avgRebalanceGas;
    uint256 reserveTopUpThreshold;  // e.g., $1 on Base, $0.50 on Solana
    uint256 maxGasPercentPositionValue;  // e.g., 300 = 3%
}
mapping(Chain => ChainConfig) public chainConfigs;
```

---

## Gas Estimation Strategy

### Problem
Gas costs are variable (network congestion, swap path complexity). Hard to pre-calculate exactly.

### Solution: Three-Tier Estimation

1. **Static baseline** — `avgRebalanceGas` stored per-chain (configurable by governance)
2. **Dynamic override** — `estimateRebalanceGas(tokenId)` does:
   - Fetch current pool tick / tick range
   - Calculate sqrtPriceX96 delta needed
   - Query on-chain oracle for current tick → estimate swap cost
   - Return: `baseline * marketMultiplier + buffer`

3. **Circuit breaker guard** — actual gas cost (captured post-rebalance) compared to estimate:
   - If actual > estimate × 1.5 → flag for review, may tighten reserve guard
   - If actual < estimate × 0.5 → update baseline downward (slow decay)

### Conservative Guard Formula

```solidity
function _canRebalance(uint256 tokenId) internal view returns (bool) {
    uint256 positionValue = getPositionValue(tokenId);
    uint256 maxGas = positionValue * maxGasPct / 10000;  // e.g., 3% cap
    uint256 gasEstimate = estimateRebalanceGas(tokenId);

    return gasEstimate <= maxGas &&
           gasReserveBalance[msg.sender] >= gasEstimate;
}
```

**Why cap as % of position value?** Prevents griefing where tiny position gets drained by expensive rebalance. Also prevents reserve depletion through sudden gas spike.

**Buffer:** Set `maxGasPct` to 300 (3%) — comfortably covers most spikes while preventing abuse.

---

## Keeper / Operator Authentication

### Required Properties
1. **Single operator only** — Gentech agent wallet
2. **Governance can rotate operator** (in case of key compromise)
3. **Rate-limited** — prevent spam rebalances
4. **Economic alignment** — operator should have skin in the game (not pure altruism)

### Recommended Pattern: Timelock + 2-Step

```solidity
address public operator;
address public pendingOperator;
uint256 public constant OPERATOR_TIMELOCK = 2 days;

modifier onlyOperator() {
    require(msg.sender == operator, "Only operator");
    _;
}

function proposeOperator(address newOp) external onlyOwner {
    pendingOperator = newOp;
    emit OperatorProposed(newOp, block.timestamp);
}

function acceptOperator() external {
    require(msg.sender == pendingOperator, "Not proposed");
    require(block.timestamp >= proposalTimestamp + OPERATOR_TIMELOCK, "Timelock active");
    operator = pendingOperator;
    pendingOperator = address(0);
}
```

**Operator incentives:** Not strictly necessary for feasibility, but for production:
- Operator earns small fee ($0.02–$0.05 per rebalance) from user's reserve
- Or operator is Gentech-owned (internal agent), no fee — just operational cost

---

## Security Checklist

### 🔴 CRITICAL (Must Fix Before Deployment)

1. **Reentrancy Guard**
   All external calls (`safeTransferFrom`, LP Manager calls) must happen AFTER state changes.
   ✅ Already covered by `nonReentrant` + CEI in spec.

2. **OnlyOperator modifier**
   The spec says "Operator (Gentech's agent wallet)" — MUST be enforced in code, NOT just documented.
   ✅ Add `onlyOperator` to `rebalance()`.

3. **Gas overdraw protection**
   `estimateRebalanceGas()` must return conservative estimate. Add 30% buffer by default.
   ✅ Flagged for implementation.

### 🟡 HIGH (Must Fix Before Mainnet)

4. **Reserve snapshot guard**
   Between `estimateRebalanceGas()` check and actual `rebalance()` call, gas cost or position value could change.
   **Fix:** Store reserve snapshot in `rebalance()`:

   ```solidity
   function rebalance(...) external onlyOperator {
       uint256 reserveBefore = gasReserveBalance[user];
       // ... perform rebalance
       uint256 actualGas = tx.gasprice * gasUsed;  // or passed from off-chain estimator
       require(actualGas <= reserveBefore, "Reserve overdrawn");
   }
   ```

5. **Max gas % of position guard**
   Prevent griefing on low-value positions.
   ✅ Add `require(actualGas <= positionValue * maxGasPct / 10000)`.

6. **Operator griefing (forced rebalances)**
   Operator could rebalance continuously to drain gas reserves.
   **Mitigation:**
   - Rate limit per user (e.g., 1 rebalance per 6 hours per tokenId)
   - Or require minimum tick movement (e.g., Δ > 50 ticks) to trigger
   ✅ Recommend: `require(newLower != currentLower || newUpper != currentUpper, "No-op")` + 6h cooldown per tokenId.

### 🟢 MEDIUM (Recommended)

7. **Slippage protection**
   When swapping to rebalance, user should define acceptable slippage.
   ✅ Add `slippageBps` parameter to `rebalance()` (optional, defaults to 50 bps).

8. **Emergency pause**
   `Pausable` contract — owner can pause all deposits/rebalances in emergency.
   ✅ Add `Pausable` + `whenNotPaused` guards.

9. **Events for off-chain monitoring**
   Already in spec — `Rebalanced` event includes `gasCost`. Essential for YoYo's monitoring.
   ✅ Acceptable.

10. **Solana expansion**
    The spec says "Free tier auto-rebalance" on Solana due to negligible gas. This is **strategically sound** — it's a competitive differentiator. No on-chain reserve needed on Solana, just abstraction from subscription fee.
    ✅ APPROVED — separate Anchor program, simpler logic.

---

## Implementation Roadmap (DMOB-Recommended)

**Phase 1 (EVM Core — 5 days)**
- Deploy `GasReserveAutoRebalance.sol` on Base Sepolia
- Integrate with `AgentEscrow.sol` (onlyOperator registration)
- Test: deposit → rebalance → withdraw flow
- Test: rebalance guard triggers (max gas %, insufficient reserve, spam prevention)

**Phase 2 (Multi-Chain Abstraction — 3 days)**
- Write `UniswapV3Manager` adapter (Base/Ethereum)
- Write `LFJManager` adapter (Avalanche) — confirm LFJ pool interface
- Test each adapter with mock pool

**Phase 3 (Production Readiness — 4 days)**
- YoYo monitoring integration (Beam Cloud alerts on rebalance failures)
- Frontend: gas reserve display, rebalance history
- Documentation: operator rotation, timelock, emergency pause process

**Total:** ~12 days (2 weeks)

---

## YoYo Monitoring Requirements (from Spec)

The spec mentions YoYo monitors out-of-range status. For auto-rebalance:

**Needed events:**
```solidity
event Rebalanced(
    address indexed user,
    uint256 tokenId,
    uint256 gasCost,
    int24 oldLower,
    int24 oldUpper,
    int24 newLower,
    int24 newUpper
);
event ReserveToppedUp(address indexed user, uint256 amount);
event ReserveWithdrawn(address indexed user, uint256 gasAmount, uint256 lpAmount);
```

**YoYo should track:**
1. Rebalance success rate per tokenId
2. Average gas cost vs estimate deviation
3. Reserve depletion warnings (< $1 threshold)
4. Operator health (uptime, latency)

---

## Open Questions for Jordan

1. **Operator key custody:** Is the operator wallet solely controlled by Gentech (internal agent)? Or multi-sig? If multi-sig, rotation timelock should be longer (7–14 days).

2. **Gas buffer percentage:** The spec suggests `maxGasPct = 1-5%`. DMOB recommends 3% as starting point. Agreed?

3. **Rebalance cooldown:** Should there be a minimum time between rebalances for same position? (Prevents spam if tick oscillates). Suggestion: 6 hours.

4. **Slippage:** Should user set slippage tolerance at deposit (e.g., 50 bps) or per-rebalance? Per-rebalance gives more control but more UX friction.

5. **Partial rebalance:** If gas reserve is insufficient for full rebalance, should protocol do partial tick adjustment (cheaper) or skip? DMOB recommends skip + alert.

6. **Free tier on Base:** Spec says "Free tier → manual rebalance only, user pays own gas." This is clean. APPROVED.

---

## DMOB Approval

✅ **APPROVED — Ready for Implementation**

The gas abstraction pattern is proven in DeFi (e.g., Eignlayer restaking gas sponsorship patterns). The main implementation risks are operational (accurate gas estimation) not cryptographic.

**Conditions:**
1. `onlyOperator` enforced on `rebalance()` with timelock governor
2. Conservative `estimateRebalanceGas()` with 30% buffer
3. `maxGasPct` cap (suggest 300 = 3%) enforced per-rebalance
4. Rebalance requires tick movement (no-op prevention)
5. Reserve snapshot guard in `rebalance()` (snapshot before external calls)
6. All external calls happen after state changes (CEI) + `nonReentrant`

**Deliverables:**
- `contracts/GasReserveAutoRebalance.sol`
- `contracts/adapters/UniswapV3Manager.sol` (Base/Ethereum)
- `contracts/adapters/LFJManager.sol` (Avalanche)
- `test/GasReserveAutoRebalance.t.sol` (Foundry — rebalance scenarios, edge cases)

**Audit trigger:** Once Phase 1 code is complete, schedule joint DMOB + YoYo review before testnet deployment.

---

*Approved by DMOB, Labs | Spec: `Labs/Gas-Abstraction-Auto-Rebalance-Spec.md`*
