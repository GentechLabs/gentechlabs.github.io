# Incident Type → Source Prioritization Matrix

**When investigating a security incident, start with these sources in order per incident type.**

---

## Bridge / Interoperability Exploit (LayerZero, Hyperlane, Axelar, Wormhole)

**Priority 1 — Find community forensic analysis repo FIRST:**
```
Search: "<protocol> hack tracker" OR "<protocol> incident analysis"
Expected: username/protocol-hack-tracker or protocol-incident-analysis
Why: Contains transaction hashes, addresses, timeline extracted by security researchers
Example found: indexing-co/kelpdao-hack-tracker
```

**Priority 2 — Live config census/indexer:**
```
Expected form: username/protocol-stats OR protocol-explorer
Dashboard URL: https://observatory.indexing.co/<protocol>-<feature>
Why: Shows real-time exposure ("how many apps still vulnerable?")
Example found: observatory.indexing.co/layerzero-dvn-census
```

**Priority 3 — Official communications:**
- X/Twitter official account `@<Protocol>`
- Official blog `protocol.xyz/blog/incident` or `protocol.xyz/security`
- GitHub Security Advisory (`github.com/org/<org>/security-advisories`)

**Priority 4 — Repository forensics:**
- Commits ±7 days (look for `security:`, `hotfix:`, or anonymous "chore:" that might hide patches)
- Issues opened/closed during incident window (security label)
- Pull requests merged without announcement

**Priority 5 — Ecosystem impact chain:**
- Protocols that paused OFT routes (search `"paused LayerZero" site:twitter.com`)
- TVL charts (Defi Llama) for sudden drops
- Governance forum posts from affected protocols (Aave, Compound, etc.)

---

## Smart Contract Vulnerability (Reentrancy, Oracle Manipulation, Access Control)

**Priority 1 — Audit firm / protocol post-mortem:**
```
Search: "<protocol> post-mortem" OR "<protocol> incident report"
Expected: Medium post, Mirror article, or GitHub release
Why: Authoritative root cause (usually)
```

**Priority 2 — Etherscan transaction analysis:**
- Locate exploit transaction hash from official announcement
- Decode calldata (if custom): `cast calldata decode <sig> <data>`
- Trace internal calls: `cast trace <tx_hash>`
- Check ` SOLUTION` or `Salvage` functions called post-exploit

**Priority 3 — Whitehat disclosure threads:**
- Search `"<protocol> vulnerability" site:mirror.xyz`
- Check Twitter threads from known whitehats (@samczsun, @tinchoabbate, etc.)
- Look for pre-incident disclosure timeline ("we reported this on X, ignored")

**Priority 4 — Contract code changes:**
- Identify affected contract address
- Find source repo + commit before/after
- `git diff` the vulnerable function
- Check if fix was backported or only to master

**Priority 5 — Affected contracts enumeration:**
From incident analysis repo, collect all vulnerable contract addresses
Cross-check on Etherscan for verification status (unverified = higher risk)

---

## Governance / DAO Attack (Proposal Spoof, Quorum Bypass, Flash Loan Vote)

**Priority 1 — Governance forum thread:**
```
Search: "<protocol> governance incident" OR "<protocol> proposal hack"
Expected: forum.protocol.xyz/t/<proposal-title>
Why: Shows attacker's strategy, community response, counter-proposals
```

**Priority 2 — Snapshot / Tally history:**
- `snapshot.org/#/proposal/<id>` — vote breakdown
- `tally.xyz/gov/<protocol>` — check for emergency withdrawals
- Look for: "voting power > 100%", "multiple votes from same address"

**Priority 3 — Transaction forensics:**
- Flash loan tx (Aave, Balancer) preceding proposal
- Voting power acquisition (token transfer before vote)
- `cast call` on governance contract's `state()` or `voters()` mapping

**Priority 4 — Post-attempt state changes:**
- Treasury balance before/after
- Token minting/burning events
- Role changes (admin, executor, guardian)

**Priority 5 — Protocol response classification:**
- Emergency `pause()` or `stop()` call
- Emergency upgrade (timelock bypass?)
- Rollback attempted (rare on L1, common on L2 via council)

---

## Oracle / Price Feed Manipulation

**Priority 1 — Oracle provider incident response:**
- Chainlink: check `chain.link` status page, blog posts
- Pyth: check `pyth.network/blog`, Twitter `@PythNetwork`
- API3: check `api3.org/status`

**Priority 2 — Affected protocol announcements:**
- Search `"oracle manipulation" + "<protocol>" site:twitter.com
- Check protocol's Discord #announcements channel
- Look for "paused due to oracle" in tx memo

**Priority 3 — Price deviation evidence:**
- Compare reported price vs. other sources (CoinGecko, DeFi Llama)
- Check for sharp divergence on affected chain (via Dune query if available)
- Identify which assets were stale or manipulated

**Priority 4 — Transaction sequence:**
- Find large borrow/swap that triggered liquidation cascade
- Trace back to oracle update transaction
- Check if oracle update was from unauthorized address

**Priority 5 — Scope of impact:**
- How many lending markets used same oracle?
- Cross-protocol contamination (e.g., same Chainlink feed used by Aave + Compound)
- Total value at risk (TVR) — protocol's exposure

---

## Access Control / Privileged Key Compromise

**Priority 1 — Emergency transaction forensics:**
- Find the malicious transaction (often `setOwner`, `transferOwnership`, `upgradeTo`)
- Check if `execute()` or `schedule()` was called on TimelockController
- If multisig: check Safe transaction history, confirmations count

**Priority 2 — Owner/Admin address identification:**
- `cast call <contract> "owner()(address)"`
- `cast call <contract> "admin()(address)"`
- Check if proxy admin is separate from implementation
- Look for `Guardian` (Axelar), `Controller` (LayerZero), `Executor` (OpenZeppelin Governor)

**Priority 3 — Post-compromise recovery actions:**
- Was the compromised role revoked/transferred?
- Emergency recovery (pause + upgrade)?
- Timelock delay bypassed? (Red flag)

**Priority 4 — Key exposure source:**
- Was private key leaked (GitHub commit, hardcoded in frontend)?
- Was the signer device compromised (social engineering)?
- Was it a multisig with insufficient threshold?

**Priority 5 — Funds movement tracing:**
- Where did stolen funds go? (Tornado Cash, THORChain, fixed float)
- Bridge usage to exit chain
- Mixer usage (if still operational)

---

## Cross-Reference: Quick Source Lookup

| Incident Type | Start Here | Then Check | Critical Keyword |
|---|---|---|---|
| Bridge exploit | Community hack-tracker repo | dvnstats/ config census | `"1-of-1 DVN"`, `"default config"` |
| Contract vuln | Protocol post-mortem | Etherscan exploit tx | `"reentrancy"`, `"oracle"` |
| Governance attack | Governance forum | Snapshot vote history | `"quorum"`, `"voting power"` |
| Oracle issue | Oracle provider status | Affected protocol pause | `"stale price"`, `"deviation"` |
| Key compromise | Malicious transaction hash | Multisig confirmations | `"owner()"`, `"admin()"` |

---

*Keep this matrix open during research. It maps incident types to source prioritization, so you don't waste time on low-value sources.*
