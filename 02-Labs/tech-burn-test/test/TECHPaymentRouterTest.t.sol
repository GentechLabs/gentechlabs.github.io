// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/MockTECH.sol";
import "../src/TECHPaymentRouter.sol";
import "../src/MockOracle.sol";

/// @title TECHPaymentRouterTest — Full test suite for dynamic burn/recycle mechanism
contract TECHPaymentRouterTest is Test {
    MockTECH tech;
    TECHPaymentRouter router;
    MockOracle oracle;

    address treasury = makeAddr("treasury");
    address user1 = makeAddr("user1");
    address user2 = makeAddr("user2");

    uint256 constant ONE_ETHER = 1e18;
    uint256 constant BURN_ADDR_BALANCE_SLOT = 0; // not used, we check balance directly

    function setUp() public {
        tech = new MockTECH();
        // Start: 50% burn, 25% discount
        router = new TECHPaymentRouter(
            address(tech),
            treasury,
            5000, // 50% burn
            2500  // 25% discount
        );
        oracle = new MockOracle(1e18); // $1 per $TECH

        // Mint tokens to users
        tech.mint(user1, 1000 * ONE_ETHER);
        tech.mint(user2, 1000 * ONE_ETHER);

        // Approve router
        vm.prank(user1);
        tech.approve(address(router), type(uint256).max);
        vm.prank(user2);
        tech.approve(address(router), type(uint256).max);
    }

    // ================================================================
    // CORE FUNCTIONALITY
    // ================================================================

    function test_basicPayment_50_50_split() public {
        uint256 payment = 100 * ONE_ETHER;
        uint256 burnAddrBefore = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        uint256 treasuryBefore = tech.balanceOf(treasury);

        vm.prank(user1);
        router.processPayment(payment);

        // 50% burned, 50% to treasury
        assertEq(
            tech.balanceOf(0x000000000000000000000000000000000000dEaD) - burnAddrBefore,
            50 * ONE_ETHER,
            "Should burn 50%"
        );
        assertEq(
            tech.balanceOf(treasury) - treasuryBefore,
            50 * ONE_ETHER,
            "Treasury should get 50%"
        );
    }

    function test_highBurnRatio_90_10() public {
        // Set 90% burn
        router.updateBurnRatio(9000);

        uint256 payment = 100 * ONE_ETHER;
        uint256 burnAddrBefore = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        uint256 treasuryBefore = tech.balanceOf(treasury);

        vm.prank(user1);
        router.processPayment(payment);

        assertEq(
            tech.balanceOf(0x000000000000000000000000000000000000dEaD) - burnAddrBefore,
            90 * ONE_ETHER
        );
        assertEq(
            tech.balanceOf(treasury) - treasuryBefore,
            10 * ONE_ETHER
        );
    }

    function test_lowBurnRatio_10_90() public {
        // Set 10% burn (minimum)
        router.updateBurnRatio(1000);

        uint256 payment = 100 * ONE_ETHER;
        uint256 burnAddrBefore = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        uint256 treasuryBefore = tech.balanceOf(treasury);

        vm.prank(user1);
        router.processPayment(payment);

        assertEq(
            tech.balanceOf(0x000000000000000000000000000000000000dEaD) - burnAddrBefore,
            10 * ONE_ETHER
        );
        assertEq(
            tech.balanceOf(treasury) - treasuryBefore,
            90 * ONE_ETHER
        );
    }

    // ================================================================
    // DYNAMIC BURN RATIO SIMULATION
    // ================================================================

    function test_scenario_bullMarket_increasesBurn() public {
        // Simulate: $TECH price pumping → increase burn to accelerate deflation
        // Starting: 50% burn

        // Price goes up 30% in a week
        oracle.setPrice(1.3e18); // $1.30

        // Keeper decides: more burn during pumps
        router.updateBurnRatio(7000); // 70% burn

        uint256 payment = 100 * ONE_ETHER;
        uint256 burnedBefore = tech.balanceOf(0x000000000000000000000000000000000000dEaD);

        vm.prank(user1);
        router.processPayment(payment);

        uint256 burned = tech.balanceOf(0x000000000000000000000000000000000000dEaD) - burnedBefore;
        assertEq(burned, 70 * ONE_ETHER, "Bull market should increase burn to 70%");

        // Total supply effectively reduced
        // Before: 2000 $TECH total minted
        // After 100 payments of 100 $TECH each at 70% burn:
        // Burned: 7000 $TECH, Recycled: 3000 $TECH
    }

    function test_scenario_bearMarket_decreasesBurn() public {
        // Simulate: $TECH price dumping → decrease burn, fund ecosystem growth
        oracle.setPrice(0.7e18); // $0.70

        // Keeper decides: less burn during dumps, more to treasury for competitions/grants
        router.updateBurnRatio(3000); // 30% burn

        uint256 payment = 100 * ONE_ETHER;
        uint256 burnedBefore = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        uint256 treasuryBefore = tech.balanceOf(treasury);

        vm.prank(user1);
        router.processPayment(payment);

        uint256 burned = tech.balanceOf(0x000000000000000000000000000000000000dEaD) - burnedBefore;
        uint256 recycled = tech.balanceOf(treasury) - treasuryBefore;

        assertEq(burned, 30 * ONE_ETHER, "Bear market: 30% burn");
        assertEq(recycled, 70 * ONE_ETHER, "Bear market: 70% to treasury for ecosystem");
    }

    function test_scenario_paymentVolumeOverTime() public {
        // Simulate 10 payments with changing burn ratios over time
        uint256[] memory ratios = new uint256[](10);
        ratios[0] = 5000; // Start 50%
        ratios[1] = 5500; // Gradually increase
        ratios[2] = 6000;
        ratios[3] = 6500;
        ratios[4] = 7000; // Peak burn
        ratios[5] = 6500; // Start decreasing
        ratios[6] = 5500;
        ratios[7] = 4000;
        ratios[8] = 3500;
        ratios[9] = 5000; // Back to neutral

        for (uint256 i = 0; i < 10; i++) {
            router.updateBurnRatio(ratios[i]);
            vm.prank(user1);
            router.processPayment(100 * ONE_ETHER);
        }

        (uint256 totalBurned, uint256 totalRecycled, uint256 totalPayments,,) = router.getStats();

        assertEq(totalPayments, 10, "Should have 10 payments");
        // Total sent: 1000 $TECH
        // Burned: 50+55+60+65+70+65+55+40+35+50 = 545 $TECH
        // Recycled: 455 $TECH
        assertEq(totalBurned, 545 * ONE_ETHER, "Total burned should match cumulative");
        assertEq(totalRecycled, 455 * ONE_ETHER, "Total recycled should match cumulative");
    }

    // ================================================================
    // DISCOUNT MECHANISM
    // ================================================================

    function test_discountCalculation_at$1() public {
        // Both inputs in 18 decimals for simplicity
        // $10 agent (in 18 dec), $TECH at $1, 25% discount
        // Discounted: $7.50 → 7.5 $TECH
        uint256 techAmount = router.calculateTechPayment(10e18, 1e18);
        assertEq(techAmount, 7.5e18, "At $1 TECH, should pay 7.5 TECH for $10 agent");
    }

    function test_discountCalculation_at$0_10() public {
        // $10 agent, $TECH at $0.10, 25% discount
        // Discounted: $7.50 → 75 $TECH
        uint256 techAmount = router.calculateTechPayment(10e18, 0.1e18);
        assertEq(techAmount, 75e18, "At $0.10 TECH, should pay 75 TECH");
    }

    function test_discountCalculation_at$5() public {
        // $10 agent, $TECH at $5, 25% discount
        // Discounted: $7.50 → 1.5 $TECH
        uint256 techAmount = router.calculateTechPayment(10e18, 5e18);
        assertEq(techAmount, 1.5e18, "At $5 TECH, should pay 1.5 TECH");
    }

    function test_discountAlwaysCheaperThanUSDC() public {
        // At any $TECH price, paying in $TECH should always be cheaper
        // Using 18-decimal inputs
        uint256 usdcPrice = 10e18; // $10

        uint256[] memory prices = new uint256[](5);
        prices[0] = 0.01e18;  // $0.01
        prices[1] = 0.1e18;   // $0.10
        prices[2] = 1e18;     // $1.00
        prices[3] = 10e18;    // $10.00
        prices[4] = 100e18;   // $100.00

        for (uint256 i = 0; i < prices.length; i++) {
            uint256 techAmount = router.calculateTechPayment(usdcPrice, prices[i]);
            uint256 usdCost = (techAmount * prices[i]) / 1e18;
            // usdCost should be $7.50 (75% of $10)
            assertEq(usdCost, 7.5e18, "Discounted cost should always be $7.50 equivalent");
        }
    }

    // ================================================================
    // CIRCUIT BREAKER
    // ================================================================

    function test_paused_revertsPayments() public {
        router.setPaused(true);

        vm.prank(user1);
        vm.expectRevert();
        router.processPayment(100 * ONE_ETHER);
    }

    function test_unpaused_allowsPayments() public {
        router.setPaused(true);
        router.setPaused(false);

        vm.prank(user1);
        router.processPayment(100 * ONE_ETHER);

        (,,uint256 totalPayments,,) = router.getStats();
        assertEq(totalPayments, 1);
    }

    // ================================================================
    // BOUNDS CHECKING
    // ================================================================

    function test_burnRatio_rejectsBelow10Percent() public {
        vm.expectRevert("Ratio OOB");
        router.updateBurnRatio(999);
    }

    function test_burnRatio_rejectsAbove90Percent() public {
        vm.expectRevert("Ratio OOB");
        router.updateBurnRatio(9001);
    }

    function test_burnRatio_accepts10Percent() public {
        router.updateBurnRatio(1000);
        assertEq(router.burnRatioBps(), 1000);
    }

    function test_burnRatio_accepts90Percent() public {
        router.updateBurnRatio(9000);
        assertEq(router.burnRatioBps(), 9000);
    }

    function test_discount_rejectsAbove50Percent() public {
        vm.expectRevert("Discount OOB");
        router.updateDiscount(5001);
    }

    // ================================================================
    // SUPPLY TRACKING
    // ================================================================

    function test_totalSupplyDecreasesWithBurn() public {
        uint256 totalSupplyBefore = tech.totalSupply();

        vm.prank(user1);
        router.processPayment(100 * ONE_ETHER);

        // Burn address holds tokens but they're effectively out of circulation
        uint256 burnBalance = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        assertEq(burnBalance, 50 * ONE_ETHER, "50 $TECH burned");

        // Circulating supply = totalSupply - burnAddress balance
        uint256 circulatingSupply = tech.totalSupply() - burnBalance;
        assertLt(circulatingSupply, totalSupplyBefore, "Circulating supply decreased");
    }

    function test_multiplePayments_trackCumulativeBurn() public {
        for (uint256 i = 0; i < 5; i++) {
            vm.prank(i % 2 == 0 ? user1 : user2);
            router.processPayment(100 * ONE_ETHER);
        }

        uint256 burnBalance = tech.balanceOf(0x000000000000000000000000000000000000dEaD);
        assertEq(burnBalance, 250 * ONE_ETHER, "500 TECH sent x 50% = 250 burned");
    }

    // ================================================================
    // EDGE CASES
    // ================================================================

    function test_zeroAmountPayment() public {
        vm.prank(user1);
        router.processPayment(0);
        // Should not revert, just no-op
        (,,uint256 totalPayments,,) = router.getStats();
        assertEq(totalPayments, 1);
    }

    function test_fullBalancePayment() public {
        uint256 balance = tech.balanceOf(user1);
        vm.prank(user1);
        router.processPayment(balance);

        assertEq(tech.balanceOf(user1), 0, "User spent full balance");
    }

    function test_multipleUsers() public {
        vm.prank(user1);
        router.processPayment(50 * ONE_ETHER);
        vm.prank(user2);
        router.processPayment(75 * ONE_ETHER);

        (uint256 totalBurned, uint256 totalRecycled, uint256 totalPayments,,) = router.getStats();
        // 50*0.5 + 75*0.5 = 25 + 37.5 = 62.5 burned
        assertEq(totalBurned, 62.5e18);
        assertEq(totalRecycled, 62.5e18);
        assertEq(totalPayments, 2);
    }

    // ================================================================
    // KEEPER SIMULATION (off-chain logic → on-chain call)
    // ================================================================

    function test_keeperAdjustsBurnRatioDaily() public {
        // Simulate a keeper that adjusts burn ratio based on price momentum
        // Day 1: Price stable → 50%
        // Day 2: Price +15% → 60%
        // Day 3: Price +25% → 70% (capped)
        // Day 4: Price -10% → 45%
        // Day 5: Price -30% → 20% (floor)

        uint256[] memory expectedRatios = new uint256[](5);
        expectedRatios[0] = 5000;
        expectedRatios[1] = 6000;
        expectedRatios[2] = 7000;
        expectedRatios[3] = 4500;
        expectedRatios[4] = 2000;

        for (uint256 day = 0; day < 5; day++) {
            router.updateBurnRatio(expectedRatios[day]);
            vm.prank(user1);
            router.processPayment(100 * ONE_ETHER);
        }

        (uint256 totalBurned, uint256 totalRecycled,,,) = router.getStats();
        // Burned: 50+60+70+45+20 = 245
        // Recycled: 50+40+30+55+80 = 255
        assertEq(totalBurned, 245 * ONE_ETHER);
        assertEq(totalRecycled, 255 * ONE_ETHER);
    }
}
