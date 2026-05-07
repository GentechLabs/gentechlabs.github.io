# Gentech Domain Signals — Session-Specific Patterns Discovered

## Discrepancy Resolution Protocol (May 3 Incident)
**Context:** D5 monitoring scripts reported divergent position values ($55 variance) across `d5-master-cron.py`, `defi-milestone-summary.py`, `lp-position-reader.py`.

### Ground Truth Hierarchy
1. **Primary source** — `lp-position-reader.py` (on-chain decoded balances + active bin + efficiency)
2. **Secondary source** — `d5-master-cron.py` (use for watchlist prices and pool volume metrics only)
3. **Tertiary source** — `defi-milestone-summary.py` (narrative templating only; ignore numeric discrepancies)

### Vault Update Rule
Balance fields in vault entries **MUST** match `lp-position-reader.py` numbers exactly. If any script diverges by >$0.50 or efficiency differs by >5 percentage points, document variance in vault entry notes.

### Documentation
Full protocol: `09-Green Room/skills-captures/d5-monitoring-script-discrepancy-resolution.md`

## State File Fragmentation Bug
**Root cause:** Scripts maintain independent state caches in different filesystem locations:
- `~/.hermes/scripts/` (central)
- `~/.hermes/profiles/yoyo/home/.hermes/scripts/` (profile-specific)

`.lfj-*.json` files diverge, causing cross-script reporting divergence.

**Fix:** Symlink all `.lfj-*.json` across all HERMES profiles to central location.
```bash
# Proposed fix (run by DMOB)
ln -sf ~/.hermes/scripts/.lfj-*.json ~/.hermes/profiles/yoyo/home/.hermes/scripts/
# Repeat for all profiles: dmob, desmond, gentech
```

**Impact:** Affects all LP monitoring, milestone tracking, DCA calculations.

## Milestone Ladder Inconsistency
Two sources of truth for milestone thresholds:

| Source | Ladder | Values |
|--------|--------|--------|
| `d5-master-cron.py` (hardcoded) | $5/$20/$55/$200 | Scout→Journeyman→... |
| AAE config file | $3/$5/$8/$10/... | Continuous ladder per AAE spec |

**Owner:** YoYo to reconcile (deadline May 3 EOD)
**Impact:** Vault milestone entries may be misaligned; consolidation work blocked until resolved.

## IL Spike Threshold Logic
- **Threshold:** 2% IL deviation triggers review flag
- **LFJ AVAX/USDC position:** -17.65% IL on May 3 → 🚨 Review flag auto-triggered
- **Efficiency:** 38.2% (watch zone, not yet critical ≤30%)
- **Milestone alignment:** Still in Scout tier ($3/day target) despite IL spike

**On-chain verification required** before any rebalance decision.

## Understand-Anything Integration Assessment
**Trigger:** Jordan identified UA as P1 stack accelerator (May 3). Three parallel team assessments requested.

### DMOB — Technical Review
- Questions: runtime (Python/Node?), graph DB (Neo4j/NetworkX), self-host requirements, privacy
- Deliverable: Installation validation on AgentEscrow codebase, graph export, dashboard launch
- Due: May 5 EOD

### YoYo — Strategic Review
- Questions: Portfolio graph mapping, correlation discovery, real-time data feeds, Karpathy wiki compatibility
- Deliverable: Strategic value assessment, integration plan for vault-wide indexing
- Due: May 5 EOD

### Desmond — Creative Review
- Questions: Export formats (SVG/Mermaid/Excalidraw), video fly-through, content series plan
- Deliverable: Visual storytelling opportunities, brand differentiation angle
- Due: May 5 EOD

**Decision point:** Group reconvene May 5 EOD; Jordan go/no-go.

## Hermes OAuth Incident Pattern
**Revocation trigger:** Refresh token expired/revoked on provider side (Nous Portal)

**Symptoms:**
- `refresh_nous_oauth.py` returns `needs_reauth: true`
- Gateway auth failures on first request
- Data collection scripts blocked
- Active agent keys continue until expiry (~24h)

**Resolution:**
- Manual `hermes model` re-auth required (cannot auto-recover from refresh revocation)
- Verify `config.yaml` has `fallback_providers` to avoid single-point failures
- Monitor agent key expiry timestamps

**Monitoring gap:** Watchdog monitors session errors but **NOT** cron auth failures — should extend to parse `cron/jobs.json` `last_error` fields and flag `needs_reauth` as P0.

## Solana Frontier Track Items (as of May 3)
**Status:** DMOB OFFLINE; build progress unknown

**Deliverables remaining:**
- Anchor workspace scaffold (4 programs) — ?
- AgentRegistry (World ID CPI + Swig wallet) — ?
- JobEscrow (PDA vaults, 8-state lifecycle) — ?
- Reputation (Metaplex Core NFT mint) — ?
- DisputeResolver (evidence-based resolution) — ? (needs Desmond demo materials)
- Full test suite — ?
- Devnet deployment — ?
- Demo app (Next.js + Phantom + Swig + World ID) — ?

**Deadlines:** Code complete May 8, submit May 11 (T-8 days)

**Kite AI Hackathon (May 17):** Secondary track; scoping doc overdue EOD May 3.

## Master Todo Staleness Pattern
`09-Green Room/master-todo.md` last updated **Apr 25** (as of May 3). Desmond tasked with refresh to incorporate Apr 29–May 2 scope changes.

**Impact:** Sprint planning based on stale baseline; missing recent approvals and scope changes.

**Remedy:** Weekly refresh every Monday (W kickoff) mandatory.

## Agent Offline Weekend Pattern
All agents OFFLINE Sunday May 3 (typical weekend cadence). No weekend sessions logged.

**Consequences:**
- No handoff acknowledgments
- No progress updates
- Monday morning catch-up flood
- Escalation windows still run (cron enforcement) regardless

**Mitigation:** Weekends excluded from ACK deadlines (policy suggestion for future).

## File Modification Surges
May 3: 242 files modified (script discrepancy incident + vault sweep)  
May 2: 13+ files (major D5 consolidation shipped)  
Normal days: 2–7 files

**Interpretation:** High modification count = incident response or major refactor day. Correlate with daily log "Key Decisions" and "Escalations" sections.

## DisputeResolver Demo Blockage
- **Requested:** May 1 (Desmond)
- **Due:** May 2 EOD
- **Status:** 🔴 Overdue, DMOB response pending
- **Impact:** Desmond creative work (submission demo) blocked
- **Handoff:** DMOB → Desmond (code snippets + 30-second clip concept)

## Notes
These patterns are **Gentech-specific** and differ from generic handoff advice. Always check:
1. OAuth incident file first when data pipelines fail
2. Handoff board for P0 escalations (not just Mess Hall chat)
3. Master todo staleness indicator (Apr 25 baseline = stale)
4. Weekend agent OFFLINE state (normal, but escalations still apply)
5. Two-source-of-truth issues (hardcoded vs config mismatches)
