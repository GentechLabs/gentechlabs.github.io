// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

/// @dev Minimal interface for FixedAPRRewardCalculator
/// @notice Only includes functions we call in PoCs
interface IFixedAPRRewardCalculator {
    function calculateIncrementalReward(
        uint256 stakeAmount,
        uint64 lastClaimTime,
        uint64 currentTime,
        uint64 lastClaimUptimeSeconds,
        uint64 currentUptimeSeconds,
        uint64 validatorStartTime
    ) external view returns (uint256 reward);
    
    function setRewardBasisPoints(uint64 newRewardBasisPoints) external;
    function rewardBasisPoints() external view returns (uint64);
    function owner() external view returns (address);
}
