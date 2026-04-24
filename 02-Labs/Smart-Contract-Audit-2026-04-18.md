# Smart Contract Audit — 2026-04-18

**Auditor**: Dmob  
**Repos**: ethglobal-open-agents, agent-escrow, AAE  
**Tool**: Forge 1.5.1-stable

---

## Summary

| Repo | Tests | Pass | Fail | Verdict |
|------|-------|------|------|---------|
| ethglobal-open-agents | 44 | 44 | 0 | ✅ Hackathon-ready with minor fixes |
| agent-escrow | 40 | 40 | 0 | ✅ Solid, hackathon-grade |
| AAE | 24 | 24 | 0 | ⚠️ Needs access control fix |

---

## ETHGlobal Open Agents

### AgentRegistry.sol — ✅ Clean
- Custom errors throughout (gas-efficient)
- Proper checks-effects-interactions in `updateSkills`
- `incrementReputation` is open — noted as "simplified for hackathon" (line 122). **Acceptable for hackathon, must gate before mainnet.**
- `tokenURI` override properly reverts for non-existent tokens

### TaskManager.sol — ⚠️ Minor Issues
1. **`require` with strings** (lines 156, 161, 179, 196): Replace with custom errors for gas savings
   - `require(feeSuccess, "Fee transfer failed")` → `error FeeTransferFailed()`
2. **Push pattern for payments** in `resolveTask` (line 155-161): Two external calls to different recipients — reentrancy-safe because no state changes between them. **Acceptable but pull-over-push is safer for production.**
3. **Dispute is poster-only**: Agent has no recourse. Fine for hackathon scope.

### AgentKeeper.sol — ⚠️ Minor Issues  
1. **Arbitrary external call** in `execute()` (line 158): `k.target.call(k.executeData)` — intentional by design (keeper pattern). Works with KeeperHub's `check-and-execute`.
2. **`require` with string** (line 159): Same gas issue as TaskManager.
3. **Missing cooldown in `updateKeeper`**: Can't update `maxExecutions` or `conditionType`. **Consider adding those fields to `updateKeeper`.**

---

## Agent Escrow (agent-escrow)

### AgentNFT.sol — ✅ Excellent
- Proper state machine with `_isValidTransition` matrix
- `ERC721Enumerable` properly overrides `_update` and `_increaseBalance`
- `mintAgent` gated to `onlyOwner` 
- `markSold` correctly transfers NFT + resets performance
- Custom errors throughout

### AgentVault.sol — ✅ Excellent  
- `SafeERC20` for all token transfers
- `nonReentrant` on all value-moving functions
- Gas reserve enforcement in `withdrawGas` and `executeTrade`
- `minAmountOut` check protects against slippage
- `onlyOwner` / `onlyAgent` / `onlyAuthorized` properly scoped

**One note**: `withdrawGas` uses `require` with string (line 207). Minor gas hit.

---

## AAE (Avalanche Agent Economy)

### AgentRegistry.sol — 🔴 Critical Issue
1. **`setJobEscrow()` (line 186)**: **NO ACCESS CONTROL.** Anyone can call this and point `jobEscrow` to a malicious contract that calls `updateReputation` to inflate/deflate scores.
   - **Fix**: Add `onlyOwner` modifier or timelock

### JobEscrow.sol — ⚠️ Issues
1. **Push pattern** in `approveJob` (lines 171, 175): Sends ETH to agent and fee recipient directly. Comment says "For MVP, we send directly. In production, use pull pattern." **Correct assessment.**
2. **`require` with strings** (lines 172, 176, 206): Minor gas issue.
3. **Dispute has no resolution**: `disputeJob` just sets state to `Disputed` with no payout mechanism. **Needs arbitration or timelock-based auto-resolution.**
4. **`refundExpired` calls `updateReputation`** with `false` (line 203): Punishes agent for creator's deadline. Consider whether this is fair — agent might never have seen the job.

### AgentToken.sol — ✅ Clean
- Fixed max supply (1M tokens)
- Initial mint to creator (100K)
- `onlyOwner` on mint — correct
- `remainingSupply()` view — nice touch

### AgentTokenFactory.sol — Not reviewed (need to check)

---

## Priority Fixes

### Must Fix (Before Any Deployment)
- [ ] **AAE AgentRegistry**: Gate `setJobEscrow()` with `onlyOwner` or governance

### Should Fix (Pre-Hackathon Polish)
- [ ] **TaskManager**: Replace `require` strings with custom errors
- [ ] **AgentKeeper**: Replace `require` string with custom error
- [ ] **AgentVault**: Replace `require` string with custom error
- [ ] **JobEscrow**: Replace `require` strings with custom errors

### Consider (Post-Hackathon)
- [ ] ETHGlobal `incrementReputation` access control
- [ ] TaskManager pull-over-push payment pattern
- [ ] JobEscrow dispute resolution mechanism

---

## Tags
#audit #security #smart-contract #ethglobal #AAE #agent-escrow
