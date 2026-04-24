---
name: genlayer-dev-setup
description: GenLayer intelligent contract development setup — CLI, SDK, project scaffolding, account creation, network config, and deployment to Bradbury testnet.
version: 1.0
created: 2026-04-21
triggers:
  - genlayer setup
  - deploy intelligent contract
  - genlayer account
  - bradbury testnet
  - genlayer cli
---

# GenLayer Dev Setup

## Prerequisites
- Python 3.11+ (GenVM docs say 3.12+ but 3.11 works for SDK)
- Node.js 18+ (for CLI)
- Docker (optional, only for localnet)

## 1. Install Tools

```bash
# CLI (Node.js)
npm install -g genlayer

# Python SDK + test framework + linter
pip install genlayer genlayer-test genvm-linter
```

**Pitfall:** `genvm-linter` downloads ~206MB of models on first run. Allow 60s+ timeout for first lint.

## 2. Create Project

```bash
genlayer new <project-name>
cd <project-name>
```

Scaffolds: `contracts/`, `test/`, `tools/`, `config/`, `app/` (Vue frontend).
Default template includes a football betting contract as example.

## 3. Create Account

```bash
# PITFALL: Interactive prompt doesn't work in non-PTY mode.
# Use --password flag:
genlayer account create --name default --password "YourSecureP@ss"

# Verify:
genlayer account
```

**Keystore saved to:** `~/.genlayer/keystores/<name>.json`

## 4. Configure Network

```bash
# List available networks:
genlayer network list

# Set to Bradbury testnet:
genlayer config set network=testnet-bradbury

# Verify:
genlayer config get network
```

Available networks:
| Network | RPC | Chain ID |
|---------|-----|----------|
| localnet | http://localhost:4000/api | 61127 |
| studionet | https://studio.genlayer.com/api | 61999 |
| testnet-asimov | https://rpc-asimov.genlayer.com | 4221 |
| testnet-bradbury | https://rpc-bradbury.genlayer.com | 4221 |

## 5. Get Testnet GEN (Faucet)

**URL:** https://testnet-faucet.genlayer.foundation

**Requirements:**
- GitHub account older than 3 months
- At least 1 public repo
- 0.01 ETH on mainnet (balance check)
- One claim per 24h → 100 GEN

**BLOCKER:** Faucet uses GitHub OAuth — cannot automate via CLI. User must sign in via browser manually.

## 6. Lint Contract

```bash
genvm-lint check contracts/my_contract.py
```

**Fallback:** Use Python syntax check if linter is slow:
```bash
python3 -c "import ast; ast.parse(open('contracts/my_contract.py').read()); print('Syntax OK')"
```

## 7. Deploy

```bash
genlayer deploy --contract contracts/my_contract.py --arg1 arg2
```

## 8. Useful Commands

```bash
genlayer call <address> <method>        # Read-only call
genlayer write <address> <method>       # State-modifying tx
genlayer schema <address>               # Get contract schema
genlayer code <address>                 # Get deployed source
genlayer receipt <txId>                 # Transaction receipt
genlayer appeal <txId>                  # Appeal a transaction
genlayer trace <txId>                   # Execution trace
```

## Contract Structure Reference

```python
# { "Depends": "py-genlayer:<hash>" }
from genlayer import *

class MyContract(gl.Contract):
    field: u32

    def __init__(self, init_val: u32):
        self.field = init_val

    @gl.public.view
    def get_field(self) -> int:
        return self.field

    @gl.public.write
    def set_field(self, val: u32):
        self.field = val

    @gl.public.write.payable
    def deposit(self):
        amount = gl.message.value  # GEN received
```

## Security Patterns (from Escrow audit)
1. **Timeouts** — Always add block-based timeout to prevent permanent fund locks
2. **HTTPS-only URLs** — Validate evidence/web URLs use HTTPS to reduce prompt injection surface
3. **Evidence truncation** — Cap at 10K chars for gas safety but allow real evidence
4. **Equivalence principle** — All `gl.nondet.*` calls MUST be inside eq_principle blocks; storage writes outside
5. **Arbiter fees** — Deduct from loser's share proportionally, not from total

## Tags
#GenLayer #intelligent-contracts #Python #WASM #Bradbury #smart-contract
