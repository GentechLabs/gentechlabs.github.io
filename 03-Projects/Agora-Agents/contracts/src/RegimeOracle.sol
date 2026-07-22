// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RegimeOracle
 * @notice On-chain regime feed for the Adaptive Portfolio Manager
 * @dev Authorized agents submit regime classifications; portfolio reads them
 *
 * The oracle doesn't compute regimes — it receives them from the Python agent
 * and makes them available on-chain for trustless portfolio decisions.
 */
contract RegimeOracle {
    // ── State ──────────────────────────────────────────────────────────────

    enum Regime { BULL_TRENDING, BEAR_TRENDING, RANGE_BOUND, HIGH_VOLATILITY, ACCUMULATION, PRICE_DISCOVERY }

    struct RegimeUpdate {
        uint256 timestamp;
        Regime regime;
        uint256 confidence;      // 0-100
        uint256 priceUsd;        // Reference price at time of classification
        bytes32 dataHash;        // Hash of off-chain data used for classification
    }

    address public owner;
    mapping(address => bool) public authorizedOracles;

    RegimeUpdate public latestUpdate;
    RegimeUpdate[] public history;

    uint256 public maxStaleness = 1 hours; // Regime data expires after 1 hour

    // Events
    event RegimeUpdated(
        uint256 timestamp,
        Regime regime,
        uint256 confidence,
        uint256 priceUsd
    );
    event OracleAuthorized(address oracle);
    event OracleRevoked(address oracle);

    // Errors
    error NotOwner();
    error NotAuthorized();
    error DataStale();
    error InvalidConfidence();

    // ── Modifiers ──────────────────────────────────────────────────────────

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyOracle() {
        if (!authorizedOracles[msg.sender]) revert NotAuthorized();
        _;
    }

    // ── Constructor ────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
    }

    // ── Core Functions ─────────────────────────────────────────────────────

    /**
     * @notice Submit a regime classification from off-chain agent
     * @param regime The classified market regime
     * @param confidence Confidence score (0-100)
     * @param priceUsd Reference price at classification time
     * @param dataHash Hash of the off-chain data used
     */
    function submitRegime(
        Regime regime,
        uint256 confidence,
        uint256 priceUsd,
        bytes32 dataHash
    ) external onlyOracle {
        if (confidence > 100) revert InvalidConfidence();

        latestUpdate = RegimeUpdate({
            timestamp: block.timestamp,
            regime: regime,
            confidence: confidence,
            priceUsd: priceUsd,
            dataHash: dataHash
        });

        history.push(latestUpdate);

        emit RegimeUpdated(block.timestamp, regime, confidence, priceUsd);
    }

    /**
     * @notice Get current regime (reverts if stale)
     */
    function getCurrentRegime() external view returns (Regime, uint256, uint256) {
        if (block.timestamp > latestUpdate.timestamp + maxStaleness) {
            revert DataStale();
        }
        return (latestUpdate.regime, latestUpdate.confidence, latestUpdate.timestamp);
    }

    /**
     * @notice Check if regime data is fresh
     */
    function isFresh() external view returns (bool) {
        return block.timestamp <= latestUpdate.timestamp + maxStaleness;
    }

    // ── Admin ──────────────────────────────────────────────────────────────

    function authorizeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = true;
        emit OracleAuthorized(oracle);
    }

    function revokeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = false;
        emit OracleRevoked(oracle);
    }

    function setMaxStaleness(uint256 seconds_) external onlyOwner {
        maxStaleness = seconds_;
    }
}
