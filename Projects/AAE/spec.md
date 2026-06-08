# Automated Alert Engine (AAE) — Starting Spec

**Status:** Draft / Queued  
**Created:** 2026-05-10  
**Owner:** Jordan  

---

## Overview

AAE is a three-layer framework for intelligent event detection, automated response, and notification UX in GenTech operations.

---

## Layer 1: Event Detection Thresholds

- Define trigger conditions for alerts (price movements, portfolio changes, system events)
- Configurable sensitivity per alert type
- Noise filtering to reduce false positives
- Multi-source signal aggregation (on-chain, market data, system metrics)

---

## Layer 2: Automated Response Rules

- Predefined actions triggered by detected events
- Conditional logic chains (if X then Y, with fallbacks)
- Manual override / pause capabilities
- Audit trail of all automated actions

---

## Layer 3: Notification UX

- Tiered severity levels (info, warning, critical)
- Channel routing (Telegram, vault log, both)
- Summarized vs. detailed message formats
- Quiet hours / escalation paths

---

## Next Steps

- [ ] Define concrete event types and thresholds
- [ ] Map response rules to each event type
- [ ] Design notification templates
- [ ] Prototype MVP detection loop
- [ ] Integration points with existing cron jobs and agents

---

## Open Questions

- Which events are highest priority for MVP?
- Should AAE be a standalone agent or integrated into existing agents (YoYo, DMOB)?
- Data sources: purely on-chain, or include CEX/off-chain feeds?
- Rate limiting and cooldown periods?
