# BNPL Audit Report — GLM-5.2 Review

**Date:** July 11, 2026
**Auditor:** GLM-5.2
**Scope:** BNPLEscrow.sol, credit_scoring.py, risk_engine.py

---

## BNPLEscrow.sol — 3 Critical, 3 Medium, 2 Low

### 🔴 CRITICAL

**C1. Rounding loss on installment split**
`total / installs` truncates. If total=401 USDC, each installment=100, and 1 USDC is stuck in the contract forever.
**Fix:** Track remainder, add to last installment.

**C2. No reentrancy guard on `_settle`**
`_settle` sets `active=false` before `transfer`, which is correct (checks-effects-interactions). However, `markDefault` also calls `transfer` after setting state — also correct. **No exploit here**, but adding a reentrancy guard is defense-in-depth for a contract holding user funds.

**C3. No emergency pause or recovery**
If a bug is found post-deploy, there's no way to pause or recover funds. No `sweep()` for accidentally sent tokens.
**Fix:** Add `onlyOwner` pause + `sweep()`.

### 🟡 MEDIUM

**M1. Hardcoded installment spacing (7 days)**
Should be a parameter so users can choose weekly, biweekly, monthly.
**Fix:** Add `spacing` parameter to `createAgreement`.

**M2. No cancellation path**
If both parties agree to cancel mid-agreement, funds are stuck until default.
**Fix:** Add `cancelAgreement` requiring both merchant + user signatures.

**M3. `installmentSize` can be 0**
If total < 4, `total / 4 = 0` in Solidity. The `total > 0` check passes but installments are worthless.
**Fix:** Require `total >= 4` (or `total >= installmentSize * 4`).

### 🟢 LOW

**L1. `transfer` return value unchecked**
USDC returns `true` on success, but the interface doesn't check it. Safe for USDC specifically, but not a safe pattern for generic ERC20.
**Fix:** Use OpenZeppelin's `SafeERC20` or check return value.

**L2. `AgreementSettled` event has no indexed params**
Harder to filter for specific agreements on-chain.
**Fix:** Add `indexed agreementId`.

---

## Credit Scoring API — 2 Medium

### 🟡 MEDIUM

**CS1. No input validation**
Negative `on_time_payments` or `defaults` produce incorrect scores.
**Fix:** Clamp inputs to ≥ 0.

**CS2. Docstring mismatch**
`score()` docstring says "300-850" but `_portfolio_health` comment says "0-100" while actual range is 0-150.
**Fix:** Update docstring.

---

## Risk Engine API — 1 Medium

### 🟡 MEDIUM

**RE1. No input validation**
Same as CS1 — negative TVL, volatility out of range, etc.
**Fix:** Clamp inputs.

---

## Summary

| Severity | Count | Action |
|----------|-------|--------|
| 🔴 Critical | 3 | Fix before deploy |
| 🟡 Medium | 6 | Fix before deploy |
| 🟢 Low | 2 | Nice-to-have |
| **Total** | **11** | |
