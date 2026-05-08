# Milestone Threshold Configuration — User Preference

## Default Thresholds (AAE Config)

The **canonical milestone ladder** lives in `~/.hermes/scripts/.lfj-aae-config.json` under the `milestones` key. This is the single source of truth for all monitoring scripts.

### Jordan's Preferred Thresholds (2026-05-02)

| Tier | Label | Daily Fees Target | Note |
|------|-------|-------------------|------|
| 1 | Scout | $5.00 | Entry rank — basic strategies |
| 2 | Scout+ | $10.00 | Micro-goal (early momentum) |
| 3 | Raider | $20.00 | Consistent earner |
| 4 | Raider+ | $35.00 | Bridge tier (stretch) |
| 5 | Warlord | $50.00 | High performer — **compound threshold aligned** |
| 6 | Warlord+ | $75.00 | Advanced single-pool |
| 7 | Sovereign | $100.00 | Elite — portfolio strategies |
| 8 | Freedom | $200.00 | Legend — custom strategy creation |

**Compound trigger:** $50.00 (tied to Warlord tier — compound when you hit a meaningful milestone)

**DCA base:** $50 | **DCA boost:** $15 (trigger when efficiency <50%)

**Rationale for 5/20/50/100/200 core tiers:**
- Rounded, memorable numbers
- Rough doubling progression at key inflection points
- Warlord ($50) aligns with compound threshold — psychological "hey, time to reinvest"
- Freedom ($200) is aspirational but achievable with consistent farming

### Alternative: Simplified 4-Tier D5 (for high-level reporting)

Some scripts (e.g., `d5-master-cron.py`) use a condensed view:
- Scout ($5)
- Raider ($20)
- Warlord ($55)  ← note: slightly higher than config's Warlord+
- Sovereign ($200)

**Recommendation:** Keep AAE config as canonical; update any hardcoded script thresholds to read from config instead of maintaining separate ladders.

---

## Configuration Updates

When adjusting thresholds:

1. **Edit** `~/.hermes/scripts/.lfj-aae-config.json` → `milestones` array
2. **Ensure ordering** by `daily_fees` ascending (lowest to highest)
3. **Patch any hardcoded ladders** in scripts:
   - `d5-master-cron.py` — reads config? (currently hardcoded)
   - `d5-milestone-summary.py` — reads config? (currently hardcoded)
   - `lp-aae-signal-monitor.py` ✅ already reads config
   - `lp-range-monitor-v3.py` — uses separate crown tracker ($0.50→$100), keep independent

4. **Re-run** a test: `python3 lp-aae-signal-monitor.py` and verify tier progression logic matches new thresholds
5. **Sync vault**: Update `03-Projects/DeFi/D5-Milestone-Tracker.md` table to reflect current tier

---

## Gamification vs. Strategic Tiers

The **8-tier gamified ladder** (Scout → Freedom with micro-tiers) is for:
- AAE agent progression UI
- Streak tracking and XP
- Fine-grained DCA triggers

The **4-tier strategic ladder** (Scout/Raider/Warlord/Sovereign) is for:
- Executive summaries
- High-level roadmap presentations
- Cross-protocol benchmarking

Both can coexist; just ensure each script knows which ladder it's referencing.

---

## Pitfall: Duplicate Ladders

**Symptom:** `d5-master-cron.py` reports "Tier 1: Scout — $5/day" while `lp-aae-signal-monitor.py` says "Tier 0: Unranked" for same position.

**Cause:** Different threshold sets + different state tracking (one uses cumulative fees, other uses estimated daily fees).

**Fix:**
- Use `lp-aae-signal-monitor.py` as the authority (it reads unified config)
- Disable or consolidate `d5-master-cron.py`'s milestone calculation to call the same function
- Never maintain two separate milestone arrays — compute tier from config only

---

## Related

- See `defi-lp-monitoring` skill core workflow → D5 Milestone Alignment Rules section
- See `references/alert-thresholds-config.md` for efficiency/range/IL thresholds (separate from tier ladder)
- Vault: `03-Projects/DeFi/D5-Milestone-Tracker.md`
