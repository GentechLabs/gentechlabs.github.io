---
name: foundry-project-scaffold
description: Scaffold a Foundry project with OpenZeppelin v5, write contracts, and run tests. Covers common pitfalls and OZ v5 patterns.
triggers:
  - "create foundry project"
  - "set up solidity test"
  - "forge init"
  - "foundry test"
  - "openzeppelin v5"
---

# Foundry Project Scaffold + OZ v5

## Quick Start

```bash
# Initialize project (use --force if dir exists)
forge init --force <path>

# Install OpenZeppelin v5
cd <path> && forge install OpenZeppelin/openzeppelin-contracts@v5.0.0

# Add remapping to foundry.toml
```

## foundry.toml

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
remappings = [
    "@openzeppelin/=lib/openzeppelin-contracts/"
]
```

## Write Contracts → Test → Iterate

```bash
# Write contracts to src/, tests to test/
forge test -vvv           # Run all tests with traces
forge test --match-test <name> -vvv   # Single test
forge snapshot            # Gas snapshot
```

---

## OpenZeppelin v5 Gotchas

### 1. Pausable Pattern (v5 uses custom errors)

```solidity
import "@openzeppelin/contracts/utils/Pausable.sol";

contract MyContract is Ownable, Pausable {
    // DON'T declare `bool public paused` — Pausable has it built-in

    function doThing() external whenNotPaused {
        // ...
    }

    function setPaused(bool _paused) external onlyOwner {
        if (_paused) {
            _pause();      // internal function from Pausable
        } else {
            _unpause();
        }
    }
}
```

**Test for paused revert (v5 custom error, NOT string):**
```solidity
// WRONG — v5 uses custom error EnforcedPause()
vm.expectRevert("Pausable: paused");

// RIGHT — just catch any revert
vm.expectRevert();

// OR match the custom error specifically
vm.expectRevert(Pausable.EnforcedPause.selector);
```

### 2. SafeERC20 Import Path (v5)

```solidity
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
using SafeERC20 for IERC20;
```

### 3. Burn Address Pattern

```solidity
address public constant BURN_ADDRESS = 0x000000000000000000000000000000000000dEaD;
// Transfer to burn address — visible on-chain, tokens exist but unrecoverable
token.safeTransfer(BURN_ADDRESS, burnAmount);

// OR use ERC20Burnable._burn() to reduce totalSupply directly
```

---

## Decimal Handling Pitfall

When mixing USDC (6 decimals) with tokens (18 decimals), keep inputs consistent in tests:

```solidity
// WRONG — mixed decimals in calculation
calculateTechPayment(10e6, 1e18)  // 6-dec USD, 18-dec price
// Returns unexpected result because formula assumes same decimals

// RIGHT — use consistent 18 decimals in tests
calculateTechPayment(10e18, 1e18)  // both 18-dec
// Returns clean 7.5e18
```

If the contract must handle mixed decimals, add a normalization step:
```solidity
// Convert 6-decimal USDC to 18-decimal representation
uint256 usdNormalized = usdcPrice * 1e12;
```

---

### 4. `supportsInterface` Must Be `view`, Not `pure`

When overriding `supportsInterface` with `AccessControl`, it reads state — so it must be `view`:

```solidity
// WRONG — compiler error
function supportsInterface(bytes4 interfaceId)
    public pure override(AccessControl) returns (bool) { ... }

// RIGHT
function supportsInterface(bytes4 interfaceId)
    public view override(AccessControl) returns (bool) { ... }
```

---

## Common Test Patterns

```solidity
function setUp() public {
    token = new MockToken();
    router = new PaymentRouter(address(token), treasury, ...);
    token.mint(user, 1000e18);
    vm.prank(user);
    token.approve(address(router), type(uint256).max);
}

// Track balance changes
uint256 before = token.balanceOf(addr);
vm.prank(user);
router.doThing();
assertEq(token.balanceOf(addr) - before, expectedAmount);

// Bound checking
vm.expectRevert("Ratio OOB");
router.updateRatio(9999);
```

### vm.startPrank in setUp Conflicts with vm.prank

`vm.startPrank()` in `setUp()` persists across all test functions. Subsequent `vm.prank()` calls in tests will revert with: _"cannot override an ongoing prank with a single vm.prank"_

**Fix:** Don't use `startPrank` in `setUp`. Use individual `vm.prank()` calls per test:

```solidity
// WRONG — breaks all tests that use vm.prank()
function setUp() public {
    vm.startPrank(address(this));
    adapter = new MyContract();
}

// RIGHT — no persistent prank in setUp
function setUp() public {
    adapter = new MyContract();
}
```

### Inline Interfaces & Override

When embedding an interface directly in the same `.sol` file (common in standalone/hackathon projects), the `override` keyword won't resolve.

**Fix:** Remove `override` when interface is in-file:

```solidity
// Interface embedded in same file
interface IAdapter {
    function adapterName() external view returns (string memory);
}

contract BirdeyeAdapter is IAdapter {
    // WRONG — compiler: "does not override anything"
    function adapterName() external pure override returns (string memory) { ... }

    // RIGHT — just drop override
    function adapterName() external pure returns (string memory) { ... }
}
```

---

## forge Install (v1.5.x)

Different syntax from older versions — no `--no-commit` flag:

```bash
# Init git first (forge install requires git)
git init && git add -A && git commit -m "initial"

# Install
forge install foundry-rs/forge-std OpenZeppelin/openzeppelin-contracts@v5.0.2
```

---

## Project Structure

```
project/
├── foundry.toml
├── src/
│   ├── Token.sol
│   └── Router.sol
├── test/
│   └── Router.t.sol
└── lib/
    ├── forge-std/
    └── openzeppelin-contracts/
```
