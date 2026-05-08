#!/usr/bin/env python3
"""
Unified Gmail Wrapper — routes between direct Google API and Composio proxy.

Usage:
    export GMAIL_BACKEND=composio|direct
    export COMPOSIO_API_KEY=...
    export GOOGLE_CREDENTIALS_PATH=~/path/to/credentials.json  # for direct

    from gmail_unified import GmailUnified

    gmail = GmailUnified()
    gmail.send(
        to="test@example.com",
        subject="Test",
        body="Hello from unified wrapper",
        use_workspace=False  # force direct API if available
    )
"""

import os
from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class GmailConfig:
    """Configuration for Gmail backends."""
    backend: Literal['composio', 'direct', 'auto']
    composio_api_key: Optional[str] = None
    composio_connection_id: Optional[str] = None
    google_credentials_path: Optional[str] = None
    google_token_path: Optional[str] = None


class GmailUnified:
    """
    Unified Gmail client that abstracts backend selection.

    Priority:
    1. If use_workspace=True AND direct API configured → use direct
    2. If Composio connection available → use Composio
    3. Raise error if neither available
    """

    def __init__(self, config: Optional[GmailConfig] = None):
        self.config = config or GmailConfig(
            backend=os.getenv('GMAIL_BACKEND', 'auto')
        )
        self._composio_client = None
        self._composio_connection = None
        self._direct_client = None
        self._initialized = False

    def _ensure_composio(self):
        """Lazy-load Composio client and connection."""
        if self._composio_client is None:
            from composio import Composio
            api_key = self.config.composio_api_key or os.getenv('COMPOSIO_API_KEY')
            if not api_key:
                raise ValueError("COMPOSIO_API_KEY required for Composio backend")
            self._composio_client = Composio(api_key=api_key)

        if self._composio_connection is None:
            accounts = self._composio_client.connected_accounts.list()
            active = [
                a for a in dict(accounts)['items']
                if a.status == 'ACTIVE' and a.toolkit.slug == 'gmail'
            ]
            if not active:
                raise RuntimeError(
                    "No ACTIVE Gmail connection in Composio. "
                    "Run OAuth flow first."
                )
            # Use specified connection or first active
            conn_id = self.config.composio_connection_id or active[0].id
            self._composio_connection = self._composio_client.connected_accounts.get(conn_id)

    def _ensure_direct(self):
        """Lazy-load direct Google Workspace client."""
        if self._direct_client is None:
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError as e:
                raise ImportError(
                    "google-api-python-client required for direct backend. "
                    "Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
                ) from e

            token_path = self.config.google_token_path or os.path.expanduser('~/.config/gmail/token.json')
            if not os.path.exists(token_path):
                raise FileNotFoundError(
                    f"Gmail token not found at {token_path}. "
                    "Run OAuth flow for direct API first."
                )

            creds = Credentials.from_authorized_user_file(token_path)
            self._direct_client = build('gmail', 'v1', credentials=creds)

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        use_workspace: bool = False,
        dry_run: bool = False
    ) -> dict:
        """
        Send email via selected backend.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            use_workspace: Force direct API if available
            dry_run: validate but don't send (returns preview)

        Returns:
            dict with backend used and message ID
        """
        backend_used = None

        # Try direct if requested and available
        if use_workspace:
            try:
                self._ensure_direct()
                if dry_run:
                    return {'backend': 'direct', 'action': 'preview', 'to': to, 'subject': subject}
                # Direct send (implementation depends on google-workspace skill)
                message_id = self._send_direct(to, subject, body)
                return {'backend': 'direct', 'message_id': message_id}
            except Exception as e:
                print(f"⚠️ Direct API failed: {e}")
                print("Falling back to Composio...")

        # Use Composio
        self._ensure_composio()
        session = self._composio_client.use(connection_id=self._composio_connection.id)

        if dry_run:
            return {'backend': 'composio', 'action': 'preview', 'to': to, 'subject': subject}

        # Composio send (tool name varies by version)
        try:
            result = session.gmail.send_email(
                to=to,
                subject=subject,
                body=body
            )
        except AttributeError:
            # Try alternative naming
            result = session.gmail.send(to=to, subject=subject, body=body)

        return {
            'backend': 'composio',
            'message_id': getattr(result, 'id', str(result))
        }

    def fetch_inbox(self, max_results: int = 10) -> list:
        """Fetch recent inbox messages."""
        self._ensure_composio()
        session = self._composio_client.use(connection_id=self._composio_connection.id)
        result = session.gmail.get_emails(max_results=max_results)
        # Normalize result format
        return result if isinstance(result, list) else [result]

    def _send_direct(self, to: str, subject: str, body: str) -> str:
        """Send via direct Gmail API (requires google-workspace skill patterns)."""
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = self._direct_client.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        return result['id']

    def status(self) -> dict:
        """Return backend availability status."""
        status = {
            'backend': self.config.backend,
            'composio_available': False,
            'direct_available': False
        }

        # Check Composio
        try:
            self._ensure_composio()
            status['composio_available'] = True
            status['composio_connection_id'] = self._composio_connection.id
            status['composio_status'] = self._composio_connection.status
        except Exception:
            pass

        # Check Direct
        try:
            self._ensure_direct()
            status['direct_available'] = True
        except Exception:
            pass

        return status


# CLI for testing
if __name__ == '__main__':
    import sys

    gmail = GmailUnified()
    print("Gmail Unified Wrapper Status:")
    print(gmail.status())

    if len(sys.argv) > 1 and sys.argv[1] == 'send':
        to = sys.argv[2] if len(sys.argv) > 2 else input("To: ")
        subject = sys.argv[3] if len(sys.argv) > 3 else input("Subject: ")
        body = sys.argv[4] if len(sys.argv) > 4 else input("Body: ")
        result = gmail.send(to=to, subject=subject, body=body, dry_run=True)
        print("Would send via:", result)
