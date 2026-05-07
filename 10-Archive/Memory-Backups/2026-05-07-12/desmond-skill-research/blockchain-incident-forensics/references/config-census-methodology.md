# Config Census Methodology

## What Is a Configuration Census?

A **configuration census** is a live indexer that continuously scans **all deployed protocol configurations** across tracked chains and presents them in a searchable dashboard.

**Purpose:**
- Answer: "How many apps are still vulnerable?"
- Show: Pre-incident vs post-incident config shifts
- Expose: Default vs overridden values in the wild
- Quantify: Protocol's security posture at ecosystem scale

**Examples discovered:**
- `dvnstats` → `observatory.indexing.co/layerzero-dvn-census` — LayerZero DVN configs
- `ethstorage explorer` — storage provider configurations
- `bridge exposure dashboards` — cross-chain bridge verifier settings

---

## Finding an Existing Config Census

### Step 1: Identify the Indexer Repo
Search GitHub:
```bash
curl -s "https://api.github.com/search/repositories?q=<protocol>+config+indexer&per_page=10" |
  jq '.[].full_name, .[].description'
```

Common naming patterns:
- `<protocol>-stats`
- `<protocol>-explorer`
- `<protocol>-census`
- `<protocol>-config-tracker`
- `*-dvnstats` (LayerZero-specific)

**Found in this session:** `sekuba/dvnstats` — "explore the scary web of layerzero security configs"

### Step 2: Locate Deployed Dashboard
The indexer README almost always contains:
```markdown
## Live Dashboard
https://observatory.indexing.co/<protocol>-<feature>
```

Check:
- `README.md` in the indexer repo
- `deploy-pages.sh` or CI config (points to hosting URL)
- GitHub Pages URL: `https://<username>.github.io/<repo>/`

**Found:** `https://observatory.indexing.co/layerzero-dvn-census`

### Step 3: Extract Current Metrics
Scrape the deployed dashboard HTML:
```bash
curl -s 'https://observatory.indexing.co/layerzero-dvn-census' |
  grep -oP '1-of-1\s+\(?\K[0-9]+'  # extract vulnerable count
  grep -oP 'Routes verified\s+\(?\K[0-9]+' # total tracked
```

**Key metrics to capture:**
- `Routes at 1-of-1` — vulnerable count
- `Routes at 4+ DVNs` — upgraded count
- `OApps still running 1-of-1` — list of at-risk apps
- `Confirmations` — pre/post comparison (e.g., 42 → 64)

---

## Building a Simple Config Census (If None Exists)

If no community indexer exists, you can **query on-chain directly** for snapshot.

### LayerZero Example (from dvnstats spec.md)

**Contract addresses (mainnet):**
```typescript
const ENDPOINT_V2 = "0x1a44076050125825900e736c501f859c50fE728c";
const RECEIVE_ULN302 = "0xc02Ab410f0734EFa3F14628780e6e695156024C2";
```

**Events to index:**
- `DefaultUlnConfigsSet((uint32,(uint64,uint8,uint8,uint8,address[],address[])[])` — global defaults
- `UlnConfigSet(address oapp, uint32 eid, (uint64,uint8,uint8,uint8,address[],address[]) config)` — per-OApp overrides

**Compute effective config:**
```typescript
effectiveRequiredDVNs = 
  oapp.requiredDVNCount !== 255 && oapp.requiredDVNs.length > 0
    ? oapp.requiredDVNs
    : default.requiredDVNs
```

**Query pattern:**
1. Index all `OApp` addresses (tokens/bridges)
2. For each OApp, fetch `UlnConfig` for each `eid` (destination chain)
3. Merge with default config if OApp doesn't override
4. Count `requiredDVNCount` and `requiredDVNs.length`
5. Group by configuration pattern (1-of-1, 2-of-3, 4-of-4, etc.)

---

## Interpreting Census Results

### DVN Configuration Patterns

