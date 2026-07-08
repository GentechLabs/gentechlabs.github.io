// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title DryPowderVault
 * @notice ERC-4626 compatible vault for cross-chain USDC yield rotation.
 *         Tracks per-chain balances, emits events for agent monitoring,
 *         and supports CCTP/Across bridging via authorized operators.
 *
 * @dev    MVP scope: Base (home chain) -> Avalanche, Solana rotation.
 *         Operator role = Hermes agent orchestrator wallet.
 */
contract DryPowderVault is ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // ──────────────────── Types ────────────────────

    enum Chain { Base, Avalanche, Solana }

    struct ChainBalance {
        uint256 deposited;   // Total USDC deposited on this chain
        uint256 yield;       // Cumulative yield earned (accrued off-chain, synced)
        uint256 locked;      // Currently locked in LP or bridging
        uint8  status;       // 0=inactive, 1=active, 2=paused
    }

    struct BridgeRequest {
        uint256 id;
        address user;
        Chain   fromChain;
        Chain   toChain;
        uint256 amount;
        uint256 fee;
        uint256 timestamp;
        uint8   status;     // 0=pending, 1=submitted, 2=completed, 3=failed
    }

    struct RotationProposal {
        uint256 id;
        Chain   fromChain;
        Chain   toChain;
        uint256 amount;
        string  reason;     // e.g. "yield_diff>3%, AVAX LP 12% APY"
        uint256 timestamp;
        uint8   status;     // 0=pending, 1=approved, 2=executed, 3=rejected
    }

    // ──────────────────── State ────────────────────

    IERC20 public immutable usdc;

    address public owner;
    address public operator;    // Hermes agent wallet

    uint256 public totalDeposited;
    uint256 public totalYield;
    uint256 public bridgeNonce;
    uint256 public rotationNonce;

    uint256 public performanceFeeBps = 1000; // 10%
    uint256 public bridgeFeeBps = 20;        // 0.20% gas markup

    mapping(Chain => ChainBalance) public chainBalances;
    mapping(uint256 => BridgeRequest) public bridgeRequests;
    mapping(uint256 => RotationProposal) public rotationProposals;

    // user => deposited amount (on home chain)
    mapping(address => uint256) public deposits;

    // ──────────────────── Events ────────────────────

    event Deposit(address indexed user, uint256 amount, uint256 shares);
    event Withdraw(address indexed user, uint256 shares, uint256 amount);
    event BridgeInitiated(uint256 indexed id, address indexed user, Chain fromChain, Chain toChain, uint256 amount, uint256 fee);
    event BridgeCompleted(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount);
    event BridgeFailed(uint256 indexed id, string reason);
    event RotationProposed(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount, string reason);
    event RotationExecuted(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount);
    event RotationRejected(uint256 indexed id, string reason);
    event YieldReported(Chain indexed chain, uint256 yieldAmount, uint256 totalYield);
    event OperatorUpdated(address indexed oldOp, address indexed newOp);
    event FeeUpdated(uint256 performanceBps, uint256 bridgeBps);
    event ChainStatusChanged(Chain indexed chain, uint8 status);

    // ──────────────────── Modifiers ────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }

    modifier onlyOperator() {
        require(msg.sender == operator || msg.sender == owner, "NOT_OPERATOR");
        _;
    }

    // ──────────────────── Constructor ────────────────────

    constructor(address _usdc) {
        require(_usdc != address(0), "ZERO_ADDRESS");
        usdc = IERC20(_usdc);
        owner = msg.sender;
        operator = msg.sender;

        // Initialize Base as home chain (status=active)
        chainBalances[Chain.Base].status = 1;
    }

    // ──────────────────── ERC-4626 Core ────────────────────

    /// @notice Deposit USDC into the vault. Shares = amount (1:1 for MVP).
    function deposit(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "ZERO_AMOUNT");
        require(deposits[msg.sender] + amount <= type(uint128).max, "OVERFLOW");

        usdc.safeTransferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        totalDeposited += amount;
        chainBalances[Chain.Base].deposited += amount;

        emit Deposit(msg.sender, amount, amount);
    }

    /// @notice Withdraw USDC from vault (home chain only).
    function withdraw(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "ZERO_AMOUNT");
        require(deposits[msg.sender] >= amount, "INSUFFICIENT_BALANCE");
        require(chainBalances[Chain.Base].deposited >= amount, "INSUFFICIENT_CHAIN_BALANCE");

        deposits[msg.sender] -= amount;
        totalDeposited -= amount;
        chainBalances[Chain.Base].deposited -= amount;

        usdc.safeTransfer(msg.sender, amount);
        emit Withdraw(msg.sender, amount, amount);
    }

    /// @notice View: user's total deposited value across all chains.
    function totalAssets() external view returns (uint256) {
        return totalDeposited + totalYield;
    }

    /// @notice View: user's balance (deposited + proportional yield).
    function balanceOf(address user) external view returns (uint256) {
        if (totalDeposited == 0) return deposits[user];
        uint256 userShare = (deposits[user] * (totalDeposited + totalYield)) / totalDeposited;
        return userShare;
    }

    // ──────────────────── Bridge Operations ────────────────────

    /// @notice Operator initiates a CCTP/Across bridge.
    function initiateBridge(
        address user,
        Chain fromChain,
        Chain toChain,
        uint256 amount
    ) external onlyOperator returns (uint256 id) {
        require(fromChain != toChain, "SAME_CHAIN");
        require(amount > 0, "ZERO_AMOUNT");
        require(chainBalances[fromChain].deposited >= amount, "INSUFFICIENT_FROM_CHAIN");

        uint256 fee = (amount * bridgeFeeBps) / 10000;
        id = ++bridgeNonce;

        chainBalances[fromChain].deposited -= amount;
        chainBalances[fromChain].locked += amount;
        chainBalances[fromChain].status = 1;

        bridgeRequests[id] = BridgeRequest({
            id: id,
            user: user,
            fromChain: fromChain,
            toChain: toChain,
            amount: amount,
            fee: fee,
            timestamp: block.timestamp,
            status: 0
        });

        emit BridgeInitiated(id, user, fromChain, toChain, amount, fee);
    }

    /// @notice Operator confirms bridge completion (called after CCTP confirms).
    function completeBridge(uint256 id) external onlyOperator {
        BridgeRequest storage req = bridgeRequests[id];
        require(req.status == 0 || req.status == 1, "INVALID_STATUS");

        chainBalances[req.fromChain].locked -= req.amount;
        chainBalances[req.toChain].deposited += req.amount;
        req.status = 2;

        emit BridgeCompleted(id, req.fromChain, req.toChain, req.amount);
    }

    /// @notice Operator marks bridge as failed and refunds.
    function failBridge(uint256 id, string calldata reason) external onlyOperator {
        BridgeRequest storage req = bridgeRequests[id];
        require(req.status == 0 || req.status == 1, "INVALID_STATUS");

        chainBalances[req.fromChain].locked -= req.amount;
        chainBalances[req.fromChain].deposited += req.amount;
        req.status = 3;

        emit BridgeFailed(id, reason);
    }

    // ──────────────────── Rotation Proposals ────────────────────

    /// @notice Operator proposes a rotation (agent decision).
    function proposeRotation(
        Chain fromChain,
        Chain toChain,
        uint256 amount,
        string calldata reason
    ) external onlyOperator returns (uint256 id) {
        id = ++rotationNonce;

        rotationProposals[id] = RotationProposal({
            id: id,
            fromChain: fromChain,
            toChain: toChain,
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            status: 0
        });

        emit RotationProposed(id, fromChain, toChain, amount, reason);
    }

    /// @notice Owner approves a rotation proposal.
    function approveRotation(uint256 id) external onlyOwner {
        RotationProposal storage prop = rotationProposals[id];
        require(prop.status == 0, "NOT_PENDING");
        prop.status = 1;
    }

    /// @notice Operator marks rotation as executed.
    function executeRotation(uint256 id) external onlyOperator {
        RotationProposal storage prop = rotationProposals[id];
        require(prop.status == 1, "NOT_APPROVED");

        require(chainBalances[prop.fromChain].deposited >= prop.amount, "INSUFFICIENT_FROM");
        chainBalances[prop.fromChain].deposited -= prop.amount;
        chainBalances[prop.toChain].deposited += prop.amount;
        prop.status = 2;

        emit RotationExecuted(id, prop.fromChain, prop.toChain, prop.amount);
    }

    // ──────────────────── Yield Reporting ────────────────────

    /// @notice Operator reports yield earned on a chain.
    function reportYield(Chain chain_, uint256 amount) external onlyOperator {
        chainBalances[chain_].yield += amount;
        totalYield += amount;
        emit YieldReported(chain_, amount, totalYield);
    }

    // ──────────────────── Admin ────────────────────

    function setOperator(address newOp) external onlyOwner {
        require(newOp != address(0), "ZERO_ADDRESS");
        emit OperatorUpdated(operator, newOp);
        operator = newOp;
    }

    function setFees(uint256 perfBps, uint256 bridgeBps) external onlyOwner {
        require(perfBps <= 5000 && bridgeBps <= 1000, "FEE_TOO_HIGH");
        performanceFeeBps = perfBps;
        bridgeFeeBps = bridgeBps;
        emit FeeUpdated(perfBps, bridgeBps);
    }

    function setChainStatus(Chain chain_, uint8 status) external onlyOperator {
        chainBalances[chain_].status = status;
        emit ChainStatusChanged(chain_, status);
    }

    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    /// @notice Emergency withdrawal (owner only, paused state).
    function emergencyWithdraw(uint256 amount) external onlyOwner {
        require(paused(), "NOT_PAUSED");
        usdc.safeTransfer(owner, amount);
    }

    // ──────────────────── Views ────────────────────

    function getChainBalance(Chain chain_) external view returns (ChainBalance memory) {
        return chainBalances[chain_];
    }

    function getBridgeRequest(uint256 id) external view returns (BridgeRequest memory) {
        return bridgeRequests[id];
    }

    function getRotationProposal(uint256 id) external view returns (RotationProposal memory) {
        return rotationProposals[id];
    }

    function getUSDCBalance() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }
}
