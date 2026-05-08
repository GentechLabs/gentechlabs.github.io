---
name: blockchain-incident-forensics
description: Systematic research methodology for blockchain protocol/application security incidents — triangulate official response, community analysis, live configuration exposure, and ecosystem impact.
triggers:
  - research security incident exploit hack
  - investigate protocol vulnerability exposure
  - assess cross-chain bridge incident
  - forensic analysis blockchain exploit
  - post-mortem research DeFi incident
  - dvn config census analysis
related:
  - security-research
  - blockchain-data-analysis
  - github-forensics
templates: []
scripts: []
---

# Blockchain Incident Forensics

## Overview

When a blockchain protocol or application suffers a security incident, research requires **triangulating multiple unconventional sources**:
1. **Official communications** (X/Twitter, blog posts, GitHub announcements)
2. **Community forensic analysis** (forked analysis repos, tracking dashboards)
3. **Live configuration exposure** (on-chain indexers, config census)
4. **Repository forensics** (commit history, issue discussions, PR activity)
5. **Ecosystem impact** (paused protocols, TVL changes, affected contracts)

This skill provides a repeatable methodology for assembling a comprehensive incident picture from fragmented public sources.

---

## Trigger Conditions

Use this skill when you need to research:
- **Bridge/ interoperability exploits** (LayerZero, Hyperlane, Axelar, Wormhole)
- **Smart contract vulnerabilities** with ecosystem-wide implications
- **Protocol incidents** where official response may be incomplete or conflicting
- **Configuration-based vulnerabilities** (e.g., "1-of-1 DVN", "owner-only", "missing guard")
- **Ecosystem exposure assessment** — "how many apps are still vulnerable?"

---

## Research Phases

### Phase 1: Official Source Mapping (Timeframe: incident date ± 72h)

**Objective:** Establish the official timeline and LayerZero's (or protocol's) stated position.

#### Step 1.1: Official Communications
Search for posts on **incident date ± 2 days**:
- **X/Twitter posts** from protocol official account (use `cdn.syndication.twimg.com/tweet?id=<ID>`)
- **Blog posts** (typically at `layerzero.network/blog/`, `protocol.xyz/blog/`, etc.)
- **Discord/Telegram announcements** (check `discord.com/channels/...` via search)
- **GitHub Security Advisories** (`github.com/orgs/<org>/security-advisories`)

**Key data to extract:**
- Incident acknowledgment date/time
- Official blame attribution (user error vs protocol fault)
- Claims about "first exploit" or "zero core exploits"
- Any admission of infrastructure compromise

#### Step 1.2: Repository Activity Scan
For protocol's **active repositories**:
```bash
# Check last updated dates
curl -s "https://api.github.com/orgs/<Org>/repos?per_page=50" |
  jq '.[] | {name, updated_at}'

# Scan commits for keywords in 7-day window around incident
curl -s "https://api.github.com/repos/<Org>/<Repo>/commits?since=<incident-7d>&until=<incident+3d>" |
  jq '.[].commit.message'
```

**Security-relevant commit keywords:**
```
security, dvn, verifier, enforce, require, minimum, multi,
redundan, config, threshold, quorum, guard, protect, patch,
hotfix, urgent, critical, CVE, exploit, vuln, mitigation
```

**Note:** GitHub JSON responses often truncate. If JSON parsing fails, fall back to:
- HTML scraping: `github.com/<Org>/<Repo>/commits`
- Or download raw: `curl -o file.json` then extract with regex

#### Step 1.3: Issue/PR Discussions
Check opened/updated issues within 7 days post-incident:
```bash
curl -s "https://api.github.com/repos/<Org>/<Repo>/issues?state=all&since=<incident-7d>"
```

Look for labels: `security`, `incident`, `post-mortem`, `hotfix`

---

### Phase 2: Community Forensic Analysis (Timeframe: incident + 1 day to + 14 days)

**Objective:** Gather third-party analysis that may contradict/official narrative.

#### Step 2.1: Forked Analysis Repositories
Search GitHub for repos with naming patterns:
```
<protocol>-hack-tracker
<protocol>-incident-analysis
<protocol>-exploit-forensics
<protocol>-postmortem
```

**Examples discovered in this session:**
- `indexing-co/kelpdao-hack-tracker` — live on-chain recovery dashboard
- `dnakhoa/kelp-dao-hack-analysis` — forensic breakdown with transaction-level detail

**What to extract:**
- Transaction hashes and block numbers
- Affected contract addresses
- Money flow diagrams
- Challenge to official narrative (if any)

#### Step 2.2: Configuration Exposure Census
Look for **community-run indexers** that track protocol configurations:
- **dvnstats** (LayerZero DVN config explorer): `sekuba/dvnstats` → `observatory.indexing.co/layerzero-dvn-census`
- Similar: `ethstorage tracker`, `bridge exposure dashboards`

