# GenTech Tool Evaluation Quick Reference

Use this matrix when Jordan shares a new tool, repo, or bookmark.

## Immediate Questions

1. **What project does this serve?** (AAE, Travel, Hackathon, Brain, Strategies)
2. **Cost to run?** Free / Freemium / Paid / Requires GPU?
3. **License?** MIT/Apache (✅) vs GPL (⚠️) vs Proprietary (❌ for open-source stack)
4. **Maintenance?** Recent commit? Active issues? Community?

## Verdicts at a Glance

| Verdict | Meaning | Example |
|---------|---------|---------|
| 🚀 **Core** | Essential infrastructure; integrate now | Understand-Anything (vault graph) |
| 🔧 **Integrate** | Valuable; create integration task | mapcn (travel visualization) |
| 🅿️ **Park** | Interesting; not urgent; watchlist | Fancy dashboard library, no immediate use |
| ❌ **Pass** | Misaligned; cost too high; abandon | Paid-only GPU tools without free tier |

## Cost-Aware Checklist

- [ ] Can it run on CPU or do we need to pay for GPU/cloud?
- [ ] Is there a free tier for prototyping? (ElevenLabs Agents = 15 free min)
- [ ] Does this duplicate something we already have?
- [ ] Will we need to maintain it or is it "set and forget"?
- [ ] Does our 32GB local workstation cover this workload?

## Output Template

```
**Tool:** <name>
**Verdict:** 🚀/🔧/🅿️/❌
**Rationale:** <one sentence>
**Next action:** <specific step, or "Parked on watchlist">
```

Example:
```
**Tool:** mapcn
**Verdict:** 🔧 Integrate
**Rationale:** Enables interactive travel previews; free + React components.
**Next action:** Desmond creates integration folder; prototype hotel map.
```
