# AgentEscrow Contract Audit — Cycle 1

**Date:** 2026-04-18
**Tester:** Hermes Agent
**Scope:** 3 hackathon repos — AgentEscrow, AgentPaymentFlow, AgentRegistry/TaskManager/AgentKeeper
**Chain:** N/A (local Foundry tests)
**Deadline:** Arc Hackathon Apr 25 (7 days)

---

## Repo 1: `arc-hackathon` — AgentEscrow.sol

### Summary
| Metric | Value |
|--------|-------|
| Compiler | Solc 0.8.24 (optimizer 200 runs) |
| Tests | 14 total — **12 PASS, 2 FAIL** |
| Deployment Gas | 1,638,460 |
| OZ Version | v5.0.0 (EIP712, ECDSA, IERC20) |
| Chain Config | Constructor params (validator, USDC address) ✅ |

### Unit Test Results

| Test Function | Description | Status |
|--------------|-------------|--------|
| testCreateEscrow | Create escrow, transfer USDC | ✅ |
| testValidateWork | Validator confirms work | ✅ |
| testValidateWithSignature | EIP712 off-chain validation | ✅ |
| testReleaseFunds | Release to seller after validation | ✅ |
| testRefundBuyer | Owner refunds buyer | ✅ |
| testCannotReleaseWithoutValidation | Can't release unvalidated | ✅ |
| testOnlyValidatorCanValidate | Random can't validate | ✅ |
| testCannotValidateTwice | Double-validation blocked | ❌ |
| testUpdateValidator | Owner changes validator | ✅ |
| testDepositAndWithdraw | Owner deposits/withdraws | ✅ |
| testTransferOwnership | Transfer ownership | ✅ |
| testSignatureReplayProtection | Signature reuse blocked | ❌ |
| testInvalidSignatureFails | Wrong signer rejected | ✅ |
| testMultipleEscrows | Multi-escrow tracking | ✅ |

### Gas Report (Key Functions)

| Function | Min | Avg | Max | # Calls |
|----------|-----|-----|-----|---------|
| createEscrow | 237,171 | 268,521 | 271,371 | 12 |
| validateWork | 25,873 | 53,976 | 71,971 | 5 |
| validateWithSignature | 27,677 | 66,037 | 100,974 | 4 |
| releaseFunds | 25,842 | 46,706 | 67,570 | 2 |
| refundBuyer | 67,527 | 67,527 | 67,527 | 1 |

### Issues Found

#### Issue 1: [MEDIUM] Check ordering masks EscrowAlreadyValidated error
- **File:** `src/AgentEscrow.sol:130-135`
- **Description:** `validateWork()` checks `escrow.status != EscrowStatus.Created` BEFORE checking `escrow.validated`. After first validation, status becomes `Validated`, so double-validation throws `EscrowAlreadyCompleted` instead of `EscrowAlreadyValidated`. Same bug in `validateWithSignature()`.
- **Repro:** Run `testCannotValidateTwice` or `testSignatureReplayProtection`
- **Fix:** Swap check order — check `escrow.validated` before `escrow.status`

#### Issue 2: [MEDIUM] No reentrancy guard on fund transfers
- **File:** `src/AgentEscrow.sol:203,222`
- **Description:** `releaseFunds()` and `refundBuyer()` transfer USDC without updating state first or using reentrancy guard. USDC is non-reentrant but pattern is unsafe for other ERC20s.
- **Fix:** Use checks-effects-interactions or add `nonReentrant` modifier

#### Issue 3: [LOW] No return value check on transferFrom
- **File:** `src/AgentEscrow.sol:103`
- **Description:** `createEscrow` calls `usdc.transferFrom()` but doesn't check return value. Some tokens return false instead of reverting.
- **Fix:** Wrap in `require(usdc.transferFrom(...))` or use OZ SafeERC20

#### Issue 4: [LOW] Missing zero-address validation on seller
- **File:** `src/AgentEscrow.sol:99`
- **Description:** No check that `_seller != address(0)` in `createEscrow`
- **Fix:** Add `require(_seller != address(0))`

