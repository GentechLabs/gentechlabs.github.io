# AAE Event Detection & Response Framework

**Status:** Starting Spec (Queued)
**Created:** 2026-05-10
**Author:** Jordan + AAE Team
**Priority:** Pending — ready for deeper design when time allows

---

## Overview

Three-layer framework for AAE's event detection, automated response, and user notification system. This is the starting point — details to be fleshed out when we go deeper on each layer.

---

## Layer 1: Event Detection Thresholds

**What:** Define what constitutes a "meaningful event" vs noise.

- Price movement thresholds (percentage, absolute, timeframe)
- Volume anomalies (spike detection, divergence from baseline)
- Liquidity events (LP additions/removals, pool composition shifts)
- Sentiment/news triggers (social volume, narrative shifts)
- Cross-asset correlation breaks

**Open Questions:**
- How do we tier events by severity (critical, notable, informational)?
- Do thresholds adapt per asset or stay global?
- How do we handle black swan events that fall outside normal thresholds?

---

## Layer 2: Automated Response Rules

**What:** Once an event is detected, what happens automatically?

- Portfolio actions (rebalance, hedge, take profit, stop loss)
- Intelligence gathering (pull additional context, cross-reference)
- Signal generation (alert users, trigger education flow)
- Risk mitigation (reduce exposure, diversify, pause strategies)

**Open Questions:**
- What's the autonomy level? Fully auto vs human-confirmation-gated?
- How do we handle conflicting signals (e.g., price down but fundamentals strong)?
- Rollback/undo capabilities for automated actions?

---

## Layer 3: Notification UX

**What:** How does the user experience these events and responses?

- Notification channels (in-app, Telegram, email, push)
- Notification frequency and batching (avoid alert fatigue)
- Context-rich vs minimal notifications
- User control over notification preferences per event type
- Escalation paths (silent → summary → urgent → critical)

**Open Questions:**
- How do we balance urgency vs noise?
- Should notifications include recommended actions?
- How do we handle events while user is offline?

---

## Next Steps

- [ ] Deep-dive on each layer (separate sessions)
- [ ] Define MVP scope vs full vision
- [ ] Map to existing AAE architecture (02-Labs/AAE-Six-Layer-Architecture.md)
- [ ] Identify technical dependencies and blockers

---

## Related Vault Files

- `02-Labs/AAE-Six-Layer-Architecture.md`
- `02-Labs/AAE-Brain-Layer.md`
- `02-Labs/AAE-Portfolio-Intelligence-Layer.md`
- `03-Strategies/AAE-Watchdog-Layer.md`
- `03-Strategies/AAE-Body-Layer-Pattern.md`
- `09-Green Room/BirdeyeBIP-Reuse-for-AAE.md`
