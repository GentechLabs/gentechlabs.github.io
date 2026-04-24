---
name: foundry-testing-patterns
description: Common Foundry testing pitfalls and patterns for Solidity smart contract development — vm.prank gotchas, daily reset logic, and debugging failing tests.
category: smart-contract
triggers:
  - forge test failing
  - vm.prank
  - daily limit reset
  - msg.sender in test
  - Foundry test debug
---

# Foundry Testing Patterns

Common pitfalls when writing Foundry tests for Solidity contracts. Learned from real debugging sessions building agent payment and escrow contracts.

## Pitfall 1: `vm.prank` Required for View Functions Using `msg.sender`

**Problem:** A contract has a public view function that reads `msg.sender`:

```solidity
function getDailySpending() external view returns (uint256 spent, uint256 limit, uint256 remaining) {
    uint256 currentSpent = spentToday[msg.sender]; // msg.sender is the caller
    return (currentSpent, dailyLimits[msg.sender], dailyLimits[msg.sender] - currentSpent);
}
```

**In the test**, calling this without `vm.prank` means `msg.sender` = test contract address, NOT the agent address:

```solidity
// ❌ WRONG — msg.sender = test contract, not agent1
(uint256 spent, , uint256 remaining) = paymentContract.getDailySpending();
assertEq(spent, 0);
assertEq(remaining, DAILY_LIMIT); // FAILS: dailyLimits[testContract] is 0

// ✅ CORRECT — vm.prank sets msg.sender for the next call
vm.prank(agent1);
(uint256 spent, , uint256 remaining) = paymentContract.getDailySpending();
assertEq(spent, 0);
assertEq(remaining, DAILY_LIMIT); // PASSES: dailyLimits[agent1] is DAILY_LIMIT
```

**Rule:** Any external/public function that reads `msg.sender` needs `vm.prank(address)` in the test. This applies to both state-changing AND view functions.

**Note:** `vm.prank` only affects the NEXT external call. For multiple calls, repeat it:

```solidity
vm.prank(agent1);
paymentContract.deposit{value: 1 ether}();

vm.prank(agent1); // Must repeat — prank doesn't persist
paymentContract.setDailyLimit(0.5 ether);
```

## Pitfall 2: Daily Reset Logic — Initialize `lastSpendingDay` on First Use

**Problem:** A contract tracks daily spending with automatic reset:

```solidity
mapping(address => uint256) public spentToday;
mapping(address => uint256) public lastSpendingDay;

function _processPayment(...) internal {
    uint256 currentDay = block.timestamp / 1 days;
    if (lastSpendingDay[msg.sender] < currentDay) {
        spentToday[msg.sender] = 0; // Auto-reset on new day
        lastSpendingDay[msg.sender] = currentDay;
    }
    // ... payment logic
}
```

**Bug:** If `lastSpendingDay[msg.sender]` is 0 (never set), then `0 < currentDay` is always true, so `spentToday` always resets. But `dailyLimits[msg.sender]` might also be 0 if it was set in a different transaction context.

**Fix:** Initialize `lastSpendingDay` when the daily limit is first set:

```solidity
function setDailyLimit(uint256 limit) external whenNotPaused {
    dailyLimits[msg.sender] = limit;
    // Initialize spending day if first time setting a limit
    if (lastSpendingDay[msg.sender] == 0) {
        lastSpendingDay[msg.sender] = block.timestamp / 1 days;
    }
    emit DailyLimitUpdated(msg.sender, limit);
}
```

## Pitfall 3: `vm.warp` Doesn't Trigger State Changes

**Problem:** Warping time doesn't automatically call any functions. State variables that should "reset" on a new day won't reset until a transaction triggers the reset logic.

```solidity
// After making a payment on day 0:
vm.prank(agent1);
paymentContract.pay(service1, 0.1 ether, "Test");

// Warp to next day
vm.warp(block.timestamp + 1 days);

// ❌ spentToday is STILL 0.1 ether — no transaction triggered the reset
// ✅ The reset happens INSIDE _processPayment or getDailySpending (view)
```

**Pattern:** Either:
1. Call a state-changing function after warp (which triggers the reset internally)
2. Or test the view function's auto-reset behavior (which should compute the reset without modifying state)

## Pitfall 4: Assertion on Public Mappings vs View Functions

**Problem:** Public mappings generate automatic getter functions, but those getters use `msg.sender` too:

