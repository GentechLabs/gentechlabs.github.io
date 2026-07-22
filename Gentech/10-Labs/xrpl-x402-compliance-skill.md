---
name: xrpl-x402-compliance
description: >
  x402 payment compliance for XRPL agent developers. Covers the full x402 integration
  lifecycle: 402 challenge handling, EIP-3009 proof generation, RLUSD settlement on XRPL,
  facilitator integration (Q402, Coinbase CDP), and agent-to-agent payment patterns.

  Use this skill whenever a user asks about x402 payments on XRPL, RLUSD micropayments,
  pay-per-call API patterns, agent-to-agent billing, or integrating the x402 protocol
  with XRPL settlement. Also trigger on: "x402", "402 Payment Required", "pay-per-call",
  "micropayment", "RLUSD x402", "agent billing", "facilitator", "EIP-3009 on XRPL".

  This skill constructs x402 payment flows and coordinates with the XRPL Payments skill
  for transaction building and the XRPL Agent Wallet skill for signing and submission.
---

# XRPL x402 Compliance

x402 is the HTTP 402 Payment Required protocol that enables pay-per-call API access
via USDC/RLUSD micropayments. On XRPL, x402 settlement uses RLUSD (Ripple USD) —
a regulated stablecoin native to the XRP Ledger — for fast, low-cost agent payments.

This skill bridges the x402 protocol with XRPL settlement infrastructure, enabling
agents to pay for API calls with RLUSD in 3-5 seconds with deterministic finality.

## How x402 Works on XRPL

```
Agent → API Server → 402 Challenge → Agent signs EIP-3009 → Facilitator settles on XRPL → Verified Response
```

1. **Agent** calls an API endpoint without payment
2. **Server** responds `402 Payment Required` with payment challenge (chain, amount, recipient)
3. **Agent** creates an EIP-3009 `transferWithAuthorization` signature
4. **Facilitator** (Q402, Coinbase CDP) submits the settlement on XRPL, sponsoring gas
5. **Agent** retries with `Authorization: x402 <proof>` header
6. **Server** verifies the proof and returns `200 OK` with data

## XRPL-Specific Advantages

| Property | XRPL | Why It Matters for x402 |
|----------|------|------------------------|
| Finality | 3-5 seconds | Agent payments settle faster than the HTTP round-trip |
| Fee | < $0.001 | $0.001 API calls are economically viable |
| RLUSD | Native stablecoin | Regulated, NYDFS-approved, no wrapping needed |
| No gas token | XRP for fees, RLUSD for value | Agents hold one asset for both |
| Deterministic | No mempool, no reorgs | Payment proof is final once confirmed |

## Integration Patterns

### Pattern 1: Server-Side 402 Challenge (API Provider)

When building an x402-enabled API on XRPL:

```python
from fastapi import FastAPI, Request, Response
import time
import uuid

app = FastAPI()

# Your XRPL wallet address (where RLUSD payments go)
RLUSD_RECIPIENT = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

@app.get("/api/data")
async def get_data(request: Request):
    # Check for payment proof
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("x402 "):
        # Issue 402 challenge
        now = int(time.time())
        challenge = {
            "version": "x402-v1",
            "payment": {
                "chain": "xrpl",
                "token": "RLUSD",
                "amount": "0.001",
                "recipient": RLUSD_RECIPIENT,
                "validAfter": now,
                "validBefore": now + 1800,
                "reference": str(uuid.uuid4()),
            },
            "instructions": f"Send 0.001 RLUSD on XRPL to {RLUSD_RECIPIENT}. Valid for ~30 min.",
        }
        return Response(
            content=json.dumps(challenge),
            status_code=402,
            headers={"Content-Type": "application/json"},
        )

    # Verify proof (delegate to facilitator or verify EIP-3009)
    proof = json.loads(auth[5:])
    if not verify_x402_proof(proof):
        return Response(
            content=json.dumps({"error": "Invalid or expired payment proof"}),
            status_code=402,
        )

    # Return the actual response
    return {"data": "your valuable data here", "paid": proof["amount"]}
```

### Pattern 2: Client-Side Payment (Agent Consumer)

When an agent needs to pay for an x402 API call:

```python
import httpx
from xrpl.wallet import Wallet
from xrpl.core.keypairs import sign

async def pay_and_fetch(url: str, wallet: Wallet, amount: str) -> dict:
    """Pay for an x402 API call and fetch the response."""

    # Step 1: Trigger 402 challenge
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 402:
            return resp.json()

        challenge = resp.json()
        payment = challenge["payment"]

    # Step 2: Create EIP-3009 authorization
    # (In production, use a facilitator like Q402 or Coinbase CDP)
    proof = {
        "chain": "xrpl",
        "token": "RLUSD",
        "amount": payment["amount"],
        "recipient": payment["recipient"],
        "validAfter": payment["validAfter"],
        "validBefore": payment["validBefore"],
        "nonce": payment["reference"],
        "signature": "facilitator-signed-proof",
    }

    # Step 3: Retry with proof
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            headers={"Authorization": f"x402 {json.dumps(proof)}"},
        )
        return resp.json()
```

