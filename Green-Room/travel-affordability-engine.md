# 💰 Trip Affordability Engine — Product Spec

**Created:** May 26, 2026
**Status:** 🟢 APPROVED (Jordan confirmed May 26)
**Purpose:** Answer "Can I afford this trip?" with precision, not guesswork

---

## The Problem

Most travel planners show you trips but don't answer the hard question:
- "Can I actually afford this?"
- "When should I buy the ticket?"
- "What happens if prices go up?"
- "Am I being irresponsible?"

This is the **#1 stress point** for budget-conscious travelers. We solve it.

## How It Works

### Inputs (User Provides)
| Input | Example | Source |
|-------|---------|--------|
| Pay rate | $23.75/hr | User |
| Average hours/week | 55 hrs | User |
| Overtime rate | $32.78/hr (1.5x) | Calculated |
| Monthly bills | $1,712.60 | User spreadsheet |
| Savings window | 8 weeks | User |
| Trip cost range | $1,300-1,800 | Research |

### Processing
1. Calculate weekly gross (regular + OT)
2. Project savings over window (gross)
3. Apply tax estimate (22-28% effective)
4. Compare net savings to trip cost
5. Factor in ticket price volatility
6. Generate risk assessment

### Outputs (Agent Delivers)
| Output | Format |
|--------|--------|
| Affordability verdict | "You're solid" / "Doable, but tight" / "Not this time" |
| Week-by-week savings tracker | Table with cumulative savings |
| Buy timeline | "Buy ticket by Week X" |
| Price sensitivity | "If flights go up $200, you're still OK" |
| Risk buffer | "Keep $X emergency cushion" |
| Recommendation | "Buy now" / "Wait for price drop" / "Save more first" |

## Affordability Tiers

### 🟢 "You're Solid"
- Trip cost < 50% of net savings window
- Emergency buffer remains after booking
- OT income provides cushion
- **Action:** Buy with confidence

### 🟡 "Doable, But Tight"
- Trip cost = 50-70% of net savings window
- Minimal buffer remains
- Requires consistent OT
- **Action:** Buy, but watch spending on-ground

### 🟠 "Stretch"
- Trip cost = 70-85% of net savings window
- No buffer for price increases
- Requires every OT hour
- **Action:** Consider cheaper dates/routes or shorter trip

### 🔴 "Not This Time"
- Trip cost > 85% of net savings window
- No buffer at all
- Risk of debt
- **Action:** Delay trip, increase savings rate, or find cheaper option

## Example: Jordan's Trip 1

### Inputs
- Pay rate: $23.75/hr
- Avg hours: 55/week (40 regular + 15 OT)
- Monthly bills: $1,712.60
- Savings window: 8 weeks (Jun-Jul)
- Trip cost: $1,300-1,800

### Calculations
- Weekly gross: (40 × $23.75) + (15 × $32.78) = $950 + $491.70 = **$1,441.70**
- 8-week gross: **$11,533.60**
- After taxes (~22%): **$8,996.21**
- After bills (2 months): **$8,996.21 - $3,425.20 = $5,571.01**

### Verdict
- Trip cost ($1,300-1,800) = **23-32%** of available savings
- **Rating: 🟢 You're Solid**
- Emergency buffer: $3,771-4,271 remaining
- **Action:** Buy ticket with confidence

## Price Sensitivity Analysis

### What If Prices Change?
| Scenario | Impact | Recommendation |
|----------|--------|----------------|
| Flights +$200 | Still 🟢 Solid | Buy |
| Flights +$400 | Still 🟢 Solid | Buy |
| Flights -$200 | Great deal | Buy immediately |
| OT reduced to 10 hrs/wk | Still 🟡 Doable | Monitor closely |
| OT reduced to 5 hrs/wk | 🟠 Stretch | Consider cheaper dates |
| Bills increase $200/mo | Still 🟢 Solid | Buy |

## Week-by-Week Tracker Template

| Week | Date | Saved This Week | Cumulative | Milestone |
|------|------|-----------------|------------|-----------|
| 1 | Jun 2 | $650 | $650 | Start tracking |
| 2 | Jun 9 | $650 | $1,300 | ✅ One ticket |
| 3 | Jun 16 | $650 | $1,950 | ✅ Two tickets |
| 4 | Jun 23 | $650 | $2,600 | ✅ Flights + hotel |
| 5 | Jun 30 | $650 | $3,250 | 🎯 Full trip paid |
| 6 | Jul 7 | $650 | $3,900 | Buffer zone |
| 7 | Jul 14 | $650 | $4,550 | Extra activities |
| 8 | Jul 21 | $650 | $5,200 | Comfortable cushion |

## Integration Points

### For Travel Agent Product
- **Pre-trip briefing:** Include affordability check 4 weeks before departure
- **Price alerts:** Notify when ticket price crosses affordability threshold
- **Savings reminders:** Weekly "you're on track" or "you're behind" nudges
- **Post-trip:** "Here's what you actually spent vs. budget"

### Data Sources
- User-provided pay info
- Google Flights / LetsFG for ticket prices
- Local cost research for accommodation/food
- Weather data for seasonal pricing

## Privacy & Sensitivity

- **Never store actual salary** — use rate + hours only
- **Never share with third parties** — this is personal data
- **Local processing only** — no cloud uploads
- **User controls all inputs** — agent never assumes

---

## Next Steps

1. [ ] Build calculator function (Python)
2. [ ] Integrate with LetsFG for real-time pricing
3. [ ] Create Telegram notification templates
4. [ ] Test with Jordan's Trip 1 data
5. [ ] Expand for Trip 2 and Trip 3

---

*This is a core differentiator for the travel agent product. Most planners show trips. We answer: "Can you actually go?"*
