// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PortfolioManager
 * @notice Adaptive portfolio management on Arc (Circle L1)
 * @dev Handles multi-asset allocation, regime-based rebalancing, and USDC settlement
 *
 * RFB 04 — Adaptive Portfolio Manager
 * Agora Agents Hackathon (Canteen × Circle × Arc)
 */
contract PortfolioManager {
    // ── State ──────────────────────────────────────────────────────────────

    address public owner;
    address public oracle; // RegimeOracle address
    address public paymaster; // Circle Paymaster for USDC gas

    enum Regime { BULL_TRENDING, BEAR_TRENDING, RANGE_BOUND, HIGH_VOLATILITY, ACCUMULATION, PRICE_DISCOVERY }

    struct AssetAllocation {
        address token;
        uint256 targetBps;   // Target allocation in basis points (10000 = 100%)
        uint256 currentBps;  // Current allocation in basis points
        bool active;
    }

    struct PortfolioState {
        Regime currentRegime;
        uint256 lastRebalance;
        uint256 totalValueUsd;     // In USDC (6 decimals)
        uint256 rebalanceCount;
        uint256 minRebalanceInterval; // Minimum seconds between rebalances
    }

    struct RebalanceRecord {
        uint256 timestamp;
        Regime regime;
        uint256 totalBefore;
        uint256 totalAfter;
        int256 profitLoss;         // Signed P&L in USDC
    }

    // State
    PortfolioState public portfolio;
    AssetAllocation[] public allocations;
    RebalanceRecord[] public history;

    // Access
    mapping(address => bool) public authorizedAgents;
    uint256 public maxSlippageBps = 500; // 5% max slippage

    // Events
    event RebalanceExecuted(
        uint256 timestamp,
        Regime regime,
        uint256 totalBefore,
        uint256 totalAfter,
        int256 profitLoss
    );
    event AllocationUpdated(address token, uint256 targetBps);
    event RegimeChanged(Regime oldRegime, Regime newRegime);
    event AgentAuthorized(address agent);
    event AgentRevoked(address agent);

    // Errors
    error NotOwner();
    error NotAuthorized();
    error NotOracle();
    error RebalanceTooFrequent();
    error SlippageExceeded();
    error InvalidAllocation();
    error InsufficientBalance();

    // ── Modifiers ──────────────────────────────────────────────────────────

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyAuthorized() {
        if (!authorizedAgents[msg.sender] && msg.sender != owner) revert NotAuthorized();
        _;
    }

    modifier onlyOracle() {
        if (msg.sender != oracle) revert NotOracle();
        _;
    }

    // ── Constructor ────────────────────────────────────────────────────────

    constructor(address _paymaster) {
        owner = msg.sender;
        paymaster = _paymaster;
        portfolio = PortfolioState({
            currentRegime: Regime.RANGE_BOUND,
            lastRebalance: 0,
            totalValueUsd: 0,
            rebalanceCount: 0,
            minRebalanceInterval: 1 hours
        });
    }

    // ── Core Functions ─────────────────────────────────────────────────────

    /**
     * @notice Update regime from oracle — triggers potential rebalance
     * @param newRegime The current market regime
     * @param confidence Oracle confidence (0-100)
     */
    function updateRegime(Regime newRegime, uint256 confidence) external onlyOracle {
        Regime oldRegime = portfolio.currentRegime;
        portfolio.currentRegime = newRegime;

        if (oldRegime != newRegime) {
            emit RegimeChanged(oldRegime, newRegime);
        }
    }

    /**
     * @notice Execute rebalance — authorized agents call this after regime change
     * @dev Swaps assets to match target allocation for current regime
     * @param tokens Array of token addresses
     * @param targetBps Array of target allocation in basis points
     * @param deadline Transaction deadline timestamp
     */
    function rebalance(
        address[] calldata tokens,
        uint256[] calldata targetBps,
        uint256 deadline
    ) external onlyAuthorized {
        if (block.timestamp < portfolio.lastRebalance + portfolio.minRebalanceInterval) {
            revert RebalanceTooFrequent();
        }
        if (block.timestamp > deadline) {
            revert SlippageExceeded(); // Reuse as "deadline exceeded"
        }

        uint256 totalBefore = portfolio.totalValueUsd;

        // Validate allocations sum to 10000 (100%)
        uint256 totalBps = 0;
        for (uint256 i = 0; i < targetBps.length; i++) {
            totalBps += targetBps[i];
        }
        if (totalBps != 10000) revert InvalidAllocation();

        // Update allocations
        // In production, this would execute swaps via Arc DEX
        // For hackathon: update state and emit events
        for (uint256 i = 0; i < tokens.length; i++) {
            _updateAllocation(tokens[i], targetBps[i]);
        }

        portfolio.lastRebalance = block.timestamp;
        portfolio.rebalanceCount++;

        // Record history
        history.push(RebalanceRecord({
            timestamp: block.timestamp,
            regime: portfolio.currentRegime,
            totalBefore: totalBefore,
            totalAfter: portfolio.totalValueUsd,
            profitLoss: int256(portfolio.totalValueUsd) - int256(totalBefore)
        }));

        emit RebalanceExecuted(
            block.timestamp,
            portfolio.currentRegime,
            totalBefore,
            portfolio.totalValueUsd,
            int256(portfolio.totalValueUsd) - int256(totalBefore)
        );
    }

    /**
     * @notice Deposit USDC into portfolio
     * @param amount Amount of USDC to deposit (6 decimals)
     */
    function deposit(uint256 amount) external onlyAuthorized {
        if (amount == 0) revert InsufficientBalance();
        portfolio.totalValueUsd += amount;
        // In production: pull USDC via Paymaster/transferFrom
    }

    /**
     * @notice Withdraw USDC from portfolio
     * @param amount Amount to withdraw
     */
    function withdraw(uint256 amount) external onlyOwner {
        if (amount > portfolio.totalValueUsd) revert InsufficientBalance();
        portfolio.totalValueUsd -= amount;
    }

    // ── View Functions ─────────────────────────────────────────────────────

    /**
     * @notice Get current portfolio allocation breakdown
     */
    function getAllocations() external view returns (AssetAllocation[] memory) {
        return allocations;
    }

    /**
     * @notice Get rebalance history
     */
    function getHistory() external view returns (RebalanceRecord[] memory) {
        return history;
    }

    /**
     * @notice Get regime-specific allocation targets
     * @dev Returns recommended BPS for each regime
     */
    function getRegimeAllocation(Regime regime) external pure returns (uint256[] memory) {
        // Regime-based allocation profiles
        // Each regime has a different risk/reward profile
        uint256[] memory alloc = new uint256[](6);

        if (regime == Regime.BULL_TRENDING) {
            // Aggressive: 60% risk assets, 20% yield, 20% stable
            alloc[0] = 6000; // Risk assets
            alloc[1] = 2000; // Yield (USYC)
            alloc[2] = 2000; // Stable (USDC)
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        } else if (regime == Regime.BEAR_TRENDING) {
            // Defensive: 10% risk, 30% yield, 60% stable
            alloc[0] = 1000;
            alloc[1] = 3000;
            alloc[2] = 6000;
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        } else if (regime == Regime.RANGE_BOUND) {
            // Balanced: 30% risk, 40% yield, 30% stable
            alloc[0] = 3000;
            alloc[1] = 4000;
            alloc[2] = 3000;
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        } else if (regime == Regime.HIGH_VOLATILITY) {
            // Conservative: 5% risk, 25% yield, 70% stable
            alloc[0] = 500;
            alloc[1] = 2500;
            alloc[2] = 7000;
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        } else if (regime == Regime.ACCUMULATION) {
            // DCA mode: 40% risk, 20% yield, 40% stable (dry powder)
            alloc[0] = 4000;
            alloc[1] = 2000;
            alloc[2] = 4000;
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        } else {
            // PRICE_DISCOVERY: 20% risk, 30% yield, 50% stable
            alloc[0] = 2000;
            alloc[1] = 3000;
            alloc[2] = 5000;
            alloc[3] = 0;
            alloc[4] = 0;
            alloc[5] = 0;
        }

        return alloc;
    }

    // ── Internal ───────────────────────────────────────────────────────────

    function _updateAllocation(address token, uint256 targetBps) internal {
        bool found = false;
        for (uint256 i = 0; i < allocations.length; i++) {
            if (allocations[i].token == token) {
                allocations[i].targetBps = targetBps;
                allocations[i].active = true;
                found = true;
                emit AllocationUpdated(token, targetBps);
                break;
            }
        }
        if (!found) {
            allocations.push(AssetAllocation({
                token: token,
                targetBps: targetBps,
                currentBps: 0,
                active: true
            }));
            emit AllocationUpdated(token, targetBps);
        }
    }

    // ── Admin ──────────────────────────────────────────────────────────────

    function setOracle(address _oracle) external onlyOwner {
        oracle = _oracle;
    }

    function authorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = true;
        emit AgentAuthorized(agent);
    }

    function revokeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
        emit AgentRevoked(agent);
    }

    function setMaxSlippage(uint256 bps) external onlyOwner {
        if (bps > 2000) revert SlippageExceeded(); // Max 20%
        maxSlippageBps = bps;
    }
}
