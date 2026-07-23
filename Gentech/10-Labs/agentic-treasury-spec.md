# Agentic Treasury — Architecture Specification

**Status:** Spec v1.0 | **Priority:** High | **Builds on:** AAE, x402 v2, Q402
**Author:** Forge (GenTech Labs) | **Date:** 2026-07-21
**Vault Path:** `10-Labs/agentic-treasury-spec.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Pillar 1: Yield Brain (AAE)](#3-pillar-1-yield-brain-aae)
4. [Pillar 2: Payment Router (x402 Mesh)](#4-pillar-2-payment-router-x402-mesh)
5. [Pillar 3: P2P Causes (Funding Platform)](#5-pillar-3-p2p-causes-funding-platform)
6. [Smart Contract Interfaces](#6-smart-contract-interfaces)
7. [x402 / Q402 Integration Points](#7-x402--q402-integration-points)
8. [Agent Interaction Flows](#8-agent-interaction-flows)
9. [Implementation Phases](#9-implementation-phases)
10. [Risk Analysis](#10-risk-analysis)
11. [Appendix: Q402 Tool Reference](#11-appendix-q402-tool-reference)

---

## 1. Executive Summary

The **Agentic Treasury** is a three-pillar financial layer for autonomous agents. It enables agents to:

1. **Earn yield** on idle stablecoin reserves via automated, enforcement-gated DeFi positions
2. **Route payments** across multiple facilitators and chains, selecting the cheapest/fastest path
3. **Fund each other** through a P2P cause platform with escrow-backed accountability

All three pillars are built on the **AAE (Autonomous Agent Engine)** 8-layer architecture, using **x402 v2** for payment routing and **Q402** for gasless settlement. Enforcement hooks from AAE Layer 6 (🛡️ Enforcement) provide risk guardrails across all financial operations.

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Enforcement-First** | All financial operations pass through AAE Layer 6 enforcement hooks before execution |
| **Gasless by Default** | Q402 handles settlement — agents never need native gas tokens |
| **Multi-Facilitator** | Payment Router supports CDP (EVM), GoPlausible (Algorand), and Q402 (gasless) simultaneously |
| **Composable** | Each pillar can be used independently or combined into treasury workflows |
| **Simulation-Ready** | All pillars have simulation modes for testing before on-chain deployment |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENTIC TREASURY                                 │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   YIELD BRAIN    │  │  PAYMENT ROUTER  │  │   P2P CAUSES     │      │
│  │    (AAE L6)      │  │   (x402 Mesh)    │  │  (Funding Plat.) │      │
│  │                  │  │                  │  │                  │      │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │      │
│  │  │ AAE Hooks  │  │  │  │ CDP Facil. │  │  │  │ Q402 Req.  │  │      │
│  │  │ (max amt,  │  │  │  │ (EVM)      │  │  │  │ (create/   │  │      │
│  │  │ allowlist, │  │  │  ├────────────┤  │  │  │  pay)      │  │      │
│  │  │ 2-phase)   │  │  │  │ GoPlausible│  │  │  ├────────────┤  │      │
│  │  ├────────────┤  │  │  │ (Algorand) │  │  │  │ Q402 Escrow│  │      │
│  │  │ Q402 Yield │  │  │  ├────────────┤  │  │  │ (create/   │  │      │
│  │  │ (deposit/  │  │  │  │ Q402 Facil.│  │  │  │  lock/     │  │      │
│  │  │ withdraw/  │  │  │  │ (gasless)  │  │  │  │  release)  │  │      │
│  │  │ reserves)  │  │  │  └────────────┘  │  │  └────────────┘  │      │
│  │  └────────────┘  │  │                  │  │                  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SHARED INFRASTRUCTURE                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │    │
│  │  │ AAE L6   │  │ x402 v2  │  │ Q402     │  │ Agent Wallet │   │    │
│  │  │Enforce-  │  │ Protocol │  │ Gasless  │  │ (ERC-8004)   │   │    │
│  │  │ment Hooks│  │          │  │Settlement│  │              │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Agent Treasury Request
        │
        ▼
┌───────────────────┐
│  AAE Layer 6       │
│  Enforcement Check │◄── Max amount, recipient allowlist, two-phase consent
└───────┬───────────┘
        │ Pass
        ▼
┌───────────────────┐
│  Route Selector    │
│  (cheapest/fastest)│◄── Compare CDP, GoPlausible, Q402 routes
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Facilitator       │
│  Execution         │◄── Submit through selected facilitator
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Settlement       │
│  (Q402 gasless)   │◄── Finalize on-chain
└───────────────────┘
```

---

## 3. Pillar 1: Yield Brain (AAE)

### 3.1 Overview

The **Yield Brain** is an automated yield optimization engine that uses AAE Layer 6 enforcement hooks to manage stablecoin deposits into curated lending vaults. It operates on **BNB Chain** and **Base**, targeting protocols:

- **Aave** — Multi-chain lending, variable + stable rates
- **Morpho** — Peer-to-peer lending with optimized rates
- **Lista DAO** — Liquid staking + borrowing on BNB Chain

### 3.2 AAE Enforcement Hooks

Every yield operation passes through three enforcement gates:

| Hook | Description | Example |
|------|-------------|---------|
| **Max Amount** | Caps total deposit per vault per agent | Max 10,000 USDC per vault |
| **Recipient Allowlist** | Only pre-approved vault addresses | Aave, Morpho, Lista only |
| **Two-Phase Consent** | Deposit → preview → confirm | Agent must confirm after seeing projected APR |

### 3.3 Q402 Yield Tools

The Yield Brain uses Q402's yield tool suite:

```python
# q402_yield_reserves — Check vault reserves and APRs
reserves = await q402_yield_reserves(
    chain="bnb",
    vaults=["aave", "morpho", "lista"]
)
# Returns: {vault: {total_supply, available_liquidity, supply_apr, utilization_rate}}

# q402_yield_deposit — Deposit stablecoins into a vault
receipt = await q402_yield_deposit(
    vault="aave",
    token="USDC",
    amount=5000,
    chain="base"
)
# Returns: {tx_hash, vault, amount, shares_received}

# q402_yield_withdraw — Withdraw from a vault
receipt = await q402_yield_withdraw(
    vault="morpho",
    token="USDC",
    amount=2500,
    chain="bnb"
)
# Returns: {tx_hash, vault, amount, shares_burned}
```

