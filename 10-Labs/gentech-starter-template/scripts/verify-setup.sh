#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# GenTech Starter Template — Verify Installation
# ═══════════════════════════════════════════════════════════════
# Run after setup.sh to verify everything is working.

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     GenTech Starter Template — Verification            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0
WARN=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo "  ✅ $desc"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $desc"
        FAIL=$((FAIL + 1))
    fi
}

warn() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo "  ✅ $desc"
        PASS=$((PASS + 1))
    else
        echo "  ⚠️  $desc (optional)"
        WARN=$((WARN + 1))
    fi
}

# ── Core dependencies ──
check "Node.js installed" "command -v node"
check "Git installed" "command -v git"
warn "Hermes installed" "command -v hermes"

# ── Project files ──
check "config.yaml exists" "test -f config.yaml"
check ".env.template exists" "test -f .env.template"
check "SOUL.md exists" "test -f SOUL.md"
check "README.md exists" "test -f README.md"

# ── Skills ──
check "x402-gateway skill" "test -f skills/x402-gateway/SKILL.md"
check "q402-payments skill" "test -f skills/q402-payments/SKILL.md"
check "model-routing skill" "test -f skills/model-routing/SKILL.md"
check "gentech-patterns skill" "test -f skills/gentech-patterns/SKILL.md"

# ── Environment ──
if [ -f .env ]; then
    if grep -q "your_" .env 2>/dev/null; then
        echo "  ⚠️  .env has placeholder values — edit before deploying"
        WARN=$((WARN + 1))
    else
        check ".env has keys configured" "test -f .env"
    fi
else
    echo "  ⚠️  .env not created — run: cp .env.template .env"
    WARN=$((WARN + 1))
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "╚══════════════════════════════════════════════════════════╝"

if [ "$FAIL" -gt 0 ]; then
    echo "❌ Some checks failed — review above"
    exit 1
else
    echo "✅ All critical checks passed!"
    exit 0
fi
