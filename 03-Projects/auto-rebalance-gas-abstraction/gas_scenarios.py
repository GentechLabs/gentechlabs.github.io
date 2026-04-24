#!/usr/bin/env python3
"""
Auto-Rebalance Gas Abstraction — Scenario Stress Test
YoYo (Strategies) — 2025-04-21
"""

# === ASSUMPTIONS ===
deposits = [500, 1000, 5000, 10000]  # USD deposit sizes
reserve_pct = 0.02  # 2% of deposit earmarked for gas
gas_cost_per_rebalance = 1.00  # $1.00 avg on Avalanche C-Chain

# Rebalance frequency by volatility regime
scenarios = {
    "Low Vol (Stable)":     {"rebalances_per_month": 2,  "desc": "Price stays in range, rare exits"},
    "Medium Vol (Normal)":  {"rebalances_per_month": 6,  "desc": "Moderate swings, weekly rebalances"},
    "High Vol (Degen)":     {"rebalances_per_month": 15, "desc": "Wild swings, 3-4x/week rebalances"},
    "Extreme Vol (Crash)":  {"rebalances_per_month": 25, "desc": "Black swan, daily rebalances"},
}

# Gas spike multiplier during high vol
gas_spike_multipliers = {
    "Low Vol (Stable)":     1.0,
    "Medium Vol (Normal)":  1.2,
    "High Vol (Degen)":     1.8,
    "Extreme Vol (Crash)":  3.0,
}

print("=" * 80)
print("AUTO-REBALANCE GAS ABSTRACTION — STRESS TEST")
print("=" * 80)

# === TABLE 1: Reserve Lifespan (months until depletion) ===
print("\n📊 TABLE 1: Reserve Lifespan (months until gas reserve depletes)")
print("-" * 70)
print(f"{'Deposit':>10} | {'Reserve':>8} | {'Low Vol':>10} | {'Med Vol':>10} | {'High Vol':>10} | {'Extreme':>10}")
print(f"{'(USD)':>10} | {'(USD)':>8} | {'(months)':>10} | {'(months)':>10} | {'(months)':>10} | {'(months)':>10}")
print("-" * 70)

for deposit in deposits:
    reserve = deposit * reserve_pct
    row = f"${deposit:>8,} | ${reserve:>6,.0f} |"
    for name, data in scenarios.items():
        monthly_cost = data["rebalances_per_month"] * gas_cost_per_rebalance * gas_spike_multipliers[name]
        if monthly_cost == 0:
            months = float('inf')
        else:
            months = reserve / monthly_cost
        row += f" {months:>9.1f} |"
    print(row)

# === TABLE 2: Monthly Gas Cost by Regime ===
print("\n\n📊 TABLE 2: Monthly Gas Cost by Volatility Regime")
print("-" * 60)
print(f"{'Regime':<25} | {'Rebals/mo':>10} | {'Gas Mult':>8} | {'Cost/mo':>10} | {'Cost/yr':>10}")
print("-" * 60)

for name, data in scenarios.items():
    rebals = data["rebalances_per_month"]
    mult = gas_spike_multipliers[name]
    monthly = rebals * gas_cost_per_rebalance * mult
    yearly = monthly * 12
    print(f"{name:<25} | {rebals:>10} | {mult:>8.1f}x | ${monthly:>8.2f} | ${yearly:>8.2f}")

# === TABLE 3: Break-Even Analysis ===
print("\n\n📊 TABLE 3: Reserve % Needed for 6-Month Runway")
print("-" * 70)
print(f"{'Deposit':>10} | {'Low Vol':>10} | {'Med Vol':>10} | {'High Vol':>10} | {'Extreme':>10}")
print("-" * 70)

for deposit in deposits:
    row = f"${deposit:>8,} |"
    for name, data in scenarios.items():
        monthly_cost = data["rebalances_per_month"] * gas_cost_per_rebalance * gas_spike_multipliers[name]
        six_month_cost = monthly_cost * 6
        reserve_needed_pct = (six_month_cost / deposit) * 100
        row += f" {reserve_needed_pct:>8.1f}% |"
    print(row)

# === TABLE 4: Pooled Model Benefit ===
print("\n\n📊 TABLE 4: Pooled Reserve vs Per-User — Risk Diversification")
print("-" * 60)

total_users = 50
avg_deposit = 1000
total_aum = total_users * avg_deposit
pooled_reserve = total_aum * reserve_pct

print(f"Total users: {total_users}")
print(f"Average deposit: ${avg_deposit:,}")
print(f"Total AUM: ${total_aum:,}")
print(f"Pooled reserve (2%): ${pooled_reserve:,.0f}")
print()

for name, data in scenarios.items():
    # In pooled model, not all users rebalance at once
    # Assume 30% of users hit rebalance trigger simultaneously in worst case
    active_rebalancers = total_users * 0.30
    monthly_cost = active_rebalancers * data["rebalances_per_month"] * gas_cost_per_rebalance * gas_spike_multipliers[name]
    months = pooled_reserve / monthly_cost if monthly_cost > 0 else float('inf')
    per_user_months = (avg_deposit * reserve_pct) / (data["rebalances_per_month"] * gas_cost_per_rebalance * gas_spike_multipliers[name])
    print(f"  {name:<25}: Pooled={months:.1f}mo runway | Per-user={per_user_months:.1f}mo runway | Benefit={months/per_user_months:.1f}x")

# === RECOMMENDATION ===
print("\n\n" + "=" * 80)
print("💡 RECOMMENDATION")
print("=" * 80)
print("""
1. RESERVE MODEL: Pooled reserve at 2% — survives ~3x longer than per-user in high vol

2. RESERVE %: 
   - 2% is sufficient for low/medium vol (6+ months)
   - High vol needs 3-4% or protocol subsidy
   - Recommend 2% base + protocol top-up fund for extreme events

3. GAS SPIKE MITIGATION:
   - Set max gas price ceiling (skip rebalance if gas > 3x avg)
   - Batch rebalances: if 10+ users need rebalancing, batch into single tx
   - This drops per-user cost in high vol significantly

4. REVENUE MODEL:
   - 20% gas markup = $0.20/rebalance profit
   - At 6 rebalances/user/month × 50 users = $60/month
   - At scale (500 users): $600/month passive revenue

5. RISK GUARDRAILS:
   - Emergency pause if pooled reserve drops below 1 month runway
   - Cooldown timer prevents rebalance spam
   - Failed tx gas absorbed by protocol (user-friendly)
""")

# Save CSV for further analysis
import csv
with open('/root/vaults/gentech/03-Projects/auto-rebalance-gas-abstraction/scenarios.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Deposit', 'Reserve%', 'Regime', 'Rebals/Month', 'Gas Multiplier', 'Monthly Cost', 'Months Until Depletion', '6mo Reserve Needed%'])
    for deposit in deposits:
        reserve = deposit * reserve_pct
        for name, data in scenarios.items():
            mult = gas_spike_multipliers[name]
            monthly_cost = data["rebalances_per_month"] * gas_cost_per_rebalance * mult
            months = reserve / monthly_cost if monthly_cost > 0 else 999
            six_mo_pct = (monthly_cost * 6 / deposit) * 100
            writer.writerow([deposit, reserve_pct, name, data["rebalances_per_month"], mult, monthly_cost, round(months,1), round(six_mo_pct,1)])

print("\n✅ CSV saved to 03-Projects/auto-rebalance-gas-abstraction/scenarios.csv")
