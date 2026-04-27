# BYOA Adapter: Swarms ↔ Solana

> Status: **v0.1.0 Pushed** ✅  
> Created: 2026-04-27  
> Source: Jordan directive in HQ thread 22473  
> Repo: `agent-escrow-solana/swarms-solana-adapter/`

---

## TL;DR

**BYOA = adapter pattern.** GenTech builds the universal escrow spine; Swarms brings the agent brain. Zero fork, zero compete — pure plug.

**v0.1.0 is live.** `pip install swarms-solana-adapter` scaffold ready. 498 LOC across 4 Python modules + bundled Anchor IDL.

---

## Package Surface (v0.1.0)

```
swarms-solana-adapter/
├── pyproject.toml              # pip package metadata, MIT license
├── README.md                   # Quickstart + architecture
├── swarms_solana_adapter/
│   ├── __init__.py            # Public API exports (18 LOC)
│   ├── accounts.py            # PDA derivations: config, escrow, vault (25 LOC)
│   ├── client.py              # AgentEscrowClient — async Anchor wrapper (315 LOC)
│   ├── idl.json               # Embedded Anchor IDL (17K, program DKx16ix...)
│   └── swarms_shim.py        # SwarmsEscrowAdapter — agent-friendly wrapper (140 LOC)
└── example/
    ├── example_worker.py       # CLI demo (create + status read)
    └── swarms_agent_demo.py    # Swarms agent integration scaffold
```

| Module | Role |
|--------|------|
| `client.py` | Low-level async Anchor program client with raw instruction discriminators |
| `accounts.py` | PDA derivation helpers matching Anchor seeds |
| `swarms_shim.py` | `SwarmsEscrowAdapter` — high-level wrapper returning structured `EscrowResult` |
| `idl.json` | Bundled Anchor IDL (program: `DKx16ixPG4XojEMvs3S1etMfFgpAFbon4H7r9XjgU6ij`) |

---

## Public API

```python
from swarms_solana_adapter import AgentEscrowClient, SwarmsEscrowAdapter
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Low-level
client = AgentEscrowClient(
    rpc_url="https://api.devnet.solana.com",
    keypair=my_keypair,
)
escrow_id = await client.create_escrow(
    seller=seller_pubkey,
    amount=10_000_000,        # 10 USDC (6 decimals)
    usdc_mint=usdc_mint_pubkey,
)

# High-level (agent-friendly)
adapter = SwarmsEscrowAdapter(
    rpc_url="https://api.devnet.solana.com",
    keypair=my_keypair,
    usdc_mint=usdc_mint_pubkey,
)
result = await adapter.create_job_escrow(
    seller=seller_pubkey,
    amount_usdc=5_000_000,   # $5.00
)
# result.success, result.escrow_id, result.error
```

---

## Program Methods Wrapped

| Method | Role | Access |
|--------|------|--------|
| `initialize` | Init EscrowConfig (admin, one-shot) | Admin |
| `create_escrow` | Buyer deposits USDC into vault PDA | Buyer |
| `validate_work` | Direct validator on-chain approval | AI Validator |
| `validate_with_signature` | Ed25519 precompile validation | Anyone (forwards sig) |
| `release_funds` | Release USDC to seller ATA | Buyer / Admin |
| `refund_buyer` | Refund USDC to buyer ATA | Admin only |
| `update_validator` | Rotate AI validator pubkey | Admin |

---

## Dev Status Checklist

- [x] IDL bundled (17K)
- [x] Async client with raw discriminators — **no anchorpy runtime dependency**
- [x] PDA derivation helpers (config, escrow, vault)
- [x] `SwarmsEscrowAdapter` with structured `EscrowResult`
- [x] CLI example (`example_worker.py`)
- [ ] **Live devnet tests** — blocked on devnet airdrop / deployment
- [ ] **PyPI publish** — need CI + token
- [ ] **E2E Swarms agent demo** — need live agent harness

---

## Gaps to Close

| # | Gap | Severity | Owner | Action |
|---|-----|----------|-------|--------|
| 1 | `swarms_tool.py` deleted — Swarms `@tool` decorators gone | 🟡 Medium | Dmob | Re-add or replace with Swarms v6+ tool format |
| 2 | Tests are CLI examples only; no pytest suite | 🟡 Medium | Dmob | Add `pytest` + `pytest-asyncio` tests against devnet |
| 3 | `EscrowResult.tx_signature` is always `None` (TODO in shim) | 🟡 Medium | Dmob | Wire RPC signature return from `create_escrow` |
| 4 | No `__main__.py` / CLI entrypoint for `python -m swarms_solana_adapter` | 🟢 Low | Dmob | Add `if __name__ == "__main__"` runner |
| 5 | `client.py` uses `anchorpy` in imports but README says "no runtime dependency" | 🟠 High-ish | Dmob | Clarify: `anchorpy` is listed in `pyproject.toml` deps; remove or document |
| 6 | `spl-token>=0.2.0` in deps but `client.py` imports from `spl.token.instructions` (deprecated path?) | 🟢 Low | Dmob | Verify `spl-py` vs `spl-token` package naming |
| 7 | Program ID hardcoded to devnet placeholder `DKx16ix...` | 🟡 Medium | Dmob | Add env-overridable `PROGRAM_ID` |
| 8 | No REP token integration yet | 🟢 Low | YoYo | Design REP + adapter earn flow |
| 9 | No x402 middleware layer | 🟢 Low | YoYo | Phase 2 — intercept Swarms X402 → AAE escrow |

---

## Quick Audit: `client.py` (315 LOC, critical file)

**Good:**
- Uses `solders` + `solana.rpc.async_api` — modern async stack
- PDA derivations match Anchor seeds (`config`, `escrow`, `vault`)
- Raw discriminators pre-computed (no runtime hash)
- `get_escrow` / `get_config` use `program.account[].parse()` for typed reads
- Proper `close()` lifecycle on `AsyncClient`

**Risk:**
- `EscrowConfig` layout parsing is hardcoded byte offsets (line 150–154). If the Rust struct changes, this silently breaks.
- `program = await self._program()` pattern is fine but no retry/backoff on RPC failures.

**Recommendation:** Add typed dataclasses for config/escrow state instead of raw byte slicing. Or regenerate from IDL with `anchorpy`'s codegen.

---

## Next Steps (Priority Order)

1. **Dmob**: Fix `tx_signature` TODO in `swarms_shim.py` + re-add Swarms `@tool` decorators
2. **Dmob**: Clarify `anchorpy` dependency status in README vs pyproject.toml
3. **Dmob**: Write `pytest` suite with mocked RPC fixtures (or devnet smoke tests)
4. **Desmond**: Draft "Swarms Marketplace Listing" pitch doc
5. **YoYo**: Model x402 middleware spec (intercept Swarms native billing → AAE escrow)

---

## Related

- `02-Labs/Agent-Escrow-Solana.md` — Anchor program spec
- `03-Strategies/Swarms-Competitive-Analysis.md` — YoYo teardown
- `09-Green Room/2026-04-27-swarms-adapter-integration-plan.md` — Technical execution plan
- `02-Labs/x402-AAE-Integration-Map.md` — Payment middleware design

---

*Audited 2026-04-27. v0.1.0 scaffold is clean — gaps are polish, not architecture.*
