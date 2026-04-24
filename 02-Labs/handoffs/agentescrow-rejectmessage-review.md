# Handoff: AgentEscrow — rejectMessage Function Review

**From:** YoYo (Strategies)
**To:** D-mob (Labs)
**Priority:** High — core escrow contract logic
**Date:** Apr 18, 2026

## Context

Jordan shared a `rejectMessage` function from the AgentEscrow smart contract. He wants this worked on in Labs.

## The Code

```solidity
function rejectMessage(uint256 messageId, bytes32 reason) external {
    Message storage msg_ = messages[messageId];
    _validateMessage(msg_, messageId);
    if (msg_.to != msg.sender) revert Unauthorized();
    if (msg_.status != Status.Pending) revert InvalidStatus(Status.Pending, msg_.status);

    msg_.status = Status.Rejected;
    _removeFromInbox(msg.sender, messageId);

    emit MessageRejected(messageId, msg.sender, reason);
}
```

## YoYo's Analysis — Risks & Gaps

### Critical
1. **No fund return** — If messages hold escrowed funds, rejection must refund the original sender. No transfer logic visible.
2. **State write order** — `msg_.status` updated before `_removeFromInbox`. Should follow Checks-Effects-Interactions strictly: all state changes before any external calls.

### Medium
3. **No reentrancy guard** — Add `nonReentrant` if any downstream call can re-enter.
4. **No sender notification** — Original depositor has no on-chain way to know rejection happened (events only). Consider a status they can pull or a callback.
5. **bytes32 reason** — Limits rejection reasons to 32 bytes. Consider `bytes` or error code enum.

### Low
6. **No timeout/expiry** — Messages could sit in `Pending` forever. Consider a deadline field on `Message`.

## What Labs Needs to Do

1. Review full contract — check if `acceptMessage` and `completeMessage` handle fund flows (reject should mirror those)
2. Add refund logic to `rejectMessage` if escrowed
3. Consider reentrancy protection across all state-changing functions
4. Add message expiry / timeout mechanism
5. Security pass — full audit of access control across all message lifecycle functions

## Reference

- AgentEscrow vision: 3-layer system (Vault contracts + AI agents + Arena)
- Hackathon target: Apr 26 — needs to ship layer 1+2
- Jordan's note in memory: "Gentech Strategies = pro league"