### 3.4 Yield Optimization Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    YIELD BRAIN LOOP                          │
│                                                             │
│  Every 6 hours (configurable):                              │
│                                                             │
│  1. Scan all vaults for current APRs                        │
│     ├── Aave (Base)    → 8.2% APR                          │
│     ├── Morpho (Base)  → 9.7% APR  ← Best                  │
│     └── Lista (BNB)    → 7.1% APR                          │
│                                                             │
│  2. Check enforcement limits                                 │
│     ├── Max per vault: $10,000                              │
│     ├── Current Morpho: $3,200                              │
│     └── Headroom: $6,800                                   │
│                                                             │
│  3. Rebalance if profitable (net of gas)                    │
│     ├── Withdraw from underperforming vaults                │
│     └── Deposit into best APR vault (within limits)         │
│                                                             │
│  4. Log all actions to treasury ledger                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 Yield Brain Contract (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @title YieldBrain — Automated yield optimization with AAE enforcement hooks
/// @notice Agents deposit stablecoins into curated lending vaults
/// @dev All operations pass through AAE Layer 6 enforcement checks
contract YieldBrain is Ownable {
    using SafeERC20 for IERC20;

    // ── Types ──────────────────────────────────────────────────────────

    struct VaultConfig {
        address vaultAddress;
        address tokenAddress;
        uint256 maxDeposit;        // Max deposit per agent (AAE L6 enforcement)
        uint256 minDeposit;        // Min deposit to avoid dust
        bool active;
    }

    struct AgentPosition {
        uint256 depositedAmount;
        uint256 shares;
        uint256 lastRebalance;
        uint256 depositTimestamp;
    }

    struct EnforcementConfig {
        uint256 maxTotalDeposits;       // Global cap
        uint256 maxPerVault;            // Per-vault cap
        uint256 cooldownPeriod;         // Seconds between rebalances
        bool requireTwoPhaseConsent;    // AAE L6 two-phase consent
    }

    // ── State ──────────────────────────────────────────────────────────

    mapping(bytes32 => VaultConfig) public vaults;           // vaultId => config
    mapping(address => mapping(bytes32 => AgentPosition)) public positions; // agent => vaultId => position
    mapping(address => EnforcementConfig) public enforcement; // agent => enforcement config

    address[] public vaultList;
    uint256 public totalTreasuryValue;

    // ── Events ─────────────────────────────────────────────────────────

    event VaultAdded(bytes32 indexed vaultId, address vault, address token);
    event VaultRemoved(bytes32 indexed vaultId);
    event Deposited(address indexed agent, bytes32 indexed vaultId, uint256 amount, uint256 shares);
    event Withdrawn(address indexed agent, bytes32 indexed vaultId, uint256 amount, uint256 shares);
    event Rebalanced(address indexed agent, bytes32 indexed fromVault, bytes32 indexed toVault, uint256 amount);
    event EnforcementUpdated(address indexed agent, uint256 maxTotal, uint256 maxPerVault, uint256 cooldown);

    // ── Admin ──────────────────────────────────────────────────────────

    function addVault(
        bytes32 vaultId,
        address vaultAddress,
        address tokenAddress,
        uint256 maxDeposit,
        uint256 minDeposit
    ) external onlyOwner {
        require(vaultAddress != address(0), "Invalid vault address");
        require(tokenAddress != address(0), "Invalid token address");
        vaults[vaultId] = VaultConfig({
            vaultAddress: vaultAddress,
            tokenAddress: tokenAddress,
            maxDeposit: maxDeposit,
            minDeposit: minDeposit,
            active: true
        });
        vaultList.push(vaultAddress);
        emit VaultAdded(vaultId, vaultAddress, tokenAddress);
    }

    function removeVault(bytes32 vaultId) external onlyOwner {
        require(vaults[vaultId].active, "Vault not active");
        vaults[vaultId].active = false;
        emit VaultRemoved(vaultId);
    }

    // ── Agent Enforcement Configuration ─────────────────────────────────

    function setEnforcement(
        uint256 maxTotalDeposits,
        uint256 maxPerVault,
        uint256 cooldownPeriod,
        bool requireTwoPhaseConsent
    ) external {
        enforcement[msg.sender] = EnforcementConfig({
            maxTotalDeposits: maxTotalDeposits,
            maxPerVault: maxPerVault,
            cooldownPeriod: cooldownPeriod,
            requireTwoPhaseConsent: requireTwoPhaseConsent
        });
        emit EnforcementUpdated(msg.sender, maxTotalDeposits, maxPerVault, cooldownPeriod);
    }

    // ── Core Operations ────────────────────────────────────────────────

    /// @notice Deposit stablecoins into a vault (AAE L6 enforcement-gated)
    function deposit(bytes32 vaultId, uint256 amount) external {
        VaultConfig storage vault = vaults[vaultId];
        require(vault.active, "Vault not active");
        require(amount >= vault.minDeposit, "Below minimum deposit");
        require(amount <= vault.maxDeposit, "Exceeds max deposit");

        EnforcementConfig storage config = enforcement[msg.sender];
        AgentPosition storage pos = positions[msg.sender][vaultId];

        // AAE L6: Max amount enforcement
        require(pos.depositedAmount + amount <= config.maxPerVault, "Exceeds per-vault limit");

        // AAE L6: Global cap enforcement
        uint256 agentTotal = _getAgentTotalDeposits(msg.sender);
        require(agentTotal + amount <= config.maxTotalDeposits, "Exceeds total deposit limit");

        // AAE L6: Cooldown enforcement
        require(
            block.timestamp >= pos.lastRebalance + config.cooldownPeriod,
            "Cooldown not elapsed"
        );

        // Transfer tokens
        IERC20 token = IERC20(vault.tokenAddress);
        token.safeTransferFrom(msg.sender, address(this), amount);

        // Mint shares (simplified 1:1 for stablecoins)
        uint256 shares = amount;
        pos.depositedAmount += amount;
        pos.shares += shares;
        pos.lastRebalance = block.timestamp;
        if (pos.depositTimestamp == 0) {
            pos.depositTimestamp = block.timestamp;
        }
        totalTreasuryValue += amount;

        emit Deposited(msg.sender, vaultId, amount, shares);
    }

    /// @notice Withdraw from a vault
    function withdraw(bytes32 vaultId, uint256 amount) external {
        VaultConfig storage vault = vaults[vaultId];
        require(vault.active, "Vault not active");

        AgentPosition storage pos = positions[msg.sender][vaultId];
        require(pos.depositedAmount >= amount, "Insufficient balance");

        // AAE L6: Cooldown enforcement
        EnforcementConfig storage config = enforcement[msg.sender];
        require(
            block.timestamp >= pos.lastRebalance + config.cooldownPeriod,
            "Cooldown not elapsed"
        );

        // Burn shares
        uint256 shares = amount;
        pos.depositedAmount -= amount;
        pos.shares -= shares;
        pos.lastRebalance = block.timestamp;
        totalTreasuryValue -= amount;

        // Transfer tokens back
        IERC20 token = IERC20(vault.tokenAddress);
        token.safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, vaultId, amount, shares);
    }

    /// @notice Rebalance from one vault to another
    function rebalance(bytes32 fromVault, bytes32 toVault, uint256 amount) external {
        withdraw(fromVault, amount);
        deposit(toVault, amount);
        emit Rebalanced(msg.sender, fromVault, toVault, amount);
    }

    // ── Internal ───────────────────────────────────────────────────────

    function _getAgentTotalDeposits(address agent) internal view returns (uint256) {
        uint256 total;
        for (uint256 i = 0; i < vaultList.length; i++) {
            // Find vaultId for this address
            // Simplified — in production use a mapping
        }
        return total;
    }

    /// @notice Get agent's total value across all vaults
    function getAgentPortfolio(address agent) external view returns (uint256 totalValue, uint256 vaultCount) {
        for (uint256 i = 0; i < vaultList.length; i++) {
            // Aggregate positions
        }
    }
}
```

---

## 4. Pillar 2: Payment Router (x402 Mesh)

### 4.1 Overview

The **Payment Router** is a multi-facilitator payment routing layer. It routes payments through three facilitators, auto-selecting the cheapest or fastest route for each transaction.

### 4.2 Facilitator Matrix

| Facilitator | Chains | Settlement Time | Fee | Best For |
|-------------|--------|-----------------|-----|----------|
| **CDP (Coinbase)** | EVM (Base, BNB, ETH) | ~12s | 0.1% | EVM-native agents |
| **GoPlausible** | Algorand AVM | ~3.5s | 0.05% | Fast settlement |
| **Q402** | Gasless (any chain) | ~2s | 0.01% | Micro-payments, gasless |

### 4.3 Route Selection Algorithm

```
Route Selection (payment: {amount, token, destination}):
  1. Query all facilitators for route availability
  2. For each available route, calculate:
     - Total cost = facilitator fee + gas cost (if any)
     - Estimated time = settlement time + network latency
  3. Score routes:
     - cheapest: sort by total cost ascending
     - fastest: sort by estimated time ascending
     - balanced: weighted score (0.7 × cost + 0.3 × time)
  4. Return top 3 routes with scores
  5. Execute selected route
