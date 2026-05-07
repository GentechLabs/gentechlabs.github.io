# GitHub Forensic Extraction

**Problem:** GitHub API responses often truncate or contain control characters for large orgs (LayerZero-Labs has 30+ repos). Standard JSON parsing fails.

**Solutions discovered:**
1. **HTML scraping** commit logs from GitHub web UI
2. **Regex extraction** from partial JSON/HTML responses
3. **Download → file → parse** with line-by-line extraction
4. **Paginated fetching** with manual array reconstruction

---

## 1. Regex Extraction from Partial JSON

When GitHub API returns truncated array:
```bash
# Extract repo names
curl -s "https://api.github.com/orgs/LayerZero-Labs/repos?per_page=100" |
  grep -oP '"name":\s*"\K[^"]+' | sort -u

# Extract full_names (with org prefix)
grep -oP '"full_name":\s*"\K[^"]+' | sort -u

# Extract commit messages
grep -oP '"message":\s*"\K[^"]+' | head -20

# Extract dates
grep -oP '"committer":\s*\{[^}]*"date":\s*"\K[^"]+' | head -20
```

**Pitfall:** `grep -oP` uses Perl regex; if unavailable use `sed`/`awk`:
```bash
sed -n 's/.*"name": "\([^"]*\)".*/\1/p'
```

---

## 2. HTML Scraping Commit Logs

When JSON parsing fails (`Invalid control character at line 335`), fetch HTML commit page:

```bash
# Get commit log page
curl -s 'https://github.com/LayerZero-Labs/LayerZero-v2/commits' -A 'Mozilla/5.0' > /tmp/commits.html

# Extract commit SHAs (GitHub's data-commit-id attribute)
grep -oP 'data-commit-id="\K[a-f0-9]+' /tmp/commits.html | head -20

# Or anchor href pattern
grep -oP '/LayerZero-Labs/LayerZero-v2/commit/\K[a-f0-9]+' /tmp/commits.html | head -20

# Extract commit messages (inside <p class="mb-1">)
grep -oP '<p class="[^"]*mb-1[^"]*">\K.*?(?=</p>)' /tmp/commits.html | head -20

# Extract dates (relative-time datetime attribute)
grep -oP '<relative-time[^>]*datetime="\K[^"]+' /tmp/commits.html | head -20
```

**Combined extraction script:**
```bash
#!/bin/bash
URL="https://github.com/LayerZero-Labs/LayerZero-v2/commits"
curl -s "$URL" -A 'Mozilla/5.0' | \
  grep -oP '(data-commit-id="\K[a-f0-9]+)|(<p class="[^"]*mb-1[^"]*">\K.*?(?=</p>))|<relative-time[^>]*datetime="\K[^"]+' | \
  paste - - - | column -t
```

**Output format:**
```
a1b2c3d [2026-04-29] Commit message here
e4f5g6h [2026-04-28] Another commit message
```

---

## 3. Download → File → Line-by-Line Parse

Avoid in-memory truncation by saving full response:

```bash
# Download raw response
curl -s 'https://api.github.com/orgs/LayerZero-Labs/repos?per_page=100' -o /tmp/lz_repos.json

# Check file size (should be >30KB for 50 repos)
ls -lh /tmp/lz_repos.json

# Extract with grep (handles large files)
grep -o '"name": ".*"' /tmp/lz_repos.json | sed 's/"name": "//;s/"$//' | sort -u

# Extract description + updated_at pairs (parse context lines)
grep -oP '"name": "\K[^"]+(?="),.*"updated_at": "\K[^"]+' /tmp/lz_repos.json | \
  while IFS= read -r line; do
    name=$(echo "$line" | cut -d',' -f1)
    updated=$(echo "$line" | grep -oP '"updated_at": "\K[^"]+')
    echo "$name | $updated"
  done
```

---

## 4. Paginated Fetching with Manual Array Assembly

GitHub API paginates at 100 items max. For orgs with >100 repos:

```bash
#!/bin/bash
ORG="LayerZero-Labs"
PAGE=1
ALL_REPOS="/tmp/all_$ORG repos.json"
> "$ALL_REPOS"  # empty file

while true; do
  echo "Fetching page $PAGE..."
  curl -s "https://api.github.com/orgs/$ORG/repos?per_page=100&page=$PAGE" \
    -H 'Accept: application/vnd.github+json' | \
    jq -c '.[]' >> "$ALL_REPOS" 2>/dev/null
    
  # Check if page returned <100 items (last page)
  COUNT=$(wc -l < "$ALL_REPOS")
  LAST_PAGE_COUNT=$(tail -n 100 "$ALL_REPOS" | wc -l)
  if [ "$LAST_PAGE_COUNT" -lt 100 ]; then
    break
  fi
  PAGE=$((PAGE+1))
done

echo "Total repos: $(wc -l < $ALL_REPOS)"
```

