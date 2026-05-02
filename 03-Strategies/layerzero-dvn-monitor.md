# LayerZero DVN Security Monitor — Intelligence Report

**Checked:** Thursday, April 30, 2026 UTC
**Analyst:** YoYo, Head of Strategies @ Gentech
**Source:** layerzero.network/blog, LayerZero official statements, web reconnaissance

---

## Executive Summary

**Risk Level: UNCHANGED — protocol-level DVN minimums still not enforced.**

LayerZero Labs has taken a **single concrete action** post-KelpDAO: its own DVN will refuse to sign for any 1-of-1 configurations. However, the protocol **still does not mandate multi-DVN setups at the smart-contract level**. The blame remains squarely placed on KelpDAO for "choosing" a 1/1 setup, reinforcing a "buyer beware" security model rather than systemic hardening.

---

## 1. Protocol-Level Changes

**Finding:** No new protocol upgrade or governance proposal detected that would enforce minimum DVN redundancy (e.g., require ≥2 DVNs at the Endpoint/OApp level).

- The KelpDAO Incident Statement (Apr 19, 2026) explicitly states: *"The LayerZero protocol is built on a foundation of modular, application-configurable security... the protocol does not prescribe a single security configuration."*
- This means 1-of-1 DVN configurations remain **technically possible** even if LayerZero Labs refuses to participate in them.

**New Policy from LayerZero Labs:**
- LayerZero Labs DVN **will no longer sign or attest messages for any 1/1 configuration**.
- Team is reaching out to all 1/1-configured apps to migrate to multi-DVN setups.
- All compromised RPC nodes deprecated and replaced; DVN is back online.

---

## 2. Official Blog & Communications

**Latest blog posts (most recent first):**

| Date | Title | Category | Relevance |
|------|-------|----------|-----------|
| Apr 19 | **KelpDAO Incident Statement** | Announcements | **Primary response** — blames KelpDAO 1/1 config, attributes to Lazarus/TraderTraitor |
| Mar 31 | Worldpay's "Payments DVN" | Announcements | Pre-incident; enterprise DVN option live on 9+ chains |
| Mar 26 | LayerZero Partners with Canton | Announcements | Institutional tokenization |
| Feb 10 | Zero: The Decentralized Multi-Core World Computer | Announcements | Zero blockchain launch (zk-based world computer) |

**No new DVN-security-specific posts since Apr 19.**

---

## 3. LayerZero Labs Public Response Assessment

**Beyond blaming KelpDAO:** Yes, but only incrementally.

- Attribution: Highly-sophisticated state actor, likely DPRK Lazarus Group (TraderTraitor).
- Attack vector: RPC infrastructure poisoning + DDoS on uncompromised nodes to force failover.
- Defensive posture: SOC2 audit/verification in final stages; full EDR; least-privilege access controls.
- Cooperation: Direct contact with multiple global law enforcement agencies; supporting Seal911 to track funds.

**However:** The framing remains *"protocol functioned exactly as intended — zero contagion risk throughout the system."* This is technically true for modular architecture, but it does not address the **moral hazard** of allowing $290M to drain because a default/allowed configuration was insecure.

---

## 4. DVN Minimum Security Standards

**Finding:** No formally announced "DVN minimum security standards" as a protocol-wide rule.

- Current standard: **Best-practice recommendation** (multi-DVN with diversity and redundancy).
- Enforcement: **Soft** — LayerZero Labs DVN opt-out of 1/1, but other DVNs may still participate in 1/1 configs.
- Gap: No on-chain enforcement (e.g., Endpoint rejecting 1/1 configs during `setConfig`).

---

## 5. Competitor Responses

**Finding:** No explicit public competitor campaigns detected capitalizing on the KelpDAO incident.

Search attempted for Wormhole, Axelar, Hyperlane responses. No blog posts, Twitter threads, or marketing materials found explicitly contrasting their security model vs. LayerZero's DVN model in the wake of the exploit.

*Note: Web search heavily rate-limited during this run; competitor social channels may have organic commentary not captured.*

---

## 6. Dune Dashboard — DVN Stats

**Finding:** Dune.com blocked by Cloudflare bot detection during reconnaissance. Could not verify current percentages for 1-of-1 vs 2-of-2 vs 3-of-3+.

- **Baseline from prior monitoring:** ~47% 1-of-1, ~45% 2-of-2, ~5% 3-of-3+.
- **Hypothesis:** 1-of-1 percentage likely declining as LayerZero Labs pushes migrations, but hard data unavailable.
- **Action:** Recommend manual check of Dune dashboard when possible, or query LayerZero Scan API directly.

---

## 7. Action Items

