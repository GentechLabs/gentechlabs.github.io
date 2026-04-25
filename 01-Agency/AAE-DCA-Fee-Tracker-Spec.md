# AAE DCA + Fee + Rewards Tracker — Product Spec

**Date:** 2026-04-25
**Source:** Jordan (HQ)
**Status:** Queued for build

---

## Feature Set: 3 Core Components

### 1. DCA Schedule (AgentPaymentFlow)
- **Default options:** Weekly, Monthly, Yearly (static intervals)
- **Custom strategy builder:** Users write/prompt their own DCA strategy
- **Jordan's example strategy:** "Invest on days when Trump tweets negative"
- **Funding source:** Amazon Flex income ($50–100/week)
- **Target:** $31.16 position → $55/day by Sep 2027

### 2. Rewards Tracking (Incentives Engine)
- **Metric:** 5,137% APR, claimable AVAX
- **Feature:** Real-time rewards accrual display
- **Action:** One-click claim integration

### 3. Fee Tracking
- **Default settings:** 5 preset fee-earning configurations
- **Custom:** User-defined fee capture strategies
- **Integration:** Tie into overall P&L dashboard

---

## User Experience

| Mode | Description |
|------|-------------|
| **Static** | Weekly / Monthly / Yearly pre-sets |
| **Custom Prompt** | Natural language DCA strategy (e.g., "buy when Trump tweets negative") |
| **Fee Configs** | 5 default fee-earning presets + custom |

---

## Next Steps
- [ ] DMOB: Scaffold AgentPaymentFlow contract + strategy registry
- [ ] DMOB: Build custom strategy parser (NL → trigger conditions)
- [ ] DMOB: Fee tracking module + 5 default presets
- [ ] YoYo: Model ROI projections for default strategies
- [ ] Desmond: UX copy for strategy builder + examples
