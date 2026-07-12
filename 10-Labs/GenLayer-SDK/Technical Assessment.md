# GenLayer SDK Technical Assessment

> **Date:** 2026-04-19
> **Author:** Hermes Agent (Nous Research)
> **Purpose:** Evaluate feasibility of building Kite L4 (Enforcement/SLAs) or L5 (Marketplace + Escrow) as a GenLayer "Skill" (Intelligent Contract)
> **Target:** ETHGlobal Open Agents (May 3, $50K)

---

## 1. Executive Summary

GenLayer does **not** have a standalone "Skills SDK" in the sense of a separate framework for building revenue-sharing contract templates. The term "GenLayer Skills" refers to a **Claude Code plugin marketplace** (github.com/genlayerlabs/skills) providing dev tooling plugins for linting, testing, and validator node setup.

The actual building primitive is the **Intelligent Contract** — a Python-based smart contract running on GenVM, a WASM-based VM with native LLM and web access. Every Intelligent Contract is functionally a "skill" in that it encodes AI-powered logic with on-chain enforcement. There is no distinct "skill builder" revenue-share model documented in their official docs — validators earn staking rewards (10% operator fee), and contract builders earn through whatever economics they design into their contracts.

**Verdict:** Building Kite L4/L5 as GenLayer Intelligent Contracts is **feasible for L4 (Enforcement/SLAs)** and **partially feasible for L5 (Escrow)**. The architecture maps well to GenLayer's capabilities, but there are meaningful constraints around execution latency, cost model, and composability with existing Kite infrastructure.

---

## 2. Architecture Deep Dive

### 2.1 Two-Layer Architecture

GenLayer operates as two integrated layers:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GenLayer Chain** | zkSync Elastic Chain (EVM-compatible L2) | Account balances via ghost contracts, standard Ethereum ops (`eth_*` methods), anchors to Ethereum security |
| **GenVM** | WebAssembly VM (Wasmtime) with embedded Python interpreter | Executes Intelligent Contracts — Python classes with native LLM/web access |

**Key concept:** Every Intelligent Contract has a corresponding **ghost contract** on the chain layer at the same address. Ghost contracts hold GEN balances, relay transactions to consensus, and execute external messages.

```
User → eth_sendRawTransaction → Ghost Contract → ConsensusMain → GenVM Execution → Result back on-chain
```

### 2.2 GenVM Execution Environment

- **Language:** Python (3.12+) — not Solidity/Rust
- **Runtime:** WASM-based (Wasmtime), sandboxed Python interpreter
- **Storage:** Persistent on-chain via class-level typed fields
- **Import restrictions:** Forbidden: `os`, `sys`, `subprocess`, etc. (statically linted by `genvm-lint`)
- **Contract format:** Single Python class extending `gl.Contract`, one contract per file

```python
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class MyContract(gl.Contract):
    counter: u32

    def __init__(self):
        self.counter = 0

    @gl.public.view
    def get_counter(self) -> int:
        return self.counter

    @gl.public.write
    def increment(self):
        self.counter = self.counter + 1
```

### 2.3 Consensus: Optimistic Democracy

GenLayer uses **Optimistic Democracy** — an enhanced dPoS where validators run diverse AI models:

1. User submits transaction
2. Leader validator executes contract, proposes result
3. Validators independently re-compute and submit encrypted votes
4. Leader reveals execution data
5. Validators reveal votes
6. If majority agrees → Accepted → Finality window → Finalized
7. Any party can appeal → larger validator set re-evaluates

**Equivalence Principle** handles non-determinism:
- **`strict_eq`**: Exact match (deterministic outputs only)
- **`run_nondet_unsafe(leader_fn, validator_fn)`**: Custom leader/validator pattern (recommended for LLM calls)
- **`prompt_comparative`**: LLM-based comparison convenience wrapper
- **`prompt_non_comparative`**: Validator evaluates leader output without re-running

