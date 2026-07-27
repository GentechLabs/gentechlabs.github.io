# Copyright 2026 GenTech Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""x402 (HTTP 402 Payment Required) authentication scheme for ADK.

The x402 standard enables AI agents to pay for API calls on-the-fly using
gasless USDC payments via EIP-7702 delegation or EIP-3009 signatures.

When an agent calls an API that responds with HTTP 402 + a payment challenge,
this scheme handles:
1. Parsing the payment challenge (network, token, amount, recipient)
2. Signing the payment with the agent's wallet
3. Returning the credential for retrying the request with the proof
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .auth_schemes import CustomAuthScheme


class X402AuthScheme(CustomAuthScheme):
    """Authentication scheme for x402 (HTTP 402 Payment Required) payments.

    Describes the payment parameters an agent needs to settle before calling
    a paid API endpoint.

    Attributes:
        chain: Target blockchain (e.g. 'base', 'solana', 'ethereum').
        token: Token symbol for payment (e.g. 'USDC', 'USDT').
        amount: Per-call payment amount in human-readable decimal.
        recipient: Address that receives the payment.
        rpc_url: Optional custom RPC URL for the chain.
        price_feed: Optional price feed contract for dynamic pricing.
    """

    type_: str = Field(default="x402", alias="type")
    """Auth scheme type identifier — always 'x402'."""

    chain: str = Field(default="base")
    """Target blockchain for payment settlement."""

    token: str = Field(default="USDC")
    """Token symbol (USDC, USDT, etc.)."""

    amount: Optional[str] = None
    """Per-call payment amount as a decimal string (e.g. '0.01')."""

    recipient: Optional[str] = None
    """Recipient address that receives the payment."""

    rpc_url: Optional[str] = None
    """Optional custom RPC URL override."""

    price_feed: Optional[str] = None
    """Optional price feed contract or URL for dynamic pricing."""

    max_retries: int = Field(default=3, ge=1, le=10)
    """Max retry attempts if the payment challenge changes."""

    def requires_signing(self) -> bool:
        """Returns True — x402 always requires a cryptographic signature."""
        return True
