# Chain Ecosystem Scan Methodology

## Trigger

When asked "what [category] projects exist on [chain]?" — this is a broader ecosystem mapping task, not a single-token farming assessment. Use this methodology instead of (or before) the cross-chain farming assessment.

## Primary Data Source: DeFiLlama API

**DeFiLlama is the only reliable on-chain data source from Hermes.** All other sources (CoinGecko, DeFiLlama website, Google, DuckDuckGo) are blocked by Cloudflare/CAPTCHA from the Hermes agent environment.

### Endpoint: `/protocols`
```bash
curl -s --max-time 15 "https://api.llama.fi/protocols" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data:
    chains = p.get('chains', [])
    category = p.get('category', '')
    name = p.get('name', '')
    tvl = p.get('tvl', 0)
    # Filter by chain and category
    has_chain = any('avalanche' in c.lower() for c in chains)
    if has_chain and 'rwa' in category.lower() and tvl > 10000:
        print(f'{name} — TVL: \${tvl:,.0f} — {category}')
"
```

### Endpoint: `/protocol/{name}`
```bash
# Get detailed info for a specific protocol
curl -s --max-time 10 "https://api.llama.fi/protocol/centrifuge" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Description: {data.get(\"description\", \"\")[:300]}')
print(f'URL: {data.get(\"url\")}')
print(f'Chains: {data.get(\"chains\")}')
print(f'Chain TVL: {data.get(\"currentChainTvls\", {})}')
"
```

### Key Fields
- `chains`: list of chain names (e.g., `["Ethereum", "Avalanche", "Base"]`)
- `category`: protocol category (e.g., "RWA", "Dexs", "Lending")
- `tvl`: total value locked in USD
- `currentChainTvls`: dict of per-chain TVL breakdown
- `slug`: URL-safe name for detail endpoint
- `symbol`: token symbol

## Research Workflow

### Step 1: Broad Category Scan
```bash
curl -s --max-time 15 "https://api.llama.fi/protocols" | python3 -c "
import json, sys
data = json.load(sys.stdin)
TARGET_CHAIN = 'avalanche'  # or 'solana', 'base', etc.
TARGET_CATEGORY = 'rwa'     # or 'defi', 'dexs', etc.

results = []
for p in data:
    chains = p.get('chains', [])
    category = p.get('category', '')
    name = p.get('name', '')
    tvl = p.get('tvl', 0)
    has_chain = any(TARGET_CHAIN in c.lower() for c in chains) if isinstance(chains, list) else False
    if has_chain and TARGET_CATEGORY in category.lower() and tvl and tvl > 10000:
        is_native = len(chains) == 1
        results.append({
            'name': name,
            'symbol': p.get('symbol', ''),
            'tvl': tvl,
            'category': category,
            'chains': chains,
            'native': is_native
        })

results.sort(key=lambda x: -x['tvl'])
for r in results:
    flag = '🟢 NATIVE' if r['native'] else f'🔵 Multi-Chain ({len(r[\"chains\"])} chains)'
    print(f'{r[\"name\"]} ({r[\"symbol\"]}) — TVL: \${r[\"tvl\"]:,.0f} — {flag}')
    print(f'  Chains: {\", \".join(r[\"chains\"][:5])}')
"
```

### Step 2: Deep-Dive on Top Results
For protocols with highest TVL or native to target chain, fetch detail endpoint for description and URL.

### Step 3: Cross-Reference with Vault
```bash
# Check if any protocols are already tracked
rg -i "PROTOCOL_NAME" /root/vaults/gentech/03-Strategies/ --type markdown
```

### Step 4: Write Vault Entry
Use structured format with tiers by TVL, asset class breakdown, and clear recommendation.

## API Reliability Notes

| Source | Status | Notes |
|--------|--------|-------|
| DeFiLlama API (`api.llama.fi`) | ✅ Works | No auth needed, `--max-time 15` recommended |
| CoinGecko API | ⚠️ Unreliable | Frequent timeouts from Hermes environment. Use as fallback only. Free tier: 10-30 calls/min |
| DeFiLlama website | ❌ Blocked | Cloudflare bot detection |
| CoinGecko website | ❌ Blocked | Cloudflare bot detection |
| Google Search | ❌ Blocked | CAPTCHA from Hermes IP |
| DuckDuckGo | ❌ Blocked | Bot detection + CAPTCHA |
| X/Twitter | ❌ Blocked | Requires login for most content |

**Rule**: Always start with DeFiLlama API. If it fails, try CoinGecko API with rate limiting. Browser-based research is essentially non-functional from Hermes.

## Output Format: Tiered Protocol Landscape

Structure findings by tier:
- **Tier 1 — Institutional Grade** ($100M+ TVL): Major protocols with deep liquidity
- **Tier 2 — Established** ($10M–$100M): Proven but smaller
- **Tier 3 — Emerging** (<$10M): Newer or niche

For each protocol:
- Name, ticker, TVL
- Asset class (what does it tokenize?)
- Chain presence (native vs multi-chain)
- Whether it's relevant to the user's specific question

## Related

- `cross-chain-farming-assessment.md` — for evaluating whether a specific token can be farmed on a target chain
- `protocol-due-diligence-framework.md` — for deep-diving into a specific protocol's risk profile