### 2.4 Network Environments

| Network | Purpose | RPC | Setup |
|---------|---------|-----|-------|
| **Localnet** | Local dev | `http://localhost:4000/api` | `genlayer init && genlayer up` (Docker) |
| **Studionet** | Hosted dev | `https://studio.genlayer.com/api` | Zero setup, browser |
| **Testnet Asimov** | Infra/stress testing | `https://rpc-asimov.genlayer.com` | Faucet available |
| **Testnet Bradbury** | Production-like + real AI | `https://rpc-bradbury.genlayer.com` | Faucet available |

Chain ID: 4221 (testnets), 61999 (studionet), 61127 (localnet)

---

## 3. Programming Model

### 3.1 Contract Structure

```
# Version comment (like pragma solidity)
{ "Depends": "py-genlayer:<hash>" }

# Imports
from genlayer import *

# Contract class
class ContractName(gl.Contract):
    # State variables (typed, persistent)
    field: Type

    # Constructor (not decorated)
    def __init__(self, init_args):
        self.field = init_args

    # Read-only methods
    @gl.public.view
    def getter(self) -> ReturnType:
        return self.field

    # State-modifying methods
    @gl.public.write
    def setter(self, value: Type):
        self.field = value

    # Payable methods (receive GEN)
    @gl.public.write.payable
    def pay_me(self):
        amount = gl.message.value
        ...
```

### 3.2 Storage Types

| Python Type | GenVM Replacement | Notes |
|-------------|-------------------|-------|
| `list[T]` | `DynArray[T]` | Persistent dynamic array |
| `dict[K,V]` | `TreeMap[K,V]` | Persistent ordered map (str keys for calldata) |
| `int` | `u8`..`u256`, `i8`..`i256` | Sized integers enforced on storage |
| Custom classes | `@allow_storage @dataclass` | Must be decorated for storage |

### 3.3 Non-Deterministic Operations

**Critical rule:** All `gl.nondet.*` calls MUST be inside equivalence principle blocks. Storage writes, contract calls, and message emission MUST be outside.

```python
@gl.public.write
def make_decision(self, data: str):
    def leader_fn():
        # Non-deterministic: LLM call
        response = gl.nondet.exec_prompt(
            f"Evaluate: {data}",
            response_format="json"
        )
        return json.loads(response)

    def validator_fn(leaders_res) -> bool:
        if not isinstance(leaders_res, gl.vm.Return):
            return False
        my_result = leader_fn()
        # Compare decision fields, not reasoning text
        return my_result["decision"] == leaders_res.calldata["decision"]

    result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
    # Storage write AFTER consensus
    self.decision = result["decision"]
```

### 3.4 Web Access

```python
# HTTP requests
response = gl.nondet.web.request(url, method='POST', body={})

# Page rendering (HTML/text/screenshot)
html = gl.nondet.web.render(url, mode='html')
screenshot = gl.nondet.web.render(url, mode='screenshot')

# Convenience GET
response = gl.nondet.web.get(url)
```

### 3.5 Inter-Contract Communication

| Pattern | Mechanism | Timing |
|---------|-----------|--------|
| **IC → IC** | `other.emit(on='finalized').method()` | Async, after parent tx accepted/finalized |
| **IC → EVM** | `@gl.evm.contract_interface` → `.emit()` | On finalization only |
| **IC → EOA** | `._Recipient(addr).emit_transfer(value=...)` | On finalization |
| **View calls** | `other.view().method()` | Synchronous, current block state |
| **Deploy child** | `gl.deploy_contract(code=..., salt=..., on='...')` | Async |

### 3.6 Value Transfers (GEN)

- Native token: GEN, denominated in wei (1 GEN = 10¹⁸ wei)
- `@gl.public.write.payable` methods receive `gl.message.value`
- `self.balance` reads from ghost contract on chain layer
- Internal messages: `other.emit(value=u256(amount), on='finalized').deposit()`

