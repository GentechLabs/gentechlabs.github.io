# Filter Criteria — Realized Preferences (Session 2026-05-02)

## Core Rules (Jordan-confirmed)
- Prize ≥ $1,000 USD equivalent
- Time remaining ≥ 7 days
- Chains: Ethereum, Base, Solana (primary)
- Include other chains **only if prize > $5,000** (e.g., Stellar $135K qualifies)
- Exclude contests requiring expert-level approval/portfolio gate

## Platform-Specific Adjustments

### Devpost Exceptions
- For non-blockchain hackathons (general AI, healthcare, etc.), raise prize threshold to **≥ $10,000** to avoid low-value noise.
- Example: Agents Assemble ($32,500) qualifies despite being healthcare-focused; smaller dev contests ignored.

### Code4rena Chain Handling
- `league` field may say "Stellar", "Hyperliquid", "Ethereum", etc.
- If league is missing or says "EVM", use sponsor logos or contest description to infer chain; default to "EVM" only if truly chain-agnostic.

### Colosseum / Solana
- All Frontier tracks are Solana-native; chain = "Solana"
- Prize often shown as "Up to $X" — record as-given; flag as non-guaranteed max in notes field

### Cantina
- Chain is explicit in card ("Base", "Ethereum", "Arbitrum") or in `assetGroups[].chains[]`
- Date ambiguity: three dates may appear (opens, submission opens, deadline). Use **latest** date as deadline.

## Cross-Chain Flags (boolean fields in output)
- `layerzero`: description mentions LayerZero, OFIN, cross-chain messaging
- `kite_ai`: sponsor includes Kite AI or Kite Pavilion (Colosseum track)
- `agentescrow_solana`: AgentEscrow protocol name + Solana chain mentioned

## Prize Parsing Nuances
- Format: `$135,000 USDC` → extract 135000; currency field optional but store if present
- Ranges: `$10,000 – $50,000` → take **maximum** value (conservative prioritization)
- Devpost `prizes` array may have multiple tiers; sum all `amount` fields for total

## Time Remaining Calculation
- Use timezone-aware `datetime.now(timezone.utc)` vs deadline parsed as UTC-aware
- If deadline string contains timezone abbreviation (PST, ET), use `dateutil.parser.parse()` to normalize
- Return integer days (floor), not rounded
- For "ongoing"/"TBD" contests, return `999` (qualifies under prize rule if over $5K on non-EVM chains)

## Decision Tree
```
Is prize >= $1000?
 ├─ No → EXCLUDE
 └─ Yes
    ├─ Is days_remaining >= 7?
    │   ├─ No → EXCLUDE (except high-value ongoing)
    │   └─ Yes
    │       ├─ Chain in (ETH, BASE, SOL)? → INCLUDE
    │       └─ Chain other + prize > $5000? → INCLUDE
    └─ Else EXCLUDE
```

## Sessions Using This Criteria
- 2026-05-02 initial scan: 5 qualifying contests identified (see `Contest-Scan-2026-05-02.md`)
- Updated `02-Labs/Bug-Bounties/00-Active-Bounties.md` daily via cron
