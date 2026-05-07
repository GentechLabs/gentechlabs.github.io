#!/bin/bash
# Cron flush verification test
# Usage: ./verify_cron_flush.sh /path/to/script [/path/to/test.log]

set -e

SCRIPT_PATH="${1:-/root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py}"
TEST_LOG="${2:-/tmp/cron_flush_test.log}"

echo "=== Cron Flush Verification Test ==="
echo "Script: $SCRIPT_LOG"
echo "Test log: $TEST_LOG"
echo ""

# Clean slate
> "$TEST_LOG"

# Test 1: Raw python without explicit flush
echo "[TEST 1] Running script as-is (no modification)"
env -i \
  PATH=/usr/bin:/bin \
  HOME=/root \
  HERMES_HOME=/root/.hermes/profiles/yoyo \
  python3 "$SCRIPT_PATH" >> "$TEST_LOG" 2>&1
echo "Exit code: $?"
echo "Bytes written: $(wc -c < "$TEST_LOG")"
echo "Lines: $(wc -l < "$TEST_LOG")"
echo ""

# Test 2: With explicit flush wrapper
echo "[TEST 2] Running with forced flush after script"
cat > /tmp/cron_flush_wrapper.py <<'EOF'
import sys, subprocess, os
sys.path.insert(0, '/usr/local/lib/hermes-agent')
exec(open(os.getenv('SCRIPT')).read())
sys.stdout.flush()
EOF

env -i \
  PATH=/usr/bin:/bin \
  HOME=/root \
  HERMES_HOME=/root/.hermes/profiles/yoyo \
  SCRIPT="$SCRIPT_PATH" \
  python3 /tmp/cron_flush_wrapper.py >> "$TEST_LOG" 2>&1
echo "Exit code: $?"
echo "Bytes written: $(wc -c < "$TEST_LOG")"
echo "Lines: $(wc -l < "$TEST_LOG")"
echo ""

# Test 3: Using stdbuf
echo "[TEST 3] Running with stdbuf -o0 (unbuffered)"
env -i \
  PATH=/usr/bin:/bin \
  HOME=/root \
  HERMES_HOME=/root/.hermes/profiles/yoyo \
  stdbuf -o0 python3 "$SCRIPT_PATH" >> "$TEST_LOG" 2>&1
echo "Exit code: $?"
echo "Bytes written: $(wc -c < "$TEST_LOG")"
echo "Lines: $(wc -l < "$TEST_LOG")"
echo ""

# Diagnosis
echo "=== DIAGNOSIS ==="
if [ $(wc -c < "$TEST_LOG") -eq 0 ]; then
    echo "❌ ALL TESTS produced zero output → likely permission/IO issue"
    echo "   Check: disk full? inode limit? file handle limit?"
elif [ $(grep -c "2026-05-04" "$TEST_LOG") -eq 0 ]; then
    echo "⚠️  Output produced but no timestamp → script may be stale"
else
    echo "✅ Output confirmed on $(grep -o '2026-05-04 [0-9:]*' "$TEST_LOG" | head -1)"
fi

echo ""
echo "Recommendation:"
echo "  1. If only TEST 1 fails → add sys.stdout.flush() to script end"
echo "  2. If all fail → check HERMES_HOME path, script readability"
echo "  3. If all succeed → cron environment differs; capture via 'env > /tmp/cron_env'"