---

## 4. Developer Workflow: Zero → Deployed Contract

### 4.1 Setup (10-15 minutes)

```bash
# Prerequisites: Python 3.12+, Node.js 18+, Docker 26+

# Clone boilerplate
git clone https://github.com/genlayerlabs/genlayer-project-boilerplate
cd genlayer-project-boilerplate
pip install -r requirements.txt

# Install CLI
npm install -g genlayer
genlayer init
genlayer up          # Starts local Studio at localhost:8080
```

### 4.2 Development Loop

```bash
# 1. Write contract in contracts/
# 2. Lint
genvm-lint check contracts/my_contract.py

# 3. Direct mode tests (fast, in-memory, no server)
pytest tests/direct/ -v

# 4. Integration tests (against Studio/localnet)
gltest tests/integration/ -v -s --network localnet
```

### 4.3 Deploy

```bash
# CLI (simple)
genlayer deploy --contract contracts/my_contract.py --args "arg1" 42

# Deploy scripts (complex, multi-contract)
genlayer deploy    # Runs deploy/*.ts in order

# Testnet
genlayer network testnet-bradbury
genlayer deploy --contract contracts/my_contract.py
```

### 4.4 Frontend Integration

```typescript
import { createClient, createAccount } from 'genlayer-js';

const client = createClient({
  chain: testnetBradbury,
  account: createAccount(privateKey),
});

// Read
const result = await client.readContract({
  address: contractAddress,
  functionName: "get_status",
  args: [orderId],
});

// Write
const txHash = await client.writeContract({
  address: contractAddress,
  functionName: "submit_evidence",
  args: [orderId, evidenceHash],
});

const receipt = await client.waitForTransactionReceipt({
  hash: txHash,
  status: "FINALIZED",
});
```

---

## 5. Technical Constraints

### 5.1 Language & Runtime

| Aspect | Constraint |
|--------|-----------|
| **Language** | Python only (no Solidity/Rust/TS contracts) |
| **Runtime** | WASM sandbox — no `os`, `sys`, `subprocess`, file I/O, network sockets |
| **One contract per file** | Single `gl.Contract` subclass per `.py` file |
| **Version pinning** | Magic comment pins GenVM version hash |
| **No debugger** | `print()` and `gl.trace` only — no interactive debugger |

### 5.2 Gas Model

- Transactions require gas, but Studio/localnet don't simulate gas costs
- Gas covers appeals — users can include optional tips for appeal coverage
- LLM calls and web requests add significant computational cost vs deterministic contracts
- Validators run full LLM inference per transaction — real cost passed through
- **No detailed gas pricing table found in docs** — gas model is opaque

### 5.3 Data Access

| Capability | Available | Method |
|-----------|-----------|--------|
| **Web HTTP** | ✅ | `gl.nondet.web.request()` / `.get()` |
| **Web rendering** | ✅ | `gl.nondet.web.render(mode='html/screenshot')` |
| **LLM calls** | ✅ | `gl.nondet.exec_prompt()` |
| **Image processing** | ✅ | `gl.nondet.exec_prompt(images=[bytes])` (max 2) |
| **Vector search** | ✅ | `VecDB` from stdlib |
| **EVM contract reads** | ✅ | `@gl.evm.contract_interface` → `.view()` |
| **EVM contract writes** | ✅ | `.emit()` on finalization |
| **Random** | ⚠️ | Seeded only (use `message` fields, time, stdin hash) |
| **External APIs** | ✅ | Via `gl.nondet.web.request()` |
| **File system** | ❌ | Sandboxed WASM |
| **Raw network** | ❌ | Only via `gl.nondet.web.*` |

### 5.4 Latency & Finality

