# AAE Project: Frontend Concept - Yield Farm Tracker (V1.0)
**Role:** Head of Creative (Desmond)
**Reference:** YIELD FARM TRACKER Infographic (March 31, 2026)

## 🎨 Design Philosophy
The goal is to translate "Financial Logic" into "Visual Motivation." The AAE frontend shouldn't just be a dashboard; it should be a **Wealth Journey Map**. We move away from boring tables and toward "high-signal" infographic modules.

---

## 🛠️ UI Blueprint (Modular Layout)

### 1. The "North Star" Header (Global State)
- **Element:** Top wide banner with gradient accent (Orange/Yellow).
- **Content:** 
    - Title: `S2S WEALTH PATH: AAE ACTIVE`
    - Sub-text: Current active pool (e.g., `AVAX/USDC - Trader Joe`)
    - Global Status: `SITUATION: STEADY BOTTOM ACCUMULATION`

### 2. Milestone Progress Ring (The "Game" Element)
- **Component:** A radial progress gauge.
- **Logic:**
    - Center: `M2: $20/day`
    - Percentage fill based on `Current Daily Yield / $20`.
    - Visual Cue: Ring glows gold when M1 is breached; pulses when M2 is within 10%.

### 3. The "Situation Update" Alert Box
- **Component:** High-contrast warning/info box (Red/Yellow).
- **Content:** Dynamic strings from the cron (e.g., *"Thailand trip delayed. DCA locked at $50-100/wk"*).
- **UX:** User can "Swoosh" away the alert once acknowledged.

### 4. Asset Split Visualizer (The Balance Bar)
- **Component:** A segmented horizontal bar (Custom CSS/SVG).
- **Logic:** 
    - Green (AVAX) vs Blue (USDC).
    - Real-time percentage labels (e.g., `39.5%` | `60.5%`).
    - Hover state: Shows exact token amount and current market value.

### 5. The Yield Grid (High Density Data)
- **Component:** A 2x3 or 3x2 grid of "Data Cards."
- **Cards:**
    - `Total Position` (with trend arrow $\uparrow$)
    - `Rewards APR` (Comparison to yesterday)
    - `24h Fees` (Range status: `IN RANGE`)
    - `Claimable` (CTA Button: `CLAIM & COMPOUND`)

### 6. The DCA Conviction Meter
- **Component:** A horizontal "slider" or gauge.
- **Content:** `Conviction: HIGH` $\rightarrow$ `Entry $0-$4 AVAX`.
- **Purpose:** Reminds the user *why* they are holding through volatility.

---

## 🚀 Technical Implementation Ideas (for DMOB)
- **Theme:** Dark Mode (Slate/Carbon background) with Neon Orange accents.
- **Animation:** Use Framer Motion for the "Progress Ring" filling effect.
- **Data Source:** JSON output from the `Defi Milestone` and `LP-Tracker` crons.
- **Layout:** Mobile-first vertical stack (Infographic style) $\rightarrow$ Expanded Grid for Desktop.

## 🗒️ Creative Note
*The core emotional driver here is "Accumulation." Every claim, every DCA, and every fee earned should feel like a "level up" in a game. The UI should reflect a sense of inevitable progress.*