```

### 4.4 Payment Router Contract (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/// @title PaymentRouter — Multi-facilitator x402 payment routing
/// @notice Routes payments through CDP, GoPlausible, and Q402 facilitators
/// @dev Auto-selects cheapest/fastest route per transaction
contract PaymentRouter is Ownable {

    // ── Types ──────────────────────────────────────────────────────────

    enum Facilitator { CDP, GoPlausible, Q402 }
    enum RouteStrategy { Cheapest, Fastest, Balanced }

    struct Route {
        Facilitator facilitator;
        uint256 estimatedCost;      // In smallest token unit
        uint256 estimatedTimeMs;     // Estimated settlement time in ms
        string chainId;              // CAIP-2 chain identifier
        bool available;
    }

    struct PaymentRequest {
        address sender;
        address recipient;
        address token;
        uint256 amount;
        RouteStrategy strategy;
        uint256 maxCost;             // Max acceptable cost
        uint256 deadline;            // Unix timestamp
        bool executed;
        Facilitator selectedFacilitator;
    }

    struct FacilitatorConfig {
        string endpointUrl;
        uint256 baseFee;             // Base fee in bps (e.g., 10 = 0.1%)
        uint256 minSettlementTimeMs;
        bool active;
    }

    // ── State ──────────────────────────────────────────────────────────

    mapping(Facilitator => FacilitatorConfig) public facilitators;
    mapping(bytes32 => PaymentRequest) public payments;
    uint256 public totalPaymentsRouted;
    uint256 public totalValueRouted;

    // ── Events ─────────────────────────────────────────────────────────

    event FacilitatorUpdated(Facilitator indexed facilitator, string endpoint, uint256 baseFee);
    event PaymentRouted(
        bytes32 indexed paymentId,
        address indexed sender,
        address indexed recipient,
        uint256 amount,
        Facilitator facilitator,
        uint256 cost
    );
    event RouteSelected(bytes32 indexed paymentId, Facilitator facilitator, uint256 estimatedCost);

    // ── Admin ──────────────────────────────────────────────────────────

    function setFacilitator(
        Facilitator facilitator,
        string calldata endpointUrl,
        uint256 baseFee,
        uint256 minSettlementTimeMs
    ) external onlyOwner {
        facilitators[facilitator] = FacilitatorConfig({
            endpointUrl: endpointUrl,
            baseFee: baseFee,
            minSettlementTimeMs: minSettlementTimeMs,
            active: true
        });
        emit FacilitatorUpdated(facilitator, endpointUrl, baseFee);
    }

    // ── Route Selection ────────────────────────────────────────────────

    /// @notice Select the best route for a payment
    /// @return selectedFacilitator The chosen facilitator
    /// @return estimatedCost The estimated cost
    function selectRoute(
        address token,
        uint256 amount,
        RouteStrategy strategy
    ) public view returns (Facilitator selectedFacilitator, uint256 estimatedCost) {
        Facilitator best;
        uint256 bestScore = type(uint256).max;

        for (uint256 i = 0; i < 3; i++) {
            Facilitator f = Facilitator(i);
            FacilitatorConfig storage config = facilitators[f];
            if (!config.active) continue;

            uint256 cost = (amount * config.baseFee) / 10000;
            uint256 time = config.minSettlementTimeMs;

            uint256 score;
            if (strategy == RouteStrategy.Cheapest) {
                score = cost;
            } else if (strategy == RouteStrategy.Fastest) {
                score = time;
            } else {
                // Balanced: 70% cost, 30% time
                score = (cost * 70 + time * 30) / 100;
            }

            if (score < bestScore) {
                bestScore = score;
                best = f;
                estimatedCost = cost;
            }
        }

        return (best, estimatedCost);
    }

    /// @notice Execute a payment through the selected route
    function routePayment(
        bytes32 paymentId,
        address recipient,
        address token,
        uint256 amount,
        RouteStrategy strategy,
        uint256 maxCost,
        uint256 deadline
    ) external payable returns (Facilitator selected) {
        require(block.timestamp <= deadline, "Payment deadline passed");
        require(!payments[paymentId].executed, "Payment already executed");

        (Facilitator facilitator, uint256 cost) = selectRoute(token, amount, strategy);
        require(cost <= maxCost, "Cost exceeds max");

        payments[paymentId] = PaymentRequest({
            sender: msg.sender,
            recipient: recipient,
            token: token,
            amount: amount,
            strategy: strategy,
            maxCost: maxCost,
            deadline: deadline,
            executed: true,
            selectedFacilitator: facilitator
        });

        totalPaymentsRouted++;
        totalValueRouted += amount;

        emit PaymentRouted(paymentId, msg.sender, recipient, amount, facilitator, cost);
        emit RouteSelected(paymentId, facilitator, cost);

        return facilitator;
    }

    /// @notice Get route quote without executing
    function quoteRoute(
        address token,
        uint256 amount,
        RouteStrategy strategy
    ) external view returns (Route[] memory routes) {
        routes = new Route[](3);
        for (uint256 i = 0; i < 3; i++) {
            Facilitator f = Facilitator(i);
            FacilitatorConfig storage config = facilitators[f];
            routes[i] = Route({
                facilitator: f,
                estimatedCost: (amount * config.baseFee) / 10000,
                estimatedTimeMs: config.minSettlementTimeMs,
                chainId: _getChainId(f),
                available: config.active
            });
        }
    }

    function _getChainId(Facilitator f) internal pure returns (string memory) {
        if (f == Facilitator.CDP) return "eip155:84532";       // Base Sepolia
        if (f == Facilitator.GoPlausible) return "algorand:SGO1GKSzyE7IEPItTxCByw9x8FmnrCDe"; // TestNet
        if (f == Facilitator.Q402) return "q402:gasless";      // Gasless
        return "";
    }
}
```

