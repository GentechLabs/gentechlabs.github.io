# IResolver Interface Spec — Two-Tier Dispute Resolution

**Author:** YoYo (Strategies)
**Date:** Apr 21, 2026
**Status:** 🔵 PROPOSED — Awaiting DMOB review
**Target:** `arc-hackathon` / `agent-escrow-solana`

---

## Problem

Current `DisputeResolver.sol` is a monolith — tightly coupled to `AgentEscrow`, manages its own lifecycle, handles fund transfers directly. This makes it impossible to:
- Swap in GenLayer (or any AI oracle) as an alternative resolver
- Use the same escrow contract with different resolution strategies
- Escalate from human arbitration to AI adjudication

## Solution

Extract a minimal `IResolver` interface. Both our custom DisputeResolver and a future GenLayer adapter implement it. The escrow contract takes a resolver address at creation — swappable, composable, no lock-in.

---

## Interface Design

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IResolver
 * @notice Standard interface for dispute resolution in agent escrow
 * @dev Implementations: HumanDisputeResolver, GenLayerOracleResolver, MultisigResolver
 */
interface IResolver {

    // ============ Types ============

    enum Verdict {
        Pending,        // Not yet decided
        BuyerWins,      // Full refund
        SellerWins,     // Full payout
        Split,          // 50/50 default (implementations can add custom ratios)
        Escalated       // Routed to higher-tier resolver
    }

    struct DisputeContext {
        uint256 escrowId;
        address buyer;
        address seller;
        address token;
        uint256 amount;
        string serviceDescription;  // What was the SLA?
        bytes metadata;              // Resolver-specific data (IPFS hash, GenLayer config, etc.)
    }

    // ============ Core ============

    /**
     * @notice File a dispute — resolver takes ownership of resolution
     * @param ctx The dispute context (who, what, how much)
     * @return disputeId Unique ID within this resolver
     */
    function fileDispute(DisputeContext calldata ctx)
        external
        returns (uint256 disputeId);

    /**
     * @notice Submit evidence for an open dispute
     * @param disputeId Resolver-internal dispute ID
     * @param evidence Encoded evidence (IPFS CID, URL, raw bytes)
     */
    function submitEvidence(uint256 disputeId, bytes calldata evidence)
        external;

    /**
     * @notice Get the current verdict for a dispute
     * @param disputeId Resolver-internal dispute ID
     * @return verdict Current verdict state
     * @return reasoning Human/AI-readable explanation
     * @return buyerPayout Amount to return to buyer
     * @return sellerPayout Amount to release to seller
     */
    function getVerdict(uint256 disputeId)
        external
        view
        returns (
            Verdict verdict,
            string memory reasoning,
            uint256 buyerPayout,
            uint256 sellerPayout
        );

    /**
     * @notice Finalize and execute — called by escrow after verdict is non-Pending
     * @param disputeId Resolver-internal dispute ID
     * @return buyerPayout Confirmed amount to buyer
     * @return sellerPayout Confirmed amount to seller
     */
    function executeVerdict(uint256 disputeId)
        external
        returns (uint256 buyerPayout, uint256 sellerPayout);

    // ============ Lifecycle ============

    /**
     * @notice Check if a dispute is ready for execution
     * @param disputeId Resolver-internal dispute ID
     * @return ready True if verdict is final and can be executed
     */
    function isReady(uint256 disputeId) external view returns (bool ready);

    /**
     * @notice Cancel a dispute (initiator or admin only, before verdict)
     * @param disputeId Resolver-internal dispute ID
     */
    function cancelDispute(uint256 disputeId) external;
}
```

---

## How It Works — Two Tiers

### Tier 1: `HumanDisputeResolver` (our custom one)

```
Escrow → fileDispute() → Open state, evidence window starts
Parties → submitEvidence() → Store on-chain / IPFS ref
Arbitrator → resolveDispute() → Sets verdict + reasoning
Escrow → executeVerdict() → Transfers funds per verdict
```

**Refactors from current DisputeResolver.sol:**
- Remove `import {AgentEscrow}` — escrow passes context in, resolver doesn't reach out
- `fileDispute()` replaces `openDispute()` — takes `DisputeContext` instead of calling `escrowContract.getEscrow()`
- `executeVerdict()` returns payout amounts — escrow handles the actual transfers
- Keep arbitrator management, evidence window, EIP-712 signatures (battle-tested)

### Tier 2: `GenLayerOracleResolver` (optional upgrade)

```
Escrow → fileDispute() → Posts to GenLayer Intelligent Contract
GenLayer → AI reads evidence URL, evaluates SLA
GenLayer → Optimistic Democracy consensus → verdict
Escrow → executeVerdict() → Reads GenLayer result, transfers funds
```

**Key differences:**
- `fileDispute()` calls GenLayer's Intelligent Contract (escrow-with-ai-arbiter template)
- `getVerdict()` is async — may return `Pending` until GenLayer consensus completes
- `isReady()` checks GenLayer finality (Optimistic Democracy challenge period)
- `metadata` field carries the resolution URL / evidence endpoint for AI to read
- Cost: GenLayer gas + oracle fee (can be priced in $TECH with REP discount)

---

## Escrow Integration

**Minimal change to AgentEscrow.sol:**

```solidity
// In escrow creation:
IResolver resolver = IResolver(_resolverAddress);

