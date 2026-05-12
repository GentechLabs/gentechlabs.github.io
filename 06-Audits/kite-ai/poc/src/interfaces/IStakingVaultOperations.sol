// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

/// @dev Minimal interface for StakingVaultOperations
/// @notice Only includes functions we call in PoCs
interface IStakingVaultOperations {
    function forceClaimOperatorFees(address operator) external;
    function claimOperatorFees() external;
    function setOperatorFeeRecipient(address feeRecipient) external;
    
    // Events
    event OperatorFeesClaimed(address indexed operator, uint256 amount);
    event OperatorFeesForfeited(address indexed operator, uint256 amount);
}
