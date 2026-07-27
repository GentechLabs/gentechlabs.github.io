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

"""x402 authentication provider for ADK.

Handles the HTTP 402 Payment Required flow:
1. Detects 402 responses from API calls
2. Parses the payment challenge headers
3. Signs the payment using the configured wallet
4. Returns the signed credential for retry
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Callable, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.auth.auth_credential import (
    AuthCredential,
    AuthCredentialTypes,
    BaseModelWithConfig,
    HttpAuth,
    HttpCredentials,
)
from google.adk.auth.auth_schemes import AuthScheme
from google.adk.auth.auth_tool import AuthConfig
from google.adk.auth.base_auth_provider import BaseAuthProvider
from google.adk.features import experimental, FeatureName

from .x402_auth_scheme import X402AuthScheme


class X402SignedPayload(BaseModelWithConfig):
    """Payload containing the signed x402 payment proof."""

    signature: str
    """Hex-encoded ECDSA signature over the payment hash."""

    payment_hash: str
    """Hash of the payment parameters that were signed."""

    chain: str
    """Chain the payment settles on."""

    token: str
    """Token used for payment."""

    amount: str
    """Amount paid."""

    recipient: str
    """Who received the payment."""

    timestamp: int
    """Unix timestamp when the payment was signed."""

    expires_at: Optional[int] = None
    """Optional expiry timestamp for the payment proof."""


# Callback signature for signing x402 payments.
# Receives (X402AuthScheme) and returns (X402SignedPayload | None).
SigningCallback = Callable[
    [X402AuthScheme],
    Optional[X402SignedPayload],
]


@experimental(FeatureName.PLUGGABLE_AUTH)
class X402AuthProvider(BaseAuthProvider):
    """Authentication provider for x402 (HTTP 402) pay-per-call APIs.

    An ADK tool configured with an X402AuthScheme will use this provider to
    obtain payment credentials before calling the underlying API. The provider
    invokes the configured signing callback to produce the cryptographic proof
    of payment, then returns an AuthCredential containing the proof as an
    HTTP bearer token in the 'PAYMENT-SIGNATURE' header.
    """

    def __init__(
        self,
        signing_callback: SigningCallback,
    ):
        """Initialise the provider with a signing callback.

        Args:
            signing_callback: A callable that receives the X402AuthScheme and
                returns an X402SignedPayload (or None if signing fails).
                The caller is responsible for implementing the actual wallet
                signing — this keeps the provider wallet-agnostic.
        """
        self._signing_callback = signing_callback

    @property
    def supported_auth_schemes(self) -> tuple[type[AuthScheme], ...]:
        return (X402AuthScheme,)

    async def get_auth_credential(
        self,
        auth_config: AuthConfig,
        context: CallbackContext,
    ) -> AuthCredential | None:
        """Obtain an x402 payment credential.

        Args:
            auth_config: The auth config containing the X402AuthScheme.
            context: The callback context (not used for x402).

        Returns:
            An AuthCredential with the signed payment proof as an HTTP auth
            header, or None if signing failed.

        Raises:
            ValueError: If the auth scheme is not X402AuthScheme.
        """
        scheme = auth_config.auth_scheme
        if not isinstance(scheme, X402AuthScheme):
            raise ValueError(
                f"X402AuthProvider requires X402AuthScheme, got {type(scheme)}"
            )

        # If we already have a valid exchanged credential, reuse it.
        if auth_config.exchanged_auth_credential:
            existing = auth_config.exchanged_auth_credential
            if existing.http and existing.http.credentials.token:
                return existing

        # Invoke the signing callback.
        signed = self._signing_callback(scheme)
        if signed is None:
            return None

        # Build a serialisable form of the signed payload for the HTTP header.
        signed_json = signed.model_dump_json(by_alias=True, exclude_none=True)
        token_value = f"x402 {signed.signature} {signed.payment_hash}"

        return AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="PAYMENT-SIGNATURE",
                credentials=HttpCredentials(token=token_value),
                additional_headers={
                    "X-P402-Chain": signed.chain,
                    "X-P402-Token": signed.token,
                    "X-P402-Amount": signed.amount,
                    "X-P402-Recipient": signed.recipient,
                    "X-P402-Timestamp": str(signed.timestamp),
                    "X-P402-Payment-Hash": signed.payment_hash,
                },
            ),
        )
