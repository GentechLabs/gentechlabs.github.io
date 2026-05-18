# SignalRegistry — Agent Signal On-Chain Registry

## Project Overview
Smart contract for storing agent signal hashes on-chain — proof of agent-chain interaction.
Part of Gentech Labs dev work.

## Phase 1: Core Contract ✅ COMPLETE (May 18, 2026)

**Status:** Built, compiled, 14/14 tests passing.

**Contract:** `SignalRegistry.sol`
- Stores agent signal hashes on-chain (proof of agent-chain interaction)
- Batch registration (up to 20 signals per tx)
- Agent authorization system
- Signal verification and query functions
- Gas-efficient: single signal ~137K gas

**Test Coverage:**
- ✅ Registration (single + batch)
- ✅ Authorization/deauthorization
- ✅ Verification queries
- ✅ Error handling (empty hash, empty agent, etc.)

## Phase 2: TODO (queued for tomorrow)
- [ ] Deployment script (testnet)
- [ ] Integration with agent signaling workflow
- [ ] Frontend/UI for querying signals
- [ ] Documentation + README

## Files
- Contract: `SignalRegistry.sol`
- Tests: `SignalRegistry.t.sol`
