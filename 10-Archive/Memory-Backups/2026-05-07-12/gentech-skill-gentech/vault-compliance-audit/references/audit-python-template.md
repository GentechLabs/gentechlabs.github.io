## Two-Phase Document Discovery

### Stage 1: Filename/Metadata Scan (Fast)
```bash
# Quick broad scan — look for date prefixes and obvious keywords
find /root/vaults/gentech/ -type f -name "*.md" 2>/dev/null | \
  grep -vE "(10-Archive|11-Mess Hall|12-Skills|\.git|\.obsidian|memories)" | \
  grep -iE "(2026-0[5-9]|2026-1[0-2]|llc|formation|legal|compliance)"
```
**Why first:** Eliminates 80% of files instantly. Date-prefixed files (`YYYY-MM-DD`) are often approvals, handoffs, or periodic reviews — high-value targets.

### Stage 2: Content Deep-Scan (Targeted)
Once candidate files are identified, scan file contents for keyword combinations. Python gives fine-grained control:

```python
import os

active_root = '/root/vaults/gentech/'
exclude = ['10-Archive', '11-Mess Hall', '12-Skills', '.git', '.obsidian', 'memories']

results = []
for root, dirs, files in os.walk(active_root):
    dirs[:] = [d for d in dirs if d not in exclude and not d.startswith('.')]
    for fname in files:
        if fname.endswith('.md'):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    content = f.read().lower()
                    # Multi-term search: entity + temporal + action
                    if ('llc' in content and 
                        any(t in content for t in ['target', 'deadline', 'due', 'before']) and
                        any(a in content for a in ['todo', 'action', 'next', 'step', 'plan'])):
                        results.append(os.path.relpath(fpath, active_root))
            except:
                pass

print(f"High-priority documents: {len(results)}")
for r in results:
    print(f"  {r}")
```

### Stage 3: Action Item Extraction
Within matched files, look for imperative or assignment language:

```python
action_items = []
with open(fpath) as f:
    for i, line in enumerate(f, 1):
        line_lower = line.lower()
        if ('llc' in line_lower and 
            any(kw in line_lower for kw in ['todo:', 'action:', 'next:', 'deadline:', 'due:'])):
            action_items.append(f"L{i}: {line.strip()}")
        elif ('llc' in line_lower and 
              any(verb in line_lower for verb in ['should begin', 'need to', 'must', 'plan to'])):
            action_items.append(f"L{i}: {line.strip()}")
```

### Stage 4: Timeline Calculation
```python
from datetime import datetime, timedelta

def assess_urgency(target_date_str, today=None):
    """Convert various date formats to urgency bucket."""
    today = today or datetime.now()
    # Normalize: accept "September 2, 2026", "2026-09-02", "9/2/2026"
    target = datetime.strptime(target_date_str, '%Y-%m-%d')  # ISO preferred
    days = (target - today).days
    
    if days < 30:
        return 'urgent', days
    elif days < 90:
        return 'setup_window', days
    else:
        return 'planning', days
```

---

## Common Search Terms by Document Type

| Document Type | Keywords |
|---|---|
| LLC Formation | `llc`, `articles of organization`, `certificate of formation`, `operating agreement` |
| Annual Reports | `annual report`, `statement of information`, `renewal`, `anniversary` |
| Tax Filings | `tax`, `ein`, `employer id`, `quarterly`, `estimated` |
| Licenses | `license`, `permit`, `registration`, `certification` |
| Deadlines | `deadline`, `due`, `by `, `no later than`, `target` |

---

## Output Format (Three-Part Summary)

```markdown
# [Entity] — [Review Type] Status

**Date:** YYYY-MM-DD
**Auditor:** [Your Name]

## Status
- Phase: [Planning | Active | Urgent | Complete]
- Target Date: YYYY-MM-DD (in N days)
- Urgency: [Low | Medium | High]

## Key Documents
| File | Purpose | Notes |
|------|---------|-------|
| `path/to/doc.md` | Description | Status/ gaps |

## Action Items
1. **[Who]** [What] — [When]
2. **[Who]** [What] — [When]

## Next Review
[Date] — [Trigger condition]
```
