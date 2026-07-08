// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/mocks/MockERC20.sol";
import "../src/mocks/MockPriceFeed.sol";
import "../src/DiscountCalculator.sol";
import "../src/BurnSplitter.sol";
import "../src/TechPaymentRouter.sol";

contract TechPaymentRouterTest is Test {
    MockERC20 techToken;
    MockPriceFeed priceFeed;
    DiscountCalculator discountCalc;
    BurnSplitter burnSplitter;
    TechPaymentRouter router;

    address treasury = makeAddr("treasury");
    address user = makeAddr("user");
    address deadAddress = 0x000000000000000000000000000000000000dEaD;

    uint256 constant INITIAL_SMA = 0.05e18;
    uint256 constant INITIAL_MINT = 1_000_000 ether;

    function setUp() public {
        techToken = new MockERC20();
        priceFeed = new MockPriceFeed(8, int256(0.05 * 1e8));

        discountCalc = new DiscountCalculator(address(priceFeed), INITIAL_SMA);
        burnSplitter = new BurnSplitter(address(techToken), treasury, address(this));
        router = new TechPaymentRouter(
            address(techToken),
            address(discountCalc),
            address(burnSplitter)
        );
        // Wire burnSplitter to accept calls from router (test contract is initial router)
        burnSplitter.setRouter(address(router));

        techToken.mint(user, INITIAL_MINT);
        vm.prank(user);
        techToken.approve(address(router), type(uint256).max);

        vm.prank(user);
        techToken.approve(address(burnSplitter), type(uint256).max);
    }

    // --- Discount Calculator ---

    function test_discountPriceAtSMA() public view {
        uint256 discount = discountCalc.calculateDiscount(0);
        assertEq(discount, 2000, "Price at SMA should give 20% discount");
    }

    function test_discountPriceAboveSMA() public {
        priceFeed.setPrice(int256(0.06 * 1e8));
        uint256 discount = discountCalc.calculateDiscount(0);
        assertEq(discount, 1000, "Price at 120% of SMA should give min 10%");
    }

    function test_discountPriceBelowSMA() public {
        priceFeed.setPrice(int256(0.04 * 1e8));
        uint256 discount = discountCalc.calculateDiscount(0);
        assertEq(discount, 3000, "Price at 80% of SMA should give max 30%");
    }

    function test_discountLinearInterpolation() public {
        priceFeed.setPrice(int256(0.055 * 1e8));
        uint256 discount = discountCalc.calculateDiscount(0);
        assertEq(discount, 1500, "110% of SMA should give 15%");
    }

    function test_loyaltySilver() public view {
        uint256 discount = discountCalc.calculateDiscount(10_000 ether);
        assertEq(discount, 2100, "Silver adds 1%");
    }

    function test_loyaltyGold() public view {
        uint256 discount = discountCalc.calculateDiscount(100_000 ether);
        assertEq(discount, 2300, "Gold adds 3%");
    }

    function test_loyaltyDiamond() public view {
        uint256 discount = discountCalc.calculateDiscount(1_000_000 ether);
        assertEq(discount, 2500, "Diamond adds 5%");
    }

    function test_absoluteCap() public {
        priceFeed.setPrice(int256(0.01 * 1e8));
        uint256 discount = discountCalc.calculateDiscount(1_000_000 ether);
        assertEq(discount, 3500, "Absolute cap is 35%");
    }

    // --- Burn Splitter ---

    function test_burnSplit70_30() public {
        vm.prank(address(router));
        burnSplitter.split(user, 1000 ether);

        assertEq(techToken.balanceOf(deadAddress), 700 ether, "70% burned");
        assertEq(techToken.balanceOf(treasury), 300 ether, "30% treasury");
    }

    function test_burnSplitTotals() public {
        vm.prank(address(router));
        burnSplitter.split(user, 500 ether);

        assertEq(burnSplitter.totalBurned(), 350 ether);
        assertEq(burnSplitter.totalToTreasury(), 150 ether);
    }

    function test_previewSplit() public view {
        (uint256 burn, uint256 treasuryAmt) = burnSplitter.previewSplit(1000 ether);
        assertEq(burn, 700 ether);
        assertEq(treasuryAmt, 300 ether);
    }

    // --- Full Payment Flow ---

    function test_fullPaymentFlow() public {
        uint256 usdPrice = 10e18;
        uint256 userBalBefore = techToken.balanceOf(user);

        vm.prank(user);
        (uint256 techPaid, uint256 discountBps) = router.payWithTech(usdPrice, "Agent Rental");

        uint256 spent = userBalBefore - techToken.balanceOf(user);

        assertEq(discountBps, 2000, "20% discount");
        assertEq(techPaid, 160 ether, "Pay 160 $TECH");
        assertEq(spent, 160 ether);

        assertEq(techToken.balanceOf(deadAddress), 112 ether, "112 burned");
        assertEq(techToken.balanceOf(treasury), 48 ether, "48 treasury");
        assertEq(router.cumulativeSpent(user), 160 ether);
    }

    function test_paymentDropsWhenPricePumps() public {
        uint256 usdPrice = 10e18;

        vm.prank(user);
        (uint256 techPaid1,) = router.payWithTech(usdPrice, "Service");

        priceFeed.setPrice(int256(0.10 * 1e8));

        vm.prank(user);
        (uint256 techPaid2,) = router.payWithTech(usdPrice, "Service");

        assertLt(techPaid2, techPaid1, "Higher price = fewer tokens");
    }

    function test_paymentIncreasesWhenPriceDumps() public {
        uint256 usdPrice = 10e18;

        vm.prank(user);
        (uint256 techPaid1,) = router.payWithTech(usdPrice, "Service");

        priceFeed.setPrice(int256(0.025 * 1e8));

        vm.prank(user);
        (uint256 techPaid2,) = router.payWithTech(usdPrice, "Service");

        assertGt(techPaid2, techPaid1, "Lower price = more tokens");
    }

    function test_previewPayment() public view {
        (uint256 techAmount, uint256 discountBps, uint256 savings) = router.previewPayment(10e18);
        assertEq(techAmount, 160 ether);
        assertEq(discountBps, 2000);
        assertEq(savings, 40 ether);
    }

    function test_zeroPaymentReverts() public {
        vm.prank(user);
        vm.expectRevert("TechPaymentRouter: zero payment");
        router.payWithTech(0, "Free Stuff");
    }

    function test_deadAddressHasBurnedTokens() public {
        vm.prank(user);
        router.payWithTech(10e18, "Test");
        assertGt(techToken.balanceOf(deadAddress), 0);
    }

    function test_multiplePaymentsTrackCumulative() public {
        vm.startPrank(user);
        router.payWithTech(10e18, "S1");
        router.payWithTech(10e18, "S2");
        router.payWithTech(10e18, "S3");
        vm.stopPrank();

        assertEq(router.cumulativeSpent(user), 480 ether);
    }

    function test_dustHandling() public view {
        (uint256 burn, uint256 treasuryAmt) = burnSplitter.previewSplit(1001 ether);
        assertEq(burn + treasuryAmt, 1001 ether, "No dust loss");
    }
}
