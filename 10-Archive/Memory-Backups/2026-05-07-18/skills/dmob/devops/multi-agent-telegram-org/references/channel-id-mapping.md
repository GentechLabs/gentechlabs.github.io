# Channel ID Mapping — GenTech Telegram Org

Last updated: 2026-05-05

## Department Groups (Main)

| Department | Group Name | Channel ID |
|------------|-----------|------------|
| HQ | Gentech HQ | `-1003863540828` |
| Labs | Gentech Labs | `-1003872552815` |
| Strategies | Gentech Strategies | `-1002916759037` |
| Entertainment | Gentech Entertainment | `-1003893562036` |

## Cron Delivery Targets

Use explicit `telegram:<ID>` instead of `origin` whenever possible.

| Cron Job | Should Deliver To | Target ID |
|----------|------------------|-----------|
| DeFi Milestone (Morning/Evening) | Strategies | `-1002916759037` |
| LP Position Monitor | Strategies | `-1002916759037` |
| Blockchain Contest Scanner | Labs | `-1003872552815` |
| x402 Ecosystem Watch | Labs | `-1003872552815` |
| LayerZero DVN Monitor | Labs | `-1003872552815` |
| Skill Update Check | HQ | `-1003863540828` |
| Brain Backup | HQ | `-1003863540828` |
| Omni Summary (YoYo) | HQ | `-1003863540828` |
| Portfolio Site (YoYo) | HQ | `-1003863540828` |
| College.xyz (YoYo) | HQ | `-1003863540828` |

## The `origin` Trap

When a cron job uses `deliver: origin`, it delivers to whatever chat the job was CREATED in. If a job is created in HQ (system admin work) but the results belong in Strategies, `origin` delivers to HQ — wrong.

**Rule:** Always use explicit `telegram:<channel-id>` for delivery targets. Only use `origin` if the job was created in the correct department group AND results belong there.