| Priority | Action | Owner |
|----------|--------|-------|
| 🔴 HIGH | Verify if Gentech/any portfolio exposure uses LayerZero with <2 DVNs | DeFi Risk |
| 🔴 HIGH | Re-run Dune DVN stats query when possible to measure migration velocity | YoYo |
| 🟡 MEDIUM | Monitor for any on-chain protocol upgrade that enforces ≥2 DVNs | YoYo |
| 🟡 MEDIUM | Track if competitors (Wormhole, Axelar, Hyperlane) launch security-marketing campaigns | Comms |
| 🟢 LOW | Evaluate Worldpay DVN as a credible institutional verifier option | DeFi Risk |

---

## Risk Assessment

| Dimension | Status |
|-----------|--------|
| Protocol-level mandatory DVN minimums | **NOT IMPLEMENTED** |
| LayerZero Labs DVN participation in 1/1 | **BLOCKED** ✅ |
| Third-party DVN 1/1 participation | **Still possible** ⚠️ |
| Competitor capitalizing on incident | **Not detected** |
| Public blame posture | **Shifted to KelpDAO + state actor** |
| Fund recovery / law enforcement | **Active cooperation** |

**Overall Risk: UNCHANGED.** The modular-security model continues to place the burden on individual applications. Until the protocol itself rejects 1-of-1 configurations at the configuration layer, similar incidents remain possible with other DVN operators.

---

*Report generated by YoYo (Gentech Strategies) via autonomous monitor.*

---

## Supplement — May 1, 2026 Check

**Checked:** Friday, May 1, 2026 09:47 UTC
**Analyst:** YoYo, Head of Strategies @ Gentech

### Delta Since Apr 30 Report

**No new material changes detected.**

| Item | Apr 30 Status | May 1 Status |
|------|---------------|--------------|
| Latest official blog post | Apr 19 KelpDAO Incident Statement | **Still Apr 19** — no new DVN/security posts |
| GitHub LayerZero-v2 commits | Last Feb 27, 2026 | **Still Feb 27, 2026** — zero post-incident commits |
| GitHub releases | Last May 6, 2025 | **Unchanged** — no security patch releases |
| Protocol-level mandatory DVN minimums | Not implemented | **Still not implemented** |
| Governance proposals (Snapshot, etc.) | None detected | **Still none detected** |
| Competitor capitalizing (Wormhole, Axelar, Hyperlane) | Not detected | **Still not detected** |
| Dune DVN stats dashboard | Blocked by Cloudflare | **Still blocked** — stats unavailable |
| LayerZero Labs DVN 1/1 signing | Blocked | **Still blocked** |

### Detail

1. **Official Blog (layerzero.network/blog):** Re-crawled. Most recent posts remain Apr 19 KelpDAO statement, followed by pre-incident partnership announcements (KorDA $KGLD, Worldpay Payments DVN, Canton, Centrifuge). No new security updates, no clarifying follow-ups, no "Path Forward Part 2."

2. **Public Response Beyond KelpDAO Blame:** Unchanged. The Apr 19 statement remains LayerZero Labs' sole extended public response. It continues to frame the incident as: (a) KelpDAO's fault for choosing 1/1, (b) protocol architecture worked as designed (zero contagion), (c) state-actor sophistication excuses single-point failure. No new statements from leadership on X/Twitter beyond what was in the blog.

3. **Code/Protocol Activity:** No commits, no PRs, no releases since Feb 27, 2026 on the public v2 repo. There is **zero on-chain or code-level reaction** to the $290M exploit visible in open-source repositories.

4. **DVN Minimum Security Standards:** Still a recommendation, not a requirement. The integration checklist continues to advise multi-DVN setups, but there is no evidence of an on-chain `setConfig` guardrail that would reject 1-of-1 configurations.

5. **Competitor Responses:** Searches for Wormhole, Axelar, Hyperlane blog posts, security updates, or competitive messaging referencing LayerZero or KelpDAO returned no results in this monitoring window. The competitor landscape remains silent on public channels.

### Risk Assessment (May 1)

**Risk Level: UNCHANGED.**

The 12-day window since the exploit has produced no protocol hardening, no governance action, and no additional public accountability beyond the initial Apr 19 statement. LayerZero Labs is relying on voluntary integrator migration away from 1/1 and its own DVN's refusal to participate. This remains a soft-pressure mechanism, not a systemic fix.

**Key concern:** If another integrator (especially a smaller team) is running 1/1 with a non-LayerZero-Labs DVN, the exact same exploit path is still viable against that DVN operator.

### Action Items (Carried Forward)

- 🔴 Verify Gentech portfolio for any 1/1 DVN exposure immediately.
- 🔴 Source alternative Dune DVN migration data (via API, subgraph, or community dashboard) to quantify whether 1-of-1 % is actually declining.
- 🟡 Monitor GitHub commits daily for any sudden post-incident protocol patch.
- 🟡 Track competitor social channels manually if search remains rate-limited.