// When dispute opened:
uint256 disputeId = resolver.fileDispute(IResolver.DisputeContext({
    escrowId: escrowId,
    buyer: escrow.buyer,
    seller: escrow.seller,
    token: escrow.token,
    amount: escrow.amount,
    serviceDescription: escrow.description,
    metadata: "" // or IPFS hash, GenLayer config, etc.
}));

// When executing verdict:
if (resolver.isReady(disputeId)) {
    (uint256 buyerPayout, uint256 sellerPayout) = resolver.executeVerdict(disputeId);
    // Transfer funds...
}
```

**Escrow doesn't care which resolver it uses.** That's the whole point.

---

## Escalation Model (Advanced)

For the "both A and C" pitch:

```solidity
contract EscalatingResolver is IResolver {
    IResolver public primary;   // HumanDisputeResolver (Tier 1)
    IResolver public secondary; // GenLayerOracleResolver (Tier 2)

    function escalate(uint256 disputeId) external {
        // Check primary verdict
        (Verdict v, , , ) = primary.getVerdict(disputeId);
        require(v == Verdict.Split, "Can only escalate split decisions");

        // Route to GenLayer for re-adjudication
        // GenLayer gets the evidence + primary's reasoning as context
    }
}
```

**Business logic:**
- Default: human resolver handles everything (cheap, fast, deterministic)
- Either party can escalate a Split verdict to GenLayer (costs more, but fairer)
- GenLayer override is final — no re-escalation
- Escalation fee: paid in $TECH, REP holders get discount

---

## Revenue Implications

| Tier | Fee Source | Pricing |
|------|-----------|---------|
| Human resolver | Flat dispute fee (USDC) | $5-20 per dispute |
| GenLayer oracle | Oracle fee + gas | $1-5 in $TECH (20-30% discount for REP) |
| Escalation | Premium adjudication | $TECH only, higher tier |

Maps directly to the dual-pricing model: USDC for base layer, $TECH for AI-powered upgrades.

---

## Next Steps (DMOB)

1. **Refactor `DisputeResolver.sol` → `HumanDisputeResolver.sol`** implementing `IResolver`
   - Decouple from `AgentEscrow` import — take `DisputeContext` instead
   - Move fund transfers out of resolver — return amounts, escrow executes
   - Keep arbitrator management, evidence, EIP-712

2. **Update `AgentEscrow.sol`** to accept `IResolver` at construction
   - Store resolver address
   - Route disputes through `resolver.fileDispute()`
   - Execute through `resolver.executeVerdict()`

3. **Scaffold `GenLayerOracleResolver.sol`** (can be stub for hackathon)
   - Implements `IResolver`
   - `fileDispute()` → posts to GenLayer Intelligent Contract
   - `getVerdict()` → reads from GenLayer consensus
   - Ship as "planned integration" in pitch, working stub for demo

4. **Write tests** for interface compliance
   - Both resolvers pass same test suite
   - Proves swap-ability to judges

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Interface too rigid for GenLayer quirks | 30% | Medium | `metadata` field is opaque bytes — GenLayer can encode whatever it needs |
| Escrow refactor breaks existing tests | 40% | Low | 32/33 passing now, interface is additive |
| GenLayer oracle latency kills UX | 50% | Medium | Tier 1 is default — GenLayer is opt-in escalation only |
| Judges don't understand tiered model | 20% | Low | "Works out of the box, scales with AI" — pitch-ready |

**Bottom line:** Low-risk refactor, high-reward architecture. The interface gives us optionality without complexity.

---

*Hand off to DMOB for implementation. YoYo handles revenue modeling and pitch framing.*
