---
name: foundry-solidity-testing
description: Build, test, and debug Solidity smart contracts using Foundry (forge/fuzz) with OpenZeppelin v5 on EVM chains.
---

# Foundry + Solidity Testing

Build, test, and debug Solidity smart contracts using Foundry (forge/fuzz) with OpenZeppelin v5 on EVM chains.

## Setup

Install Foundry per https://book.getfoundry.sh/getting-started/installation — then run `foundryup`.
Binary is at `~/.foundry/bin/forge`. Add to PATH: `export PATH="$HOME/.foundry/bin:$PATH"`

Verify: `forge --version` (1.5.x+ stable as of 2026-04)

## Project Structure

Existing project at `/root/gentech/agent-escrow/`:
```
contracts/     — Solidity source
test/          — Foundry tests (forge-std/Test.sol)
lib/           — forge-std, openzeppelin-contracts
out/           — Compilation artifacts
foundry.toml   — Config (fuzz runs: 256)
```

## Common Commands

```bash
export PATH="$HOME/.foundry/bin:$PATH"
cd /root/gentech/agent-escrow

# Run all tests
forge test -vvv

# Run specific contract
forge test --match-contract MyContractTest -vvv

# Run specific test
forge test --match-test testSpecific -vv

# Build only
forge build
```

## OpenZeppelin v5 Gotchas (Critical)

### Custom Errors, Not Strings
OZ v5 uses custom errors. The old string-based reverts DON'T work:
```solidity
// ❌ OLD (OZ v4) — won't match in tests
vm.expectRevert("Ownable: caller is not the owner");

// ✅ NEW (OZ v5) — just check for any revert
vm.expectRevert();
```

Common OZ v5 errors:
- `OwnableUnauthorizedAccount(address)` — replaces "caller is not the owner"
- `ERC20InsufficientBalance(address, uint256, uint256)`
- `ERC20InsufficientAllowance(address, uint256, uint256)`

### SafeERC20 Import Path
```solidity
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

## Mixed-Decimal Math Patterns

When contracts handle tokens with different decimals (e.g., USDC 6, ERC20 18):

```solidity
// Calculate token amount from USDC price
// usdcPrice = 10e6 ($10 USDC, 6 decimals)
// tokenPrice = 0.1e18 ($0.10, 18 decimals)
// result = (usdcPrice * 1e18) / tokenPrice = raw units

function calculateAmount(
    uint256 usdcPrice,    // 6 decimals
    uint256 tokenPrice    // 18 decimals
) public pure returns (uint256) {
    // Result is in mixed-decimal units, not 18-dec
    return (usdcPrice * 1e18) / tokenPrice;
}
// calculateAmount(10e6, 0.1e18) = 100_000_000 (not 100e18!)
```

**In tests:** Don't assume result is 18-decimal. Trace the math:
- `(10e6 * 1e18) / 1e17 = 100_000_000` ← this is the correct assertion

## Fuzz Test Patterns

```solidity
// Bound to valid range
amount = bound(amount, 1, 1_000_000e18);

// Skip edge cases that should revert (e.g., NoChange guards)
if (newValue == currentValue) return;

// Prove invariants over 256 random runs
function testFuzz_alwaysConserves(uint256 amount) public {
    amount = bound(amount, 1, type(uint128).max);
    uint256 before = token.balanceOf(user);
    vm.prank(user);
    contract.processPayment(amount);
    assertEq(token.balanceOf(BURN) + token.balanceOf(TREASURY) + token.balanceOf(user), before);
}
```

## Isolating Tests From Other Contracts

If another contract in the project has compile errors:
```bash
mv test/BrokenTest.t.sol test/BrokenTest.t.sol.bak
forge test --match-contract WorkingTest -vvv
mv test/BrokenTest.t.sol.bak test/BrokenTest.t.sol
```

## Key Imports Reference

```solidity
import {Test} from "forge-std/Test.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
```

## Test Contract Boilerplate

```solidity
contract MyTest is Test {
    MyContract public target;
    MockERC20 public token;
    address public owner = makeAddr("owner");
    address public user = makeAddr("user");

    function setUp() public {
        vm.startPrank(owner);
        token = new MockERC20();
        target = new MyContract(address(token));
        vm.stopPrank();
        token.mint(user, 1_000_000e18);
        vm.prank(user);
        token.approve(address(target), type(uint256).max);
    }
}
```

## EIP-712 Signature Testing — Critical Gotcha

When testing EIP-712 off-chain signatures, the private key and address MUST be a matching pair:

```solidity
// ❌ WRONG — address(0x3) is NOT derived from private key 0x03
address public signer = address(0x3);
vm.sign(uint256(uint160(signer)), digest);  // ecrecover returns wrong address

// ✅ CORRECT — derive address from private key
uint256 public signerPK = 0xA11CE;
address public signer;

function setUp() public {
    signer = vm.addr(signerPK);  // Derives actual address from private key
    // Now vm.sign(signerPK, digest) will match ECDSA.recover in contract
}
```

**Why the wrong version sometimes "works":** If the typehash includes extra fields (timestamp, address), both test and contract compute the same hash regardless — masking the key/address mismatch. Once you fix the typehash, the mismatch is exposed as `InvalidSignature()`.

## EIP-712 Typehash Anti-Patterns

**Don't include `timestamp` in the typehash:**
```solidity
// ❌ BAD — every signature is unique to the exact second
// AI validator can't pre-sign, defeating EIP-712 off-chain signature purpose
bytes32 private constant VALIDATION_TYPEHASH = keccak256(
    "Validation(uint256 escrowId,address validator,uint256 timestamp)"
);

// ✅ GOOD — escrowId is enough
bytes32 private constant VALIDATION_TYPEHASH = keccak256(
    "Validation(uint256 escrowId)"
);
```

**Don't include `msg.sender` or `block.timestamp` in typehash** — these are runtime values that change per call. EIP-712 signatures are meant to be **created off-chain and submitted later**.

## Replay Protection via State Machine

If your contract has a one-way state transition, it inherently prevents replay — no `usedSignatures` mapping needed:

```solidity
// State machine: Completed → Released (one-way)
// A signature for escrowId X only works when state == Completed
// After release, state == Released → signature fails NotCompleted check
// This is cheaper (no storage writes) than tracking used signatures
```

Remove dead `usedSignatures` mappings — they waste gas per escrow and add complexity.

## Foundry Forge Lint Notes

Common lint warnings to address:
- **`unused-import`**: Remove unused `import {IERC20} ...` — clutters and triggers lint
- **`screaming-snake-case-immutable`**: Name immutables `TECH_TOKEN` not `techToken`
- **`asm-keccak256`**: Use inline assembly for keccak256 of single values (minor gas optimization)
