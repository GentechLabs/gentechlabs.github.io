# Incident Source Checklist

## Quick Reference: Where to Look for What

### For Bridge/Interoperability Exploits (LayerZero, Hyperlane, Axelar, Wormhole)

| Information Type | Primary Sources | Backup Sources | Keywords to Search |
|---|---|---|---|
| **Official Statement** | X/Twitter (protocol account), official blog, Discord announcements | GitHub Security Advisory, Telegram admin channel | "bridge", "exploit", "incident", "pause", "investigating" |
| **Transaction Evidence** | Forensic analysis repos (forked by community) | Etherscan/Arbiscan transaction traces, block explorers | "transaction", "hash", "block", "exploit tx" |
| **Vulnerable Config** | Live config census (dvnstats, bridge-explorer) | Protocol's Endpoint contract getConfig() calls | "1-of-1", "DVN", "verifier", "threshold", "requireDVNCount" |
| **Response Timeline** | Commit history (±7 days), issue PRs, forum posts | Social media timestamps, block timestamps | "commit", "hotfix", "security", "patch", CVE |
| **Ecosystem Impact** | Protocol pause announcements (other projects' X/Twitter) | Defi Llama TVL charts, governance forums (Aave, Compound) | "pause", "TVL", "governance", "exposure" |

### For Smart Contract Vulnerabilities (Reentrancy, Oracle Manipulation, Access Control)

| Information Type | Primary Sources | Backup Sources | Keywords |
|---|---|---|---|
| **Root Cause** | Audit firm report (if available), protocol post-mortem | Whitehat disclosure thread, rival protocol analysis | "reentrancy", "price oracle", "access control", "bypass" |
| **Affected Contracts** | Incident analysis repo (addresses.md) | On-chain event logs, contract verification status | "address", "contract", "vulnerable", "exploited" |

### For Governance/DAO Incidents (Governance attacks, proposal hacks)

| Information Type | Primary Sources | Backup Sources | Keywords |
|---|---|---|---|
| **Attack Vector** | Forum post-analysis, governance forum thread | Snapshot proposal history, tally.xyz voting records | "quorum", "voting", "proposal", "spoof", "flash loan" |
| **Loss Amount** } Treasury analysis, balance_of() before/after | Etherscan token transfers, Arkham alerts | "treasury", "drained", "transferred" |

---

## Priority Order of Investigation

1. **Find a community forensic analysis repo FIRST** (highest value)
   - Typically `username/<protocol>-hack-tracker` or `<protocol>-incident-analysis`
   - Contains transaction details, addresses, timeline already extracted
   - Example: `indexing-co/kelpdao-hack-tracker`, `dnakhoa/kelp-dao-hack-analysis`

2. **Find a live configuration census/indexer SECOND**
   - Shows current exposure state (how many apps still vulnerable)
   - Provides pre/post config comparison
   - Example: `dvnstats` → `observatory.indexing.co/layerzero-dvn-census`

3. **Check official sources THIRD**
   - Establish official narrative
   - Corroborate or contradict with community forensics

4. **Do repository forensics LAST**
   - Commit history (for evidence of rushed fixes)
   - Issue/PR discussions (for internal protocol debate)
   - Used to score protocol responsiveness

---

## Red Flags: When Official Narrative May Be Incomplete

- Official statement released **>24 hours after incident** (suggests internal debate)
- Blame assigned **solely to user/config error** without acknowledging infrastructure factors
- No **forensic data released** (transaction hashes, affected contracts)
- **Community analysis repos** contradict official timeline
- Protocol repo activity shows **security-related commits within 48h** but no public advisory
- **Third-party indexers** expose different config state than protocol claims

Example (KelpDAO incident):
- ❌ LayerZero: "not our responsibility, user used 1-of-1"
- ✅ Community forensics: "LayerZero's DVN RPC was poisoned, failover forced to compromised nodes"
- ✅ Live census: "40% of apps still 1-of-1, protocol did nothing to enforce minimums"

---

*Keep this checklist open while researching. Check each category systematically.*