#### Issue 5: [LOW] setValidator uses wrong error for zero-address check
- **File:** `src/AgentEscrow.sol:285`
- **Description:** `setValidator` reverts with `InvalidSignature` for zero address — misleading error
- **Fix:** Add a dedicated `ZeroAddress()` error

### Verdict
- [x] All unit tests pass — **NO** (2 failures from check-ordering bug)
- [ ] All fuzz tests pass — not run
- [x] Deployment successful
- [x] Gas within limits
- [ ] No critical/major issues — **1 medium**

**Ready for next phase:** NO — fix check ordering, add reentrancy guard

---

## Repo 2: `agent-economy-kite` — AgentPaymentFlow.sol

### Summary
| Metric | Value |
|--------|-------|
| Compiler | Solc 0.8.24 |
| Tests | 6 total — **6 PASS, 0 FAIL** |
| Deployment Gas | 1,421,139 |
| Dependencies | forge-std only (no OZ) |
| Chain Config | None (generic ETH payments) |

### Unit Test Results

| Test Function | Description | Status |
|--------------|-------------|--------|
| test_registerAgent | Register agent with spending limit | ✅ |
| test_registerAgent_revertIfAlreadyRegistered | Prevent double registration | ✅ |
| test_approveService | Owner approves service | ✅ |
| test_executePayment | Agent pays approved service | ✅ |
| test_executePayment_revertIfOverLimit | Daily limit enforcement | ✅ |
| test_updateSpendingLimit | Agent updates own limit | ✅ |

### Gas Report (Key Functions)

| Function | Min | Avg | Max | # Calls |
|----------|-----|-----|-----|---------|
| registerAgent | 24,978 | 85,352 | 97,427 | 6 |
| executePayment | 34,748 | 63,811 | 92,874 | 2 |
| approveService | 46,336 | 46,336 | 46,336 | 3 |
| updateSpendingLimit | 30,994 | 30,994 | 30,994 | 1 |

### Issues Found

#### Issue 1: [HIGH] No reentrancy protection on payment
- **File:** `contracts/AgentPaymentFlow.sol:112`
- **Description:** `executePayment` uses `_service.call{value: _amount}("")` — if the service is a contract, it can re-enter. Spending limit is tracked but the call happens during the function.
- **Fix:** Add reentrancy guard or use checks-effects-interactions

#### Issue 2: [MEDIUM] No ERC20 support — ETH only
- **File:** Entire contract
- **Description:** All payments are native ETH. No USDC/ERC20 support. The AAE architecture requires USDC-based escrow.
- **Fix:** Add ERC20 payment path alongside ETH

#### Issue 3: [MEDIUM] No escrow mechanism
- **Description:** Payments go directly to services — no escrow hold, no validation step, no dispute path. This is a payment router, not an escrow contract.
- **Fix:** Integrate with AgentEscrow pattern from arc-hackathon

#### Issue 4: [LOW] Uses require strings instead of custom errors
- **File:** Throughout
- **Description:** All error handling uses `require(condition, "string")` — wastes gas vs custom errors
- **Fix:** Migrate to custom errors (Solidity 0.8.4+)

#### Issue 5: [LOW] No service deactivation
- **Description:** Services can be approved but never un-approved
- **Fix:** Add `revokeService(address)` function

### Verdict
- [x] All unit tests pass
- [ ] All fuzz tests pass — not run
- [x] Deployment successful
- [x] Gas within limits
- [ ] No critical/major issues — **1 high, 2 medium**

**Ready for next phase:** NO — needs escrow + reentrancy guard + ERC20 support

---

## Repo 3: `ethglobal-open-agents` — AgentRegistry, TaskManager, AgentKeeper

### Summary
| Metric | Value |
|--------|-------|
| Compiler | Solc 0.8.24 (1 warning) |
| Tests | 7 total — **7 PASS, 0 FAIL** |
| AgentKeeper Tests | **0** (no test file) |
| Dependencies | forge-std only |
| Chain Config | Constructor params (agentRegistry address) ✅ |

### Unit Test Results

**AgentRegistry (4 tests)**
| Test Function | Description | Status |
|--------------|-------------|--------|
| test_registerAgent | Register with skill hash + metadata | ✅ |
| test_updateSkills | Owner updates skills | ✅ |
| test_updateSkills_revertNotOwner | Non-owner blocked | ✅ |
| test_deactivateAgent | Soft delete agent | ✅ |