| Pattern | Security Level | Typical Use | Risk |
|---|---|---|---|
| `1-of-1` | 🟥 **Critical** | Default/template | Single point of failure |
| `1-of-N` (N>1, threshold=1) | 🟨 **Weak** | Minimum viable | Any one DVN can approve |
| `M-of-N` (M=N) | 🟩 **Strong** | Post-hack pattern | All DVNs must agree |
| `M-of-N` (M > 1, M < N) | 🟩 **Strong** | Best practice | Quorum required |

**Real-world distribution from dvnstats (May 2, 2026):**
```
Total routes: 16
1-of-1:        8  (50% — still vulnerable)
4-of-4:        4  (50% — post-upgrade)
```

### Sentinel Value Trap

LayerZero uses `255` (0xff) as a **sentinel for "no required DVNs"**.

**Check this in config:**
```typescript
if (requiredDVNCount === 255) {
  effectiveRequiredDVNs = []  // Zero required — effectively 0-of-N
}
```

**Census question:** Are any routes using `requiredDVNCount = 255`? That's **even worse** than 1-of-1 — it means zero DVNs required (any message auto-approves).

---

## Key Fields to Track per OApp

From `spec.md` (dvnstats):

```
OAppSecurityConfig {
  libraryStatus: "tracked" | "unsupported" | "none"
  usesDefaultLibrary: boolean
  usesDefaultConfig: boolean
  fallbackFields: Set<string>  // which fields fall back to defaults
  
  effectiveRequiredDVNs: address[]  // merged final list
  requiredDVNCount: Int
  optionalDVNCount: Int
  optionalDVNThreshold: Int
  
  confirmations: BigInt  // blocks to wait
  peers: { [eid]: bytes32 }  // peer address per destination
}
```

**Minimum viable secure config:**
```yaml
requiredDVNCount: 2          # at least 2 DVNs
requiredDVNs: [addr1, addr2, addr3]  # 3+ distinct DVNs
confirmations: >= 50         # more than default
```

---

## Dashboard Design Pattern (for your own indexer)

If you need to build a census for a different protocol, copy this pattern from dvnstats:

### Frontend
- **index.html** — landing with summary stats
- **explorer.html** — table view of all OApps with filter/search
- **layerzero.json** — static snapshot (for static hosting)
- **slimify-layerzero.js** — data reduction for client-side

### Backend (Indexing Co / Envio)
- `config.yaml` — chain IDs + contract addresses
- `schema.graphql` — entities (DefaultUlnConfig, OAppUlnConfig, OAppStats)
- `src/EventHandlers.ts` — event parsers for `PacketDelivered`, `UlnConfigSet`, `PeerSet`
- `scripts/` — backfill, maintenance, data validation

### Deployment
- Database: Neon Postgres (serverless, branching)
- Hosting: Render (static Next.js frontend)
- CI: GitHub Actions (sync docs, update index)

---

## Quick Look: dvnstats Architecture (from this session)

```
┌─────────────────────────────────────────────┐
│  Envio Hypersync Indexer → GraphQL endpoint │
├─────────────────────────────────────────────┤
│  Events indexed:                             │
│  • PacketDelivered (usage evidence)          │
│  • DefaultUlnConfigsSet (global defaults)    │
│  • UlnConfigSet (per-OApp overrides)         │
│  • PeerSet (route enabling/blocking)         │
│  • RateLimitsChanged (throttling)            │
├─────────────────────────────────────────────┤
│  Computed: effective config per OApp route   │
│  Validates: DVN count vs array length match  │
│  Flags: zero-address filtering, threshold overflow │
└─────────────────────────────────────────────┘
            ↓
   `/dvnstats` repo frontend
            ↓
   https://observatory.indexing.co/layerzero-dvn-census
```

---

*End of methodology. Use this checklist when you need to determine: (1) is the protocol's official response accurate, (2) how widespread is the vulnerable configuration, (3) did the protocol actually fix the root cause or just deflect blame.*