### Pattern 3: Facilitator Integration (Q402 on XRPL)

Q402 provides gasless x402 settlement on XRPL using EIP-7702 delegation.
The agent never needs XRP for gas — Q402 sponsors the transaction fee.

```python
# Q402 handles the entire x402 flow:
# 1. Intercepts 402 response
# 2. Signs EIP-3009 authorization
# 3. Submits via Q402 relayer (gas sponsored)
# 4. Retries with proof

from q402 import Q402Client

q402 = Q402Client(api_key="your_q402_key")

# One call — Q402 handles the x402 handshake automatically
response = await q402.fetch(
    "https://api.example.com/v1/price?symbol=ETH",
    chain="xrpl",
    token="RLUSD",
)
```

## RLUSD on XRPL

RLUSD (Ripple USD) is a NYDFS-regulated stablecoin native to the XRP Ledger.

| Network | RLUSD Issuer Address |
|---------|---------------------|
| Testnet | `rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV` |
| Mainnet | `rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De` (verify at docs.ripple.com) |

### Trust Line Setup

Before an agent can receive RLUSD, it must set up a trust line:

```python
from xrpl.models.requests import AccountLines
from xrpl.wallet import Wallet
from xrpl.core.keypairs import sign

# Check existing trust lines
client = xrpl.clients.JsonRpcClient("https://s.altnet.rippletest.net:51234")
lines = client.request(AccountLines(account=wallet.classic_address))
has_rlusd = any(
    line["currency"] == "RLUSD"
    for line in lines.result.get("lines", [])
)
```

## Agent-to-Agent Payment Patterns

### Direct Payment (No x402)

For direct RLUSD transfers between agents (not API calls):

```python
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet
from xrpl.ledger import get_latest_validated_ledger_sequence

# Build RLUSD payment
payment_tx = Payment(
    account=source_wallet.classic_address,
    destination=dest_wallet.classic_address,
    amount=xrpl.utils.issued_currency_amount(
        currency="RLUSD",
        issuer=RLUSD_ISSUER,
        value="1.00",
    ),
    memos=[xrpl.models.transactions.Memo(
        memo_data=xrpl.utils.str_to_hex("x402:ref_abc123"),
        memo_type=xrpl.utils.str_to_hex("x402/reference"),
    )],
    source_tag=20260530,  # Agent attribution tag
)
```

### Escrow with x402

For conditional payments (pay if condition met):

```python
from xrpl.models.transactions import EscrowCreate

escrow_tx = EscrowCreate(
    account=source_wallet.classic_address,
    destination=dest_wallet.classic_address,
    amount=xrpl.utils.issued_currency_amount(
        currency="RLUSD",
        issuer=RLUSD_ISSUER,
        value="5.00",
    ),
    cancel_after=xrpl.utils.datetime_to_ripple_time(
        datetime.now() + timedelta(days=7)
    ),
    finish_after=xrpl.utils.datetime_to_ripple_time(
        datetime.now() + timedelta(hours=1)
    ),
    memos=[xrpl.models.transactions.Memo(
        memo_data=xrpl.utils.str_to_hex("x402:escrow:service_delivery"),
        memo_type=xrpl.utils.str_to_hex("x402/escrow"),
    )],
)
```

## Security Considerations

1. **Time-bound proofs**: Always set `validAfter`/`validBefore` to prevent replay attacks
2. **Reference deduplication**: Use unique references per challenge to prevent double-spending
3. **Facilitator trust**: Verify the facilitator's signature, not just the on-chain tx
4. **RLUSD issuer verification**: Always verify the RLUSD issuer address before accepting payments
5. **SourceTag attribution**: Use `SourceTag = 20260530` on all agent-initiated transactions

## What This Skill Does Not Do

- **Create wallets or handle keys**: Defer to the XRPL Agent Wallet skill
- **Construct non-x402 transactions**: Use the XRPL Payments skill for direct payments
- **Run a facilitator**: This skill integrates with existing facilitators (Q402, Coinbase CDP)
- **Guarantee mainnet RLUSD issuer**: Verify at docs.ripple.com before production use

## Related Skills

| Skill | Role |
|-------|------|
| XRPL Agent Wallet | Wallet creation, key loading, signing, submission |
| XRPL Payments | Transaction construction for XRP, RLUSD, escrow |
| x402 Protocol | Core x402 protocol reference (x402.org) |
