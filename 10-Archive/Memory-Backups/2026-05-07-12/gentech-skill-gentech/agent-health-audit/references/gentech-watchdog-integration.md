# Gentech Watchdog Integration

## Overview
The Gentech Watchdog is a specialized cron job that performs daily health checks on the four core Hermes agents: YoYo, DMOB, Desmond, and Gentech. This procedure extends the general agent-health-audit methodology with Gentech-specific requirements and checks.

## Trigger Conditions
- The Gentech Watchdog cron job runs every 5 minutes
- MUST load the `gentech-watchdog` skill for each execution
- The `gentech-watchdog` skill references this `agent-health-audit` skill for additional procedures

## Key Differentiators
1. **Mandatory Loading**: The watchdog skill has `always_required: true` to ensure it's always loaded
2. **Four-Agent Focus**: Specifically audits YoYo, DMOB, Desmond, and Gentech
3. **Cron Integration**: Designed to work with the Gentech Watchdog cron schedule
4. **Detailed Reporting**: Generates structured reports with remediation steps
5. **Alert Protocol**: Sends immediate alerts to Mess Hall on failure

## Relationship to agent-health-audit
- `gentech-watchdog` extends and specializes the general audit procedures
- Use `gentech-watchdog` for routine Gentech fleet health checks
- Use `agent-health-audit` for ad-hoc audits or other Hermes deployments
- The skills are complementary and should be loaded together when performing deep dives

## Reference
For the complete Gentech Watchdog procedure, see the `gentech-watchdog` skill.