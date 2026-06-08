// (c) 2024, Ava Labs, Inc. All rights reserved.
// See the file LICENSE for licensing terms.

// SPDX-License-Identifier: LicenseRef-Ecosystem

pragma solidity 0.8.25;

import {IRewardCalculator} from "./interfaces/IRewardCalculator.sol";
import {Ownable2Step, Ownable} from "@openzeppelin/contracts@5.0.2/access/Ownable2Step.sol";

/**
 * @title FixedAPRRewardCalculator
 * @notice A reward calculator that provides a fixed APR (Annual Percentage Rate)
 * based on actual uptime. Uses simple interest (no compounding).
 *
 * ## Linear Reward Model
 *
 * Rewards are calculated proportionally to actual uptime:
 * - reward = stakeAmount * APR * periodUptimeSeconds / SECONDS_IN_YEAR
 * - No minimum uptime threshold - validators earn rewards for any uptime
 * - This ensures fair compensation: more uptime = more rewards
 */
contract FixedAPRRewardCalculator is IRewardCalculator, Ownable2Step {
    uint256 public constant SECONDS_IN_YEAR = 31536000;

    uint16 public constant BIPS_CONVERSION_FACTOR = 10000;

    /// @notice Maximum allowed reward basis points (100% APR = 10000 basis points)
    uint64 public constant MAX_REWARD_BASIS_POINTS = 10000;

    /// @notice The reward rate in basis points (e.g., 500 = 5% APR)
    uint64 public rewardBasisPoints;

    /// @notice Emitted when the reward basis points is updated
    event RewardBasisPointsUpdated(uint64 oldBasisPoints, uint64 newBasisPoints);

    /// @notice Error thrown when reward basis points is zero
    error ZeroRewardBasisPoints();

    /// @notice Error thrown when reward basis points exceeds maximum
    error RewardBasisPointsExceedsMax(uint64 provided, uint64 maximum);

    constructor(uint64 rewardBasisPoints_, address initialOwner) Ownable(initialOwner) {
        if (rewardBasisPoints_ == 0) {
            revert ZeroRewardBasisPoints();
        }
        if (rewardBasisPoints_ > MAX_REWARD_BASIS_POINTS) {
            revert RewardBasisPointsExceedsMax(rewardBasisPoints_, MAX_REWARD_BASIS_POINTS);
        }
        rewardBasisPoints = rewardBasisPoints_;
    }

    /**
     * @notice Updates the reward basis points
     * @param newRewardBasisPoints The new reward rate in basis points
     */
    function setRewardBasisPoints(uint64 newRewardBasisPoints) external onlyOwner {
        if (newRewardBasisPoints == 0) {
            revert ZeroRewardBasisPoints();
        }
        if (newRewardBasisPoints > MAX_REWARD_BASIS_POINTS) {
            revert RewardBasisPointsExceedsMax(newRewardBasisPoints, MAX_REWARD_BASIS_POINTS);
        }
        uint64 oldBasisPoints = rewardBasisPoints;
        rewardBasisPoints = newRewardBasisPoints;
        emit RewardBasisPointsUpdated(oldBasisPoints, newRewardBasisPoints);
    }

    /**
     * @notice Calculate incremental reward for claiming during active staking.
     * @dev This allows validators and delegators to claim rewards without ending their stake.
     *
     * Linear reward model - rewards are proportional to actual uptime:
     * - reward = stakeAmount * APR * periodUptimeSeconds / SECONDS_IN_YEAR
     * - No minimum uptime threshold required
     *
     * See {IRewardCalculator-calculateIncrementalReward}
     *
     * @param stakeAmount The amount of tokens staked
     * @param lastClaimTime The timestamp of the last reward claim (or staking start if first claim)
     * @param currentTime The current timestamp
     * @param lastClaimUptimeSeconds The uptime seconds at the last claim
     * @param currentUptimeSeconds The current uptime seconds
     * @param validatorStartTime The timestamp when the validator started (unused but kept for interface compatibility)
     * @return reward The calculated reward amount
     */
    function calculateIncrementalReward(
        uint256 stakeAmount,
        uint64 lastClaimTime,
        uint64 currentTime,
        uint64 lastClaimUptimeSeconds,
        uint64 currentUptimeSeconds,
        uint64 validatorStartTime
    ) external view returns (uint256 reward) {
        // Silence unused variable warning
        validatorStartTime;

        // Calculate the time period for this claim
        uint64 periodDuration = currentTime - lastClaimTime;
        if (periodDuration == 0) {
            return 0;
        }

        // Calculate uptime for this period
        uint64 periodUptimeSeconds = currentUptimeSeconds -
            lastClaimUptimeSeconds;

        // Linear reward: proportional to actual uptime
        // reward = stakeAmount * rewardBasisPoints * periodUptimeSeconds / (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR)
        return
            (stakeAmount * rewardBasisPoints * periodUptimeSeconds) /
            (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR);
    }
}