```solidity
mapping(address => uint256) public spentToday;

// Auto-generated getter: function spentToday(address) returns (uint256)
// This does NOT use msg.sender — it takes an explicit address parameter
```

```solidity
// ✅ This works WITHOUT vm.prank — it takes the address explicitly
assertEq(paymentContract.spentToday(agent1), 0.1 ether);

// ⚠️ This NEEDS vm.prank — getDailySpending() reads msg.sender internally
vm.prank(agent1);
(uint256 spent, , ) = paymentContract.getDailySpending();
```

## Pitfall 5: Unicode Characters in String Literals

**Problem:** Solidity does NOT support Unicode characters (like em-dashes `—`, curly quotes `""`, etc.) in string literals used in `require()` or `revert()`:

```solidity
// ❌ FAILS — em-dash (U+2014) in string literal
require(!escrow.completed, "Already completed — use validate flow");
// Error: Invalid character in string. If you are trying to use Unicode characters, use a unicode"..." string literal.

// ✅ FIX — use ASCII hyphen instead
require(!escrow.completed, "Already completed - use validate flow");
```

**Why:** Solidity `string` literals default to ASCII. The compiler rejects non-ASCII bytes unless you use the `unicode"..."` prefix (Solidity 0.7.0+), but that's rarely what you want in error messages.

**Rule:** Keep `require()`/`revert()` error messages strictly ASCII. Watch out when copy-pasting from docs or notes that use typographic characters.

**Other characters to avoid in Solidity strings:**
- `—` (em dash, U+2014) → use `-`
- `"` `"` (curly quotes, U+201C/201D) → use `"`
- `…` (ellipsis, U+2026) → use `...`
- `→` (arrow, U+2192) → use `->`

## Pitfall 6: Reserved Keywords as Variable Names

**Problem:** `memory`, `storage`, `calldata`, `payable`, `constant` are Solidity reserved keywords. Using them as contract or variable names causes cryptic compiler errors:

```solidity
// ❌ FAILS — "memory" is a keyword
SharedMemory public memory;
// Error: Expected identifier but got 'memory'

// ✅ FIX — use a different name
SharedMemory public sharedMem;
SharedMemory public memStore;
```

**Common keywords to avoid as names:** `memory`, `storage`, `calldata`, `payable`, `constant`, `immutable`, `virtual`, `override`, `revert`, `emit`.

**Rule:** When naming contract instances, add a descriptive suffix or abbreviation: `sharedMem`, `tokenStore`, `escrowContract`.

## Pitfall 7: Error and Event Name Collisions

**Problem:** Solidity doesn't allow both an `error` and an `event` with the same name in one contract:

```solidity
// ❌ FAILS — "Identifier already declared"
error CircuitBreakerTripped();
event CircuitBreakerTripped(uint256 totalLoss);
// Error: Identifier already declared. The previous declaration is here.

// ✅ FIX — rename one of them
error CircuitBreakerActive();
event CircuitBreakerTripped(uint256 totalLoss);
```

**Rule:** Use different naming conventions: errors describe *what went wrong* (e.g., `NotAuthorized`, `InsufficientBalance`), events describe *what happened* (e.g., `TransferCompleted`, `BreakerTripped`).

## Pitfall 8: Struct Field Access on Mapping Auto-Getters

**Problem:** Public mappings of structs generate getter functions that return the full struct, but chained field access in a single expression can fail depending on how the compiler resolves the struct return:

```solidity
mapping(uint256 => Agent) public agents;
mapping(address => uint256) public agentIdByOwner;

// ❌ MAY FAIL — nested call + field access in one expression
bool active = AgentRegistry(registry).agents(
    AgentRegistry(registry).agentIdByOwner(msg.sender)
).isActive;
// Error: Member "isActive" not found or not visible after argument-dependent lookup

// ✅ FIX — use a dedicated view function instead
Agent memory a = AgentRegistry(registry).getAgent(msg.sender);
bool active = a.isActive;
```

**Why:** The auto-generated getter for `agents(uint256)` returns a tuple, and accessing `.isActive` on it depends on the compiler's struct return handling. View functions like `getAgent()` that return explicit `memory` structs are safer.

**Rule:** When checking nested struct fields across contracts, use explicit getter functions rather than chained mapping auto-getters.

## Pitfall 9: Pause Functions Need Idempotency Guards

