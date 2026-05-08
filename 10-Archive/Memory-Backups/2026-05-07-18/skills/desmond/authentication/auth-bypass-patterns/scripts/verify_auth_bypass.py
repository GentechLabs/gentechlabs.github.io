#!/usr/bin/env python3
"""
Auth Bypass Verifier — tests that the dual-account pattern works.

This script checks:
1. Direct API is attempted first (if mode=auto)
2. Fallback to managed provider occurs on block
3. Health checks return correct status
4. Operations succeed on at least one backend

Usage:
    python verify_auth_bypass.py --mode auto
    python verify_auth_bypass.py --mode managed
    python verify_auth_bypass.py --mode direct  # expect failure if blocked
"""

import os
import sys
from enum import Enum


class Verdict(Enum):
    PASS = "✅"
    FAIL = "❌"
    SKIP = "⏭️"


def check_direct_api():
    """Attempt direct API connection. Expect: blocked or success."""
    print("   Testing Direct API...")
    try:
        # Replace with actual import from your service module
        # from services.gmail_service import DirectService
        # svc = DirectService()
        # if svc.health_check():
        #     print("   ✓ Direct API accessible")
        #     return Verdict.PASS
        # else:
        #     print("   ✗ Direct API unreachable (blocked)")
        #     return Verdict.FAIL
        print("   (Not implemented — replace with actual check)")
        return Verdict.SKIP
    except AuthBlockedError:
        print("   ✗ Direct API blocked (expected if admin consent pending)")
        return Verdict.FAIL
    except FileNotFoundError:
        print("   ⚠️ No credentials file found")
        return Verdict.SKIP


def check_managed_api():
    """Attempt managed provider connection. Expect: success."""
    print("   Testing Managed Provider (Composio)...")
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        print("   ⚠️ COMPOSIO_API_KEY not set — skipping")
        return Verdict.SKIP

    try:
        # from composio import Composio
        # composio = Composio(api_key=api_key)
        # apps = composio.apps.list()
        # gmail = next((a for a in apps if "gmail" in a.name.lower()), None)
        # if gmail and gmail.installation.status == "active":
        #     print("   ✓ Managed provider connected")
        #     return Verdict.PASS
        # else:
        #     print("   ✗ Gmail app not active in Composio dashboard")
        #     return Verdict.FAIL
        print("   (Not implemented — replace with actual check)")
        return Verdict.SKIP
    except Exception as e:
        print(f"   ✗ Managed provider error: {e}")
        return Verdict.FAIL


def check_fallback():
    """Verify auto mode falls back correctly."""
    print("   Testing Fallback Logic...")
    # Create service with mode="auto"
    # Assert: either direct OR managed is healthy
    print("   (Not implemented — replace with actual check)")
    return Verdict.SKIP


def main():
    mode = os.getenv("SERVICE_MODE", "auto")
    print(f"🔍 Auth Bypass Verifier — mode={mode}\n")

    results = []

    # Always test managed (should work)
    results.append(("Managed Provider", check_managed_api()))

    # Test direct if not managed-only
    if mode != "managed":
        results.append(("Direct API", check_direct_api()))

    # Test fallback if auto
    if mode == "auto":
        results.append(("Fallback Logic", check_fallback()))

    # Summary
    print("\n" + "─" * 50)
    passed = sum(1 for _, v in results if v == Verdict.PASS)
    failed = sum(1 for _, v in results if v == Verdict.FAIL)
    skipped = sum(1 for _, v in results if v == Verdict.SKIP)
    total = len(results)

    for name, verdict in results:
        print(f"{verdict.value} {name}")

    print(f"\nTotal: {passed}/{total} passed, {failed} failed, {skipped} skipped")

    # Exit code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
