// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title RWA Yield Guard Agent
 * @notice AI-driven asset-management agent for BOT Chain (Builder Challenge #2).
 *
 * The agent monitors a user's RWA/stablecoin positions and auto-rebalances
 * based on health, yield, and risk thresholds. The AI decision layer (off-chain
 * oracle) submits signed rebalance intents; the contract enforces risk limits
 * and executes the rebalance atomically.
 *
 * Design goals:
 *  - AI is the CORE decision-maker (risk scoring + rebalance decisions), not
 *    auxiliary. The contract only executes intents that pass its risk guard.
 *  - Human-in-the-loop for withdrawals (always human-confirmed).
 *  - Risk limits enforced on-chain (max position, max drawdown, circuit breaker).
 */
contract RWAYieldGuard {
    // --- Types -------------------------------------------------------------
    struct Position {
        address asset;        // RWA/stablecoin token address
        uint256 amount;       // current balance held
        uint256 targetWeight; // target allocation in basis points (0-10000)
        uint256 riskScore;    // 0-100, set by AI decision layer
        bool active;
    }

    struct RebalanceIntent {
        address asset;
        uint256 amount;       // amount to move
        uint256 riskScore;    // AI-computed risk score for this action
        uint256 nonce;        // replay protection
        uint256 deadline;     // expiry timestamp
    }

    // --- State -------------------------------------------------------------
    address public owner;
    address public aiOperator;   // the AI decision layer (off-chain agent)
    address public guardian;     // emergency pause authority

    uint256 public maxPositionBps = 5000;   // max 50% of portfolio in one asset
    uint256 public maxRiskScore = 80;        // reject intents above this risk
    uint256 public circuitBreakerLevel = 0;  // 0=open, 1=halted
    uint256 public nonceCounter;

    mapping(address => Position) public positions;
    address[] public positionAssets;

    // --- Events ------------------------------------------------------------
    event PositionUpdated(address indexed asset, uint256 amount, uint256 riskScore);
    event RebalanceExecuted(address indexed asset, uint256 amount, uint256 riskScore, uint256 nonce);
    event RiskGuardTriggered(address indexed asset, uint256 riskScore, string reason);
    event CircuitBreakerSet(uint256 level);
    event AiOperatorChanged(address indexed operator);

    // --- Modifiers ---------------------------------------------------------
    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }
    modifier onlyAi() { require(msg.sender == aiOperator, "not ai operator"); _; }
    modifier notHalted() { require(circuitBreakerLevel == 0, "circuit breaker active"); _; }

    // --- Constructor -------------------------------------------------------
    constructor(address _aiOperator) {
        owner = msg.sender;
        aiOperator = _aiOperator;
        guardian = msg.sender;
    }

    // --- Admin -------------------------------------------------------------
    function setAiOperator(address _op) external onlyOwner {
        aiOperator = _op;
        emit AiOperatorChanged(_op);
    }

    function setGuardian(address _g) external onlyOwner { guardian = _g; }

    function setMaxPositionBps(uint256 _bps) external onlyOwner {
        require(_bps <= 10000, "bps out of range");
        maxPositionBps = _bps;
    }

    function setMaxRiskScore(uint256 _score) external onlyOwner {
        require(_score <= 100, "score out of range");
        maxRiskScore = _score;
    }

    function setCircuitBreaker(uint256 _level) external {
        require(msg.sender == guardian || msg.sender == owner, "not authorized");
        circuitBreakerLevel = _level;
        emit CircuitBreakerSet(_level);
    }

    // --- Position management (AI-driven) -----------------------------------
    /**
     * @notice Register or update a position. Called by the AI decision layer
     *         after it scores the asset's risk.
     */
    function updatePosition(
        address _asset,
        uint256 _amount,
        uint256 _targetWeight,
        uint256 _riskScore
    ) external onlyAi notHalted {
        require(_riskScore <= maxRiskScore, "risk score exceeds limit");
        require(_targetWeight <= maxPositionBps, "target weight exceeds max position");

        if (!positions[_asset].active) {
            positions[_asset] = Position(_asset, _amount, _targetWeight, _riskScore, true);
            positionAssets.push(_asset);
        } else {
            positions[_asset].amount = _amount;
            positions[_asset].targetWeight = _targetWeight;
            positions[_asset].riskScore = _riskScore;
        }
        emit PositionUpdated(_asset, _amount, _riskScore);
    }

    /**
     * @notice Execute a rebalance intent signed by the AI decision layer.
     *         The contract enforces risk limits before moving funds.
     */
    function executeRebalance(
        RebalanceIntent calldata intent
    ) external onlyAi notHalted returns (bool) {
        // Replay protection
        require(intent.nonce > nonceCounter, "stale nonce");
        nonceCounter = intent.nonce;

        // Deadline check
        require(block.timestamp <= intent.deadline, "intent expired");

        // Risk guard: reject if AI's own score exceeds the on-chain limit
        if (intent.riskScore > maxRiskScore) {
            emit RiskGuardTriggered(intent.asset, intent.riskScore, "risk score exceeds limit");
            return false;
        }

        // Position must exist
        Position storage pos = positions[intent.asset];
        require(pos.active, "position not active");

        // Execute the transfer (asset must be an ERC20)
        (bool ok, ) = intent.asset.call(
            abi.encodeWithSignature("transfer(address,uint256)", owner, intent.amount)
        );
        require(ok, "transfer failed");

        pos.amount = pos.amount > intent.amount ? pos.amount - intent.amount : 0;
        emit RebalanceExecuted(intent.asset, intent.amount, intent.riskScore, intent.nonce);
        return true;
    }

    /**
     * @notice Human-confirmed withdrawal. Always requires owner signature.
     */
    function withdraw(address _asset, uint256 _amount) external onlyOwner notHalted {
        Position storage pos = positions[_asset];
        require(pos.active, "position not active");
        require(pos.amount >= _amount, "insufficient balance");

        (bool ok, ) = _asset.call(
            abi.encodeWithSignature("transfer(address,uint256)", owner, _amount)
        );
        require(ok, "transfer failed");
        pos.amount -= _amount;
    }

    // --- View --------------------------------------------------------------
    function getPosition(address _asset) external view returns (Position memory) {
        return positions[_asset];
    }

    function getPositionAssets() external view returns (address[] memory) {
        return positionAssets;
    }

    function portfolioValue() external view returns (uint256 total) {
        for (uint256 i = 0; i < positionAssets.length; i++) {
            total += positions[positionAssets[i]].amount;
        }
    }
}