*— YoYo, Gentech Strategies*

---

## Supplement — May 2, 2026 Check

**Checked:** Saturday, May 2, 2026 09:05 UTC  
**Analyst:** YoYo, Head of Strategies @ Gentech

### Delta Since May 1 Report

**No new material changes detected.** The post-incident response remains entirely static.

| Item | May 1 Status | May 2 Status | Change |
|------|--------------|--------------|--------|
| Latest official blog post | Apr 19 KelpDAO Incident Statement | **Still Apr 19** — no new security/DVN posts | None |
| GitHub LayerZero-v2 commits | 0 since May 1 | **Still 0** — zero post-incident code activity | None |
| GitHub releases tag | Last May 6, 2025 | **Unchanged** — no security patch releases | None |
| Protocol-level mandatory DVN minimums | Not implemented | **Still not implemented** | None |
| Governance proposals (Snapshot) | None detected | **Still none detected** | None |
| Competitor capitalizing (Wormhole, Axelar, Hyperlane) | Not detected | **Still not detected** | None |
| Dune DVN stats dashboard | Inaccessible/Cloudflare | **Still inaccessible** — direct query blocked | None |
| LayerZero Labs DVN 1/1 signing policy | Blocked | **Still blocked** | None |

### Detail

1. **Official Blog (layerzero.network/blog):** Re-crawled. The KelpDAO Incident Statement from April 19 remains the most recent post. No follow-up clarification, no "Path Forward Part 2," and no new security advisory published.

2. **Public Response Beyond KelpDAO Blame:** Unchanged. LayerZero Labs has not issued any additional statements, tweets, or forum posts since the April 19 blog. The sole extended public narrative remains: (a) KelpDAO chose 1/1, (b) state-actor sophistication explains the compromise, (c) protocol isolation prevented contagion.

3. **Code/Protocol Activity:** Verified via GitHub API — zero software commits to the LayerZero-v2 repository in the May 1–May 2 window. No issue activity, no PRs, no release draft. The repository remains in post-exploit stasis.

4. **DVN Minimum Security Standards:** Still a best-practice recommendation only. No evidence of on-chain configuration guardrails (e.g., Endpoint rejecting `setConfig` with only one DVN). LayerZero Labs continues to rely on voluntary migration and its own DVN's unilateral opt-out.

5. **Competitor Responses:** Checked Wormhole, Axelar, and Hyperlane official Twitter/X pages and news feeds. No public posts referencing LayerZero, KelpDAO, or multi-chain security differentiators in the context of the exploit.

6. **Dune Dashboard:** Direct URL access continues to be blocked by Cloudflare or requires authentication. Independent verification of DVN distribution migration velocity remains unavailable.

### Observations

- **Silence as strategy.** LayerZero Labs appears to be pursuing a low-profile posture post-incident, relying on the technical merits of the modular-security argument and ongoing outreach to affected teams rather than public communications.
- **No governance mobilization.** The absence of any Snapshot proposal suggests either (1) no community pressure for protocol-level changes yet, or (2) internal team preference to handle DVN policy via off-chain coordination.
- **Competitor passivity notable.** Given the $290M exploit and narrative vulnerability around "single-point DVN risk," Wormhole/Axelar/Hyperlane have **not** launched competing security marketing campaigns — either tactical restraint or missed opportunity.

### Risk Assessment (May 2)

**Risk Level: UNCHANGED → HIGH.**

Thirteen days post-exploit:
- No protocol-level hardening (still no mandatory multi-DVN enforcement).
- No new transparency report or security audit release.
- Migration from 1-of-1 configurations is voluntary and unverifiable.
- Other DVN operators (non-LayerZero-Labs) could still be operating 1/1 setups exposed to identical attack path.

Systemic risk remains: **Any application using a single DVN (any operator) is still vulnerable to RPC-poisoning + DDoS attacks.**

### Action Items (Updated May 2)

| Priority | Action | Owner | Due |
|----------|--------|-------|-----|
| 🔴 CRITICAL | **Check if any Gentech portfolio protocols use LayerZero with <2 DVNs** — immediate risk assessment | DeFi Risk | ASAP |
| 🔴 HIGH | **Manually query LayerZero Scan API / subgraph to get fresh DVN distribution** (since Dune is blocked) | YoYo + Data Eng | May 3 |
| 🟡 MEDIUM | Track LayerZero Labs team socials (Brian, David, etc.) for any emergent security discourse | Comms | Ongoing |
| 🟡 MEDIUM | Set up GitHub commit watcher on LayerZero-v2 for any sudden "security fix" pushes | DevOps | Ongoing |
| 🟢 LOW | Draft competitive messaging framework in case Wormhole/Axelar pivot to security differentiation | Comms | On-hold |

*— YoYo, Gentech Strategies*

