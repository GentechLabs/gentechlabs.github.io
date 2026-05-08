"""
Auth Bypass Pattern Template — Dual Account Setup

This template shows the minimal code structure to implement Pattern 1
(Parallel Dual-Account) for any service (Gmail, Slack, GitHub, etc.).

Usage:
    1. Copy this file to your project (e.g., services/gmail_service.py)
    2. Replace placeholders [SERVICE] and [PROVIDER] with actual names
    3. Implement the two backend classes
    4. Configure via env vars or config file
"""

import os
from abc import ABC, abstractmethod
from typing import Optional


class ServiceInterface(ABC):
    """Abstract base class defining the service contract."""

    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool:
        """Send a message/notification."""
        pass

    @abstractmethod
    def fetch(self, limit: int = 10) -> list:
        """Fetch recent items (messages, events, etc.)."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify connection is working."""
        pass


# ── IMPLEMENTATION A: Direct API (may be blocked) ──────────────────────────

class DirectService(ServiceInterface):
    """
    Direct connection to [SERVICE] API (e.g., Google Workspace).
    May be subject to admin consent blocks, rate limits, OAuth flow.
    """

    def __init__(self, credentials_path: str = "token.json"):
        self.credentials_path = credentials_path
        self._init_client()

    def _init_client(self):
        # TODO: Replace with actual SDK initialization
        # Example for Gmail:
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        # self.creds = Credentials.from_authorized_user_file(self.credentials_path)
        # self.client = build("gmail", "v1", credentials=self.creds)
        raise NotImplementedError

    def send(self, to: str, subject: str, body: str) -> bool:
        try:
            # TODO: Implement actual send
            return True
        except Exception as e:
            if "admin" in str(e).lower() or "consent" in str(e).lower():
                raise AuthBlockedError("Admin consent required") from e
            raise

    def fetch(self, limit: int = 10) -> list:
        # TODO: Implement fetch
        return []

    def health_check(self) -> bool:
        try:
            self.fetch(limit=1)
            return True
        except AuthBlockedError:
            return False


# ── IMPLEMENTATION B: Managed Provider (bypass) ───────────────────────────

class ManagedService(ServiceInterface):
    """
    Connection via managed OAuth provider (Composio, Clerk, Supabase).
    No local credentials, no token refresh code, no admin blocks.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")
        if not self.api_key:
            raise ValueError("COMPOSIO_API_KEY not set")
        self._init_client()

    def _init_client(self):
        # Example for Composio:
        # from composio import Composio
        # self.client = Composio(api_key=self.api_key)
        raise NotImplementedError

    def send(self, to: str, subject: str, body: str) -> bool:
        # Example:
        # result = self.client.tools.[service]_send_message(to=to, ...)
        # return not result.get("error")
        raise NotImplementedError

    def fetch(self, limit: int = 10) -> list:
        # Example:
        # return self.client.tools.[service]_list_messages(maxResults=limit)
        raise NotImplementedError

    def health_check(self) -> bool:
        try:
            self.fetch(limit=1)
            return True
        except Exception:
            return False


# ── FACTORY: Auto-select implementation ───────────────────────────────────

class ServiceFactory:
    """Factory that selects implementation based on config and availability."""

    @staticmethod
    def create(
        mode: Optional[str] = None,
        direct_creds_path: str = "token.json",
        managed_api_key: Optional[str] = None,
    ) -> ServiceInterface:
        """
        Create service instance.

        Args:
            mode: "direct" | "managed" | "auto" (default from env)
            direct_creds_path: Path to OAuth token file for direct API
            managed_api_key: API key for managed provider

        Returns:
            ServiceInterface implementation

        Raises:
            AuthBlockedError: if mode="direct" and blocked
            ValueError: if no valid config found
        """
        mode = mode or os.getenv("SERVICE_MODE", "auto")

        if mode == "direct":
            return DirectService(credentials_path=direct_creds_path)

        elif mode == "managed":
            return ManagedService(api_key=managed_api_key)

        elif mode == "auto":
            # Try direct first, fall back to managed
            try:
                direct = DirectService(credentials_path=direct_creds_path)
                if direct.health_check():
                    log("✅ Direct API available")
                    return direct
                else:
                    log("⚠️ Direct API blocked, falling back to managed")
            except (AuthBlockedError, FileNotFoundError):
                log("⚠️ Direct API unavailable, falling back to managed")

            return ManagedService(api_key=managed_api_key)

        else:
            raise ValueError(f"Unknown mode: {mode}")


# ── USAGE EXAMPLE ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Configure via environment variables (12-factor app pattern)
    # export SERVICE_MODE=auto
    # export DIRECT_CREDS_PATH=token.json
    # export MANAGED_API_KEY=your-composio-key

    service = ServiceFactory.create()

    # Test health
    if service.health_check():
        print("✅ Service ready")

        # Send test
        service.send(
            to="test@example.com",
            subject="Auth bypass test",
            body="If you see this, the dual-account pattern works!"
        )
        print("✅ Test sent")
    else:
        print("❌ Service unhealthy — check credentials")


# ── CUSTOM EXCEPTIONS ──────────────────────────────────────────────────────

class AuthBlockedError(Exception):
    """Raised when authentication is blocked by admin or provider."""
    pass
