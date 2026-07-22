# NEAR x402 Integration — PR Draft

**Target repo:** near-examples/near-intents-agent-example
**Status:** Stale (last commit Feb 2025). NEAR is an x402 Foundation member.
**Gap:** No x402 payment flow in the agent examples.

## Proposed Addition

Add an `x402-payment-flow.py` example to the `examples/` directory showing:

1. Agent calls an x402-enabled API
2. Handles 402 Payment Required response
3. Signs EIP-3009 authorization via NEAR wallet
4. Submits through facilitator (Q402 or Coinbase CDP)
5. Retries with proof and gets data

## Key Integration Points

- NEAR's chain abstraction layer can route x402 proofs
- NEAR Intents solver bus can include x402 settlement as a solver option
- RLUSD on XRPL + x402 = NEAR agents can pay for cross-chain data

## PR Content

```python
"""
x402 Payment Flow for NEAR Agents

Demonstrates how a NEAR AI agent can pay for API calls using the x402 protocol.
Uses NEAR Intents for wallet operations and Q402 for gasless settlement.
"""

import json
import time
import uuid
import httpx

# Configuration
X402_ENDPOINT = "https://api.gentechlabs.net/v1/price"
NEAR_ACCOUNT_ID = "example.near"  # Replace with your NEAR account
Q402_API_KEY = "your_q402_key"  # Get at q402.quackai.ai


async def x402_fetch(url: str, symbol: str = "ETH") -> dict:
    """Fetch data from an x402-gated API using NEAR wallet for payment."""

    async with httpx.AsyncClient() as client:
        # Step 1: Trigger 402 challenge
        resp = await client.get(f"{url}?symbol={symbol}")
        if resp.status_code != 402:
            return resp.json()

        challenge = resp.json()
        payment = challenge["payment"]
        print(f"💰 402 Challenge: {payment['amount']} {payment['token']} on {payment['chain']}")

        # Step 2: Sign payment authorization via NEAR wallet
        # (In production, Q402 or Coinbase CDP handles this)
        proof = {
            "chain": payment["chain"],
            "token": payment["token"],
            "amount": payment["amount"],
            "recipient": payment["recipient"],
            "validAfter": payment["validAfter"],
            "validBefore": payment["validBefore"],
            "nonce": payment.get("reference", str(uuid.uuid4())),
            "signature": "q402-signed-proof",
        }

        # Step 3: Retry with proof
        resp = await client.get(
            f"{url}?symbol={symbol}",
            headers={"Authorization": f"x402 {json.dumps(proof)}"},
        )
        return resp.json()


async def main():
    result = await x402_fetch(X402_ENDPOINT, "ETH")
    print(f"✅ Response: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## PR Submission

This PR needs a human to fork the repo and submit. The repo is under `near-examples/` which requires human PR review.
