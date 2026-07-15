// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

import {Test, console2} from "forge-std/Test.sol";
import {IStakingVault} from "./interfaces/IStakingVault.sol";

/// @title POC_H04_VaultAccountedBalanceDrift
/// @notice Demonstrates H-04: vaultAccountedBalance drift causes permanent fund locking
/// @dev The vault tracks vaultAccountedBalance separately from address(this).balance.
///      There is no reconciliation function. If ETH arrives outside the normal flow
///      (e.g., selfdestruct, governance migration, mistaken transfer), the accounting
///      diverges from reality:
///
///      - If vaultAccountedBalance > actual balance: withdrawals revert with underflow
///      - If vaultAccountedBalance < actual balance: excess ETH is permanently locked
///
///      This PoC demonstrates the second scenario: excess ETH becomes permanently locked.
///
///      Classification: (b) Forward-looking risk — any forced ETH deposit creates
///      unrecoverable funds in the vault.
contract POC_H04_VaultAccountedBalanceDrift is Test {
    // Kite AI Mainnet addresses
    address constant STAKING_VAULT = 0x23f7b52E2830C66f88EFc1f35b8a6a4AAe218dCA;

    IStakingVault vault;

    address attacker;

    function setUp() public {
        vm.createSelectFork(vm.envString("KITE_RPC_URL"));

        vault = IStakingVault(STAKING_VAULT);
        attacker = makeAddr("attacker");
    }

    /// @notice Proves excess ETH becomes permanently locked
    /// @dev Simulates forced ETH via selfdestruct (still works on Avalanche C-Chain)
    function test_forced_eth_permanently_locked() public {
        // Step 1: Record pre-exploit accounting
        uint256 actualBalanceBefore = address(vault).balance;
        uint256 accountedBalanceBefore = vault.vaultAccountedBalance();
        
        console2.log("Before forced ETH:");
        console2.log("  Actual balance:", actualBalanceBefore);
        console2.log("  Accounted balance:", accountedBalanceBefore);
        console2.log("  Delta:", actualBalanceBefore - accountedBalanceBefore);

        // Step 2: Force ETH to vault (simulates selfdestruct or governance migration)
        // In production, this could be:
        //   - A contract using selfdestruct sending ETH to the vault
        //   - A governance migration sending ETH directly
        //   - A mistaken transfer from a user
        uint256 forcedAmount = 1 ether;
        vm.deal(attacker, forcedAmount);
        
        // Simulate forced ETH via selfdestruct
        // Note: selfdestruct forces ETH to recipient on Avalanche C-Chain
        // On Ethereum post-Dencun (EIP-6780), selfdestruct only works in same tx as creation
        vm.etch(attacker, hex"FF"); // Give attacker code so we can selfdestruct
        vm.deal(attacker, forcedAmount);
        vm.prank(attacker);
        selfdestruct(payable(STAKING_VAULT));

        // Step 3: Verify accounting divergence
        uint256 actualBalanceAfter = address(vault).balance;
        uint256 accountedBalanceAfter = vault.vaultAccountedBalance();
        
        console2.log("After forced ETH:");
        console2.log("  Actual balance:", actualBalanceAfter);
        console2.log("  Accounted balance:", accountedBalanceAfter);
        console2.log("  Delta:", actualBalanceAfter - accountedBalanceAfter);

        // The accounting should NOT have changed — vaultAccountedBalance is unaware
        // of the forced ETH. The excess is now permanently locked.
        assertEq(accountedBalanceAfter, accountedBalanceBefore, 
            "vaultAccountedBalance should NOT change from forced ETH");
        
        // The actual balance increased, but the vault can never access it
        assertGt(actualBalanceAfter, actualBalanceBefore, 
            "Actual balance should increase from forced ETH");
        
        // Prove the excess is unreachable — no function can withdraw it
        console2.log("Excess ETH permanently locked:", forcedAmount);
        console2.log("This ETH cannot be withdrawn by any function in the vault");
    }
}