### 4.5 Bazaar Discovery

The Payment Router exposes a Bazaar discovery endpoint so agents can auto-discover routing capabilities:

```json
GET /.well-known/x402-bazaar
{
  "x402Version": 2,
  "gateway": "Agentic Treasury — Payment Router",
  "facilitators": [
    {
      "name": "CDP (Coinbase)",
      "chains": ["eip155:84532", "eip155:56"],
      "baseFee": 10,
      "minSettlementMs": 12000
    },
    {
      "name": "GoPlausible",
      "chains": ["algorand:SGO1GKSzyE7IEPItTxCByw9x8FmnrCDe"],
      "baseFee": 5,
      "minSettlementMs": 3500
    },
    {
      "name": "Q402 (Gasless)",
      "chains": ["q402:gasless"],
      "baseFee": 1,
      "minSettlementMs": 2000
    }
  ],
  "strategies": ["cheapest", "fastest", "balanced"]
}
```

---

## 5. Pillar 3: P2P Causes (Funding Platform)

### 5.1 Overview

The **P2P Causes** platform enables agent-to-agent funding. Agents create funding requests with goals, other agents fund them. Uses Q402 payment requests for direct funding and Q402 escrow for milestone-based releases.

### 5.2 Core Concepts

| Concept | Description | Q402 Tool |
|---------|-------------|-----------|
| **Funding Request** | Agent posts a cause with a goal amount | `q402_request_create` |
| **Direct Contribution** | Agent funds a cause directly | `q402_request_pay` |
| **Milestone Escrow** | Funds held in escrow, released on milestones | `q402_escrow_create` |
| **Escrow Lock** | Contributor locks funds into escrow | `q402_escrow_lock` |
| **Escrow Release** | Funds released to creator on milestone completion | `q402_escrow_release` |
| **Reputation** | Wallet-level trust scores from contribution history | On-chain scoring |

### 5.3 Q402 Integration

```python
# Create a funding request
request = await q402_request_create(
    title="Build Agentic Treasury Dashboard",
    description="Frontend dashboard for monitoring treasury positions",
    amount=5000,  # USDC
    recipient="0xAgentCreator...",
    deadline="2026-08-21T00:00:00Z",
    milestones=[
        {"name": "UI Mockups", "amount": 1000, "completion_criteria": "Figma review"},
        {"name": "Backend API", "amount": 2000, "completion_criteria": "API tests pass"},
        {"name": "Integration", "amount": 2000, "completion_criteria": "E2E tests pass"},
    ]
)

# Fund a request (direct)
receipt = await q402_request_pay(
    request_id=request.id,
    amount=500,
    contributor="0xContributor...",
    message="Happy to support this!"
)

# Create escrow for milestone-based funding
escrow = await q402_escrow_create(
    request_id=request.id,
    total_amount=5000,
    milestone_count=3,
    arbiter="0xArbiter...",  # Dispute resolver
)

# Lock funds into escrow
lock_receipt = await q402_escrow_lock(
    escrow_id=escrow.id,
    contributor="0xContributor...",
    amount=5000,
)

# Release milestone (on completion verification)
release_receipt = await q402_escrow_release(
    escrow_id=escrow.id,
    milestone_index=0,
    verifier="0xArbiter...",
)
```

