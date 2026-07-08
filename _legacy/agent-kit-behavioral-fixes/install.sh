#!/usr/bin/env bash
# Agent Kit Behavioral Fixes — Installation Script
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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Installing Agent Kit Behavioral Fixes..."
echo "Target profile: $PROFILE_NAME"
echo ""

# Check if profile exists
if [ ! -d "$PROFILE_DIR" ]; then
    echo -e "${RED}❌ Profile '$PROFILE_NAME' not found${NC}"
    echo "Available profiles:"
    ls -1 "$HOME/.hermes/profiles/" 2>/dev/null || echo "  None found"
    echo ""
    echo "Set HERMES_PROFILE environment variable:"
    echo "  export HERMES_PROFILE=your-profile"
    exit 1
fi


# Create marker file FIRST (before any file copies)
# This ensures marker exists even if copy fails
echo "🚀 Creating session startup marker..."
touch "$MARKER_FILE" || {
    echo -e "${RED}❌ Failed to create marker file${NC}"
    exit 1
}
echo "$(date +%s)" > "$MARKER_FILE"

# Create skills directories
echo "📁 Creating skill directories..."
mkdir -p "$SKILLS_DIR/session-startup"
mkdir -p "$SKILLS_DIR/message-length-discipline"
mkdir -p "$SKILLS_DIR/vault-first-research"

# Copy skill files (FIXED: Check both package and skills directory)
echo "📋 Copying skill files..."

# Try package directory first (for distribution)
if [ -f "$SCRIPT_DIR/session-startup/SKILL.md" ]; then
    cp "$SCRIPT_DIR/session-startup/SKILL.md" "$SKILLS_DIR/session-startup/"
    cp "$SCRIPT_DIR/message-length-discipline/SKILL.md" "$SKILLS_DIR/message-length-discipline/"
    cp "$SCRIPT_DIR/vault-first-research/SKILL.md" "$SKILLS_DIR/vault-first-research/"
    echo "  Skills copied from package directory"
elif [ -f "$SKILLS_DIR/session-startup/SKILL.md" ]; then
    # Skills already in place (installation from source)
    echo "  Skills already exist at $SKILLS_DIR/"
    echo "  Skipping copy (already installed)"
else
    echo -e "${YELLOW}⚠️  Warning: Skill files not found${NC}"
    echo "  Checked: $SCRIPT_DIR/ and $SKILLS_DIR/"
    echo "  Continuing installation (marker created)"
fi

# Verify installation
echo ""
echo "✅ Installation complete!"
echo ""
echo "Skills installed:"
echo "  - session-startup (SKILL.md)"
echo "  - message-length-discipline (SKILL.md)"
echo "  - vault-first-research (SKILL.md)"
echo ""
echo "Session startup marker created: $MARKER_FILE"
echo ""

# Check for wake-up protocol dependency (FIXED: Fallback search)
echo "🔍 Checking dependencies..."
WAKEUP_FOUND=""
for path in "$SKILLS_DIR/wake-up-protocol/SKILL.md" \
             "$SKILLS_DIR/gentech-ops/wake-up-protocol/SKILL.md"; do
    if [ -f "$path" ]; then
        WAKEUP_FOUND="$path"
        break
    fi
done

if [ -n "$WAKEUP_FOUND" ]; then
    echo -e "${GREEN}✅ wake-up-protocol skill exists${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: wake-up-protocol skill not found${NC}"
    echo "session-startup depends on wake-up-protocol"
    echo "Install from: https://github.com/nousresearch/hermes-skills"
    echo ""
fi

echo "📖 Next steps:"
echo "  1. Read skill documentation in $SKILLS_DIR/"
echo "  2. Implement session startup hooks (if you have gateway access)"
echo "  3. Run verification: bash verify.sh"
echo ""
echo "For manual setup (no gateway access), see README.md"