#!/usr/bin/env bash
# Agent Kit Behavioral Fixes — Verification Script
# Version: 1.0 → 1.1 (Fixed)
# Date: July 6, 2026

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get profile name (default: gentech)
PROFILE_NAME="${HERMES_PROFILE:-gentech}"

# Paths
PROFILE_DIR="$HOME/.hermes/profiles/$PROFILE_NAME"
SKILLS_DIR="$PROFILE_DIR/skills"
MARKER_FILE="$PROFILE_DIR/.session-startup-marker"

echo "🔍 Verifying Agent Kit Behavioral Fixes..."
echo "Target profile: $PROFILE_NAME"
echo ""

# Track issues
ISSUES=0

# Check 1: Session startup skill (FIXED: Fallback search)
echo "Check 1: session-startup skill..."
SKILL_FOUND=""
for path in "$SKILLS_DIR/session-startup/SKILL.md" \
             "$SKILLS_DIR/gentech-ops/session-startup/SKILL.md" \
             "$HOME/.hermes/profiles/$PROFILE_NAME/skills/session-startup/SKILL.md"; do
    if [ -f "$path" ]; then
        SKILL_FOUND="$path"
        break
    fi
done

if [ -n "$SKILL_FOUND" ]; then
    echo -e "${GREEN}✅ session-startup skill exists${NC} ($SKILL_FOUND)"
else
    echo -e "${RED}❌ session-startup skill missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check 2: Message length discipline skill (FIXED: Fallback search)
echo "Check 2: message-length-discipline skill..."
SKILL_FOUND=""
for path in "$SKILLS_DIR/message-length-discipline/SKILL.md" \
             "$SKILLS_DIR/gentech-ops/message-length-discipline/SKILL.md" \
             "$HOME/.hermes/profiles/$PROFILE_NAME/skills/message-length-discipline/SKILL.md"; do
    if [ -f "$path" ]; then
        SKILL_FOUND="$path"
        break
    fi
done

if [ -n "$SKILL_FOUND" ]; then
    echo -e "${GREEN}✅ message-length-discipline skill exists${NC} ($SKILL_FOUND)"
else
    echo -e "${RED}❌ message-length-discipline skill missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check 3: Vault-first research skill (FIXED: Fallback search)
echo "Check 3: vault-first-research skill..."
SKILL_FOUND=""
for path in "$SKILLS_DIR/vault-first-research/SKILL.md" \
             "$SKILLS_DIR/gentech-ops/vault-first-research/SKILL.md" \
             "$HOME/.hermes/profiles/$PROFILE_NAME/skills/vault-first-research/SKILL.md"; do
    if [ -f "$path" ]; then
        SKILL_FOUND="$path"
        break
    fi
done

if [ -n "$SKILL_FOUND" ]; then
    echo -e "${GREEN}✅ vault-first-research skill exists${NC} ($SKILL_FOUND)"
else
    echo -e "${RED}❌ vault-first-research skill missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check 4: Session startup marker exists
echo "Check 4: session startup marker..."
if [ -f "$MARKER_FILE" ]; then
    echo -e "${GREEN}✅ session startup marker exists${NC}"
else
    echo -e "${RED}❌ session startup marker missing${NC}"
    echo "  Run install.sh to create marker"
    ISSUES=$((ISSUES + 1))
fi

# Check 5: Marker file has valid timestamp (FIXED: Bounds check)
echo "Check 5: marker file content..."
if [ -f "$MARKER_FILE" ]; then
    TIMESTAMP=$(cat "$MARKER_FILE" 2>/dev/null || echo "invalid")
    CURRENT_EPOCH=$(date +%s)
    
    if [[ "$TIMESTAMP" =~ ^[0-9]+$ ]] && [ "$TIMESTAMP" -gt 1000000000 ] && [ "$TIMESTAMP" -le "$((CURRENT_EPOCH + 86400))" ]; then
        echo -e "${GREEN}✅ marker has valid timestamp${NC}"
    else
        echo -e "${RED}❌ marker has invalid timestamp${NC}"
        echo "  Marker content: $TIMESTAMP"
        ISSUES=$((ISSUES + 1))
    fi
fi

# Check 6: Wake-up protocol dependency (FIXED: Fallback search)
echo "Check 6: wake-up-protocol dependency..."
WAKEUP_FOUND=""
for path in "$SKILLS_DIR/wake-up-protocol/SKILL.md" \
             "$SKILLS_DIR/gentech-ops/wake-up-protocol/SKILL.md"; do
    if [ -f "$path" ]; then
        WAKEUP_FOUND="$path"
        break
    fi
done

if [ -n "$WAKEUP_FOUND" ]; then
    echo -e "${GREEN}✅ wake-up-protocol skill exists${NC} ($WAKEUP_FOUND)"
else
    echo -e "${YELLOW}⚠️  wake-up-protocol skill missing${NC}"
    echo "  session-startup depends on wake-up-protocol"
    echo "  Install from: https://github.com/nousresearch/hermes-skills"
fi

# Check 7: Skill registration (FIXED: NEW CHECK)
echo "Check 7: skill registration..."
if command -v hermes &> /dev/null; then
    REGISTERED_SKILLS=$(hermes skills list 2>/dev/null | grep -oE '^\s+[a-z0-9-]+' | sed 's/^\s*//' || echo "")
    
    if echo "$REGISTERED_SKILLS" | grep -q "session-startup"; then
        echo -e "${GREEN}✅ session-startup registered${NC}"
    else
        echo -e "${YELLOW}⚠️  session-startup not registered${NC}"
        echo "  File exists but may not be loaded by agent"
    fi
    
    if echo "$REGISTERED_SKILLS" | grep -q "message-length-discipline"; then
        echo -e "${GREEN}✅ message-length-discipline registered${NC}"
    else
        echo -e "${YELLOW}⚠️  message-length-discipline not registered${NC}"
    fi
    
    if echo "$REGISTERED_SKILLS" | grep -q "vault-first-research"; then
        echo -e "${GREEN}✅ vault-first-research registered${NC}"
    else
        echo -e "${YELLOW}⚠️  vault-first-research not registered${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  hermes CLI not found, skipping registration check${NC}"
fi

# Summary
echo ""
echo "─────────────────────────────────"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Skills are ready to use."
    echo ""
    echo "Optional: Test session startup"
    echo "  rm $MARKER_FILE"
    echo "  (Send message to agent — should wake up automatically)"
else
    echo -e "${RED}❌ Found $ISSUES issue(s)${NC}"
    echo ""
    echo "Fix by running:"
    echo "  bash install.sh"
fi
echo "─────────────────────────────────"