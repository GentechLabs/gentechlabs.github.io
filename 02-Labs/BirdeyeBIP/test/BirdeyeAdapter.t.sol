// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/BirdeyeAdapter.sol";

contract BirdeyeAdapterTest is Test {
    BirdeyeAdapter adapter;

    address oracle = makeAddr("oracle");
    address user1 = makeAddr("user1");

    // Mock Solana token addresses (as EVM addresses for testing)
    address SOL = address(0x1111);
    address USDC = address(0x2222);

    function setUp() public {
        adapter = new BirdeyeAdapter(address(0));
        adapter.grantRole(adapter.ORACLE_ROLE(), oracle);
    }

    // ═══════════════════════════════════════════
    //              BASIC DATA FEED
    // ═══════════════════════════════════════════

    function test_PushTokenData() public {
        vm.prank(oracle);

        // SOL at $145, $500M volume, $2B liquidity
        uint256 price = 145 * 1e8;
        uint256 volume = 500_000_000 * 1e8;
        uint256 liquidity = 2_000_000_000 * 1e8;

        adapter.pushTokenData(SOL, price, volume, liquidity);

        BirdeyeAdapter.TokenSnapshot memory snap = adapter.getTokenSnapshot(SOL);
        assertEq(snap.price, price);
        assertEq(snap.volume24h, volume);
        assertEq(snap.liquidity, liquidity);
        assertEq(snap.updatedAt, block.timestamp);
        assertFalse(snap.priceDown);
    }

    function test_PriceDirectionTracking() public {
        // Push initial price
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 150 * 1e8, 500e8, 2000e8);

        // Push lower price — should flag priceDown
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 140 * 1e8, 500e8, 2000e8);

        BirdeyeAdapter.TokenSnapshot memory snap = adapter.getTokenSnapshot(SOL);
        assertTrue(snap.priceDown);
        assertEq(snap.price, 140 * 1e8);
    }

    function test_PriceUpNotFlagged() public {
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 140 * 1e8, 500e8, 2000e8);

        vm.prank(oracle);
        adapter.pushTokenData(SOL, 150 * 1e8, 500e8, 2000e8);

        BirdeyeAdapter.TokenSnapshot memory snap = adapter.getTokenSnapshot(SOL);
        assertFalse(snap.priceDown);
    }

    function test_RevertNonOracle() public {
        vm.prank(user1);
        vm.expectRevert(BirdeyeAdapter.NotOracle.selector);
        adapter.pushTokenData(SOL, 150e8, 500e8, 2000e8);
    }

    // ═══════════════════════════════════════════
    //              LP RANGE MONITORING
    // ═══════════════════════════════════════════

    function test_RegisterLPPosition() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        BirdeyeAdapter.LPPosition memory pos = adapter.getLPPosition(posId);
        assertEq(pos.agent, user1);
        assertEq(pos.tokenA, SOL);
        assertEq(pos.tokenB, USDC);
        assertEq(pos.lowerPrice, 130 * 1e8);
        assertEq(pos.upperPrice, 160 * 1e8);
        assertTrue(pos.active);
    }

    function test_LPInRange() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        // Push price within range
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 145 * 1e8, 500e8, 2000e8);

        assertTrue(adapter.isLPInRange(posId));
    }

    function test_LPOutOfRange() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        // Push price above range
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 170 * 1e8, 500e8, 2000e8);

        assertFalse(adapter.isLPInRange(posId));
    }

    function test_LPBreachEvent() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        // Push price within range first
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 145 * 1e8, 500e8, 2000e8);

        // Now breach — expect event
        vm.expectEmit(true, true, false, true);
        emit IBirdeyeAdapter.LPRangeBreached(user1, SOL, 170 * 1e8, 130 * 1e8, 160 * 1e8);

        vm.prank(oracle);
        adapter.pushTokenData(SOL, 170 * 1e8, 500e8, 2000e8);
    }

    function test_LPBackInRangeResetsBreach() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        // In range
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 145 * 1e8, 500e8, 2000e8);

        // Breach
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 170 * 1e8, 500e8, 2000e8);
        assertFalse(adapter.isLPInRange(posId));

        // Back in range
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 150 * 1e8, 500e8, 2000e8);
        assertTrue(adapter.isLPInRange(posId));
    }

    function test_DeactivatePosition() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        vm.prank(user1);
        adapter.deactivatePosition(posId);

        BirdeyeAdapter.LPPosition memory pos = adapter.getLPPosition(posId);
        assertFalse(pos.active);
    }

    // ═══════════════════════════════════════════
    //              BATCH PROCESSING
    // ═══════════════════════════════════════════

    function test_ProcessDataBatch() public {
        address[] memory tokens = new address[](2);
        tokens[0] = SOL;
        tokens[1] = USDC;

        uint256[] memory prices = new uint256[](2);
        prices[0] = 145 * 1e8;
        prices[1] = 1e8;

        uint256[] memory volumes = new uint256[](2);
        volumes[0] = 500e8;
        volumes[1] = 1000e8;

        uint256[] memory liquidities = new uint256[](2);
        liquidities[0] = 2000e8;
        liquidities[1] = 5000e8;

        bytes memory data = abi.encode(tokens, prices, volumes, liquidities);

        vm.prank(oracle);
        adapter.processData(data);

        assertEq(adapter.getTokenSnapshot(SOL).price, 145 * 1e8);
        assertEq(adapter.getTokenSnapshot(USDC).price, 1e8);
        assertEq(adapter.totalDataPushes(), 2);
    }

    // ═══════════════════════════════════════════
    //              EDGE CASES
    // ═══════════════════════════════════════════

    function test_StaleDataIgnoredInRange() public {
        vm.prank(user1);
        uint256 posId = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 160 * 1e8);

        // Push initial data
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 145 * 1e8, 500e8, 2000e8);

        // Warp 20 minutes (past 15 min threshold)
        vm.warp(block.timestamp + 20 minutes);

        // Stale data should not trigger breach alarm
        assertTrue(adapter.isLPInRange(posId));
    }

    function test_MultiplePositionsOnSameToken() public {
        vm.prank(user1);
        uint256 pos1 = adapter.registerLPPosition(SOL, USDC, 130 * 1e8, 150 * 1e8);

        vm.prank(user1);
        uint256 pos2 = adapter.registerLPPosition(SOL, USDC, 140 * 1e8, 170 * 1e8);

        // Push price 155 — breaches pos1 upper, in range for pos2
        vm.prank(oracle);
        adapter.pushTokenData(SOL, 155 * 1e8, 500e8, 2000e8);

        assertFalse(adapter.isLPInRange(pos1));
        assertTrue(adapter.isLPInRange(pos2));
        assertEq(adapter.totalBreachesDetected(), 1);
    }

    function test_AdapterName() public {
        assertEq(adapter.adapterName(), "Birdeye");
    }
}