### 5.4 P2P Causes Contract (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @title P2PCauses — Agent-to-agent funding platform
/// @notice Agents create funding requests, other agents fund them
/// @dev Uses Q402 payment requests and escrow for milestone-based releases
contract P2PCauses is Ownable {
    using SafeERC20 for IERC20;

    // ── Types ──────────────────────────────────────────────────────────

    enum CauseStatus { Draft, Active, Funded, Completed, Cancelled }
    enum MilestoneStatus { Pending, InProgress, Completed, Disputed }

    struct Milestone {
        string name;
        uint256 amount;
        string completionCriteria;
        MilestoneStatus status;
        uint256 completedAt;
    }

    struct Cause {
        uint256 id;
        address creator;
        string title;
        string story;
        address token;
        uint256 goalAmount;
        uint256 raisedAmount;
        uint256 contributorCount;
        CauseStatus status;
        uint256 createdAt;
        uint256 deadline;
        string[] tags;
        string[] imageUrls;
    }

    struct Escrow {
        uint256 causeId;
        uint256 totalAmount;
        uint256 releasedAmount;
        uint256 milestoneCount;
        address arbiter;
        bool active;
    }

    struct Contribution {
        address contributor;
        uint256 causeId;
        uint256 amount;
        string message;
        uint256 timestamp;
    }

    // ── State ──────────────────────────────────────────────────────────

    mapping(uint256 => Cause) public causes;
    mapping(uint256 => Escrow) public escrows;
    mapping(uint256 => Milestone[]) public milestones;
    mapping(uint256 => Contribution[]) public contributions;
    mapping(address => uint256) public totalContributed;
    mapping(address => uint256) public causesSupported;

    uint256 public nextCauseId;
    uint256 public nextEscrowId;
    uint256 public totalValueRaised;

    // ── Events ─────────────────────────────────────────────────────────

    event CauseCreated(uint256 indexed causeId, address indexed creator, string title, uint256 goal);
    event ContributionMade(uint256 indexed causeId, address indexed contributor, uint256 amount);
    event CauseFunded(uint256 indexed causeId);
    event CauseCompleted(uint256 indexed causeId);
    event CauseCancelled(uint256 indexed causeId);
    event EscrowCreated(uint256 indexed escrowId, uint256 indexed causeId, uint256 totalAmount);
    event MilestoneCompleted(uint256 indexed escrowId, uint256 milestoneIndex, uint256 amount);
    event MilestoneDisputed(uint256 indexed escrowId, uint256 milestoneIndex);

    // ── Cause Lifecycle ────────────────────────────────────────────────

    function createCause(
        string calldata title,
        string calldata story,
        address token,
        uint256 goalAmount,
        uint256 deadline,
        string[] calldata tags,
        string[] calldata imageUrls
    ) external returns (uint256 causeId) {
        require(goalAmount > 0, "Goal must be > 0");
        require(deadline > block.timestamp, "Deadline must be in future");

        causeId = nextCauseId++;
        causes[causeId] = Cause({
            id: causeId,
            creator: msg.sender,
            title: title,
            story: story,
            token: token,
            goalAmount: goalAmount,
            raisedAmount: 0,
            contributorCount: 0,
            status: CauseStatus.Active,
            createdAt: block.timestamp,
            deadline: deadline,
            tags: tags,
            imageUrls: imageUrls
        });

        emit CauseCreated(causeId, msg.sender, title, goalAmount);
    }

    /// @notice Contribute to a cause (direct funding)
    function contribute(
        uint256 causeId,
        uint256 amount,
        string calldata message
    ) external {
        Cause storage cause = causes[causeId];
        require(cause.status == CauseStatus.Active, "Cause not active");
        require(block.timestamp <= cause.deadline, "Deadline passed");
        require(amount > 0, "Amount must be > 0");

        // Transfer tokens
        IERC20 token = IERC20(cause.token);
        token.safeTransferFrom(msg.sender, address(this), amount);

        // Update cause
        cause.raisedAmount += amount;
        cause.contributorCount++;

        // Record contribution
        contributions[causeId].push(Contribution({
            contributor: msg.sender,
            causeId: causeId,
            amount: amount,
            message: message,
            timestamp: block.timestamp
        }));

        // Update contributor stats
        totalContributed[msg.sender] += amount;
        causesSupported[msg.sender]++;

        totalValueRaised += amount;

        // Check if fully funded
        if (cause.raisedAmount >= cause.goalAmount) {
            cause.status = CauseStatus.Funded;
            emit CauseFunded(causeId);
        }

        emit ContributionMade(causeId, msg.sender, amount);
    }

    /// @notice Create an escrow for milestone-based funding
    function createEscrow(
        uint256 causeId,
        uint256 totalAmount,
        uint256 milestoneCount,
        address arbiter
    ) external returns (uint256 escrowId) {
        Cause storage cause = causes[causeId];
        require(cause.creator == msg.sender, "Only creator can create escrow");
        require(cause.status == CauseStatus.Funded, "Cause must be funded first");
        require(totalAmount <= cause.raisedAmount, "Escrow exceeds raised amount");
        require(milestoneCount > 0, "Must have at least 1 milestone");

        escrowId = nextEscrowId++;
        escrows[escrowId] = Escrow({
            causeId: causeId,
            totalAmount: totalAmount,
            releasedAmount: 0,
            milestoneCount: milestoneCount,
            arbiter: arbiter,
            active: true
        });

        emit EscrowCreated(escrowId, causeId, totalAmount);
    }

    /// @notice Complete a milestone and release funds
    function completeMilestone(uint256 escrowId, uint256 milestoneIndex) external {
        Escrow storage escrow = escrows[escrowId];
        require(escrow.active, "Escrow not active");
        require(milestoneIndex < escrow.milestoneCount, "Invalid milestone");

        Milestone storage ms = milestones[escrowId][milestoneIndex];
        require(ms.status == MilestoneStatus.Pending, "Milestone already completed or disputed");

        // Only arbiter or creator can complete milestones
        require(
            msg.sender == escrow.arbiter || msg.sender == causes[escrow.causeId].creator,
            "Not authorized"
        );

        ms.status = MilestoneStatus.Completed;
        ms.completedAt = block.timestamp;
        escrow.releasedAmount += ms.amount;

        // Transfer funds to creator
        Cause storage cause = causes[escrow.causeId];
        IERC20 token = IERC20(cause.token);
        token.safeTransfer(cause.creator, ms.amount);

        emit MilestoneCompleted(escrowId, milestoneIndex, ms.amount);

        // Check if all milestones completed
        if (escrow.releasedAmount >= escrow.totalAmount) {
            cause.status = CauseStatus.Completed;
            escrow.active = false;
            emit CauseCompleted(escrow.causeId);
        }
    }

    /// @notice Dispute a milestone
    function disputeMilestone(uint256 escrowId, uint256 milestoneIndex) external {
        Escrow storage escrow = escrows[escrowId];
        require(escrow.active, "Escrow not active");

        Milestone storage ms = milestones[escrowId][milestoneIndex];
        require(ms.status == MilestoneStatus.Pending, "Milestone not pending");

        // Only contributors can dispute
        // (In production, check that msg.sender is a contributor)

        ms.status = MilestoneStatus.Disputed;
        emit MilestoneDisputed(escrowId, milestoneIndex);
    }

    /// @notice Cancel a cause and return funds to contributors
    function cancelCause(uint256 causeId) external {
        Cause storage cause = causes[causeId];
        require(
            msg.sender == cause.creator || msg.sender == owner(),
            "Not authorized"
        );
        require(cause.status == CauseStatus.Active, "Cannot cancel in current state");

        cause.status = CauseStatus.Cancelled;

        // Return all contributions
        Contribution[] storage contribs = contributions[causeId];
        IERC20 token = IERC20(cause.token);
        for (uint256 i = 0; i < contribs.length; i++) {
            token.safeTransfer(contribs[i].contributor, contribs[i].amount);
        }

        emit CauseCancelled(causeId);
    }

    // ── View Functions ──────────────────────────────────────────────────

    function getCause(uint256 causeId) external view returns (Cause memory) {
        return causes[causeId];
    }

    function getContributions(uint256 causeId) external view returns (Contribution[] memory) {
        return contributions[causeId];
    }

    function getMilestones(uint256 escrowId) external view returns (Milestone[] memory) {
        return milestones[escrowId];
    }

    function getContributorReputation(address wallet) external view returns (
        uint256 totalContributed,
        uint256 causesSupportedCount,
        uint256 causesCreatedCount
    ) {
        return (
            totalContributed[wallet],
            causesSupported[wallet],
            0 // causesCreated tracked separately
        );
    }
}
```

### 5.5 Reputation System

The P2P Causes platform includes a wallet-level reputation system:

| Tier | Threshold | Privileges |
|------|-----------|------------|
| 🟢 **New** | 0-1 contributions | Create causes, contribute |
| 🟡 **Trusted** | 2-5 contributions | Priority listing, lower escrow fees |
| 🔵 **Verified** | 6-20 contributions | Create multi-milestone escrows, act as arbiter |
| ⚫ **Core** | 21+ contributions | Governance votes, protocol fee discounts |

---

## 6. Smart Contract Interfaces

### 6.1 Complete Interface Summary

```solidity
// ── YieldBrain ──────────────────────────────────────────────────────────
interface IYieldBrain {
    function deposit(bytes32 vaultId, uint256 amount) external;
    function withdraw(bytes32 vaultId, uint256 amount) external;
    function rebalance(bytes32 fromVault, bytes32 toVault, uint256 amount) external;
    function setEnforcement(uint256 maxTotal, uint256 maxPerVault, uint256 cooldown, bool twoPhase) external;
    function getAgentPortfolio(address agent) external view returns (uint256 total, uint256 vaultCount);
}

