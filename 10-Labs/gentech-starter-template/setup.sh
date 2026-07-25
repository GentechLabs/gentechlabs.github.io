#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# GenTech Starter Template — One-Command Setup
# ═══════════════════════════════════════════════════════════════
# Run: bash setup.sh
# Or: chmod +x setup.sh && ./setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     GenTech Starter Template — Agent Bootstrap         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Check prerequisites ──
echo "🔍 Checking prerequisites..."

# Check Node.js
if command -v node &> /dev/null; then
    echo "  ✅ Node.js $(node --version)"
else
    echo "  ⚠️  Node.js not found. Install from https://nodejs.org"
fi

# Check Hermes
if command -v hermes &> /dev/null; then
    echo "  ✅ Hermes $(hermes --version 2>/dev/null || echo 'found')"
else
    echo "  ⚠️  Hermes not found. Install: npm install -g hermes-agent"
fi

# Check Git
if command -v git &> /dev/null; then
    echo "  ✅ Git $(git --version 2>/dev/null)"
else
    echo "  ❌ Git not found. Install from https://git-scm.com"
    exit 1
fi

echo ""

# ── 2. Set up environment ──
echo "📋 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "  ✅ Created .env from template"
    echo "  ⚠️  Edit .env and add your API keys before running"
else
    echo "  ✅ .env already exists"
fi

# Check if .env has placeholder values
if grep -q "your_" .env 2>/dev/null; then
    echo "  ⚠️  .env still has placeholder values — edit before using"
fi

echo ""

# ── 3. Install Hermes dependencies ──
echo "📦 Installing skills..."
if command -v hermes &> /dev/null; then
    # Link the skills
    SKILLS_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
    mkdir -p "$SKILLS_DIR"
    
    for skill in skills/*/; do
        skill_name=$(basename "$skill")
        target="$SKILLS_DIR/$skill_name"
        if [ ! -L "$target" ] && [ ! -d "$target" ]; then
            ln -s "$SCRIPT_DIR/$skill" "$target" 2>/dev/null && echo "  ✅ Linked skill: $skill_name" || echo "  ⚠️  Could not link skill: $skill_name (copy manually)"
        else
            echo "  ✅ Skill already linked: $skill_name"
        fi
    done
    echo "  ✅ Skills installed"
else
    echo "  ⚠️  Hermes not installed — skills are in ./skills/ for manual install"
fi

echo ""

# ── 4. Verify setup ──
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: hermes setup tools"
echo "  3. Run: hermes status"
echo "  4. Start building: hermes run"
echo ""
echo "📖 Read README.md for full documentation"