- **Transaction lifecycle**: Pending → Proposing → Committing → Leader Revealing → Revealing → Accepted → Finalized
- **Appeal process**: Multiple rounds possible (up to ~6 depending on validator set size)
- **LLM inference latency**: Each validator independently runs LLM — adds significant delay
- **Finality window**: Configurable — appeal window must close before finalization
- **Fast finality**: Possible by paying for all validators to validate immediately (costly)
- **Estimated end-to-end**: Seconds to minutes for simple calls; longer for LLM-heavy contracts

### 5.5 Token Economics

- Native token: **GEN**
- Validator rewards: Proportional to stake and transaction volume
- Validator operator fee: 10% before distribution to delegators
- **No documented "skill builder revenue share"** — the 10-20% figure from context appears to be either:
  - Validator fee structure (10% operator fee is documented)
  - A feature of the GenLayer Portal (portal.genlayer.foundation) — not documented in the SDK
  - Potentially a newer/unpublished feature

---

## 6. Kite Layer Feasibility Analysis

### 6.1 L4 (Enforcement/SLAs) — ✅ FEASIBLE

**Mapping:** Kite L4 handles SLAs, disputes, slashing, and trust enforcement. This maps directly to GenLayer's core strengths:

| Kite L4 Feature | GenLayer Implementation |
|----------------|------------------------|
| **SLA Monitoring** | `gl.nondet.web.request()` to check service endpoints, APIs, deliverables |
| **Dispute Resolution** | `gl.nondet.exec_prompt()` for AI evaluation of evidence against SLA terms |
| **Quality Evaluation** | LLM-based assessment with equivalence principle for validator consensus |
| **Evidence Processing** | `gl.nondet.exec_prompt(images=[...])` for screenshot/photo evidence |
| **Automated Verdicts** | Contract state changes based on consensus-agreed LLM output |
| **Slashing/Penalties** | Value transfers via `gl.message.value` and internal messages |
| **Appeal mechanism** | GenLayer's native appeal process provides multi-round dispute escalation |

**Example L4 Contract Skeleton:**

```python
from genlayer import *
import json

@allow_storage
@dataclass
class SLA:
    service: str
    metrics: str          # Natural language SLA terms
    stake: u256
    deadline: u256
    resolved: bool

class KiteEnforcement(gl.Contract):
    agreements: DynArray[SLA]

    @gl.public.write.payable
    def create_sla(self, service: str, metrics: str, deadline: u256):
        if gl.message.value == u256(0):
            raise gl.vm.UserError("stake required")
        sla = SLA(service=service, metrics=metrics,
                  stake=gl.message.value, deadline=deadline, resolved=False)
        self.agreements.append(sla)

    @gl.public.write
    def dispute(self, agreement_id: u32, evidence: str):
        sla = self.agreements[agreement_id]
        if sla.resolved:
            raise gl.vm.UserError("already resolved")

        def leader_fn():
            prompt = f"""
            Evaluate SLA compliance.
            SLA terms: {sla.metrics}
            Evidence: {evidence}
            Service: {sla.service}
            Return JSON: {{"compliant": true/false, "reasoning": "..."}}
            """
            return gl.nondet.exec_prompt(prompt, response_format="json")

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            my_result = leader_fn()
            return my_result["compliant"] == leaders_res.calldata["compliant"]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        sla.resolved = True

        if not result["compliant"]:
            # Slash: redistribute stake
            # ... penalty logic ...
```

**Pros:**
- Native subjective decision-making is GenLayer's core value prop
- Web access lets contracts independently verify service status
- Built-in appeal process replaces custom dispute escalation
- Python is easier to develop/maintain than Solidity
- Image processing supports visual evidence (screenshots, receipts)

**Cons:**
- Latency: LLM inference on every validator adds significant delay (seconds to minutes)
- Cost: Each LLM call is expensive — not suitable for high-frequency monitoring
- No persistent background execution — contracts only run when called
- Web access is per-validator (each validator independently fetches), not a shared oracle

### 6.2 L5 (Marketplace + Escrow) — ⚠️ PARTIALLY FEASIBLE

