// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BNPLEscrowTest
 * @notice Foundry tests for BNPLEscrow contract
 */
import "forge-std/Test.sol";
import "../contracts/BNPLEscrow.sol";

contract BNPLEscrowTest is Test {
    BNPLEscrow public escrow;
    address public merchant = address(0x1);
    address public user = address(0x2);
    address public token; // mock USDC

    uint256 constant TOTAL = 400 * 10**6; // 400 USDC (6 decimals)
    uint256 constant INSTALLMENT = 100 * 10**6; // 100 USDC
    uint256 constant GRACE = 3 days;
    uint256 constant SPACING = 7 days;

    function setUp() public {
        escrow = new BNPLEscrow();
        // Deploy mock ERC20
        token = address(new MockUSDC());
        // Fund merchant
        MockUSDC(token).mint(merchant, TOTAL);
        MockUSDC(token).mint(user, TOTAL * 2);
        // Approve escrow
        vm.prank(merchant);
        MockUSDC(token).approve(address(escrow), TOTAL);
        vm.prank(user);
        MockUSDC(token).approve(address(escrow), TOTAL * 2);
    }

    function test_CreateAgreement() public {
        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE, SPACING);
        assertEq(id, 0);

        (address m, address u, address t, uint256 total, uint256 inst, bool active,,) = escrow.getAgreement(id);
        assertEq(m, merchant);
        assertEq(u, user);
        assertEq(t, token);
        assertEq(total, TOTAL);
        assertEq(inst, INSTALLMENT);
        assertTrue(active);
    }

    function test_PayAllInstallments() public {
        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE, SPACING);

        for (uint8 i = 0; i < 4; i++) {
            vm.warp(block.timestamp + 7 days + 1 hours);
            vm.prank(user);
            escrow.payInstallment(id, i);
        }

        (,,,,, bool active,,) = escrow.getAgreement(id);
        assertFalse(active);
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL * 2);
    }

    function test_DefaultOnMissedPayment() public {
        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE, SPACING);

        vm.warp(block.timestamp + 7 days + 1 hours);
        vm.prank(user);
        escrow.payInstallment(id, 0);

        vm.warp(block.timestamp + 10 days);
        escrow.markDefault(id, 1);

        (,,,,, bool active,,) = escrow.getAgreement(id);
        assertFalse(active);
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL + INSTALLMENT);
    }

    function test_RevertIfNot4Installments() public {
        vm.expectRevert("BNPL: must be 4 installments");
        vm.prank(merchant);
        escrow.createAgreement(merchant, user, token, TOTAL, 3, GRACE, SPACING);
    }

    function test_RevertIfZeroAmount() public {
        vm.expectRevert("BNPL: total too small");
        vm.prank(merchant);
        escrow.createAgreement(merchant, user, token, 0, 4, GRACE, SPACING);
    }

    function test_RevertIfPaused() public {
        escrow.emergencyPause();
        vm.expectRevert("BNPL: paused");
        vm.prank(merchant);
        escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE, SPACING);
    }

    function test_EmergencyPause() public {
        escrow.emergencyPause();
        assertTrue(escrow.paused());
        escrow.unpause();
        assertFalse(escrow.paused());
    }

    function test_Sweep() public {
        // Send tokens directly to contract
        MockUSDC(token).mint(address(escrow), 1000);
        escrow.sweep(token, merchant);
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL + 1000);
    }

    function test_CancelAgreement() public {
        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE, SPACING);

        vm.prank(merchant);
        escrow.cancelAgreement(id);

        (,,,,, bool active,,) = escrow.getAgreement(id);
        assertFalse(active);
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL);
    }

    function test_RoundingLoss() public {
        uint256 oddTotal = 401 * 10**6; // 401 USDC — not divisible by 4
        MockUSDC(token).mint(merchant, oddTotal);
        vm.prank(merchant);
        MockUSDC(token).approve(address(escrow), oddTotal);

        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, oddTotal, 4, GRACE, SPACING);

        // Pay all 4
        for (uint8 i = 0; i < 4; i++) {
            vm.warp(block.timestamp + 7 days + 1 hours);
            vm.prank(user);
            escrow.payInstallment(id, i);
        }

        // All funds should be recoverable — no stuck dust
        // Merchant started with 400 (setUp) + 401 (minted) = 801
        // 401 pulled into escrow → merchant has 400
        // 401 paid by user → contract has 802
        // 802 settled to merchant → merchant has 400 + 802 = 1202
        assertEq(MockUSDC(token).balanceOf(merchant), 1202000000);
    }

    function test_OwnerOnly() public {
        vm.prank(user);
        vm.expectRevert("BNPL: not owner");
        escrow.emergencyPause();
    }
}

contract MockUSDC {
    string public name = "USD Coin";
    string public symbol = "USDC";
    uint8 public decimals = 6;
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "insufficient balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function approve(address, uint256) external pure returns (bool) {
        return true;
    }

    function allowance(address, address) external pure returns (uint256) {
        return type(uint256).max;
    }
}