**Problem:** A `pause()` function without a check for current state can be called multiple times without reverting, which causes confusing test failures:

```solidity
function pause() external {
    isPaused = true; // No check — always sets to true
    emit Paused();
}

function unpause() external {
    if (!isPaused) revert NotPaused(); // Has a guard
    isPaused = false;
    emit Unpaused();
}
```

```solidity
// Test: calling pause() twice
coordinator.pause();                              // ✅ Works
vm.expectRevert(Paused.selector);
coordinator.pause();                              // ❌ Does NOT revert — just sets isPaused=true again
```

**Fix:** Add a guard to `pause()` too:

```solidity
function pause() external {
    if (isPaused) revert AlreadyPaused(); // Guard
    isPaused = true;
    emit Paused();
}
```

**Rule:** State-toggling functions (`pause`/`unpause`, `activate`/`deactivate`) should be idempotent — either add guards to both directions, or document that double-calls are no-ops and write tests accordingly.

## Pitfall 10: `external` Functions Can't Be Called Internally

**Problem:** A contract has an `external view` function, and another function in the same contract tries to call it:

```solidity
function calculateDiscount(uint256 spent) external view returns (uint256) {
    // ...
}

function getDiscountedAmount(uint256 usdPrice, uint256 spent) external view returns (uint256) {
    uint256 discount = calculateDiscount(spent); // ❌ Compiler error
    // Error: Undeclared identifier. "calculateDiscount" is not (or not yet) visible at this point.
}
```

**Why:** In Solidity, `external` functions cannot be called from within the same contract using just the function name. The compiler error message is confusing — it says "not visible" rather than "external can't be called internally."

**Fix:** Change to `public`:

```solidity
function calculateDiscount(uint256 spent) public view returns (uint256) { // ✅ public
    // ...
}

function getDiscountedAmount(uint256 usdPrice, uint256 spent) external view returns (uint256) {
    uint256 discount = calculateDiscount(spent); // ✅ Works
}
```

**Alternative:** Use `this.calculateDiscount(spent)` (makes an external call, costs more gas, not recommended).

**Rule:** If a function needs to be called both externally AND from within the contract, make it `public`, not `external`.

## Pitfall 11: `forge init` and `forge install` Flag Incompatibility

**Problem:** Some Foundry versions don't support `--no-commit` flag:

```bash
forge init . --force --no-commit   # ❌ "unexpected argument '--no-commit'"
forge install oz/openzeppelin --no-commit  # ❌ Same error
```

**Fix:** Just omit the flag:

```bash
forge init . --force               # ✅ Works
forge install oz/openzeppelin@v5   # ✅ Works
```

**Note:** If working in a git repo, `forge install` will auto-commit. To avoid that, stage your work first or just `git reset` after install.

**Also:** After `forge init`, always clean up template files you don't need (`Counter.sol`, any `Mock*.sol` in `src/`, template tests in `test/`). They can cause phantom compilation errors if they import things that don't exist.

## Pitfall 12: Tests Break When Adding Access Control

**Problem:** You add `onlyOwner` or `onlyRouter` to a function, and tests that directly called it now revert:

```solidity
// Before: anyone could call split()
function split(address from, uint256 amount) external { ... }

// After: only router can call
modifier onlyRouter() { require(msg.sender == router); _; }
function split(address from, uint256 amount) external onlyRouter { ... }
```

```solidity
// ❌ TEST FAILS — "BurnSplitter: only router"
function test_burnSplit70_30() public {
    vm.prank(user);
    burnSplitter.split(user, 1000 ether); // Reverts!
}
```

**Fix:** Update the test to prank as the authorized caller:

```solidity
// ✅ CORRECT — prank as the router
function test_burnSplit70_30() public {
    vm.prank(address(router));
    burnSplitter.split(user, 1000 ether); // Passes
}
```

**Rule:** When hardening access control, search for all direct calls to the function in tests and update `vm.prank` to the authorized address. Use `forge test --match-test` to find failures quickly.

## Pitfall 13: Circular Dependency in Constructor Deployment

**Problem:** Contract A needs Contract B's address in its constructor, and Contract B needs Contract A's address:

```solidity
// BurnSplitter needs router address
new BurnSplitter(techToken, treasury, ???); // What goes here?

// TechPaymentRouter needs burnSplitter address
new TechPaymentRouter(techToken, discountCalc, burnSplitter);
```

