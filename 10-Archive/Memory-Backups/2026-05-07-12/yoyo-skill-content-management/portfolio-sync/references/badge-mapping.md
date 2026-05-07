# Badge Mapping Reference

**Purpose:** Map vault status values → CSS classes used in `index.html`.

**Source of truth:** The `<style>` block in the live site HTML defines available classes.

---

## Project Card Statuses (`.status status-XXX`)

| Vault status string | CSS class | Color | Usage |
|---------------------|-----------|-------|-------|
| `IN PRODUCTION` | `status status-live` | Green | Live, producing value |
| `LIVE` | `status status-live` | Green | Alternative phrasing |
| `PRODUCTION` | `status status-live` | Green | Shorthand |
| `BUILDING` | `status status-building` | Yellow | Actively developing |
| `DEV` / `DEVELOPMENT` | `status status-dev` | Yellow | Alternate building class |
| `AUDIT` | `status status-audit` | Red | Under security review |
| `REVIEW` | `status status-audit` | Red | Awaiting approval |
| `PROTOTYPE` | `status status-dev` | Yellow | Early stage |
| `SCOPED` | `status status-queued` | Purple | Planned, not started |
| `QUEUED` | `status status-queued` | Purple | Backlog / waiting |

---

## Hackathon Table Badges (`.badge badge-XXX`)

| Vault status string | CSS class | Color | Usage |
|---------------------|-----------|-------|-------|
| `SUBMITTED` | `badge badge-submit` | Green | Deadline passed, entry in |
| `BUILDING` | `badge badge-building` | Yellow | Actively coding |
| `SCOPED` | `badge badge-queued` | Purple | Defined, not started |
| `QUEUED` | `badge badge-queued` | Purple | On the backlog |
| `WINNER` | *(not defined — request new class)* | — | If needed, ask Jordan |

---

## Pitfalls

### 1. Class doesn't exist
If you use `status-foo` and the CSS lacks a definition, text appears unstyled. Always double-check the current site's `<style>` block before committing.

### 2. Mixing project vs hackathon classes
Project cards use `status status-XXX`. Hackathon table uses `badge badge-XXX`. They share color names but are different CSS selectors. Do not interchange.

### 3. Status inflation
Avoid labeling everything `LIVE`. Reserve `status-live` for production deployments with real users/value. `BUILDING` is the default active state.

### 4. Stale badges
When a hackathon deadline passes, immediately update:
- `BUILDING` → `SUBMITTED` (if entry was sent)
- `QUEUED` → remove if scrapped

---

## Quick Reference

```python
STATUS_MAP = {
    # Project card
    "IN PRODUCTION": "status-live",
    "LIVE": "status-live",
    "BUILDING": "status-building",
    "DEV": "status-dev",
    "AUDIT": "status-audit",
    "PROTOTYPE": "status-dev",
    "SCOPED": "status-queued",
    "QUEUED": "status-queued",
    # Hackathon table (different wrapper)
    "SUBMITTED": "badge-submit",
    "WINNER": "badge-live",  # if added
}
```
