# Agent Pass — Pricing Strategy

> GenTech Labs · June 2026
> Status: APPROVED by Jordan. Ready for implementation planning.

---

## Philosophy

**One subscription, everything included. No feature-gating, usage-gated.**

Users get the full experience from day one. Limits are on volume, not quality. The product is the drug. Usage limits are the dosage control.

**Anti-greed positioning:**
- One price, no confusion
- No premium/ultra tiers
- Platform gets better, price stays the same
- Revenue reinvested into token + platform

---

## Pricing Tiers

### Free Tier (The Hook — Permanent)
| Tier | Price | What They Get |
|------|-------|---------------|
| Free | $0 | Full features, strict usage limits |

**Usage Limits:**
- 3 recipes/day, 3 journal entries, 2 gaming queries, 1 tutor session, 1 travel search
- Full memory access (always unlimited)
- Social features: view only

**Who it's for:** Everyone. Experience the full stack, get hooked, convert.
**Why permanent (not trial):** No trial abuse. No email cycling. The free tier IS the marketing.

### Individual Layers (Entry Point)
| Layer | Price | What They Get |
|-------|-------|---------------|
| Cookbook | $5/mo | 20 recipes/day, full memory, ingredient adaptation, social sharing |
| Journal | $5/mo | 30 entries/day, full memory, reflections, daily tracking |
| Tutors | $8/mo | 15 sessions/day, full learning, skill sharpening, progress memory |
| Gaming Hub | $5/mo | 30 queries/day, full companion, build tracking, meta analysis |
| Travels | $5/mo | 15 searches/day, full planning, price tracking, itinerary memory |

**Who it's for:** Single-purpose users. "I only came here to cook." Low commitment, full experience.

### Agent Pass Bundle (The Destination)
| Tier | Price | What They Get |
|------|-------|---------------|
| Monthly Bundle | $20/mo | All layers, unlimited usage, always evolving |
| Annual Bundle | $200/yr | Same as monthly, save $40 (2 months free) |
| Lifetime (Early) | $249 once | Founding member access, limited to first 500 users |

**Who it's for:** Power users. "Give me everything." The obvious value play.

---

## The Funnel

```
Free Tier (permanent, limited)
    ↓
Individual Layer ($5-8/mo)
    ↓
Usage Limit Hit
    ↓
Upgrade Nudge: "Get everything for $12-15 more"
    ↓
Agent Pass Bundle ($20/mo)
    ↓
Annual Bundle ($200/yr)
    ↓
Lifetime Advocate ($249, early adopters)
```

---

## Future-Proofing Strategy

### Moats That Compound

**1. Memory is the lock-in**
Every recipe saved, every journal entry, every gaming build tracked — that's data the user can't take with them. The longer they use it, the more valuable it becomes. This is why memory is ALWAYS unlimited. It's the retention engine.

**2. Token creates ownership**
Users who hold the token aren't just subscribers — they're stakeholders. When the platform grows, their token grows. They don't leave because they're invested. Anti-churn mechanism.

**3. Social creates network effects**
500 people sharing recipes on the Cookbook = a community nobody wants to leave. Value isn't just the tool — it's the people using it. Compounds without marketing spend.

**4. Modular stack = infinite upside**
New layers cost almost nothing to add but increase the bundle value. Price stays at $20, value keeps climbing.

**5. Revenue diversification**
- Subscriptions (primary)
- Token appreciation + buyback
- Premium content partnerships
- Anonymized data insights (opt-in only)
- API access for developers

---

## Revenue Projections

| Users | Free | Individual | Bundle | Monthly Revenue |
|-------|------|------------|--------|-----------------|
| 500 | 200 | 100 × $6 avg | 200 × $20 | $4,600 |
| 1,000 | 350 | 200 × $6 avg | 450 × $20 | $10,200 |
| 2,500 | 800 | 450 × $6 avg | 1,250 × $20 | $27,700 |
| 5,000 | 1,500 | 800 × $6 avg | 2,700 × $20 | $58,800 |

*Assumes 55-65% bundle conversion from individual tier.*

**Annual subscribers:** ~30% of bundle users convert to annual.
- 500 annual subs × $200 = $100K upfront
- 1,000 annual subs × $200 = $200K upfront

---

## Concerns & Mitigations

### 1. Infrastructure Costs
**Concern:** Running agents costs compute. $20/mo per user might be tight at low scale.
**Mitigation:**
- Start with lighter agents (recipe gen = single LLM call, not continuous process)
- Usage limits control cost exposure
- As revenue scales, infrastructure costs per user drop
- Monitor cost-per-user monthly, adjust limits if needed
- **Target:** Keep infrastructure cost below $3/user/mo at scale

### 2. Free Tier Abuse (Email Cycling)
**Concern:** People creating multiple free accounts.
**Mitigation:**
- Require phone number OR social login (Google/Apple) for free tier
- Free tier is permanent, not a trial — less incentive to abuse
- Free tier is limited enough that power users will convert anyway
- Rate limit IP addresses (not just accounts)

### 3. Churn on Individual Tiers
**Concern:** Users subscribe to Cookbook for one month, cook 20 recipes, cancel.
**Mitigation:**
- Memory persistence warning: "Your recipes will be archived after 30 days of inactivity"
- Usage limits create natural upgrade pressure
- Bundle upsell nudge when they hit limits
- Annual discount locks them in

### 4. Token Integration
**Concern:** How does the GenTech token play into this?
**Mitigation:**
- Agent Pass can be paid in token at $16/mo (vs $20 USD) — 20% discount
- Token buyback from subscription revenue (5% of revenue)
- Token holders get priority access to new features + governance
- Creates demand + utility for the token

### 5. Payment Processing Fees
**Concern:** $5/mo individual tiers — processing fees eat margin.
**Mitigation:**
- Bundle at $20 is the real margin play
- Crypto payments (USDC) have lower processing costs
- Encourage annual/bundle to reduce transaction volume
- **Target:** Keep processing fees below 2% of revenue

### 6. Feature Creep
**Concern:** Adding new layers without updating pricing = margin compression.
**Mitigation:**
- Bundle price increases only when new MAJOR layers are added
- Individual layer prices stay stable
- Annual subscribers locked in at purchase price (grandfather clause)
- Review pricing quarterly

### 7. AI Landscape Changes
**Concern:** New AI tools/models could undercut us or make our agents obsolete.
**Mitigation:**
- Modular architecture = swap backends without breaking UX
- Memory + social = hard to replicate (not just an LLM wrapper)
- Token + community = moat competitors can't buy
- Focus on the LAYER, not the model — models change, layers persist

---

## Implementation Priorities

1. **Phase 1:** Build Cookbook (first layer, proof of concept)
2. **Phase 2:** Add Journal (personal memory layer)
3. **Phase 3:** Launch Agent Pass bundle pricing
4. **Phase 4:** Add remaining layers (Tutors, Gaming Hub, Travels)
5. **Phase 5:** Token integration + crypto payments
6. **Phase 6:** Community features + governance

---

## Tagline Options

- *"One subscription. Every tool. Always evolving."*
- *"Pick a layer. Or get everything. Your call."*
- *"The agent pass to the agentic economy."*
- *"AI that remembers. A platform that grows. A price that makes sense."*

---

*Document created: June 11, 2026*
*Updated: June 11, 2026 — $20/mo pricing, free tier model, future-proofing strategy*
*Owner: Gentech (Jordan + Agent)*
*Status: APPROVED*
