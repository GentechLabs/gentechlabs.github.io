#!/usr/bin/env bash
# Detect stale or duplicate vault clones on the system
# Usage: ./detect_stale_vault_clones.sh

set -euo pipefail

VAULT_PATTERNS=(
  "/root/*vault*"
  "/root/repos/*vault*"
  "/opt/*vault*"
  "/home/*vault*"
)

echo "=== Stale Vault Clone Detection ==="
echo "Scanning for vault-named directories outside the primary vault..."
echo ""

PRIMARY="/root/vaults/gentech"
echo "Primary vault: $PRIMARY"
echo ""

found=0

for pattern in "${VAULT_PATTERNS[@]}"; do
  for dir in $pattern 2>/dev/null; do
    # Skip primary vault
    if [[ "$dir" == "$PRIMARY" ]] || [[ "$dir" == "$PRIMARY/"* ]]; then
      continue
    fi
    # Skip known mirrors that are part of backup chain
    if [[ "$dir" == "/root/hermes-brain-backup/vault" ]]; then
      continue
    fi
    # Must be a directory
    if [[ ! -d "$dir" ]]; then
      continue
    fi
    # Must have vault-like contents (some markdown files)
    if ! find "$dir" -maxdepth 2 -name "*.md" | grep -q .; then
      continue
    fi

    echo "🔍 Candidate: $dir"
    # Size
    du -sh "$dir" 2>/dev/null || true

    # Git remote (if repo)
    if [[ -d "$dir/.git" ]]; then
      echo "  Git remote:"
      git -C "$dir" remote -v 2>/dev/null | sed 's/^/    /' || true
      # Check if remote points to ProtoJay or other obsolete
      remote_url=$(git -C "$dir" config --get remote.origin.url 2>/dev/null || true)
      if [[ "$remote_url" == *"ProtoJay"* ]] || [[ "$remote_url" == *"gentech-vault"* ]]; then
        echo "  ⚠️  Remote points to obsolete mirror (ProtoJay/gentech-vault)"
      fi
    else
      echo "  (not a git repo)"
    fi

    # Last modification
    recent=$(find "$dir" -type f -printf '%T+ %p\n' 2>/dev/null | sort -r | head -1 | cut -d' ' -f1)
    echo "  Last activity: ${recent:-unknown}"
    echo ""
    found=$((found+1))
  done
done

if [[ $found -eq 0 ]]; then
  echo "✅ No stale vault clones found."
else
  echo "Review each candidate. If stale and not part of backup chain:"
  echo "  1. Archive: tar -czf /root/vaults/gentech/10-Archive/brain-prune-$(date +%Y-%m-%d)/$(basename $dir).tar.gz -C $(dirname $dir) $(basename $dir)"
  echo "  2. Remove: rm -rf \"$dir\""
  echo "  3. Update references: grep -r \"$dir\" /root/vaults/gentech/ /root/.hermes/ 2>/dev/null"
fi
