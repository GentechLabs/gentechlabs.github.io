# TraderJoe LP Tracking Configuration

## Pool Details
- **Pair**: AVAX / USDC
- **Version**: v2.2 (5 bps)
- **Pool Address**: `0x864d4e50e7318e97483db7cb0912e09f161516ea`
- **WAVAX Address**: `0x31f66aa3c1e785363f0875b17ba74e27b85fd66c7`
- **USDC Address**: `0x9b7e9f9ef8734c71904d002f8b6bc66dd9c48a6e`

## Strategy Configuration
- **Target Range**: 9.36 - 9.53 USDC per AVAX
- **Monitoring Frequency**: Every 2 hours (7 AM - 9 PM EDT)
- **Data Sources**: DexScreener API, LFI API

## Status
- ✅ **Migrated to API-based monitoring** — vision-analysis dependency removed
- ✅ **AAE Signal Monitor v2 deployed** — structured JSON output, multi-shape support, smart severity (SILENT/OK/ALERT/CRITICAL)
- ✅ **Human-readable Telegram formatting optimized** — clean emoji headers, compact P&L section, inline squad context
- ✅ **Daily LP → D5 Milestone Report consolidated (Apr 26)** — `daily-lp-summary.py` replaced by `d5-milestone-summary.py`; produces tier-ladder report with Scout→Raider→Warlord→Sovereign progression, micro-DCA triggers, and compound tracking

---

## Frontend Impact Principle
> *"As we add more layers, we're always going to consider how this is going to affect our front end, our DeFi milestone tracker."* — Jordan, Apr 25 2026

Every new LP monitoring layer, cron optimization, or signal spec change must be evaluated against:
1. **DeFi Milestone Tracker UX** — does the new data fit the 8-tier ladder display?
2. **Dashboard real estate** — are we adding noise or signal?
3. **Notification fatigue** — does the new layer respect silent rules?
4. **Squad progression hooks** — does the output feed the Scout→Freedom tier system?
5. **Shareable card triggers** — does this create a milestone worth auto-generating a card?

New layers are gated on a frontend compatibility check before deployment.
- ✅ Cron output optimized (Apr 25) — structured Telegram alerts with emoji taxonomy, live price, range status, yield & P&L block
- Frontend implication: Output format now feeds directly into D5 Milestone Tracker data layer; every new metric added to cron must have a corresponding UI card in `DeFi-Milestone-Tracker.html`

## Frontend Contract
The cron output is the **single source of truth** for live position data. When adding new layers (e.g., IL simulation, yield projections, multi-pool), the following must stay in sync:
1. Cron JSON schema (`lp-aae-signal-monitor.py`)
2. Telegram alert template (short-form)
3. D5 Milestone Tracker HTML card (long-form dashboard view)
4. Fee Tracker Spec (`03-Strategies/Fee-Tracker-Spec.md`) presets

Last optimized: 2026-04-25 by YoYo/Desmond. Jordan approved format.