**Mapping:** Kite L5 handles agent discovery, reputation, and payment escrow.

| Kite L5 Feature | GenLayer Implementation | Feasibility |
|----------------|------------------------|-------------|
| **Payment Escrow** | `@gl.public.write.payable` + internal messages | ✅ Straightforward |
| **Agent Registry** | `TreeMap[Address, AgentProfile]` with `DynArray` | ✅ Native |
| **Reputation System** | Contract state tracking + LLM-assisted scoring | ✅ Feasible |
| **Agent Discovery** | View methods + frontend (GenLayerJS) | ✅ Feasible |
| **Multi-party Escrow** | Contract holds GEN, releases on conditions | ✅ Feasible |
| **Cross-chain payments** | External messages to EVM contracts on zkSync L2 | ⚠️ Limited (finalization only) |
| **Order matching** | Deterministic matching in contract logic | ✅ Feasible |
| **High-frequency trades** | Not suitable — LLM latency too high | ❌ Not viable |

**Key Constraint for L5:** GenLayer is optimized for **subjective judgment**, not high-throughput deterministic operations. A marketplace that needs fast order matching, price updates, or frequent state changes would be better on a traditional L2.

**Best fit:** L5 as a **dispute-aware escrow layer** — agents discover each other off-chain or via a traditional registry, but payments and dispute resolution flow through GenLayer Intelligent Contracts.

---

## 7. SDK & Tooling Ecosystem

### 7.1 Available SDKs

| SDK | Language | Purpose |
|-----|----------|---------|
| **genlayer (Python)** | Python | Intelligent Contract development (GenVM) |
| **genlayer-js** | TypeScript | Frontend DApp development (Viem-based) |
| **genlayer-test** | Python | Testing framework (direct mode + GLSim + integration) |
| **genvm-linter** | Python | Static analysis for contract safety |
| **genlayer CLI** | Node.js | Deployment, network management, Studio |

### 7.2 Development Tools

| Tool | Description |
|------|-------------|
| **GenLayer Studio** | Web IDE at studio.genlayer.com or local Docker instance |
| **GLSim** | Lightweight simulator (`pip install genlayer-test[sim]`) |
| **VS Code Extension** | Syntax highlighting, snippets |
| **GenLayer Skills** | Claude Code plugins for dev tooling |
| **GenLayer MCP Server** | `genlayer-mcp` for AI-assisted contract generation |
| **GenLayer Docs MCP** | `docs-mcp.genlayer.com` for doc search |

### 7.3 Testing Strategy

```python
# Direct mode (fast, in-memory)
def test_dispute(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/kite_enforcement.py")
    direct_vm.sender = direct_alice

    # Mock web/LLM for testing
    direct_vm.mock_web(r".*api\.service\.com.*", {"status": 200, "body": '{"uptime": "99.5%"'})
    direct_vm.mock_llm(r".*Evaluate SLA.*", '{"compliant": false, "reasoning": "..."}')

    contract.create_sla(args=["api", "99.9% uptime", 1000], value=1000)
    contract.dispute(args=[0, "Service was down"])
    assert contract.get_agreement(0).resolved == True
```

---

## 8. Build Strategy for ETHGlobal (May 3)

### 8.1 Recommended Approach: L4 Enforcement Skill

Given L4 is 60% ready and maps directly to GenLayer's strengths:

**Week 1 (now - Apr 26):**
1. Clone genlayer-project-boilerplate
2. Build `KiteEnforcement` Intelligent Contract with:
   - SLA creation with staking
   - Dispute submission with evidence
   - LLM-based verdict (equivalence principle)
   - Automated payout/slashing
3. Write direct mode tests with mocked LLM/web
4. Test in Studio with real LLM

**Week 2 (Apr 27 - May 2):**
1. Deploy to Testnet Bradbury
2. Build minimal frontend with GenLayerJS
3. Integrate with existing Kite L1-L3 (bridge via API or keep separate for demo)
4. Demo prep

