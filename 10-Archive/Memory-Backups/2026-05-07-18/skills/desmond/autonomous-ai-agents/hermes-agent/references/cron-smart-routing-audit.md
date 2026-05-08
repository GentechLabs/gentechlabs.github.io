# Multi-Profile Cron Audit — Smart Routing

## Survey All Jobs Across Profiles

```bash
cd /root/.hermes && for profile in profiles/*/cron/jobs.json; do
  echo "=== $profile ==="
  python3 -c "
import json
data=json.load(open('$profile'))
for j in data.get('jobs',[]):
    s=j.get('schedule',{})
    sched=s.get('display',s) if isinstance(s,dict) else s
    deliver = j.get('deliver', 'default (origin)')
    name = j.get('name', 'unnamed')
    enabled = j.get('enabled', True)
    last_status = j.get('last_status', 'never')
    script = j.get('script', '')
    print(f'  {j[\"id\"][:12]} | {name} | sched={sched} | deliver={deliver} | enabled={enabled} | last={last_status} | script={bool(script)}')
" 2>/dev/null
done
```

## Smart Routing Rules

Each department has a home group. Cron jobs delivering work output should route to the correct group:

| Department | Agent | Home Group | Chat ID (example) |
|------------|-------|------------|-------------------|
| **HQ** | Gentech | HQ | `-1003863540828` |
| **Labs** | DMOB | Labs | `-1003872552815` |
| **Strategies** | YoYo | Strategies | `-1002916759037` |
| **Entertainment** | Desmond | Entertainment | `-1003893562036` |

**Rules:**
1. Department work output → deliver to that department's group
2. Cross-department summaries (Omni-Summary, Portfolio, Brain Review) → deliver to HQ
3. Utility/ops jobs (watchdog, vault maintenance) → `local` or `origin`
4. Duplicate jobs across profiles should be consolidated — keep the one with `last_status: "ok"`

## Common Duplicate Patterns

| Job Type | Often duplicated in | Resolution |
|----------|-------------------|------------|
| DeFi Milestone/Monitor | All 4 profiles | Keep authoritative (usually DMOB or YoYo), pause others |
| Brain/Memory Backup | Desmond + DMOB + Gentech | Keep one (Gentech → local) |
| Skills Update Check | DMOB + Gentech | Keep one |
| Hackathon/Bounty Scout | Desmond + Gentech | Keep one |
| x402/LayerZero Monitor | DMOB + Gentech | Keep one |

## Broken Chat ID Detection

Supergroup IDs are 13-14 digits (e.g., `-1003893562036`). If a deliver target is shorter:
- Likely truncated or wrong
- Test with a manual run to confirm silent failure
- Fix or delete the job

## Post-Audit Cleanup

After identifying issues:
1. **Pause** duplicate jobs (don't delete — easy to resume)
2. **Fix** broken delivery targets
3. **Remove** jobs that belong to wrong profile
4. **Document** routing decisions in vault for future reference
