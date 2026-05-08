#!/usr/bin/env python3
"""
Provider-agnostic email client — unified interface over Hermes Gmail (OAuth) and Composio (managed OAuth).

Usage:
  from unified_email_wrapper import get_email_provider

  email = get_email_provider('workspace')  # or 'personal'
  email.send('user@example.com', 'Subject', 'Body')
  emails = email.fetch('is:unread', max_results=10)
"""

import os
import json
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# =========== Provider ABC ===========

class EmailProvider(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """Send an email."""
        pass

    @abstractmethod
    def fetch(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fetch emails matching query."""
        pass

    @abstractmethod
    def delete(self, message_id: str) -> bool:
        """Delete a message by ID."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify provider is authenticated and ready."""
        pass


# =========== Hermes Gmail (google-workspace skill) ===========

class HermesGmail(EmailProvider):
    """
    Wraps the Hermes google-workspace skill (custom OAuth flow).
    Token stored at ~/.hermes/google_token.json
    """
    def __init__(self, skill_path: Optional[str] = None):
        self.skill_path = skill_path or os.path.expanduser(
            "~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
        )
        self._check_auth()

    def _run(self, *args) -> Dict[str, Any]:
        import subprocess
        cmd = ["python", self.skill_path] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"Gmail API error: {result.stderr[:200]}")
        return json.loads(result.stdout)

    def _check_auth(self):
        check_path = os.path.join(os.path.dirname(self.skill_path), "setup.py")
        result = subprocess.run(
            ["python", check_path, "--check"],
            capture_output=True, text=True
        )
        if "AUTHENTICATED" not in result.stdout:
            raise RuntimeError(
                "Hermes Gmail not authenticated. Run setup:\n"
                f"  python {check_path} --client-secret /path/to/client_secret.json\n"
                "Then follow: --auth-url → --auth-code"
            )

    def send(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        args = ["gmail", "send", "--to", to, "--subject", subject, "--body", body]
        if html:
            args.append("--html")
        return self._run(*args)

    def fetch(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        result = self._run("gmail", "search", query, "--max", str(max_results))
        return result if isinstance(result, list) else result.get('messages', [])

    def delete(self, message_id: str) -> bool:
        result = self._run("gmail", "delete", message_id)
        return result.get('status') == 'deleted'

    def health_check(self) -> bool:
        try:
            self._check_auth()
            # Quick test: search for 1 recent email
            self.fetch("is:unread", max_results=1)
            return True
        except Exception as e:
            print(f"Hermes health check failed: {e}")
            return False


# =========== Composio Gmail ===========

class ComposioGmail(EmailProvider):
    """
    Wraps Composio SDK (managed OAuth).
    Requires COMPOSIO_API_KEY environment variable.
    """
    def __init__(self, connection_id: str = "gmail"):
        self.connection_id = connection_id
        self._init_composio()

    def _init_composio(self):
        try:
            from composio import Composio
        except ImportError:
            raise ImportError("Composio SDK not installed. Run: pip install composio")

        api_key = os.environ.get("COMPOSIO_API_KEY")
        if not api_key:
            raise ValueError("COMPOSIO_API_KEY not set in environment")

        self.composio = Composio()

        # Verify connection is active
        conns = self.composio.integrations.list()
        connected = any(
            c.connectionId == self.connection_id and c.connectionStatus == "connected"
            for c in conns
        )
        if not connected:
            raise RuntimeError(
                f"Composio Gmail connection '{self.connection_id}' not found or not connected.\n"
                "Run: python -c \"from composio import Composio; Composio().integrations.link('gmail')\""
            )

    def send(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        # GMAIL_SEND_EMAIL tool expects specific param schema
        params = {
            "recipient_email": to,
            "subject": subject,
            "body": body,
        }
        if html:
            params["body"] = f"<html><body>{body}</body></html>"

        result = self.composio.tools.execute(
            action="GMAIL_SEND_EMAIL",
            params=params,
            connection_id=self.connection_id
        )
        return result.execution_details

    def fetch(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        # GMAIL_FETCH_EMAILS uses `maxResults` (camelCase) in Composio
        result = self.composio.tools.execute(
            action="GMAIL_FETCH_EMAILS",
            params={"query": query, "maxResults": max_results},
            connection_id=self.connection_id
        )
        emails = result.execution_details.get('response', [])
        return emails if isinstance(emails, list) else []

    def delete(self, message_id: str) -> bool:
        result = self.composio.tools.execute(
            action="GMAIL_DELETE_MESSAGE",
            params={"message_id": message_id},
            connection_id=self.connection_id
        )
        return result.execution_details.get('status') == 'success'

    def health_check(self) -> bool:
        try:
            conns = self.composio.integrations.list()
            return any(
                c.connectionId == self.connection_id and c.connectionStatus == "connected"
                for c in conns
            )
        except Exception as e:
            print(f"Composio health check failed: {e}")
            return False


# =========== Factory ===========

def get_email_provider(provider: str = "workspace") -> EmailProvider:
    """
    Get email provider by name.

    Args:
        provider: 'workspace' (Hermes OAuth) or 'personal' (Composio)

    Returns:
        EmailProvider instance

    Raises:
        ValueError: if provider unknown or auth not configured
    """
    if provider == "workspace":
        return HermesGmail()
    elif provider == "personal":
        return ComposioGmail()
    else:
        raise ValueError(f"Unknown provider '{provider}'. Use 'workspace' or 'personal'.")


# =========== Quick Test ===========

if __name__ == "__main__":
    import sys

    provider_name = sys.argv[1] if len(sys.argv) > 1 else "workspace"
    print(f"Testing {provider_name} provider...")

    try:
        email = get_email_provider(provider_name)
        healthy = email.health_check()
        print(f"Health check: {'✓ OK' if healthy else '✗ FAILED'}")

        if healthy:
            # Test fetch (dry-run — don't send anything)
            print("\nFetching 1 recent email (test query: 'is:unread')...")
            msgs = email.fetch("is:unread", max_results=1)
            if msgs:
                print(f"  Found: {msgs[0].get('subject', '(no subject)')}")
            else:
                print("  No unread messages (that's OK)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
