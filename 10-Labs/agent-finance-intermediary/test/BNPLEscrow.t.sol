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
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE);
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
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE);

        // Installments due at 7, 14, 21, 28 days. Grace = 3 days after each.
        // Warp 7 days + 1 hour each time — just past due, well within grace
        for (uint8 i = 0; i < 4; i++) {
            vm.warp(block.timestamp + 7 days + 1 hours);
            vm.prank(user);
            escrow.payInstallment(id, i);
        }

        // Agreement should be settled
        (,,,,, bool active,,) = escrow.getAgreement(id);
        assertFalse(active);

        // Merchant should have received full amount (deposit back + user payments)
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL * 2);
    }

    function test_DefaultOnMissedPayment() public {
        vm.prank(merchant);
        uint256 id = escrow.createAgreement(merchant, user, token, TOTAL, 4, GRACE);

        // Pay first installment — 1 hour past due
        vm.warp(block.timestamp + 7 days + 1 hours);
        vm.prank(user);
        escrow.payInstallment(id, 0);

        // Skip second — warp past its grace period
        // Installment 1 due at 14 days, grace ends at 17 days
        // We're at 7 days + 1 hour, so warp 10 more days = 17 days + 1 hour
        vm.warp(block.timestamp + 10 days);

        escrow.markDefault(id, 1);

        (,,,,, bool active,,) = escrow.getAgreement(id);
        assertFalse(active);

        // Merchant keeps deposit + paid installment
        assertEq(MockUSDC(token).balanceOf(merchant), TOTAL + INSTALLMENT);
    }

    function test_RevertIfNot4Installments() public {
        vm.expectRevert("BNPL: must be 4 installments");
        escrow.createAgreement(merchant, user, token, TOTAL, 3, GRACE);
    }

    function test_RevertIfZeroAmount() public {
        vm.expectRevert("BNPL: zero amount");
        escrow.createAgreement(merchant, user, token, 0, 4, GRACE);
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
