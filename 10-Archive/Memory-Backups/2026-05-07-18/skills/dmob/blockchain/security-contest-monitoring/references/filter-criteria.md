# Filter Criteria Reference
**Skill:** security-contest-monitoring  
**Version:** 2026-05-02  

---

## Mandatory Filters (ALL must pass)

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Prize pool** | ≥ $1,000 USD equivalent | Minimum viable bounty value |
| **Time remaining** | ≥ 7 days from scan date | Enough time to research & submit |
| **Chain eligibility** | Ethereum, Base, Solana (always OK) | Matches Gentech Labs chain focus |
| **Chain exception** | Other chains OK **if prize > $5,000** | Stellar ($135K), Hyperliquid ($22K) qualify |
| **Contest status** | "Live", "Active", "Open" only | Not upcoming or closed |
| **Eligibility gate** | None required | Skip "expert-only" or portfolio-review contests |

---

## Time Calculation

```python
from datetime import datetime, timezone
from dateutil import parser

def days_remaining(end_date_str):
    """Parse any date string, return whole days remaining."""
    dt = parser.parse(end_date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    return max(0, (dt - now).days)
```

---

## Chain Mapping Table

| Platform field value | Canonical chain | Qualifies? |
|----------------------|----------------|------------|
| `ethereum`, `mainnet` | Ethereum | ✅ |
| `base` | Base | ✅ |
| `solana` | Solana | ✅ |
| `stellar` | Stellar | ✅ (if prize > $5K) |
| `hyperliquid` | Hyperliquid | ✅ (if prize > $5K) |
| `monad` | Monad (EVM) | ✅ (EVM) |
| `arbitrum` | Arbitrum | ✅ |
| `polygon` | Polygon | ✅ |
| `avalanche`, `avax` | Avalanche C-Chain | ✅ |
| `sui` | Sui | ✅ |
| `evm`, "multi-chain" | Unknown – infer from context or mark "Multi-chain" | ⚠️ Requires explicit chain mention |

---

## Prize Qualification Logic

```python
def qualifies(prize_str, days_left, chain, prize_numeric=None):
    if prize_numeric is None:
        prize_numeric = parse_prize(prize_str)  # → int USD
    if prize_numeric < 1000:
        return False, "Prize below $1K"
    if days_left < 7:
        return False, f"Only {days_left} days left"
    if chain in ['ethereum', 'base', 'solana']:
        return True, "Chain qualified"
    if prize_numeric > 5000:
        return True, "Exception chain with high prize"
    return False, "Chain not eligible and prize ≤ $5K"
```

---

## Cross-Chain Flags (when to set)

| Flag | Trigger keywords |
|------|-----------------|
| `layerzero` | "LayerZero", "OFIN", "cross-chain messaging", Omnichain |
| `kite_ai` | "Kite AI", "kite.ai", "Kite Pavilion", "Kite track" |
| `agentescrow_solana` | "AgentEscrow", "agentescrow.xyz" + "Solana" nearby |

---

## Excluded Platforms (per Jordan)

- **HackenProof**: "Account doesn't qualify" → skip entirely
- **Hack and Pro**: Inaccessible (as of 2026-05-02) → skip

---

*Reference only — not used directly in automation.*
