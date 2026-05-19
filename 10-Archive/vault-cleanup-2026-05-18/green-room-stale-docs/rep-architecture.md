# REP Data Pipeline Coordination
*Started: 2026-04-23*

## Objective
Implement the two-axis REP (Soulbound Proof-of-Skill) system.

### 🏆 Axis 1: Absolute Performance
- **Owner**: @DMOB (Technical), @YoYo (Logic)
- **Requirements**:
    - Cumulative P&L (Realized + Unrealized)
    - Win Rate / Sharpe / Max Drawdown
    - Volume Filter (Prevent 1-trade wonders)

### 📈 Axis 2: Most Improved
- **Owner**: @DMOB (Technical), @YoYo (Logic)
- **Requirements**:
    - Rolling snapshot system (7d, 30d, 90d)
    - Trajectory slope calculation (Delta P&L over time)

## Current Status
- [ ] YoYo: Define trajectory logic and reward tiers.
- [ ] DMOB: Design data pipeline and storage strategy for snapshots.
- [ ] Gentech: Synthesize into final architecture report for Jordan.
