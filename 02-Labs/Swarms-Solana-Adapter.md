# BYOA Adapter: Swarms ↔ Solana

> Status: Concept → Lab  
> Created: 2026-04-27  
> Source: Jordan directive in HQ thread 22473

---

## TL;DR

**BYOA = adapter pattern.** We build the universal escrow spine; Swarms brings the agent brain. Zero fork, zero compete — pure plug.

---

## Integration Path

### Swarms → Solana Bridge

- Swarms agents speak Python. Our agent-escrow is Anchor → `solana-py` gives them async RPC + tx signing natively.
- We publish a `swarms-solana-adapter` pip package:  
  ```bash
  pip install agentech-solana
  ```
- One-line swap from OpenAI/ETH provider to Solana.

### Swarms Marketplace Listing

- If Swarms marketplace charges SaaS fees, we undercut with on-chain settlement.
- Our adapter lets any Swarms agent post jobs, hold USDC in escrow, and release on validated work — no middleman SaaS cut.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Swarms Agent                      │
│              (Python — kyegomez/swarms)              │
└────────────────────┬────────────────────────────────┘
                     │ pip install agentech-solana
                     ▼
┌─────────────────────────────────────────────────────┐
│              AgentechSolanaAdapter                   │
│  ├─ Async RPC client (solana-py / asyncio)         │
│  ├─ Anchor IDL loader + CPI builder                  │
│  ├─ Ed25519 signer wrapper (agent keypair → Swarms)│
│  └─ x402 middleware (optional nanopayments)          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│             Solana Devnet / Mainnet                 │
│  ├─ agent-escrow program (Anchor CPI)               │
│  ├─ USDC vault PDA                                  │
│  ├─ RepToken mint + ATA                             │
│  └─ x402 settlement wrapper                       │
└─────────────────────────────────────────────────────┘
```

---

## Adapter Surface

```python
from swarms import Agent
from agentech_solana import SolanaAdapter

adapter = SolanaAdapter(
    rpc="https://api.devnet.solana.com",
    program_id="...",
    wallet=os.getenv("SWARMS_AGENT_KEYPAIR")
)

agent = Agent(
    name="TradeBot",
    llm=adapter.as_llm_provider(),   # swaps OpenAI calls for on-chain inference payments
    tools=[adapter.escrow_tool(),    # create / fund / release escrow
           adapter.rep_tool()]      # query / stake REP
)
```

---

## Jobs to Be Done

| Layer | Task | Priority | Owner |
|-------|------|----------|-------|
| 1 | `agentech-solana` pip scaffold + `solana-py` RPC | 🔴 P0 | Dmob |
| 2 | Anchor IDL → Python dataclass codegen | 🔴 P0 | Dmob |
| 3 | Escrow CPI wrappers (create, validate, release, refund) | 🟡 P1 | Dmob |
| 4 | Ed25519 precompile helper (off-chain sign → on-chain verify) | 🟡 P1 | Dmob |
| 5 | x402 middleware (pay-per-inference) | 🟢 P2 | Dmob / YoYo |
| 6 | Swarms marketplace listing spec | 🟢 P2 | Desmond |
| 7 | Docs + README quickstart | 🟢 P2 | Desmond |

---

## Open Questions

1. **SaaS undercut math** — what % does Swarms marketplace charge? Can we price-compare on-chain vs off-chain settlement?
2. **RepToken bridge** — should Swarms agents earn REP natively, or is REP a Solana-only concept?
3. **Validator wiring** — Swarms agents validate work via AI. Does our `validate_work` CPI accept arbitrary off-chain proof (LLM output hash, etc.)?
4. **Colosseum angle** — is this a standalone hackathon track, or does it fold into `agent-escrow-solana` submission?

---

## Related

- `02-Labs/Agent-Escrow-Solana.md` — Anchor program spec
- `03-Strategies/Swarms-Competitive-Analysis.md` — YoYo's full teardown
- `02-Labs/x402-AAE-Integration-Map.md` — payment middleware

---

*Filed in Labs. Next: flesh out pip package scaffold or draft Swarms marketplace pitch?*

---

**See also:** YoYo's full technical execution plan in the Green Room: `09-Green Room/2026-04-27-swarms-adapter-integration-plan.md`
