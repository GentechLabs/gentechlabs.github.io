# AAE Interactive Demo — Build Plan

**Date:** 2026-05-21
**Status:** 🟢 COMPLETE
**Source:** Build brief from Labs/build-briefs/AAE-Interactive-Page.md

## Scope
Single HTML file: interactive AAE game loop demo. No backend, no deps, no build tools.

## Tasks

### Task 1: Build the full interactive demo
- **File:** `/root/ProtoJay4789.github.io/aae-interactive/index.html`
- **Spec:** Build brief (see source above)
- **Components:**
  1. Entry state: $100 balance, rep meter, pulsing borrow button
  2. Borrow state: click borrow → $600 balance, rep drops
  3. Trade state: LONG/SHORT buttons, animated price chart (canvas), P&L display
  4. Outcome state A (70%): liquidation — shake effect, margin call, balance/rep drop
  5. Outcome state B (30%): profit — confetti, balance grows, rep recovers, tier upgrade
  6. CTA state: "This is Agent Arena" messaging, waitlist link
- **Design tokens:** #0a0a0a bg, #22c55e green, #fbbf24 gold, #ef4444 red
- **Animations:** balance counter, rep bar transition, canvas price chart, glow effects, liquidation shake, confetti
- **Mobile responsive**

### Task 2: Smoke test (manual verify)
- Open in browser, play through both paths
- Verify responsive on mobile viewport
- Check no console errors

### Task 3: Deploy to GitHub Pages
- Push to ProtoJay4789.github.io repo
- Verify accessible at URL

## Verification
- [ ] Single HTML file, zero external deps
- [ ] Full loop playable: Entry → Borrow → Trade → Outcome → CTA
- [ ] Both liquidation and profit paths work
- [ ] Rep meter responds to actions
- [ ] Mobile responsive
- [ ] No console errors