**Key data points:**
- Pre-incident vulnerable configuration count
- Post-incident upgraded configuration count
- Percentage of ecosystem still exposed
- Specific apps/routes still at risk

**How to access:**
1. Find the indexer repo (often `username/protocol-stats` or `username/protocol-explorer`)
2. Check README for deployed dashboard URL
3. Scrape dashboard HTML for current metrics
4. Check indexer's own config files to understand what it tracks

#### Step 2.3: Research Threads & Threads
- **Twitter/X threads** from security researchers (ZachXBT, samczsun, etc.)
- **Mirror/paragraph.xyz posts** with deep technical analysis
- **Discord server messages** (public channels) via search or archive

**Search query pattern:**
```
"<Protocol> hack" "configuration" "DVN" "post-mortem" site:mirror.xyz
```

---

### Phase 3: Configuration Deep Dive

**Objective:** Determine if the vulnerability was:
- A **default configuration** problem (protocol shipped insecure defaults)
- An **opt-in misconfiguration** (user deviated from best practices)
- An **infrastructure compromise** (DVN nodes/RPC poisoned)
- A **protocol-level bug** (unexpected behavior in execution)

#### Step 3.1: Identify Configurable Parameters
From the protocol's source code or documentation, identify:
- `defaultDVNCount`, `requiredDVNCount`, `minimumDVNs`
- Config sentinel values (e.g., `255 = zero required DVNs`)
- Override paths: application-level vs global defaults

#### Step 3.2: Compare Pre/Post Incident Defaults
Check if **default values changed** in protocol repos:
```bash
# Compare files across commits
curl -s "https://github.com/<Org>/<Repo>/commit/<pre-hash>.patch" |
  grep -A3 -B3 "DVN\|require\|threshold"
```

**Look for:**
- `chore:` commits that bump config defaults
- `security:` or `hotfix:` labels on commits
- Changes to `default` or `initialValue` constants

#### Step 3.3: Exposure Quantification
From the live census/indexer:
```yaml
Total OApps tracked: 16
Routes at 1-of-1: 8 (50%)
Routes at 4-of-4: 4 (50% — post-upgrade)
High-risk examples:
  - ZAI OFT Adapter: 4 routes, all 1-of-1
  - Confirmations: 5 (vs Kelp's 64 post-upgrade)
```

---

### Phase 4: Ecosystem Impact Assessment

**Objective:** Measure real-world consequences beyond the primary victim.

#### Step 4.1: Affected Protocols Chain
From forensic analysis repos, extract:
- **Direct victims** (who lost funds)
- **Secondary exposure** (protocols that paused as precaution)
- **TVL impact** (before/after numbers)
- **Governance actions** (Arbitrum council freeze, Aave socialized loss proposals)

#### Step 4.2: Response Timeline
Create a chronological marker table:
```
Apr 18 17:35 UTC — Exploit transaction (block X)
Apr 18 20:xx UTC — First Twitter/X acknowledgment
Apr 19 12:xx UTC — Protocol official blog post
Apr 20 03:xx UTC — Arbitrum Security Council emergency action
Apr 20 14:xx UTC — KelpDAO configuration upgrade tx
Apr 21 04:xx UTC — Victim publishes detailed analysis
```

#### Step 4.3: Protocol Stance Classification
Categorize the response:
- **Deflective** — "user error, not our fault"
- **Accepting** — "we take responsibility, here's recovery plan"
- **Mixed** — "our infrastructure was compromised but user config contributed"
- **Silent** — no official statement

---

### Phase 4.5: GenLayer / Competing Protocol Positioning

**Objective:** Assess how neighboring protocols respond (opportunity/risk).

#### Step 4.5.1: Transport-Layer Dependencies
If incident involves a **bridge/transport protocol** (LayerZero, Hyperlane):
- Check if **GenLayer** lists this transport in its docs
- Review their **SDK documentation** for config examples
- Scan commits for "transport", "bridge" keywords

**Key question:** Does the incident create an opening for GenLayer to position itself as a safer alternative?

#### Step 4.5.2: SDK Changes Post-Incident
Check if competing protocols updated SDKs to:
- **Enforce minimum verifier counts**
- **Add configuration linting**
- **Provide secure-by-default templates**
- **Warn on insecure setups**

#### Step 4.5.3: Competitive Positioning
From ecosystem skill files and strategy docs:
- How does GenLayer differentiate? (e.g., "transport-agnostic", "AI consensus not DVN")
- Are they **capitalizing** on competitor's misfortune?
- Are they **doubling down** on the same vulnerable patterns?

**Signal detection for positioning opportunities:**
- Competitor's vulnerable default configuration = your "secure-by-default" marketing angle
- Competitor's delayed response = your "proactive security" narrative
- Competitor's deflective stance = your "responsible ownership" contrast

