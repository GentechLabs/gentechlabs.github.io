#!/bin/bash
# portfolio-diff.sh — Show exact HTML differences between current live and proposed update
# Usage: ./portfolio-diff.sh /path/to/current.html /path/to/updated.html

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <current-site-html> <proposed-update-html>"
  echo "Example: $0 /tmp/portfolio-current.html /root/vaults/gentech/06-Content/portfolio-updated-2026-05-04.html"
  exit 1
fi

CURRENT="$1"
UPDATED="$2"

if [ ! -f "$CURRENT" ]; then
  echo "Error: current file not found: $CURRENT"
  exit 1
fi
if [ ! -f "$UPDATED" ]; then
  echo "Error: updated file not found: $UPDATED"
  exit 1
fi

echo "=== Portfolio HTML Diff ==="
echo "Current:    $CURRENT"
echo "Proposed:   $UPDATED"
echo ""

# Extract just the body content sections for cleaner diff
# (strip doctype, head, keep body)
tmp1=$(mktemp)
tmp2=$(mktemp)

# Try to extract <body>...</body> only; fall back to full file
if grep -q "<body>" "$CURRENT"; then
  sed -n '/<body>/,/<\/body>/p' "$CURRENT" > "$tmp1"
else
  cp "$CURRENT" "$tmp1"
fi

if grep -q "<body>" "$UPDATED"; then
  sed -n '/<body>/,/<\/body>/p' "$UPDATED" > "$tmp2"
else
  cp "$UPDATED" "$tmp2"
fi

echo "--- Section-level change summary ---"
echo ""

# Show added/removed/changed lines
diff -u "$tmp1" "$tmp2" | sed 's/^/  /' || true

echo ""
echo "--- Key section markers ---"
echo "  Checking for: About, Projects, Hackathon, Tech Stack, Current Focus"
echo ""

# Quick regex presence check
for section in "About" "Projects" "Hackathon" "Tech Stack" "Current Focus"; do
  in_cur=$(grep -c "$section" "$tmp1" || echo 0)
  in_upd=$(grep -c "$section" "$tmp2" || echo 0)
  if [ "$in_cur" -eq "$in_upd" ]; then
    echo "  [$section] present in both"
  else
    echo "  [$section] count changed: current=$in_cur → updated=$in_upd"
  fi
done

rm -f "$tmp1" "$tmp2"
echo ""
echo "Tip: Use the full diff output above to spotline-by-line changes before committing."
