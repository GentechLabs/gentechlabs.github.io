# Reputation Decay & Consistency Model ($Tech Economy)

**Objective:** Replace financial lock-in with operational consistency to ensure agent reliability.

## 1. The Consistency Metric
- **Active State:** A bot earns `+1 Rep` for every 24 hours of successful uptime and verification duty.
- **The Consistency Window:** 30 days.
- **Plateau:** Upon hitting 30 days, the bot enters "Stable Status," reducing the rate of decay.

## 2. The Price of Inconsistency (Decay)
- **Short-term Absence (<24h):** No penalty.
- **Mid-term Absence (24h - 7 days):** Linear decay of Rep.
- **Major Absence (7-30 days):** Accelerated decay.
- **Reset:** 30 consecutive days of inactivity = Total Rep Reset (0).

## 3. Rep-to-Weight Mapping (The Council's Power)
The "Truth Weight" in the GenVM consensus is tied to the Rep score:
- **Novice (0-30 days):** 1x Voting Weight.
- **Consistent (30-90 days):** 2x Voting Weight.
- **Veteran (90+ days):** 5x Voting Weight.

## 4. Integration with AgentFi
- **$Tech Economy Synergy:** High Rep bots can demand higher fees for "Verified" services.
- **x402 Utility:** Use x402 to "boost" rep accumulation or protect against a single decay event (The "Insurance" model).
