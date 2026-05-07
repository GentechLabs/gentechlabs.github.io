# x402 Ecosystem Partner Data Extraction Pattern

## Problem
The x402 ecosystem page (`x402.org/ecosystem`) displays partners in a Next.js frontend with data embedded in the HTML or loaded from TypeScript files, not from a public JSON endpoint.

## Data Locations (as of May 2026)

### Primary source: TypeScript data file
```
typescript/site/app/ecosystem/data.ts
```
This file exports `Partner[]` array. You need to extract the array literal from TypeScript syntax (not valid JSON due to trailing commas, comments, or type annotations).

**Extraction pattern:**
```python
import re

content = fetch("https://raw.githubusercontent.com/x402-foundation/x402/main/typescript/site/app/ecosystem/data.ts").text

# Find the partners export array
match = re.search(r'export\s+const\s+partners\s*=\s*(\[\{[\s\S]*?\}\])', content)
if match:
    partners_ts = match.group(1)
    # Convert TypeScript array to JSON (remove trailing commas, comments)
    partners_json = ts_to_json(partners_ts)
    partners = json.loads(partners_json)
```

### Secondary source: HTML page scrapers
The rendered page contains GitHub org/repo references in card markup:

```bash
# Extract all GitHub org/repo pairs from ecosystem page HTML
curl -s https://x402.org/ecosystem \
  | grep -oP 'github\.com/\K[A-Za-z0-9_-]+/[A-Za-z0-9_-]+' \
  | sort -u
```

This yields projects like:
- `OpenZeppelin/relayer-plugin-x402-facilitator`
- `BlockRunAI/ClawRouter`
- `wahyucom/x402-sandbox`
- `grimn0va/boltzpay`

### Fallback: GitHub code search
If data.ts is inaccessible (rate-limited), search GitHub directly:

```bash
# Search for x402 + integrator name
curl -s "https://api.github.com/search/repositories?q=x402+stripe&per_page=5" | jq -r '.items[] | "\(.full_name): \(.description)"'
```

## x402-Specific Findings (May 2026)
- **Total ecosystem projects on site:** ~200+ across 11 categories (Client-Side, Services, Infrastructure, Facilitators, Tools)
- **Major integrators count (mentions on site):**
  - Base: 449 mentions (dominant L2)
  - Solana: 86 mentions
  - Polygon: 40 mentions
  - AWS: 22 mentions
  - Stripe: 11 mentions
  - Alchemy/QuickNode: 11 mentions each
  - OpenAI + Anthropic: 11 total
- **Unknown exact partner list:** The `data.ts` file was rate-limited during access; partner enumeration incomplete. Prioritize raw fetch in future session.

## Partner Data Schema (from data.ts interface)
```typescript
interface Partner {
  name: string;
  description: string;
  logoUrl: string;      // /images/ecosystem/logos/project-logo.png
  websiteUrl: string;
  category: string;     // e.g., "client-side-integrations"
  typeLabel?: string;
  top_section?: boolean;
  slug?: string;
  facilitator?: FacilitatorInfo;  // only for facilitators
}

interface FacilitatorInfo {
  baseUrl: string;
  networks: string[];   // e.g., ["base", "solana"]
  schemes: string[];    // e.g., ["exact"]
  assets: string[];     // e.g., ["USDC"]
  addresses: { [key: string]: string[] };  // chain → contract addresses
  supports: {
    verify: boolean;
    settle: boolean;
    supported: boolean;
    list: boolean;
  };
}
```

## Extraction Script Pattern (Python)
```python
import requests, re, json, demjson3  # or custom TS→JSON converter

def fetch_x402_partners():
    url = "https://raw.githubusercontent.com/x402-foundation/x402/main/typescript/site/app/ecosystem/data.ts"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    
    # Extract partners array
    partners_match = re.search(r'export\s+const\s+partners\s*=\s*(\[[\s\S]*?\]);', resp.text)
    if not partners_match:
        raise ValueError("partners array not found")
    
    partners_ts = partners_match.group(1)
    
    # Convert TS→JSON: remove comments, fix trailing commas
    partners_json = re.sub(r'//.*?\n|/\*.*?\*/', '', partners_ts, flags=re.DOTALL)
    partners_json = re.sub(r',(\s*[}\]])', r'\1', partners_json)  # trailing commas
    
    partners = json.loads(partners_json)
    return partners
```

## Verification
After extraction, deduplicate and categorize:
```python
from collections import Counter
cats = Counter(p['category'] for p in partners)
print(f"Categories: {dict(cats)}")

# Faciltator count
facilitators = [p for p in partners if 'facilitator' in p]
print(f"Facilitators: {len(facilitators)}")
for f in facilitators:
    net = f['facilitator']['networks']
    print(f"  {p['name']} — networks: {net}, assets: {f['facilitator']['assets']}")
```
