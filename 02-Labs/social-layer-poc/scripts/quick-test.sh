#!/usr/bin/env bash
# quick-test.sh — Verify xurl is working before setting up cron jobs

echo "=== Social Layer POC — Quick Test ==="
echo ""

# Check xurl binary
echo -n "xurl installed: "
which xurl && echo "✓" || echo "✗ — run install.sh first"

# Check auth
echo -n "Auth status: "
xurl auth status 2>&1

# Test read (cheapest call — $0.001)
echo ""
echo "--- Testing read capability ---"
xurl whoami 2>&1 && echo "✓ Auth working" || echo "✗ Auth needed — run: xurl auth oauth2"

# Test search
echo ""
echo "--- Testing search ---"
xurl search "ethereum" -n 1 2>&1 && echo "✓ Search working" || echo "✗ Search failed"

echo ""
echo "=== Quick test complete ==="
