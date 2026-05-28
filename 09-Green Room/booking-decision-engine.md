# ✈️ Flight Booking Decision Engine

**Created:** May 26, 2026
**Purpose:** Smart booking recommendations based on reliability, price, and risk tolerance

---

## How It Works

When you ask about flights, the agent will:
1. **Search** for prices across airlines and OTAs
2. **Compare** direct airline vs OTA prices
3. **Ask your preference** if not set
4. **Recommend** based on your rules

---

## Booking Channel Reliability Ratings

### Tier 1: Airlines Direct (Best)
| Airline | Rating | Notes |
|---------|--------|-------|
| Philippine Airlines | ⭐⭐⭐⭐⭐ | Direct service, best rebooking |
| Korean Air | ⭐⭐⭐⭐⭐ | Excellent service, reliable |
| Cathay Pacific | ⭐⭐⭐⭐⭐ | Premium, great support |
| EVA Air | ⭐⭐⭐⭐⭐ | Taiwan hub, reliable |
| ANA | ⭐⭐⭐⭐⭐ | Japanese quality |
| United | ⭐⭐⭐⭐ | Good for CVG connections |
| American | ⭐⭐⭐⭐ | CVG hub advantages |
| Delta | ⭐⭐⭐⭐ | CVG hub, SkyMiles |

**Why book direct:**
- Easiest rebooking if cancelled
- Direct customer service line
- Miles/points earning
- Cleaner refunds
- Status benefits

### Tier 2: Major OTAs (Good)
| Platform | Rating | Best For | Watch Out |
|----------|--------|----------|-----------|
| Google Flights | ⭐⭐⭐⭐⭐ | Price tracking, redirects to airline | Not a booking platform |
| Expedia | ⭐⭐⭐⭐ | Package deals, price | Support can be slow |
| Travelocity | ⭐⭐⭐⭐ | Price comparison | Owned by Expedia |
| Orbitz | ⭐⭐⭐⭐ | Price | Owned by Expedia |
| Priceline | ⭐⭐⭐⭐ | Express Deals | Less transparent |
| Kayak | ⭐⭐⭐⭐ | Price search, redirects | Meta-search, not OTA |

**Why OTAs are okay:**
- Often cheapest prices
- Price matching available
- Package deals (flight + hotel)
- Good for simple bookings

### Tier 3: Budget OTAs (Use Caution)
| Platform | Rating | Best For | Watch Out |
|----------|--------|----------|-----------|
| CheapOair | ⭐⭐⭐ | Budget hunting | Hidden fees |
| Kiwi.com | ⭐⭐⭐ | Virtual interlining | Self-connection risk |
| Skiplagged | ⭐⭐⭐ | Hidden city tickets | Baggage risk |
| Momondo | ⭐⭐⭐ | Price comparison | Owned by Kayak |

**Why be careful:**
- Hidden fees possible
- Self-connection risk (if miss first flight, rest cancelled)
- Harder to get refunds
- Customer support varies

### Tier 4: Avoid for International
| Platform | Rating | Why |
|----------|--------|-----|
| Unknown OTAs | ⭐⭐ | Too risky for international |
| Social media ads | ⭐ | Scam potential high |

---

## Your Booking Preferences

### Default Rules (unless you change them)
```
1. ALWAYS prefer airline direct
2. Consider OTAs if savings > $75
3. For international trips: airline direct preferred
4. For simple domestic: OTA okay if significantly cheaper
5. Never use Tier 4 for international
```

### Preference Questions
When booking, agent asks:
- "Do you have a preferred airline?"
- "Are you okay with OTAs if savings are significant?"
- "Do you want to earn miles on this flight?"
- "How important is flexible rebooking?"

---

## Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Price difference < $50 | Book airline direct |
| Price difference $50-100 | Ask preference |
| Price difference > $100 | OTA is okay (Tier 1-2 only) |
| Complex itinerary | Book airline direct |
| Tight connection | Book airline direct |
| Need flexibility | Book airline direct |
| Budget trip, simple route | OTA okay |
| First time to destination | Book airline direct |
| International long-haul | Book airline direct |

---

## Price Alert Rules

### When to Alert
- Price drops > 10% from last check
- Price hits target range
- Seat availability low
- Price rising (buy now warning)

### Alert Format
```
✈️ CVG → MNL Price Alert

Current: $1,096 (Philippine Airlines)
Previous: $1,222
Change: -$126 (-10.3%)

Assessment: ✅ Good deal — within target range

Recommendation: Book now if dates are firm
Target: $1,000-1,100 RT

Book direct: philippineairlines.com
Or check: Google Flights for price comparison
```

---

## Integration with Travel Agent

### Pre-Trip Briefing
Before booking, agent provides:
1. **Price comparison** (airline vs OTAs)
2. **Reliability assessment** (which channel)
3. **Risk analysis** (what if cancelled?)
4. **Recommendation** (book direct or OTA)
5. **Your preference** (if set)

### Post-Booking
After booking, agent provides:
1. **Confirmation details**
2. **Airline contact info**
3. **What to do if cancelled**
4. **Baggage rules**
5. **Check-in reminders**

---

## Notes

- This system prioritizes **safety and reliability** over cheapest price
- For international trips, the $50-100 premium for airline direct is worth it
- OTAs are fine for simple, domestic, low-risk trips
- Always check airline direct price before booking OTA
- Keep confirmation emails and booking references

---

**Next Steps:**
1. [ ] Set your booking preference (airline direct vs OTA flexible)
2. [ ] Configure price alert thresholds
3. [ ] Test with CVG → MNL booking
4. [ ] Add to travel agent product spec