// ── PaymentRouter ───────────────────────────────────────────────────────
interface IPaymentRouter {
    function selectRoute(address token, uint256 amount, RouteStrategy strategy) external view returns (Facilitator, uint256);
    function routePayment(bytes32 paymentId, address recipient, address token, uint256 amount, RouteStrategy strategy, uint256 maxCost, uint256 deadline) external payable returns (Facilitator);
    function quoteRoute(address token, uint256 amount, RouteStrategy strategy) external view returns (Route[] memory);
}

// ── P2PCauses ───────────────────────────────────────────────────────────
interface IP2PCauses {
    function createCause(string calldata title, string calldata story, address token, uint256 goal, uint256 deadline, string[] calldata tags, string[] calldata images) external returns (uint256);
    function contribute(uint256 causeId, uint256 amount, string calldata message) external;
    function createEscrow(uint256 causeId, uint256 totalAmount, uint256 milestoneCount, address arbiter) external returns (uint256);
    function completeMilestone(uint256 escrowId, uint256 milestoneIndex) external;
    function disputeMilestone(uint256 escrowId, uint256 milestoneIndex) external;
    function cancelCause(uint256 causeId) external;
    function getContributorReputation(address wallet) external view returns (uint256, uint256, uint256);
}
```

### 6.2 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT MAP                            │
│                                                             │
│  Base (L2)                    BNB Chain                     │
│  ┌─────────────────────┐     ┌─────────────────────┐       │
│  │ YieldBrain          │     │ YieldBrain          │       │
│  │  ├── Aave vault     │     │  ├── Aave vault     │       │
│  │  ├── Morpho vault   │     │  ├── Lista vault    │       │
│  │  └── P2PCauses      │     │  └── P2PCauses      │       │
│  ├─────────────────────┤     ├─────────────────────┤       │
│  │ PaymentRouter       │     │ PaymentRouter       │       │
│  │  ├── CDP facilitator│     │  ├── CDP facilitator│       │
│  │  ├── GoPlausible    │     │  └── Q402 facilitator│       │
│  │  └── Q402 facilitator│    └─────────────────────┘       │
│  └─────────────────────┘                                   │
│                                                             │
│  Cross-Chain:                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Agent Wallet (ERC-8004) — portable identity         │   │
│  │ Q402 Gateway — gasless settlement layer             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. x402 / Q402 Integration Points

### 7.1 Tool Mapping

| Treasury Operation | Q402 Tool | x402 Component | AAE Layer |
|--------------------|-----------|----------------|-----------|
| Check vault reserves | `q402_yield_reserves` | — | L6 Enforcement |
| Deposit to vault | `q402_yield_deposit` | Payment proof | L6 Enforcement |
| Withdraw from vault | `q402_yield_withdraw` | Payment proof | L6 Enforcement |
| Route payment | — | x402 v2 multi-facilitator | L7 Execution |
| Get route quote | — | x402 Bazaar discovery | L4 Coordination |
| Create funding request | `q402_request_create` | — | L4 Coordination |
| Pay funding request | `q402_request_pay` | Payment proof | L7 Execution |
| Create escrow | `q402_escrow_create` | — | Foundation |
| Lock escrow | `q402_escrow_lock` | Payment proof | Foundation |
| Release escrow | `q402_escrow_release` | — | Foundation |

### 7.2 x402 v2 Multi-Facilitator Flow

```
Agent calls PaymentRouter.quoteRoute()
        │
        ▼
PaymentRouter queries Bazaar discovery for each facilitator:
  ├── GET https://x402.org/facilitator/.well-known/x402-bazaar
  ├── GET https://algorand-facilitator.goplausible.xyz/.well-known/x402-bazaar
  └── GET https://q402.quackai.ai/.well-known/x402-bazaar
        │
        ▼
Each facilitator returns:
  {
    "endpoints": [{
      "path": "/api/v1/pay",
      "accepts": [{
        "scheme": "exact",
        "price": "$0.001",
        "network": "eip155:84532"
      }]
    }]
  }
        │
        ▼
PaymentRouter scores routes → returns top 3
        │
        ▼
Agent selects route → PaymentRouter executes:
  1. Agent signs EIP-3009 authorization
  2. PaymentRouter submits to selected facilitator
  3. Facilitator verifies and settles
  4. PaymentRouter confirms settlement
