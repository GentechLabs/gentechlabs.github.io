## Date Math Snippets for Urgency Assessment

### Basic Timeline Constants
```python
from datetime import datetime, timedelta

today = datetime.now()
target = datetime(2026, 9, 2)   # Known target from Gentech plan

# Windows
urgent_window = timedelta(days=30)      # < 30 days: immediate action
setup_window = timedelta(days=90)       # 30-90 days: begin setup
planning_window = timedelta(days=365)   # > 90 days: monitor only
```

### Determining Setup Start Date
For entity formation (LLC, corporation), legal/filing prep takes 2-3 months:
```python
days_until_target = (target - today).days
setup_should_begin_by = target - timedelta(days=90)  # 3 months before
ideal_setup_start = target - timedelta(days=60)      # 2 months before

if today >= setup_should_begin_by:
    phase = "active_setup"
elif today >= ideal_setup_start:
    phase = "final_planning"
else:
    phase = "early_planning"
```

### Format Detection & Normalization
Common formats: `September 2, 2026`, `2026-09-02`, `9/2/2026`, `Sep 2 2026`.

```python
def parse_flexible_date(date_str):
    """Normalize human-written dates to datetime object."""
    from dateutil import parser
    return parser.parse(date_str, fuzzy=True)

# Without dateutil (manual):
formats = ['%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y', '%b %d %Y']
for fmt in formats:
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        continue
```

### Age Calculation for Annual/Biennial Items
```python
def years_between(d1, d2):
    return abs((d1 - d2).days / 365.25)

# For annual reports: if last filed > 1 year ago → due
last_filed = datetime(2025, 4, 15)
if years_between(today, last_filed) >= 1:
    print("Annual report overdue or imminently due")
```

---

## Reference Dates (Gentech-Specific)

| Item | Target | Notes |
|------|--------|-------|
| Gentech Entertainment LLC formation | 2026-09-02 | Begin setup 2026-06-04 to 2026-07-04 |
| Review cadence | Monthly | 1st of month or last day |
| Setup lead time | 60-90 days | Legal docs + state processing |
