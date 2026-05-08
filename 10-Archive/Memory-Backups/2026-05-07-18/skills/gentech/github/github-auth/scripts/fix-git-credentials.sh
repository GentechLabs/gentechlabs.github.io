#!/usr/bin/env bash
# github-auth/scripts/fix-git-credentials.sh
# Fixes malformed ~/.git-credentials and recovers token from gh config if available.
# Usage: ./fix-git-credentials.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

CRED_PATH="${HOME}/.git-credentials"
GH_HOSTS="${HOME}/.config/gh/hosts.yml"

echo "=== GitHub Credential Diagnostic ==="
echo ""

# Check current credential helper
echo "[1] Git credential helper:"
git config --global credential.helper 2>/dev/null || echo "  ❌ No helper set"
echo ""

# Check credential file exists and show raw content (masked)
if [[ -f "$CRED_PATH" ]]; then
  echo "[2] Credential file ($CRED_PATH):"
  cat "$CRED_PATH" | sed 's|:[^@]*@|:****@|g'
  echo ""
else
  echo "[2] ❌ Credential file not found"
fi

# Parse and validate format
if [[ -f "$CRED_PATH" ]]; then
  LINE=$(grep -m1 "github.com" "$CRED_PATH" || true)
  if [[ -n "$LINE" ]]; then
    # Expected: https://username:token@github.com
    if echo "$LINE" | grep -qE '^https://[^:]+:[^@]+@github\.com$'; then
      echo "[3] ✅ Format correct (includes username:token)"
    else
      echo "[3] ❌ Format wrong — must be https://<username>:<token>@github.com"
      echo "    Found: $LINE"
    fi
  fi
fi

# Try to extract token from gh config as fallback
echo ""
echo "[4] gh token status:"
if command -v gh &>/dev/null; then
  gh auth status 2>/dev/null || echo "  ⚠️  gh not authenticated"
  TOKEN=$(gh auth token 2>/dev/null || true)
  if [[ -n "$TOKEN" ]]; then
    echo "  ✅ Token available (length: ${#TOKEN})"
  else
    echo "  ⚠️  No active token in gh cache"
  fi
else
  echo "  ⚠️  gh CLI not installed"
fi

# Attempt to recover token from hosts.yml
RECOVERED_TOKEN=""
if [[ -f "$GH_HOSTS" ]]; then
  echo ""
  echo "[5] Checking gh hosts.yml for token:"
  if grep -q "oauth_token" "$GH_HOSTS"; then
    RECOVERED_TOKEN=$(grep "oauth_token" "$GH_HOSTS" | head -1 | awk '{print $2}' | tr -d '"')
    echo "  ✅ Found token (${#RECOVERED_TOKEN} chars)"
  else
    echo "  ⚠️  No oauth_token in hosts.yml"
  fi
fi

# If we have a recovered token, offer to rewrite credentials
if [[ -n "$RECOVERED_TOKEN" ]]; then
  echo ""
  echo "[6] Token recovery:"
  # Get username: try git config, then gh, then hosts.yml
  USERNAME=$(git config user.name 2>/dev/null || true)
  if [[ -z "$USERNAME" && -f "$GH_HOSTS" ]]; then
    USERNAME=$(grep '^  user:' "$GH_HOSTS" | head -1 | awk '{print $2}')
  fi
  
  if [[ -z "$USERNAME" ]]; then
    echo "  ⚠️  Cannot determine username (git user.name not set and not in hosts.yml)"
    echo "     Set it first: git config --global user.name 'YourGitHubUsername'"
  else
    NEW_CRED="https://${USERNAME}:${RECOVERED_TOKEN}@github.com"
    echo "  Constructed credential: https://${USERNAME}:****@github.com"
    if [[ "$DRY_RUN" == "false" ]]; then
      echo "  Writing to $CRED_PATH..."
      mkdir -p "$(dirname "$CRED_PATH")"
      echo "$NEW_CRED" > "$CRED_PATH"
      chmod 600 "$CRED_PATH"
      git config --global credential.helper store
      echo "  ✅ Credentials updated. Test with: git ls-remote https://github.com/${USERNAME}/<repo>.git"
    else
      echo "  [DRY RUN] Would write: $NEW_CRED (masked)"
    fi
  fi
fi

echo ""
echo "=== Done ==="
