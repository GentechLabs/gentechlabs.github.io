// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/PortfolioManager.sol";

contract PortfolioManagerTest is Test {
    PortfolioManager public pm;
    address public owner = address(this);
    address public oracle = address(0xBEEF);
    address public agent = address(0xCAFE);
    address public paymaster = address(0xFACE);

    // Local aliases for events
    event RegimeChanged(PortfolioManager.Regime oldRegime, PortfolioManager.Regime newRegime);
    event RebalanceExecuted(
        uint256 timestamp,
        PortfolioManager.Regime regime,
        uint256 totalBefore,
        uint256 totalAfter,
        int256 profitLoss
    );

    function setUp() public {
        pm = new PortfolioManager(paymaster);
        pm.setOracle(oracle);
        pm.authorizeAgent(agent);
    }

    function test_initial_state() public view {
        assertEq(pm.owner(), owner);
        assertEq(pm.oracle(), oracle);
        (, , uint256 totalValue, , ) = pm.portfolio();
        assertEq(totalValue, 0);
    }

    function test_update_regime() public {
        vm.prank(oracle);
        vm.expectEmit();
        emit RegimeChanged(
            PortfolioManager.Regime.RANGE_BOUND, PortfolioManager.Regime.BULL_TRENDING);
        pm.updateRegime(PortfolioManager.Regime.BULL_TRENDING, 85);

        (PortfolioManager.Regime regime, , , , ) = pm.portfolio();
        assertEq(uint(regime), uint(PortfolioManager.Regime.BULL_TRENDING));
    }

    function test_rebalance_requires_authorization() public {
        address[] memory tokens = new address[](2);
        uint256[] memory bps = new uint256[](2);
        tokens[0] = address(0x1111);
        tokens[1] = address(0x2222);
        bps[0] = 6000;
        bps[1] = 4000;

        vm.prank(address(0xDEAD));
        vm.expectRevert(PortfolioManager.NotAuthorized.selector);
        pm.rebalance(tokens, bps, block.timestamp + 1 hours);
    }

    function test_rebalance_valid() public {
        address[] memory tokens = new address[](3);
        uint256[] memory bps = new uint256[](3);
        tokens[0] = address(0x1111);
        tokens[1] = address(0x2222);
        tokens[2] = address(0x3333);
        bps[0] = 6000;
        bps[1] = 2000;
        bps[2] = 2000;

        vm.warp(block.timestamp + 2 hours); // Past 1-hour cooldown
        vm.prank(agent);
        vm.expectEmit();
        emit RebalanceExecuted(
            block.timestamp, PortfolioManager.Regime.RANGE_BOUND, 0, 0, 0
        );
        pm.rebalance(tokens, bps, block.timestamp + 1 hours);

        (, , , uint256 count, ) = pm.portfolio();
        assertEq(count, 1);
    }

    function test_rebalance_invalid_bps() public {
        address[] memory tokens = new address[](2);
        uint256[] memory bps = new uint256[](2);
        tokens[0] = address(0x1111);
        tokens[1] = address(0x2222);
        bps[0] = 6000;
        bps[1] = 3000; // Only 90%, not 100%

        vm.warp(block.timestamp + 2 hours); // Past 1-hour cooldown
        vm.prank(agent);
        vm.expectRevert(PortfolioManager.InvalidAllocation.selector);
        pm.rebalance(tokens, bps, block.timestamp + 1 hours);
    }

    function test_deposit() public {
        vm.prank(agent);
        pm.deposit(1000e6); // 1000 USDC

        (, , uint256 totalValue, , ) = pm.portfolio();
        assertEq(totalValue, 1000e6);
    }

    function test_withdraw_only_owner() public {
        vm.prank(agent);
        pm.deposit(1000e6);

        vm.prank(address(0xDEAD));
        vm.expectRevert(PortfolioManager.NotOwner.selector);
        pm.withdraw(500e6);
    }

    function test_regime_allocation_profiles() public view {
        uint256[] memory bull = pm.getRegimeAllocation(PortfolioManager.Regime.BULL_TRENDING);
        assertEq(bull[0], 6000); // 60% risk
        assertEq(bull[1], 2000); // 20% yield
        assertEq(bull[2], 2000); // 20% stable

        uint256[] memory bear = pm.getRegimeAllocation(PortfolioManager.Regime.BEAR_TRENDING);
        assertEq(bear[0], 1000); // 10% risk
        assertEq(bear[1], 3000); // 30% yield
        assertEq(bear[2], 6000); // 60% stable
    }
}
