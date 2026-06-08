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

## Phase 2: Deployment + Integration + UI ✅ COMPLETE (May 19, 2026)

**Status:** All 4 tasks shipped. 17/17 tests passing.

### 1. Deployment Script ✅
- Enhanced `script/Deploy.s.sol` with multi-network support (Arb Sepolia + Arb One)
- Post-deployment agent authorization via `AGENT_ADDRESSES` env var
- Built-in verification (owner check, authorization check)
- Added `test/Deploy.t.sol` (3 tests) for deployment validation
- Source verification support for Arbiscan

### 2. Agent Integration ✅
- New `agent/register_signals.py` — full on-chain registration client
- Web3.py bridge with SignalRegistry ABI
- Single registration and batch registration (up to 20 per tx)
- Dry-run mode for signal generation without submission
- Authorization verification before submission
- Gas-efficient: ~137K gas per single, ~500K for batch of 10

### 3. Frontend/UI ✅
- New `frontend/index.html` — zero-dependency Signal Explorer
- Direct RPC connection via ethers.js (no build step, no server)
- Stats dashboard: total signals, owner, type count, chain ID
- Filter by signal type, search by hash/ID
- URL params for quick sharing: `?contract=0x...&rpc=...`

### 4. Documentation ✅
- README fully updated with Phase 2 content
- Deployment guide with network tables and verification steps
- Gas benchmarks table
- Updated architecture diagram with client + frontend layers
- Complete usage examples for every component

## Files (Phase 2)
- `script/Deploy.s.sol` — Enhanced deployment script
- `test/Deploy.t.sol` — Deployment tests (3 tests)
- `agent/register_signals.py` — On-chain registration client
- `frontend/index.html` — Signal Explorer UI
- `README.md` — Updated documentation

## Files
- Contract: `SignalRegistry.sol`
- Tests: `SignalRegistry.t.sol`