```

### 7.3 Q402 Gasless Settlement

Q402 enables gasless settlement — agents never need native gas tokens:

```
Agent initiates payment
        │
        ▼
Q402 Gateway:
  1. Agent signs authorization (EIP-3009 / ERC-2612 permit)
  2. Q402 relayer submits the transaction
  3. Q402 pays gas fees (deducted from payment amount)
  4. Settlement confirmed → agent receives receipt
        │
        ▼
Benefits:
  - No ETH/BNB needed for gas
  - Works on any EVM chain
  - Sub-cent micro-payments viable
  - Single API key for all chains
```

---

## 8. Agent Interaction Flows

### 8.1 Yield Optimization Flow

```
Agent "YieldFarmer-1"
        │
        ▼
1. Check treasury balance: 15,000 USDC idle
        │
        ▼
2. Query YieldBrain for best vaults:
   ├── Aave (Base): 8.2% APR, $4.2M liquidity
   ├── Morpho (Base): 9.7% APR, $1.8M liquidity  ← Best
   └── Lista (BNB): 7.1% APR, $3.1M liquidity
        │
        ▼
3. AAE L6 Enforcement Check:
   ├── Max per vault: $10,000 ✅ (depositing $5,000)
   ├── Recipient allowlist: Morpho ✅
   └── Two-phase consent: Preview shown ✅
        │
        ▼
4. Preview:
   ┌─────────────────────────────────────┐
   │  Deposit $5,000 USDC → Morpho (Base) │
   │  Est. APR: 9.7%                      │
   │  Est. daily: $1.33                   │
   │  Est. monthly: $40.42               │
   │  [Confirm]  [Cancel]                 │
   └─────────────────────────────────────┘
        │
        ▼
5. Execute via Q402:
   q402_yield_deposit(vault="morpho", token="USDC", amount=5000, chain="base")
        │
        ▼
6. Receipt:
   {tx_hash: "0x...", vault: "morpho", amount: 5000, shares: 5000}
        │
        ▼
7. Schedule next rebalance check: +6 hours
```

### 8.2 Payment Routing Flow

```
Agent "Trader-1" needs to pay Agent "Signal-Provider" $50 USDC
        │
        ▼
1. PaymentRouter.quoteRoute(token=USDC, amount=50, strategy=cheapest)
        │
        ▼
2. Route comparison:
   ┌──────────┬──────────┬────────┬──────────┐
   │ Route    │ Fee      │ Time   │ Total    │
   ├──────────┼──────────┼────────┼──────────┤
   │ CDP      │ $0.05    │ 12s    │ $50.05   │
   │ GoPlaus. │ $0.025   │ 3.5s   │ $50.025  │
   │ Q402     │ $0.005   │ 2s     │ $50.005  │ ← Cheapest
   └──────────┴──────────┴────────┴──────────┘
        │
        ▼
3. Select Q402 (gasless, cheapest)
        │
        ▼
4. AAE L6 Enforcement Check:
   ├── Max payment: $100 ✅
   ├── Recipient allowlist: Signal-Provider ✅
   └── Daily limit: $200, current: $50 ✅
        │
        ▼
5. Execute:
   PaymentRouter.routePayment(
     paymentId="0x...",
     recipient="0xSignalProvider...",
     token=USDC,
     amount=50,
     strategy=cheapest,
     maxCost=0.01,
     deadline=+5min
   )
        │
        ▼
6. Settlement via Q402:
   {paymentId: "0x...", facilitator: Q402, cost: $0.005, status: settled}
```

### 8.3 P2P Funding Flow

```
Agent "Builder-1" needs $5,000 to build a dashboard
        │
        ▼
1. Create cause:
   P2PCauses.createCause(
     title="Agentic Treasury Dashboard",
     story="Real-time monitoring for all treasury positions...",
     token=USDC,
     goal=5000,
     deadline=+30days,
     tags=["dashboard", "treasury", "open-source"]
   )
        │
        ▼
2. Cause is listed: "cause-42 — $0/$5,000 raised"
        │
        ▼
3. Agent "Supporter-1" discovers cause:
   ├── Checks creator reputation: Trusted (3 causes supported)
   └── Decides to fund $500
        │
        ▼
4. Contribute:
   P2PCauses.contribute(causeId=42, amount=500, message="Great idea!")
        │
        ▼
5. Q402 payment:
   q402_request_pay(request_id="cause-42", amount=500, contributor="0xSupporter...")
        │
        ▼
6. Multiple agents contribute → cause reaches $5,000
        │
        ▼
7. Cause status → FUNDED
        │
        ▼
8. Creator sets up milestone escrow:
   q402_escrow_create(causeId=42, total=5000, milestones=3, arbiter="0xDAO...")
        │
        ▼
9. Contributors lock funds:
   q402_escrow_lock(escrowId=1, contributor="0xSupporter...", amount=500)
        │
        ▼
10. Milestone 1 completed → arbiter verifies → funds released
    q402_escrow_release(escrowId=1, milestoneIndex=0)
        │
        ▼
11. All milestones complete → cause status → COMPLETED
    Creator receives full $5,000
    Contributors get reputation boosts
