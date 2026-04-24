# 🐛 Findings Tracker — Live Issue Log

## Status Legend
- 🔴 OPEN — Must fix before deploy
- 🟡 IN PROGRESS — Fix being worked
- 🟢 FIXED — Resolved, verified by tests
- ⚪ ACKNOWLEDGED — Accepted risk, documented

---

## Critical

| ID | Contract | Issue | Status | Assignee |
|----|----------|-------|--------|----------|
| C-1 | BurnSplitter | `onlyRouter()` modifier is a no-op — anyone can call `split()` | 🟢 FIXED | DMOB |

## High

| ID | Contract | Issue | Status | Assignee |
|----|----------|-------|--------|----------|
| H-1 | TechPaymentRouter | No `nonReentrant` on `payWithTech()` | 🟢 FIXED | DMOB |
| H-2 | DiscountCalculator | `updateSMA()` has no access control | 🟢 FIXED | DMOB |
| H-3 | DiscountCalculator | Oracle `latestRoundData()` missing staleness + round checks | 🟢 FIXED | DMOB |
| H-4 | AgentEscrow | `ecrecover` malleable — should use ECDSA.recover() | 🟢 FIXED | DMOB |

## Medium

| ID | Contract | Issue | Status | Assignee |
|----|----------|-------|--------|----------|
| M-1 | TechPaymentRouter | `_getOraclePrice()` has no staleness check | 🟢 FIXED | DMOB |
| M-2 | TechPaymentRouter | `setDiscountCalculator()` / `setBurnSplitter()` lack `onlyOwner` | 🟢 FIXED | DMOB |
| M-3 | DiscountCalculator | Precision loss in linear interpolation (1 bps max) | ⚪ ACKNOWLEDGED | — |
| M-4 | BurnSplitter | `setTreasury()` has no access control | 🟢 FIXED | DMOB |
| M-5 | AgentEscrow | No signature expiry window | 🔴 OPEN | DMOB |

## Low / Informational

| ID | Contract | Issue | Status | Assignee |
|----|----------|-------|--------|----------|
| L-1 | TechPaymentRouter | `previewPayment` cosmetic note | ⚪ ACKNOWLEDGED | — |
| L-2 | DiscountCalculator | Loyalty tiers hardcoded — not updatable | ⚪ ACKNOWLEDGED | — |
| L-3 | BurnSplitter | No reentrancy guard on `split()` | ⚪ ACKNOWLEDGED | — |
| L-4 | AgentEscrow | Refund possible during `Validated` state window | ⚪ ACKNOWLEDGED | — |
| L-5 | AgentEscrow | Minor event granularity | ⚪ ACKNOWLEDGED | — |

---

## Summary Counts
- 🔴 OPEN: 1 (M-5 — signature expiry)
- 🟢 FIXED: 9
- ⚪ ACKNOWLEDGED: 5
- **Deployment Ready:** ⚠️ ALMOST — 1 medium issue remaining (M-5)

---

## Fixes Applied — Apr 21, 2026 (DMOB)

### C-1: BurnSplitter `onlyRouter` — FIXED
- Added `address public router` state variable
- Constructor now takes `_router` parameter
- `onlyRouter` modifier enforces `msg.sender == router`
- `setTreasury()` now requires `onlyRouter`
- Added `setRouter()` for router updates
- Tests: 19/19 passing ✅

### H-1: TechPaymentRouter reentrancy — FIXED
- Added `ReentrancyGuard` inheritance
- `payWithTech()` has `nonReentrant` modifier

### H-2: DiscountCalculator `updateSMA` — FIXED
- Added `Ownable` inheritance
- `updateSMA()` now has `onlyOwner`

### H-3: Oracle staleness checks — FIXED
- `_getOraclePrice()` now checks `answeredInRound >= roundId`
- Requires `block.timestamp - updatedAt < 1 hours`
- Checks `answer > 0`

### H-4: AgentEscrow `ecrecover` — FIXED
- Imported `ECDSA` from OpenZeppelin
- Changed `validateAndRelease()` from `(uint8 v, bytes32 r, bytes32 s)` to `bytes calldata _signature`
- Uses `ECDSA.recover(digest, _signature)` — handles malleability
- Added `usedSignatures` mapping to prevent replay

### M-1/M-2: TechPaymentRouter admin — FIXED
- Added `Ownable` inheritance
- Constructor passes `msg.sender` to `Ownable`
- `setDiscountCalculator()` and `setBurnSplitter()` now `onlyOwner`

### M-4: BurnSplitter `setTreasury` — FIXED
- Now requires `onlyRouter` modifier

---

## Remaining (Non-Blocking)

| ID | Issue | Priority | Notes |
|----|-------|----------|-------|
| M-5 | AgentEscrow signature expiry | Medium | Add `SIGNATURE_VALIDITY` constant + timestamp check — next session |

---

*Updated by DMOB — Apr 21, 2026*
*All CRITICAL/HIGH findings resolved. 19/19 tests passing.*