**Fallback if `jq` fails on truncated page:**
```bash
# Save raw page, extract objects manually
curl -s "url" -o /tmp/page$PAGE.raw
# Each object is {...}, separated by commas, wrapped in [...]
# Use Python to parse tolerant JSON (or extract objects via regex)
python3 -c "
import re, json
with open('/tmp/page$PAGE.raw') as f:
    text = f.read()
objs = re.findall(r'\{[^{}]*\"name\"[^{}]*\}', text)
for obj in objs:
    try:
        data = json.loads(obj)
        print(data['name'], data.get('updated_at','?'))
    except: pass
"
```

---

## 5. Extracting Specific Data from Commit Objects

From a raw commit JSON (truncated or not):

```bash
# Get just the messages
curl -s '.../commits' | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data:
    print(f\"{c['sha'][:7]} [{c['commit']['committer']['date'][:10]}] {c['commit']['message'].strip()}\")
" 2>/dev/null

# If JSON decode fails, extract via regex:
curl -s '.../commits' | \
  grep -oP '"sha": "\K[a-f0-9]+' | head -20
curl -s '.../commits' | \
  grep -oP '"message": "\K[^"]+' | head -20
curl -s '.../commits' | \
  grep -oP '"date": "\K[^"]+' | head -20

# Align them (they appear in order)
paste \
  <(curl -s URL | grep -oP '"sha": "\K[a-f0-9]+' | head -n10) \
  <(curl -s URL | grep -oP '"date": "\K[^"]+' | head -n10) \
  <(curl -s URL | grep -oP '"message": "\K[^"]+' | head -n10) | \
  column -t
```

---

## 6. Rate Limit Handling

GitHub API rate limits:
- Unauthenticated: 60 requests/hour
- Authenticated: 5000 requests/hour

**If you hit limits:**
- Switch to HTML scraping (doesn't count against API rate limit)
- Add delay: `sleep 2` between requests
- Use `curl -I` first to check `X-RateLimit-Remaining` header

```bash
RESPONSE_HEADERS=$(curl -sI "https://api.github.com/...")
echo "$RESPONSE_HEADERS" | grep -i rate
```

---

## 7. Quick-Reference Regex Library

| Field | Regex Pattern |
|---|---|
| repo `name` | `"name":\s*"([^"]+)"` |
| repo `full_name` | `"full_name":\s*"([^"]+)"` |
| repo `description` | `"description":\s*"([^"]*)"` |
| repo `updated_at` | `"updated_at":\s*"([^"]+)"` |
| commit `sha` | `"sha":\s*"([a-f0-9]+)"` |
| commit `message` | `"message":\s*"([^"]+)"` |
| commit `date` | `"committer":\s*\{[^}]*"date":\s*"([^"]+)"` |
| issue `title` | `"title":\s*"([^"]+)"` |
| issue `state` | `"state":\s*"([^"]+)"` |

**Python helper for robust extraction:**
```python
import re, json

def extract_objects(text, key='name'):
    """Extract key-value pairs from partial JSON."""
    pattern = rf'"{key}":\s*"([^"]+)"'
    return re.findall(pattern, text)

# Usage:
# curl -s URL | python3 -c "from extract import extract_objects; print(extract_objects(open(0).read()))"
```

---

## 8. Case Study: LayerZero-Labs Repo Enumeration

**From this session:**
```bash
# API call failed (JSON truncated at 20KB)
curl -s 'https://api.github.com/orgs/LayerZero-Labs/repos?per_page=100' > /tmp/full.json

# Regex extraction succeeded:
$ grep -oP '"full_name": "\K[^"]+' /tmp/full.json | head -15
LayerZero-Labs/endpoint-v1-solidity-examples
LayerZero-Labs/LayerZero-v1
LayerZero-Labs/LayerZero-Aptos-Contract
LayerZero-Labs/lz_gauges
LayerZero-Labs/wrapped-asset-bridge
LayerZero-Labs/devtools
LayerZero-Labs/LayerZero-v2
...

# HTML fallback for commit extraction:
$ curl -s 'https://github.com/LayerZero-Labs/devtools/commits' -A 'Mozilla/5.0' |
  grep -oP '<p class="[^"]*mb-1[^"]*">\K.*?(?=</p>)' | head -10

🚀 Version packages (#1936)
[DEVREL-1425] fix: chunk setConfig to avoid calldata limits on L2s (#1935) 🔒
🚀 Version packages (#1912)
[DEVREL-1193] simple config should allow for skipping of EIDs (#1910) 🔒
[DEVREL-1159] feat(wiring): for solana, display txn data as base58 (#1901)
...
```

**Determined:** devtools last security-relevant commit was **Feb 19, 2026** (pre-hack). No post-incident security commits found.

---

## Quick Decision Tree

```
GitHub API returns valid JSON?
├─ YES → Parse JSON, extract fields
└─ NO → Was response truncated (>20KB, "Invalid control character")?
   ├─ YES → Save to file, regex extract key-value pairs
   └─ NO → Try HTML scraping (commits page)
       ├─ HTML works → Extract commit messages, dates, SHAs
       └─ HTML fails → Use GitHub GraphQL API (different endpoint)
           └─ Still fails → Switch to third-party service (github-jobs.n多见 API, or use GitHub mirror)
```

---

*End of extraction patterns. Save this reference for any future protocol repository forensics where standard JSON parsing fails.*