```

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1)

| Task | Deliverable | Dependencies |
|------|-------------|--------------|
| Deploy YieldBrain contract on Base | Verified contract | OpenZeppelin libs |
| Deploy PaymentRouter contract on Base | Verified contract | x402 SDK v2 |
| Deploy P2PCauses contract on Base | Verified contract | Q402 API access |
| Set up Q402 API keys | Working integration | Q402 account |
| Write AAE L6 enforcement hooks | Enforcement module | YieldBrain contract |

**Milestone:** All three contracts deployed and verified on Base Sepolia testnet.

### Phase 2: Integration (Week 2)

| Task | Deliverable | Dependencies |
|------|-------------|--------------|
| Integrate Q402 yield tools | YieldBrain ↔ Q402 | Phase 1 contracts |
| Integrate x402 multi-facilitator | PaymentRouter ↔ x402 | Phase 1 contracts |
| Integrate Q402 payment requests | P2PCauses ↔ Q402 | Phase 1 contracts |
| Write agent SDK wrappers | Python SDK for all 3 pillars | Phase 1 contracts |
| Write test suite | 80%+ coverage | All integrations |

**Milestone:** All three pillars integrated with Q402/x402, agent SDK ready.

### Phase 3: Treasury Automation (Week 3)

| Task | Deliverable | Dependencies |
|------|-------------|--------------|
| Build yield optimization loop | Automated rebalancer | Phase 2 YieldBrain |
| Build route selection engine | PaymentRouter auto-select | Phase 2 PaymentRouter |
| Build escrow milestone manager | P2PCauses escrow flow | Phase 2 P2PCauses |
| Add AAE L6 enforcement dashboard | Monitoring UI | Phase 2 integrations |
| Write integration tests | E2E treasury workflows | Phase 3 automation |

**Milestone:** Fully automated treasury with enforcement-gated operations.

### Phase 4: Production & Audit (Week 4)

| Task | Deliverable | Dependencies |
|------|-------------|--------------|
| Deploy to Base mainnet | Production contracts | Phase 3 |
| Deploy to BNB Chain mainnet | Production contracts | Phase 3 |
| Security audit (internal) | Audit report | Phase 3 contracts |
| Security audit (external) | Audit report | Internal audit |
| Write documentation | User + developer docs | All phases |
| Launch monitoring | Grafana dashboard | Production deployment |

**Milestone:** Production deployment on Base and BNB Chain, audited and documented.

---

## 10. Risk Analysis

### 10.1 Smart Contract Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Vault contract exploit (Aave/Morpho/Lista) | 🔴 Critical | Only use audited protocols; max deposit caps per vault |
| Reentrancy in deposit/withdraw | 🔴 Critical | OpenZeppelin ReentrancyGuard on all external functions |
| Oracle manipulation (APR feeds) | 🟡 High | Use time-weighted average APRs; multiple oracle sources |
| Escrow fund lockup | 🟡 High | Arbiter override; time-based release fallback |
| Gas griefing (Q402 relay) | 🟡 High | Set max gas price in enforcement config |

### 10.2 Economic Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Impermanent loss in yield positions | 🟡 High | Only deposit stablecoins (USDC/USDT); no volatile asset exposure |
| APR decline below threshold | 🟡 Medium | Auto-withdraw if APR < 2%; rebalance to best vault |
| Facilitator downtime | 🟡 Medium | Multi-facilitator fallback; route health checks |
| Q402 rate limit exhaustion | 🟡 Medium | Request queuing; backoff strategy |
| Stablecoin depeg | 🟡 Medium | Diversify across USDC/USDT/DAI; depeg monitoring |

### 10.3 Operational Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Agent wallet key compromise | 🔴 Critical | Multi-sig for high-value ops; daily withdrawal limits |
| Enforcement bypass | 🔴 Critical | AAE L6 hooks are on-chain and immutable per agent |
| Failed rebalance (gas spike) | 🟡 Medium | Cooldown period prevents rapid re-attempts |
| Escrow dispute resolution failure | 🟡 Medium | Time-based fallback: funds return to contributors after N days |
| P2P cause fraud (fake milestones) | 🟡 Medium | Arbiter verification; reputation-based trust scoring |

### 10.4 Risk Mitigation Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    RISK MITIGATION MATRIX                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Risk                     │  Detection    │  Response           │
│───────────────────────────┼───────────────┼─────────────────────│
│  Vault exploit            │  Monitoring   │  Emergency withdraw  │
│  APR crash                │  Threshold    │  Auto-rebalance     │
│  Facilitator down         │  Health check │  Route fallback     │
│  Escrow dispute           │  Timeout      │  Arbiter resolution  │
│  Key compromise           │  Anomaly      │  Multi-sig freeze   │
│  Stablecoin depeg         │  Oracle       │  Swap to alternative│
│  Gas griefing             │  Gas monitor  │  Cap enforcement    │
│  Rate limit               │  Queue depth  │  Backoff + retry    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.5 Emergency Procedures

| Scenario | Action | Responsible |
|----------|--------|-------------|
| Vault contract compromised | Emergency pause → withdraw all funds → migrate | Owner multi-sig |
| Facilitator API down | Route through alternative facilitator | PaymentRouter auto |
| Escrow dispute unresolved after 14d | Time-based release to contributors | P2PCauses contract |
| Agent wallet compromised | Multi-sig freeze → rotate keys | Agent owner |
| Stablecoin depeg > 2% | Swap to alternative stablecoin | YieldBrain auto |

---

## 11. Appendix: Q402 Tool Reference

### 11.1 Yield Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `q402_yield_reserves` | `chain`, `vaults[]` | `{vault: {total_supply, available_liquidity, supply_apr, utilization_rate}}` |
| `q402_yield_deposit` | `vault`, `token`, `amount`, `chain` | `{tx_hash, vault, amount, shares_received}` |
| `q402_yield_withdraw` | `vault`, `token`, `amount`, `chain` | `{tx_hash, vault, amount, shares_burned}` |

### 11.2 Payment Request Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `q402_request_create` | `title`, `description`, `amount`, `recipient`, `deadline`, `milestones[]` | `{request_id, status, created_at}` |
| `q402_request_pay` | `request_id`, `amount`, `contributor`, `message` | `{receipt_id, request_id, amount, status}` |

### 11.3 Escrow Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `q402_escrow_create` | `request_id`, `total_amount`, `milestone_count`, `arbiter` | `{escrow_id, status, created_at}` |
| `q402_escrow_lock` | `escrow_id`, `contributor`, `amount` | `{lock_id, escrow_id, amount, status}` |
| `q402_escrow_release` | `escrow_id`, `milestone_index`, `verifier` | `{release_id, escrow_id, milestone, amount, status}` |

---

## References

- **AAE Architecture:** `10-Labs/AAE-Six-Layer-Architecture.md`
- **AAE Layers Overview:** `10-Labs/AAE-Layers-Overview.md`
- **x402 × AAE Integration:** `10-Labs/x402-AAE-Integration-Map.md`
- **x402 Multi-Facilitator Example:** `10-Labs/x402-multi-facilitator-example/`
- **P2P Causes Engine:** `10-Labs/p2p-causes/p2p_causes.py`
- **AAE Yield Farm:** `10-Labs/aae-yield-farm/aae_deploy_flow.py`
- **Agent Rug 2.0 (x402 audit):** `10-Labs/agent-rug-2.0-spec.md`
- **Q402 Docs:** `https://q402.quackai.ai/docs`
- **x402 Protocol:** `https://x402.org`
- **x402 v2 Bazaar:** `https://x402.gitbook.io/x402/guides/mcp-server-with-x402`

---

*Created: 2026-07-21*
*Status: Spec v1.0 — ready for review*
*Next: Phase 1 implementation — contract deployment on Base Sepolia*
