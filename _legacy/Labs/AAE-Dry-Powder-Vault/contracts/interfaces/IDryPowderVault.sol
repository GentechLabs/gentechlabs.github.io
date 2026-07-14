// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IDryPowderVault
 * @notice Interface for the Dry Powder Vault contract.
 */
interface IDryPowderVault {
    enum Chain { Base, Avalanche, Solana }

    struct ChainBalance {
        uint256 deposited;
        uint256 yield;
        uint256 locked;
        uint8  status;
    }

    event Deposit(address indexed user, uint256 amount, uint256 shares);
    event Withdraw(address indexed user, uint256 shares, uint256 amount);
    event BridgeInitiated(uint256 indexed id, address indexed user, Chain fromChain, Chain toChain, uint256 amount, uint256 fee);
    event BridgeCompleted(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount);
    event RotationProposed(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount, string reason);
    event RotationExecuted(uint256 indexed id, Chain fromChain, Chain toChain, uint256 amount);
    event YieldReported(Chain indexed chain, uint256 yieldAmount, uint256 totalYield);

    function deposit(uint256 amount) external;
    function withdraw(uint256 amount) external;
    function totalAssets() external view returns (uint256);
    function balanceOf(address user) external view returns (uint256);
    function initiateBridge(address user, Chain fromChain, Chain toChain, uint256 amount) external returns (uint256);
    function completeBridge(uint256 id) external;
    function proposeRotation(Chain fromChain, Chain toChain, uint256 amount, string calldata reason) external returns (uint256);
    function approveRotation(uint256 id) external;
    function executeRotation(uint256 id) external;
    function reportYield(Chain chain_, uint256 amount) external;
    function getChainBalance(Chain chain_) external view returns (ChainBalance memory);
    function getUSDCBalance() external view returns (uint256);
}
