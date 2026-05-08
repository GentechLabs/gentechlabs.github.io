#!/usr/bin/env bash
set -euo pipefail

# Clean-clone deployment for external portfolio repos
# Use when portfolio repo is separate from the vault (e.g., ProtoJay4789.github.io)
#
# Usage: ./scripts/portfolio-deploy-clean.sh [vault-portfolio-dir] [github-token]
# Example: ./scripts/portfolio-deploy-clean.sh /root/vaults/gentech/02-Labs/jordan-portfolio ghp_XXXXX
# NOTE: Path moved from 03-Projects/ to 02-Labs/ in May 2026

VAULT_DIR="${1:-/root/vaults/gentech/02-Labs/jordan-portfolio}"
TOKEN="${2:-}"
TEMP_CLONE="/tmp/portfolio-deploy-$(date +%s)"
REPO_URL="https://github.com/ProtoJay4789/ProtoJay4789.github.io.git"

# Auto-detect token from gh CLI if not provided
if [[ -z "$TOKEN" ]]; then
    TOKEN=$(gh auth token 2>/dev/null || true)
fi

if [[ -z "$TOKEN" ]]; then
    echo "ERROR: GitHub token required (pass as argument or run 'gh auth login')"
    echo "Usage: $0 <vault-portfolio-dir> [github-token]"
    exit 1
fi

# Validate token before clone — expired tokens silently succeed on clone but fail on push
echo "==> Validating token..."
if ! gh auth status >/dev/null 2>&1; then
    echo "WARNING: gh auth status shows token may be invalid. Attempting API check..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" https://api.github.com/user)
    if [[ "$HTTP_CODE" != "200" ]]; then
        echo "ERROR: GitHub token is invalid (HTTP $HTTP_CODE). Run 'gh auth login' to refresh."
        echo "Do NOT proceed — clone will succeed but push will fail."
        exit 1
    fi
fi
echo "    ✓ Token validated"

echo "==> Clean-clone deployment starting..."
echo "    Vault source: $VAULT_DIR"
echo "    Temp clone:   $TEMP_CLONE"

# 1. Fresh clone
echo "==> Cloning $REPO_URL ..."
git clone "https://x-access-token:${TOKEN}@github.com/ProtoJay4789/ProtoJay4789.github.io.git" "$TEMP_CLONE" > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "ERROR: Clone failed — check token and repo access"
    exit 1
fi

# 2. Copy ONLY web files
echo "==> Copying web files..."
cp "${VAULT_DIR}/index.html" "${TEMP_CLONE}/index.html"

if [[ -d "${VAULT_DIR}/assets" ]]; then
    rm -rf "${TEMP_CLONE}/assets"
    cp -r "${VAULT_DIR}/assets" "${TEMP_CLONE}/assets"
    echo "    ✓ assets/ copied"
fi

# Optional: projects.json if present
if [[ -f "${VAULT_DIR}/projects.json" ]]; then
    cp "${VAULT_DIR}/projects.json" "${TEMP_CLONE}/projects.json"
    echo "    ✓ projects.json copied"
fi

# 3. Commit
echo "==> Committing changes..."
cd "$TEMP_CLONE"
git add .
git commit -m "Portfolio sync: automated update $(date +%Y-%m-%d)" > /dev/null

# 4. Push
echo "==> Pushing to GitHub Pages..."
git push origin main > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "✓ Deployment successful: https://protojay4789.github.io/"
else
    echo "ERROR: Push failed — check token permissions"
    exit 1
fi

# 5. Cleanup
rm -rf "$TEMP_CLONE"
echo "✓ Clean clone removed"
echo "==> Done"
