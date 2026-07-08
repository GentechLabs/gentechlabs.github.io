// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

/// @dev Minimal interface for StakingVault
/// @notice Only includes functions and storage we access in PoCs
interface IStakingVault {
    function vaultAccountedBalance() external view returns (uint256);
    function totalAccruedOperatorFees() external view returns (uint256);
    function accrueOperatorFees(address operator) external;
    
    struct Operator {
        bool active;
        uint256 activeStake;
        uint256 accruedFees;
        address feeRecipient;
    }
    
    function operators(address operator) external view returns (Operator memory);
    
    // ERC20 functions
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}
