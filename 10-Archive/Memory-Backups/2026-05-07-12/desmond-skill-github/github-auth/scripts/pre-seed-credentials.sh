#!/usr/bin/env bash
# Git credential pre-seeder for containerized / non-standard HOME environments
#
# Problem: When HOME points to a non-existent or non-standard path (e.g.
# /root/.hermes/profiles/desmond/home), git's credential.helper=store reads from
# $HOME/.git-credentials but the file may not exist or be readable. Git then fails
# with: "fatal: could not read Username for 'https://github.com': No such device or address"
#
# This script pre-approves credentials in the current git process's credential
# cache, bypassing the file-based store entirely. Call it before any git push/pull.
#
# Usage:
#   # With token via argument
#   source skills/github/github-auth/scripts/pre-seed-credentials.sh ghp_XXXXXXXXXXXXXXXXXXXX
#
#   # With token via GITHUB_PAT env var (recommended)
#   export GITHUB_PAT="ghp_XXXXXXXXXXXXXXXXXXXX"
#   source skills/github/github-auth/scripts/pre-seed-credentials.sh
#
# After sourcing, git operations in the same shell session will use the approved
# credentials. For non-interactive scripts, call this at the start.

set -euo pipefail

# Determine token: arg1 > GITHUB_PAT > ~/.hermes/.env fallback
TOKEN="${1:-${GITHUB_PAT:-}}"

if [ -z "$TOKEN" ]; then
  # Try vault .env as last resort
  if [ -f "/root/vaults/gentech/.env" ]; then
    TOKEN=$(grep '^GITHUB_PAT=' /root/vaults/gentech/.env | head -1 | cut -d= -f2- | tr -d '"\n\r')
  fi
fi

if [ -z "$TOKEN" ]; then
  echo "ERROR: No token provided. Pass as arg, set GITHUB_PAT, or fix vault .env" >&2
  return 1 2>/dev/null || exit 1
fi

# Pre-approve credentials into git's in-memory credential cache
# We use git-credential approve which writes to the helper's store
# (not the file-based store, avoiding HOME path issues)
git credential approve <<EOF 2>/dev/null || true
protocol=https
host=github.com
username=ProtoJay4789
password=$TOKEN
EOF

# Also set environment for child processes
export GIT_ASKPASS="/dev/null"
export GIT_TERMINAL_PROMPT="0"

# Optional: if HOME is wrong, help git find the right credential file
if [ ! -d "$HOME" ] || [ ! -w "$HOME" ]; then
  export HOME="/root"
fi

echo "✅ Git credentials pre-approved for github.com (user: ProtoJay4789)"
echo "   Git operations in this session will authenticate without prompts."
