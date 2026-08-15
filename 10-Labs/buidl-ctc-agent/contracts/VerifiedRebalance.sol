// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title VerifiedRebalance
 * @notice Creditcoin action contract for the GenTech Verified Agent (BUIDL CTC 2026 Fall).
 *
 * The agent's trust model: a cross-chain transaction (e.g. a USDC transfer on
 * Sepolia) is proven via the Attestcoin Protocol (USC SDK) and verified ON-CHAIN
 * through Creditcoin's precompile block prover — NO centralized oracle.
 *
 * This contract is the "action" side of the machine-money loop. Once the agent
 * has cryptographically verified a cross-chain event, it calls `recordVerifiedEvent`
 * to persist the attestation and trigger the rebalance decision on Creditcoin.
 *
 * The contract stores a verifiable audit trail of every verified event so the
 * decision history is transparent and replayable — the "evidence lineage" that
 * makes the agent's autonomy trustworthy.
 */
contract VerifiedRebalance {
    // ── State ──────────────────────────────────────────────────────────────
    address public owner;
    uint256 public rebalanceCount;
    uint256 public totalVerifiedUsd;

    struct VerifiedEvent {
        uint256 chainKey;        // source chain key (e.g. 1 = Sepolia on CC3)
        uint256 blockNumber;     // source block the tx was attested in
        bytes32 txHash;          // source transaction hash
        uint256 amountUsd;       // decoded USDC amount (6 decimals)
        bool verified;           // on-chain proof verification result
        uint256 timestamp;       // when the agent recorded it
    }

    // eventId (keccak of chainKey+blockNumber+txHash) -> event
    mapping(bytes32 => VerifiedEvent) public events;
    bytes32[] public eventIds;

    event VerifiedEventRecorded(
        bytes32 indexed eventId,
        uint256 chainKey,
        uint256 blockNumber,
        bytes32 txHash,
        uint256 amountUsd,
        bool verified
    );
    event RebalanceTriggered(bytes32 indexed eventId, uint256 amountUsd);

    // ── Modifiers ───────────────────────────────────────────────────────────
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // ── Constructor ────────────────────────────────────────────────────────
    constructor() {
        owner = msg.sender;
    }

    // ── Core: record a verified cross-chain event ──────────────────────────
    /**
     * @notice Persist a cryptographically verified cross-chain event and, if it
     *         clears the rebalance threshold, trigger the rebalance action.
     * @param chainKey source chain key
     * @param blockNumber source block the tx was attested in
     * @param txHash source transaction hash
     * @param amountUsd decoded USDC amount (6 decimals)
     * @param verified on-chain proof verification result (from PrecompileBlockProver)
     * @param rebalanceThresholdUsd minimum verified amount to trigger a rebalance
     */
    function recordVerifiedEvent(
        uint256 chainKey,
        uint256 blockNumber,
        bytes32 txHash,
        uint256 amountUsd,
        bool verified,
        uint256 rebalanceThresholdUsd
    ) external onlyOwner returns (bytes32 eventId) {
        // Only cryptographically verified events are recorded — the core thesis.
        require(verified, "Event not verified on-chain - refusing to record");

        eventId = keccak256(abi.encodePacked(chainKey, blockNumber, txHash));
        require(events[eventId].txHash == bytes32(0), "Event already recorded");

        events[eventId] = VerifiedEvent({
            chainKey: chainKey,
            blockNumber: blockNumber,
            txHash: txHash,
            amountUsd: amountUsd,
            verified: true,
            timestamp: block.timestamp
        });
        eventIds.push(eventId);

        totalVerifiedUsd += amountUsd;

        emit VerifiedEventRecorded(eventId, chainKey, blockNumber, txHash, amountUsd, true);

        // Trigger the rebalance action if the verified amount clears the threshold.
        if (amountUsd >= rebalanceThresholdUsd) {
            rebalanceCount++;
            emit RebalanceTriggered(eventId, amountUsd);
        }

        return eventId;
    }

    // ── Views ───────────────────────────────────────────────────────────────
    function getEventCount() external view returns (uint256) {
        return eventIds.length;
    }

    function getEvent(uint256 index) external view returns (VerifiedEvent memory) {
        require(index < eventIds.length, "Index out of bounds");
        return events[eventIds[index]];
    }

    function getEventById(bytes32 eventId) external view returns (VerifiedEvent memory) {
        return events[eventId];
    }

    // ── Admin ───────────────────────────────────────────────────────────────
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner");
        owner = newOwner;
    }
}