### 8.2 Architecture Options

**Option A: Standalone GenLayer Skill (Recommended)**
- Pure GenLayer Intelligent Contract
- No dependency on existing Kite infra
- Clean demo, fastest path to ETHGlobal

**Option B: Hybrid Kite + GenLayer**
- Kite L1-L3 handles agent registry, order matching, discovery
- GenLayer L4 handles enforcement, disputes, SLA verification
- Requires API bridge between Kite backend and GenLayer contracts

**Option C: L5 Escrow on GenLayer**
- Build escrow contract with GEN token
- Dispute resolution via LLM consensus
- Reputation tracking on-chain

---

## 9. Risks & Open Questions

### 9.1 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **LLM latency** | High — disputes could take minutes | Use small/fast models; design for async UX |
| **Gas cost unknown** | Medium — unclear cost per LLM call | Test on Bradbury with real models |
| **No revenue-share model** | Medium — unclear monetization for skill builders | Design custom fee structure in contract |
| **Studio limitations** | Low — Studio doesn't simulate gas/appeals | Validate on testnet before demo |
| **Python SDK maturity** | Medium — "early version" per docs | Lint + test thoroughly; pin GenVM version |
| **Mainnet readiness** | High — only testnets available | Plan for testnet-only demo |

### 9.2 Open Questions

1. **What is the actual gas cost for an LLM-based contract call?** Docs don't specify pricing.
2. **Is there a "Skills" revenue-share program?** The 10-20% claim needs verification — not found in official docs.
3. **What is mainnet timeline?** Docs only reference testnets.
4. **Can contracts run scheduled/periodic tasks?** No — contracts only execute when called. Monitoring requires external triggers.
5. **What's the validator set size on Bradbury?** Affects consensus latency and appeal rounds.
6. **Can GenLayer contracts interact with our existing EVM contracts?** Yes, via external messages on finalization, but limited to zkSync L2 layer.

---

## 10. Key Repositories & Resources

| Resource | URL |
|----------|-----|
| **Documentation** | docs.genlayer.com |
| **Full docs (bulk)** | docs.genlayer.com/full-documentation.txt |
| **SDK Reference** | sdk.genlayer.com |
| **GenVM (source)** | github.com/genlayerlabs/genvm |
| **JS SDK** | github.com/genlayerlabs/genlayer-js |
| **Project Boilerplate** | github.com/genlayerlabs/genlayer-project-boilerplate |
| **Skills (Claude plugins)** | github.com/genlayerlabs/skills |
| **GenLayer Portal** | portal.genlayer.foundation |
| **Studio** | studio.genlayer.com |
| **Discord** | discord.gg/8Jm4v89VAu |
| **Testnet Faucet** | testnet-faucet.genlayer.foundation |

---

## 11. Conclusion

GenLayer's Intelligent Contracts are a **strong fit for Kite L4 (Enforcement/SLAs)**. The native ability to process subjective evidence, access web data for SLA verification, and reach AI-powered consensus maps directly to dispute resolution and enforcement use cases. The Python SDK is well-documented with solid tooling (Studio, GLSim, linter, testing framework).

**For L5 (Marketplace + Escrow)**, the escrow mechanics work but GenLayer is not optimized for high-throughput deterministic operations. A hybrid approach — traditional infra for marketplace mechanics + GenLayer for dispute-aware escrow — is more appropriate.

**The "Skills SDK" terminology is misleading** — there is no separate Skills framework. The building primitive is the Intelligent Contract, and "GenLayer Skills" refers to Claude Code dev plugins. The claimed 10-20% revenue share for skill builders was **not found in official documentation** and should be verified directly with the GenLayer team before building on this assumption.

**Recommendation:** Build L4 as a GenLayer Intelligent Contract for ETHGlobal. Use Option A (standalone) for the cleanest demo path. Verify the revenue-share model with GenLayer team directly.
