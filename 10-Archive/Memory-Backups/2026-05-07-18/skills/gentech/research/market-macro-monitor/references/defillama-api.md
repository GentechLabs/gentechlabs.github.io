# DeFiLlama API Quick Reference

Base URL: `https://api.llama.fi`

## Endpoints

| Endpoint | Response Size | Use Case |
|----------|--------------|----------|
| `/protocols` | ~5MB | All protocols, filter in Python |
| `/protocol/{name}` | Small | Single protocol detail + historical TVL |
| `/tvl/{name}` | Tiny | Just the TVL number |
| `/chains` | Small | List of all chains |

## Common Queries

### Filter protocols by chain
```python
avax_protocols = [p for p in data if 'Avalanche' in p.get('chains', [])]
```

### Filter by category
```python
rwa = [p for p in data if p.get('category','').lower() == 'rwa']
yield = [p for p in data if 'yield' in p.get('category','').lower()]
```

### Combined chain + category
```python
avax_rwa = [p for p in data if 'Avalanche' in [c.lower() for c in p.get('chains',[])] and 'rwa' in (p.get('category','') + ' ' + ' '.join(p.get('tags',[]))).lower()]
```

### Sort by TVL descending
```python
for p in sorted(protocols, key=lambda x: x.get('tvl',0) or 0, reverse=True)[:20]:
    tvl = p.get('tvl', 0) or 0
    print(f"{p['name']} | TVL: ${tvl/1e6:.2f}M | Category: {p.get('category','N/A')}")
```

### Key protocol fields
- `name` — Display name
- `slug` — URL-safe ID (use for `/protocol/{slug}`)
- `tvl` — Total Value Locked (can be None)
- `mcap` — Market cap (can be None)
- `category` — e.g., "RWA", "Lending", "Dexs", "Yield"
- `chains[]` — Array of chain names (first = primary chain)
- `tags[]` — Additional categorization tags
- `description` — Short text description

## Pitfalls

- `/protocols` returns ~5MB. Cache to disk, filter in Python. Don't try to stream or paginate.
- `tvl` and `mcap` can be `None` — always use `(p.get('tvl',0) or 0)` pattern.
- Chain names are case-sensitive: `"Avalanche"` not `"avalanche"`. Use `.lower()` for comparison.
- `category` can be empty string — check before filtering.
- Some protocols appear on multiple chains. The first chain in `chains[]` is the primary/home chain.
- Landshare was on BSC/Polygon/Arbitrum (not Avalanche despite AVAX association) — always verify chain list, don't assume from name.
