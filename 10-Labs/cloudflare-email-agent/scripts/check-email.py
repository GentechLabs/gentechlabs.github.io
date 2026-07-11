#!/usr/bin/env python3
"""
GenTech Email Agent — Forge reads inbox via Cloudflare MCP Server.

Usage:
    python3 check-email.py              # Show unread emails
    python3 check-email.py --read ID    # Mark email as read
    python3 check-email.py --send       # Send an email (interactive)
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime

# Config
ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")
API_TOKEN = os.environ.get("CF_API_TOKEN", "")
KV_NAMESPACE = "EMAIL_KV"
WORKER_URL = "https://gentech-email-agent.jordanjones0902.workers.dev"

def get_inbox():
    """Fetch inbox index from KV via Worker API."""
    try:
        req = urllib.request.Request(f"{WORKER_URL}/api/inbox")
        req.add_header("Authorization", f"Bearer {API_TOKEN}")
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching inbox: {e}")
        return []

def get_email(email_id):
    """Fetch a single email by ID."""
    try:
        req = urllib.request.Request(f"{WORKER_URL}/api/email/{email_id}")
        req.add_header("Authorization", f"Bearer {API_TOKEN}")
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching email: {e}")
        return None

def mark_read(email_id):
    """Mark an email as read."""
    try:
        data = json.dumps({"id": email_id, "read": True}).encode()
        req = urllib.request.Request(
            f"{WORKER_URL}/api/email/{email_id}/read",
            data=data,
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            method="PATCH",
        )
        resp = urllib.request.urlopen(req)
        return resp.status == 200
    except Exception as e:
        print(f"Error marking read: {e}")
        return False

def format_email(email):
    """Format an email for display."""
    lines = []
    lines.append("─" * 50)
    lines.append(f"From:    {email.get('from', '?')}")
    lines.append(f"To:      {email.get('to', '?')}")
    lines.append(f"Subject: {email.get('subject', '(no subject)')}")
    lines.append(f"Date:    {email.get('timestamp', '?')}")
    if email.get("attachments"):
        lines.append(f"Attachments: {len(email['attachments'])} file(s)")
        for att in email["attachments"]:
            lines.append(f"  - {att.get('filename', 'unknown')}")
    lines.append("")
    lines.append(email.get("text", "(no text content)")[:2000])
    lines.append("")
    return "\n".join(lines)

def main():
    args = sys.argv[1:]

    if "--read" in args:
        idx = args.index("--read")
        if idx + 1 < len(args):
            email_id = args[idx + 1]
            if mark_read(email_id):
                print(f"✅ Marked {email_id} as read")
            else:
                print(f"❌ Failed to mark {email_id} as read")
        return

    if "--send" in args:
        print("Send email mode — requires Cloudflare Email Routing API")
        print("Use Cloudflare Dashboard for now")
        return

    # Default: show inbox
    inbox = get_inbox()
    if not inbox:
        print("📭 Inbox empty")
        return

    unread = [e for e in inbox if not e.get("read")]
    print(f"📬 Inbox: {len(inbox)} total, {len(unread)} unread\n")

    for email in inbox:
        print(format_email(email))

    if unread:
        print(f"\n💡 Tip: python3 check-email.py --read <email_id> to mark as read")

if __name__ == "__main__":
    main()