**Content opportunity identification:**
During incident research, flag:
1. **"Why our approach is safer"** blog post angles (e.g., "We enforce 2-of-3 DVN at application layer, unlike LayerZero's insecure defaults")
2. **Competitive differentiators** that became relevant post-incident
3. **Architectural decisions** that previously seemed overcautious but now appear prescient

*Example from KelpDAO incident:* Gentech's AgentEscrow chose 2-of-3 DVN quorum **before** the hack; post-incident, this is a **best practice** differentiator vs protocols that relied on LayerZero defaults.

---

## Critical Pitfalls

### Pitfall 1: Relying on Official Narrative Alone
**Symptoms:** Only citing protocol's blog post, accepting their blame assignment at face value.

**Correct approach:**
- Always find **independent forensic analysis repos** (forked by security researchers)
- Cross-reference transaction hashes against block explorers
- Check if "user error" claim matches on-chain evidence (like Kelp's receipt that was 12.5 hours late and for 0.001 rsETH)

### Pitfall 2: Missing Default Configuration Context
**Symptoms:** Reporting "protocol fixed the bug" without checking if **defaults changed**.

**Correct approach:**
- Compare **pre-hack default values** vs **post-hack default values**
- If defaults unchanged, protocol did NOT fix root cause
- Look for "breaking change" notes in release notes/changelog

### Pitfall 3: Confusing Transport vs Enforcement Layer
**Symptoms:** Conflating bridge security (message passing) with contract enforcement (dispute resolution).

**Correct approach:**
- **Transport layer:** How messages cross chains (LayerZero DVNs, Hyperlane validators)
- **Enforcement layer:** How disputes are adjudicated (GenLayer AI consensus, Aave governance)
- Incidents in transport **do not automatically** propagate to enforcement
- BUT: enforcement contracts may rely on transport for state/evidence — check integration points

### Pitfall 4: JSON Truncation on GitHub API
**Symptoms:** `JSONDecodeError: Invalid control character at line 335` — API response truncated.

**Workaround sequence:**
```bash
# Step 1: Save to file
curl -s 'url' -o /tmp/response.json

# Step 2: Extract with regex (names, dates, messages)
grep -oP '"name":\s*"\K[^"]+' /tmp/response.json
grep -oP '"updated_at":\s*"\K[^"]+' /tmp/response.json
grep -oP '"message":\s*"\K[^"]+' /tmp/response.json

# Step 3: For commits, use HTML scraping as fallback
curl -s 'github.com/Org/Repo/commits' |
  grep -oP '<p class="[^"]*mb-1[^"]*">\K.*?(?=</p>)'
```

### Pitfall 5: Assuming No News = No Updates
**Symptoms:** "No security advisory found" → "protocol didn't respond."

**Correct approach:**
- Check **private repo updates** via public timeline (repo updated but no advisory)
- Look for **chore/sync** commits that bump dependencies or config templates
- Check **generated docs** for new warnings (docs may auto-sync from source)
- Search for **"silent patch"** — fixes merged without announcement

---

## Verification Checklist

Before finalizing an incident report, verify:

- [ ] **Official timeline** cross-checked against on-chain block timestamps
- [ ] **At least one independent forensic repo** cited (not just official sources)
- [ ] **Live configuration census** checked for current exposure
- [ ] **Commit history** scanned ±7 days of incident for security keywords
- [ ] **Ecosystem protocols** identified that paused/changed behavior
- [ ] **Default configuration values** compared pre/post (if defaults unchanged → protocol didn't fix root cause)
- [ ] **Transport vs enforcement** layers separated in analysis
- [ ] **Competitor positioning** assessed (if relevant to stakeholder)

---

## Support Files

This skill is paired with:

- `references/incident-source-checklist.md` — canonical list of source types to check per incident type
- `references/config-census-methodology.md` — how to build/query a live config indexer (or use existing)
- `references/github-forensic-extraction.md` — regex patterns for extracting commit data when JSON fails
- `references/incident-type-source-matrix.md` — quick-lookup source prioritization by incident category
- `scripts/enumerate-layerzero-dvns.sh` — script to query LayerZero DVN configurations for any OApp

---

## Example Application: KelpDAO Incident (Apr 2026)

Applied in this session to research LayerZero DVN security. Key findings:
- **Official stance:** LayerZero deflected blame to Kelp's "1-of-1 config"
- **Independent forensics:** `dnakhoa/kelp-dao-hack-analysis` revealed LayerZero's DVN RPC was poisoned
- **Live census:** dvnstats showed 50% of routes still 1-of-1 14 days post-incident
- **Protocol response:** **No protocol-level enforcement change** — defaults unchanged, no governance action
- **GenLayer positioning:** Transport-agnostic approach, but no SDK enforcement added (left to apps)

---

## Related Skills

- `research-blockchain-data` — on-chain transaction tracing
- `github-forensics` — commit/issue mining for incident patterns
- `security-advisory-analysis` — evaluating CVE/CGA reports
- `protocol-due-diligence` — pre-investment security assessment

---

*End of SKILL.md*
