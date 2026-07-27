"""Tests for the x402 auth scheme and provider."""

import pytest
from google.adk.auth.auth_credential import (
    AuthCredential,
    AuthCredentialTypes,
    HttpAuth,
    HttpCredentials,
)
from google.adk.auth.auth_tool import AuthConfig

from google.adk.auth.x402_auth_scheme import X402AuthScheme
from google.adk.auth.x402_auth_provider import (
    X402AuthProvider,
    X402SignedPayload,
    SigningCallback,
)


def make_signing_callback(
    *,
    should_fail: bool = False,
) -> SigningCallback:
    """Create a test signing callback that returns a predetermined payload."""

    def callback(scheme: X402AuthScheme) -> X402SignedPayload | None:
        if should_fail:
            return None
        return X402SignedPayload(
            signature="0xdeadbeef" * 8,
            payment_hash="0x" + "ab" * 32,
            chain=scheme.chain,
            token=scheme.token,
            amount=scheme.amount or "0.01",
            recipient=scheme.recipient or "0x0000000000000000000000000000000000000000",
            timestamp=1700000000,
        )

    return callback


class TestX402AuthScheme:
    """Verify the scheme serialises and validates correctly."""

    def test_defaults(self):
        scheme = X402AuthScheme()
        assert scheme.type_ == "x402"
        assert scheme.chain == "base"
        assert scheme.token == "USDC"
        assert scheme.amount is None
        assert scheme.recipient is None
        assert scheme.max_retries == 3
        assert scheme.requires_signing() is True

    def test_custom_values(self):
        scheme = X402AuthScheme(
            chain="solana",
            token="USDT",
            amount="0.05",
            recipient="0x1234567890abcdef1234567890abcdef12345678",
            max_retries=5,
            rpc_url="https://api.mainnet-beta.solana.com",
        )
        assert scheme.chain == "solana"
        assert scheme.token == "USDT"
        assert scheme.amount == "0.05"
        assert scheme.recipient == "0x1234567890abcdef1234567890abcdef12345678"
        assert scheme.max_retries == 5
        assert scheme.rpc_url == "https://api.mainnet-beta.solana.com"

    def test_serialisation(self):
        scheme = X402AuthScheme(
            chain="base",
            token="USDC",
            amount="0.01",
            recipient="0xabc",
        )
        dumped = scheme.model_dump(by_alias=True)
        assert dumped["type"] == "x402"
        assert dumped["chain"] == "base"
        assert dumped["token"] == "USDC"
        assert dumped["amount"] == "0.01"

        # Round-trip
        restored = X402AuthScheme.model_validate(dumped)
        assert restored.chain == "base"
        assert restored.amount == "0.01"


class TestX402AuthProvider:
    """Verify the provider generates credentials from the scheme."""

    def test_supported_schemes(self):
        provider = X402AuthProvider(signing_callback=make_signing_callback())
        assert X402AuthScheme in provider.supported_auth_schemes

    def test_provider_rejects_bad_scheme(self):
        """Provider raises ValueError when given a non-X402 scheme."""
        provider = X402AuthProvider(signing_callback=make_signing_callback())
        import pytest

        # Use any non-X402 concrete scheme
        from google.adk.auth.auth_schemes import OpenIdConnectWithConfig

        oidc_scheme = OpenIdConnectWithConfig(
            authorization_endpoint="https://example.com/auth",
            token_endpoint="https://example.com/token",
        )
        config = AuthConfig(auth_scheme=oidc_scheme)
        with pytest.raises(ValueError, match="requires X402AuthScheme"):
            import asyncio

            asyncio.run(provider.get_auth_credential(config, None))

    def test_get_credential_with_default_scheme(self):
        scheme = X402AuthScheme(
            chain="base",
            token="USDC",
            amount="0.01",
            recipient="0xabc",
        )
        config = AuthConfig(auth_scheme=scheme)
        provider = X402AuthProvider(signing_callback=make_signing_callback())

        import asyncio

        cred = asyncio.run(provider.get_auth_credential(config, None))

        assert cred is not None
        assert cred.auth_type == AuthCredentialTypes.HTTP
        assert cred.http is not None
        assert cred.http.scheme == "PAYMENT-SIGNATURE"
        assert cred.http.credentials.token is not None
        assert cred.http.credentials.token.startswith("x402 ")
        assert cred.http.additional_headers is not None
        assert cred.http.additional_headers["X-P402-Chain"] == "base"
        assert cred.http.additional_headers["X-P402-Token"] == "USDC"
        assert cred.http.additional_headers["X-P402-Amount"] == "0.01"
        assert cred.http.additional_headers["X-P402-Recipient"] == "0xabc"

    def test_reuses_existing_credential(self):
        scheme = X402AuthScheme(chain="base")
        existing = AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="PAYMENT-SIGNATURE",
                credentials=HttpCredentials(token="x402 abc 123"),
            ),
        )
        config = AuthConfig(auth_scheme=scheme, exchanged_auth_credential=existing)
        provider = X402AuthProvider(signing_callback=make_signing_callback())

        import asyncio

        cred = asyncio.run(provider.get_auth_credential(config, None))
        # Should return the existing credential without re-signing
        assert cred is not None
        assert cred.http.credentials.token == "x402 abc 123"

    def test_returns_none_on_signing_failure(self):
        scheme = X402AuthScheme(chain="base")
        config = AuthConfig(auth_scheme=scheme)
        provider = X402AuthProvider(
            signing_callback=make_signing_callback(should_fail=True)
        )

        import asyncio

        cred = asyncio.run(provider.get_auth_credential(config, None))
        assert cred is None
