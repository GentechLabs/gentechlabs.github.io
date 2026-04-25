# AgentEscrow — Quick Reference

## One-Liner

> AgentEscrow is AI-validated escrow for autonomous agents. Lock USDC, verify work with EIP-712 signatures, release funds automatically — no humans, no trust required.

## For Builders (Copy-Paste Integration)

```solidity
// Escrow 100 USDC for a service
uint256 id = agentEscrow.createEscrow(seller, 100_000000);

// Seller marks done
agentEscrow.markComplete(id);

// AI validator signs off-chain
bytes32 digest = keccak256(abi.encode(
    keccak256("Validation(uint256 escrowId)"), id
));
(bytes32 r, bytes32 s, uint8 v) = vm.sign(validatorKey, digest);

// Release funds
agentEscrow.validateAndRelease(id, abi.encodePacked(r, s, v));
```

## For Users

| Payment Method | Cost | Best For |
|---------------|------|----------|
| USDC (direct) | 100% | Simple, no token exposure |
| $TECH (via router) | 75% (-25% discount) | Token holders, frequent users |

## Test It

```bash
git clone https://github.com/ProtoJay4789/agent-escrow.git
cd agent-escrow
forge test -v  # 49/49 passing
```

## Deployed Where?

Currently local/testnet only. Kite AI testnet (Chain ID 2368) deployment is next.

## Learn More

- Full README: https://github.com/ProtoJay4789/agent-escrow#readme
- Architecture diagram: `docs/Kite-AI-Architecture.html`
- Demo script: `docs/demo-video-script.md`
