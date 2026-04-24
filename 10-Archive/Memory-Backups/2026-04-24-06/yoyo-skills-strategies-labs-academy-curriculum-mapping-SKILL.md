---
name: labs-academy-curriculum-mapping
description: Protocol for mapping external educational material (e.g., Cyfrin Updraft) to internal live smart contracts for the Labs Academy training program.
---

# Labs Academy Curriculum Mapping

## Trigger
Use this skill when designing "Labs Academy" modules to ensure theoretical security/architecture lessons are immediately applied to Gentech's own live codebases.

## Workflow
1. **Identify Theoretical Concept**: Select a lesson or module from the source material (e.g., Cyfrin Updraft).
2. **Scan Live Contracts**: Search `/root/vaults/gentech/03-Projects/` or GitHub for implementation of that pattern.
3. **Map Implementation**:
    - Locate exact line numbers in the contract.
    - Describe how the live code implements the theoretical pattern.
    - Identify "Edge Cases" in the live code that go beyond the basic lesson.
4. **Design Lab Task**: Create a "destructive" or "analytical" exercise:
    - *Analytical*: "Why is this modifier here?"
    - *Destructive*: "What happens if we remove this line?"
5. **Verification**: Ensure the task proves the student understands the *risk* prevented by the pattern.

## Example Mapping (Module 1)
- **Concept**: Checks-Effects-Interactions (CEI)
- **Target**: `AgentEscrow.sol`
- **Implementation**: State update to `Released` occurs before `USDC.safeTransfer`.
- **Task**: Move the transfer above the state update $\rightarrow$ analyze why this creates a reentrancy vulnerability.

## Pitfalls
- **Over-simplification**: Avoid mapping "Happy Path" code. Focus on the guards, the `revert` statements, and the constraints.
- **Stale Code**: Always verify the contract version in GitHub before mapping line numbers.