**Solution:** Deploy with a placeholder, then wire up after:

```solidity
// Step 1: Deploy BurnSplitter with test contract as temporary router
burnSplitter = new BurnSplitter(address(techToken), treasury, address(this));

// Step 2: Deploy Router with real BurnSplitter
router = new TechPaymentRouter(address(techToken), address(discountCalc), address(burnSplitter));

// Step 3: Wire BurnSplitter to accept calls from router
// (test contract is still the router at this point, so it can call setRouter)
burnSplitter.setRouter(address(router));
```

**BurnSplitter pattern:**
```solidity
address public router;

function setRouter(address newRouter) external onlyRouter {
    require(newRouter != address(0));
    router = newRouter;
}

modifier onlyRouter() {
    require(msg.sender == router, "BurnSplitter: only router");
    _;
}
```

**Rule:** When two contracts have a circular dependency, deploy the "owned" contract first with a placeholder owner, deploy the owner contract second, then wire them. The owned contract needs a `setOwner`/`setRouter` callable by the initial placeholder.

## Pitfall 14: Cross-Contract `msg.sender` Chain with `vm.prank`

**Problem:** Contract A calls Contract B. When testing, you `vm.prank(user)` and call A. But `msg.sender` inside B is **A's address**, not `user`. This breaks any access control in B that expects the original caller.

**Example — Escrow calls Resolver:**
```solidity
// AgentEscrow.openDispute() calls resolver.fileDispute()
function openDispute(...) external {
    // msg.sender here = buyer (from vm.prank)
    if (msg.sender != escrow.buyer) revert NotAuthorized();

    resolver.fileDispute(context); // msg.sender to resolver = this escrow contract!
}

// HumanDisputeResolver.fileDispute()
function fileDispute(DisputeContext calldata ctx) external {
    // ❌ This check FAILS when called via escrow — msg.sender is escrow, not buyer
    if (msg.sender != ctx.buyer && msg.sender != ctx.seller) revert NotPartyToDispute();
}
```

**Fix — remove redundant checks in the callee:**
```solidity
// Resolver trusts the context passed by escrow (escrow already verified the party)
function fileDispute(DisputeContext calldata ctx) external {
    // No party check — escrow handles authorization
    if (escrowHasDispute[ctx.escrowId]) revert EscrowAlreadyHasDispute();
    // ...
}
```

**Rule:** When Contract A is the authorized caller of Contract B, B should either:
1. Trust A's context (A handles auth) — cleanest
2. Store A's address and check `msg.sender == trustedCaller` — defense-in-depth

Never have both contracts check the same authorization independently.

## Pitfall 15: Constructor Parameter Cascading

**Problem:** Adding a new parameter to a contract constructor affects EVERY file that deploys it:
- All test `setUp()` functions that instantiate the contract
- Deploy scripts
- Other contracts that deploy it internally

**Example — Adding `resolver` to AgentEscrow constructor:**
```solidity
// Before: 2 params
constructor(address _aiValidator, address _usdc) ...

// After: 3 params
constructor(address _aiValidator, address _usdc, address _resolver) ...
```

**Broke:** 3 test files + 1 deploy script — all needed `address(0)` or a real resolver address.

**Fix pattern:**
```bash
# Find all instantiation sites
grep -rn "new AgentEscrow(" test/ script/

# Update each one — pass address(0) if resolver not needed for that test
escrow = new AgentEscrow(address(validator), address(usdc), address(0));
```

**Rule:** When changing a constructor signature, grep for all `new ContractName(` before compiling. Use `address(0)` as a safe default for optional parameters.

## Pitfall 16: OpenZeppelin v5 Custom Errors

**Problem:** OZ v5 uses custom errors instead of string revert messages. Tests expecting strings will fail.

```solidity
// OZ v4 (string message)
vm.expectRevert("Ownable: caller is not the owner");

// OZ v5 (custom error: OwnableUnauthorizedAccount(address))
vm.expectRevert(); // ✅ Just check it reverts — don't match the error
```

**If you need to match the specific error:**
```solidity
// Import the error from OZ
import {OwnableUnauthorizedAccount} from "@openzeppelin/contracts/access/Ownable.sol";

vm.expectRevert(
    abi.encodeWithSelector(OwnableUnauthorizedAccount.selector, rando)
);
```

**Rule:** When testing OZ v5 `Ownable`, `Pausable`, or `AccessControl` reverts, use `vm.expectRevert()` with no arguments unless you specifically need to match the error type.

