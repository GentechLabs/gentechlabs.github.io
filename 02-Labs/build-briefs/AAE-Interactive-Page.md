# AAE Interactive Demo Page — Build Brief

**Date:** 2026-05-21
**Source:** Jordan approved shift to Labs for build
**Status:** 🟢 READY FOR BUILD
**Priority:** HIGH — Hackathon demo hook + portfolio centerpiece

---

## 1. What We're Building

A **single-page interactive demo** that lets visitors FEEL the Agent Arena game loop in 30 seconds. No login, no wallet, no backend — pure client-side JS that simulates the core borrow → trade → rep mechanic.

**This is the hook page.** The website sells the vision. This page makes people feel it.

---

## 2. The Experience (30-Second Loop)

### State 1: Entry
- Player sees a trading dashboard with **$100 balance**
- Clean, dark UI matching portfolio aesthetic (dark bg, green accents)
- A glowing "Borrow $500" button pulses — temptation is visible

### State 2: Borrow
- Player clicks "Borrow $500"
- **Rep meter drops** (visual: rep bar shrinks, color shifts green → yellow → red)
- Balance jumps to $600
- Tooltip: "Borrowed capital costs rep. Higher rep = better rates."

### State 3: Trade
- "Open Position" button appears — player picks LONG or SHORT on a simulated asset
- Price chart animates (candlestick or line, 3-5 second movement)
- Position P&L updates in real-time

### State 4: Outcome (Two Paths)

**Path A — Liquidation (70% chance on first try):**
- Price moves against position
- P&L goes negative, turns red
- "MARGIN CALL" warning flashes
- Liquidation animation — position auto-closes
- Balance drops, rep drops further
- "Run ended. Your credit score took a hit."
- "Try again?" button resets to State 1

**Path B — Profit (30% chance):**
- Price moves in favor
- P&L turns green, grows
- "Take Profit" button appears
- Player closes position, profit added to balance
- Rep recovers slightly
- "Rank up! New borrowing power unlocked."
- Shows next tier: "Analyst → Trader → Strategist"

### State 5: CTA
- After either outcome: "This is Agent Arena. Real DeFi mechanics, zero real money."
- "Join the waitlist" or "Learn more" button
- Link to full spec or Krexa page

---

## 3. Technical Requirements

- **Single HTML file** with inline CSS + JS (portfolio style, no build tools)
- **No external dependencies** — pure vanilla JS + CSS animations
- **Mobile responsive** — works on phones (this will be shared on social)
- **Dark theme** — match existing portfolio: `#0a0a0a` bg, `#22c55e` green, `#fbbf24` gold accents
- **Deployed to:** `ProtoJay4789.github.io/aae-interactive/` or similar path

### UI Elements Needed:
1. **Balance display** — large, prominent, updates with animation
2. **Rep meter** — horizontal bar with color gradient (green → yellow → red)
3. **Borrow button** — glowing/pulsing animation
4. **Trading interface** — LONG/SHORT buttons, position size input
5. **Price chart** — animated candlestick or line chart (CSS or canvas)
6. **P&L display** — real-time updates, color-coded
7. **Margin call warning** — flashing red animation
8. **Outcome screen** — liquidation or profit celebration
9. **CTA** — waitlist link or learn more

### Animations:
- Balance counter (count up/down effect)
- Rep bar smooth transition
- Price chart movement (sinusoidal or random walk)
- Glow effects on buttons
- Liquidation shake effect
- Profit celebration (particle effect or confetti)

---

## 4. Design Tokens

```css
/* Match portfolio */
--bg-primary: #0a0a0a;
--bg-card: #111111;
--border: #222222;
--green: #22c55e;
--green-light: #86efac;
--gold: #fbbf24;
--red: #ef4444;
--red-light: #fca5a5;
--text-primary: #e0e0e0;
--text-secondary: #9ca3af;
```

---

## 5. Reference Materials

- **AAE Formal Spec:** `/root/vaults/gentech/02-Agent-Arena/AAE-FORMAL-SPEC.md`
- **Credit/Rep System:** Section 6 of formal spec (Credit Score 0-1000, Tiers: Unverified → Diamond)
- **Borrowing Mechanics:** Section 6.2 (virtual capital, simulated interest, 30% auto-repay)
- **Liquidation Engine:** Section 6.3 (80% threshold, score penalty, 7-day freeze)
- **Existing Portfolio:** `/root/ProtoJay4789.github.io/index.html`

---

## 6. Success Criteria

- [ ] Single HTML file, no build tools, no external deps
- [ ] Full 30-second loop playable on mobile
- [ ] Borrow → Trade → Outcome flow works smoothly
- [ ] Rep meter visibly responds to borrow/trade actions
- [ ] Both paths (liquidation + profit) feel satisfying
- [ ] CTA clearly communicates what Agent Arena is
- [ ] Deployed and accessible via GitHub Pages URL

---

## 7. Out of Scope (v1)

- No backend / no persistence (refresh resets)
- No wallet connection
- No real market data (simulated prices)
- No multiplayer / duo queue
- No NFT loadout system
- No account creation

---

*This page is the front door. Make people feel the game before they play it.*
