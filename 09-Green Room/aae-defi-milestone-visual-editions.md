# AAE DeFi Milestone — Visual Editions

**Date:** 2026-06-01
**Status:** Active Design
**Owner:** Gentech (CEO)

---

## Vision

"Proof of Work" for Yield Farming Agents. Like Bitcoin mining dashboards show hashrate and rewards, our dashboards show agents farming yield and hitting milestones. Visual proof that the agents are working.

**Two user paths:**
- **Manual users** — yield farm themselves (like Trader Joe)
- **Autonomous users** — let the agent do it (subscription)

**The visual = trust layer.** Users can see the agents actually working, earning, compounding. Not just promises — proof.

---

## Existing Templates

### 1. defi-milestone-tracker.html
- **Theme:** Gold (dark background, gold accents)
- **Elements:** Milestone ladder, projection table, DCA schedule
- **Use case:** `/d5` daily check-in
- **Path:** `03-Strategies/Defi-Monitor/defi-milestone-tracker.html`

### 2. yield-farm-tracker.html
- **Theme:** Green (dark background, green accents)
- **Elements:** Token breakdown, fees, range, rewards, pool info
- **Use case:** `/farm` deep-dive
- **Path:** `03-Strategies/Defi-Monitor/yield-farm-tracker.html`

---

## Visual Editions

### 1. Milestone Ladder (Existing)
- **Based on:** `defi-milestone-tracker.html`
- **New elements:** Progress bars, projection table, DCA schedule
- **Use case:** `/d5` daily check-in
- **Status:** ✅ Built

### 2. Yield Farm Detail (Existing)
- **Based on:** `yield-farm-tracker.html`
- **New elements:** Token breakdown, fees, range, rewards
- **Use case:** `/farm` deep-dive
- **Status:** ✅ Built

### 3. Agent Performance (New)
- **Based on:** New template
- **New elements:** Agent actions, before/after, ROI, last rebalance
- **Use case:** Autonomous users
- **Status:** 🔨 Building

### 4. Squad Dashboard (New)
- **Based on:** New template
- **New elements:** Multiple positions, competitive, leaderboard
- **Use case:** Social/teams
- **Status:** 📋 Planned

### 5. Celebration (New)
- **Based on:** Milestone hit
- **New elements:** Confetti, stats, share card
- **Use case:** Auto-trigger on milestone
- **Status:** 📋 Planned

### 6. Alert (New)
- **Based on:** Out of range
- **New elements:** Warning colors, action needed
- **Use case:** Auto-trigger on alert
- **Status:** 📋 Planned

### 7. Weekly Summary (New)
- **Based on:** New template
- **New elements:** 7-day chart, fees earned, trend
- **Use case:** Sunday cron
- **Status:** 📋 Planned

---

## Agent Performance Edition — Design Spec

### Purpose
Show autonomous users what their agent is doing, how it's performing, and what income it's generating.

### Sections

1. **Header**
   - Agent name + status (active/idle/rebalancing)
   - Pool name + APR
   - Last action timestamp

2. **Agent Actions**
   - Last 5 actions (rebalance, compound, DCA)
   - Timestamp + impact (before/after value)
   - Action type badge (🔄 Rebalance, 💰 Compound, 📈 DCA)

3. **Performance Metrics**
   - Total earned (24h, 7d, 30d, all-time)
   - Agent ROI (% return on position)
   - Fees earned vs rewards earned
   - Compound efficiency (% of earnings reinvested)

4. **Position Health**
   - Current value + composition
   - Range status (in-range/out-of-range)
   - IL (impermanent loss)
   - APR vs actual yield

5. **Income Projection**
   - Monthly estimate based on current performance
   - Projection to next milestone
   - DCA impact on timeline

6. **Agent Config**
   - Auto-rebalance: On/Off
   - Auto-compound: On/Off
   - DCA schedule: $X/week
   - Risk tolerance: Conservative/Moderate/Aggressive

### Visual Style
- **Theme:** Cyberpunk (dark, neon accents, matrix feel)
- **Colors:** Dark background (#0a0a0a), neon green (#00ff88), neon blue (#00d4ff), neon purple (#a855f7)
- **Fonts:** Monospace for data, sans-serif for labels
- **Badges:** Glowing effect for active states

### Data Needed
- Agent action history (from AAE agent logs)
- Position data (from RPC/DeBank)
- Price data (from CoinGecko/DexScreener)
- Performance calculations (from agent metrics)

---

## Related

→ See [[00-HQ/AAE-DeFi-Milestone-Spec.md]] (Full spec)
→ See [[03-Strategies/Defi-Monitor/]] (Templates)
→ See [[09-Green Room/lobby-ui-order-book.md]] (Order book design)