## Pitfall 17: Error Precedence in State Machines

**Problem:** When a function checks multiple error conditions, the first matching check reverts — even if a more specific error exists further down.

```solidity
function executeVerdict(uint256 disputeId) external {
    Dispute storage d = disputes[disputeId];
    if (d.id == 0) revert DisputeNotFound();          // Check 1
    if (d.status != DisputeStatus.Resolved) revert DisputeNotResolved(); // Check 2
    if (d.executedAt != 0) revert DisputeAlreadyExecuted();             // Check 3
    // ...
}
```

**After first execution:** `status = Executed` (not `Resolved`), so Check 2 reverts with `DisputeNotResolved` — NOT `DisputeAlreadyExecuted`.

**Test gotcha:**
```solidity
// ❌ WRONG — expects the more specific error
vm.expectRevert(DisputeAlreadyExecuted.selector);

// ✅ CORRECT — respects the actual check order
vm.expectRevert(DisputeNotResolved.selector);
```

**Rule:** Write tests that match the ACTUAL error precedence in the code, not the logical error you'd expect. Read the function top-to-bottom — the first matching `if` is the error you'll get.

## Pitfall 18: IResolver Interface Pattern (Escrow + Resolver Decoupling)

**Pattern:** When a dispute resolution system should support multiple resolver strategies:

```solidity
interface IResolver {
    struct DisputeContext {
        uint256 escrowId;
        address buyer;
        address seller;
        address token;
        uint256 amount;
        string serviceDescription;
        bytes metadata; // Opaque — each impl encodes what it needs
    }

    function fileDispute(DisputeContext calldata ctx) external returns (uint256 disputeId);
    function executeVerdict(uint256 disputeId) external returns (uint256 buyerPayout, uint256 sellerPayout);
    function isReady(uint256 disputeId) external view returns (bool ready);
}
```

**Key design principles:**
1. **Resolver does NOT handle fund transfers** — returns amounts, escrow executes
2. **Escrow passes context in** — resolver doesn't import escrow
3. **Metadata is opaque bytes** — each implementation encodes what it needs
4. **isReady() handles async resolution** — e.g., GenLayer consensus finality

**Escrow integration:**
```solidity
// Escrow stores resolver reference
IResolver public resolver;

// Open dispute: escrow builds context, resolver stores it
function openDispute(uint256 _escrowId, string calldata _reason) external returns (uint256) {
    Escrow storage e = escrows[_escrowId];
    if (msg.sender != e.buyer && msg.sender != e.seller) revert NotAuthorized();
    uint256 disputeId = resolver.fileDispute(IResolver.DisputeContext({...}));
    e.status = EscrowStatus.Disputed;
    return disputeId;
}

// Execute: escrow checks readiness, gets amounts, does transfers
function resolveDispute(uint256 _escrowId) external {
    if (!resolver.isReady(disputeId)) revert NotReady();
    (uint256 buyerPayout, uint256 sellerPayout) = resolver.executeVerdict(disputeId);
    if (buyerPayout > 0) usdc.transfer(escrow.buyer, buyerPayout);
    if (sellerPayout > 0) usdc.transfer(escrow.seller, sellerPayout);
}
```

**Benefit:** Proves swap-ability — both resolvers pass the same test suite, escrow doesn't care which one it uses.

## Debugging Workflow

When a Foundry test fails with assertion mismatch:

1. **Check if `msg.sender` is correct** — add `console.log("sender:", msg.sender)` or use `vm.prank`
2. **Check initialization** — are state variables set before the test scenario?
3. **Check time assumptions** — does `vm.warp` affect the logic as expected?
4. **Read the trace** — `forge test -vvvv` shows full call trace with storage reads
5. **Isolate the failure** — `forge test --match-test testName -vvv` runs just that test

## Quick Reference

| Scenario | Need `vm.prank`? |
|----------|-----------------|
| Calling `pay()` which reads `msg.sender` | ✅ Yes |
| Calling `getDailySpending()` which reads `msg.sender` | ✅ Yes |
| Reading `spentToday(address)` (public mapping getter) | ❌ No — takes explicit address |
| Reading `dailyLimits(address)` (public mapping getter) | ❌ No — takes explicit address |
| `vm.expectRevert` before a call that should revert | ✅ Yes, prank before expectRevert |