**TaskManager (3 tests)**
| Test Function | Description | Status |
|--------------|-------------|--------|
| test_postTask | Post task with ETH payment | ✅ |
| test_fullTaskLifecycle | Post → claim → complete → release | ✅ |
| test_cancelTask_refund | Cancel and get refund | ✅ |

### Gas Report (Key Functions)

| Contract | Function | Avg Gas |
|----------|----------|---------|
| AgentRegistry | registerAgent | 185,344 |
| AgentRegistry | updateSkills | 28,582 |
| AgentRegistry | deactivateAgent | 24,985 |
| TaskManager | postTask | 153,201 |
| TaskManager | claimTask | 45,373 |
| TaskManager | completeTask | 73,141 |
| TaskManager | releasePayment | 37,611 |
| TaskManager | cancelTask | 56,153 |

### Issues Found

#### Issue 1: [HIGH] claimTask doesn't verify agent ownership
- **File:** `src/TaskManager.sol:45-51`
- **Description:** `claimTask` has `// TODO: Verify msg.sender is owner of the assigned agent` — anyone can claim any task, bypassing the agent assignment.
- **Fix:** Check `agentRegistry.getAgent(task.agentId).owner == msg.sender`

#### Issue 2: [MEDIUM] AgentKeeper.executeJob is a stub
- **File:** `src/AgentKeeper.sol:53-68`
- **Description:** `executeJob` has two TODO comments — no condition checking, no execution logic. Just increments a counter. Not functional.
- **Fix:** Implement condition evaluation and execution dispatch

#### Issue 3: [MEDIUM] No AgentKeeper tests
- **Description:** Zero tests for AgentKeeper.sol. Cannot verify any functionality.
- **Fix:** Write at least basic unit tests

#### Issue 4: [MEDIUM] No reentrancy guards on ETH transfers
- **File:** `src/TaskManager.sol:80,92`
- **Description:** `cancelTask` and `releasePayment` use `.call{value}` without reentrancy protection
- **Fix:** Add reentrancy guard or follow CEI pattern

#### Issue 5: [LOW] disputeTask doesn't use `reason` parameter
- **File:** `src/TaskManager.sol:66`
- **Description:** Unused parameter triggers compiler warning. No dispute resolution logic.
- **Fix:** Either implement dispute resolution or remove the parameter

#### Issue 6: [LOW] No dispute resolution mechanism
- **Description:** Tasks can be disputed but there's no resolution — no arbitration, no timeout, no auto-release. Disputed funds are stuck forever.
- **Fix:** Add dispute resolution with timeout + arbitration

### Verdict
- [x] All unit tests pass (for tested contracts)
- [ ] All fuzz tests pass — not run
- [x] Deployment successful
- [x] Gas within limits
- [ ] No critical/major issues — **1 high, 3 medium**

**Ready for next phase:** NO — claimTask bug, AgentKeeper untested/stub

---

## Cross-Repo Comparison

| Feature | arc-hackathon | agent-economy-kite | ethglobal-open-agents |
|---------|---------------|--------------------|-----------------------|
| Escrow | ✅ Full | ❌ Direct pay | ✅ Task-based |
| AI Validation | ✅ EIP712 | ❌ | ❌ |
| ERC20 (USDC) | ✅ | ❌ ETH only | ❌ ETH only |
| Reentrancy Guard | ❌ | ❌ | ❌ |
| Custom Errors | ✅ | ❌ require strings | ✅ + require mix |
| Test Coverage | 14 tests (2 fail) | 6 tests | 7 tests |
| Interface Contracts | ❌ | ❌ | ✅ |
| Chain Config | Constructor | None | Constructor |

---

## Priority Fixes for Arc Deadline (Apr 25)

1. **Fix arc-hackathon check ordering** (30 min) — swaps 2 failing tests to passing
2. **Fix claimTask ownership check** in ethglobal-open-agents (15 min)
3. **Add reentrancy guard** to arc-hackathon release/refund (1 hour)
4. **Add ERC20 support** to agent-economy-kite (2-3 hours)
5. **Stub AgentKeeper tests** at minimum (1 hour)
