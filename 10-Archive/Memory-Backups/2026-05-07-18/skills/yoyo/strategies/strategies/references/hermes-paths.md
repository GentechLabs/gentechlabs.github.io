# Hermes Environment Path Structure (2026-05-02)

## Discovery

During the D5 milestone tracker consolidation, the following Hermes filesystem layout was identified:

```
/root/.hermes/                    # Hermes root (HERMES_HOME)
├── profiles/
│   └── yoyo/
│       └── home/
│           └── .hermes/
│               └── scripts/    # Runtime script directory for yoyo profile
│                   ├── .lfj-aae-config.json
│                   ├── .d5-lp-state.json
│                   ├── .lfj-position-tracker.json
│                   ├── .cmc-watchlist-state.json
│                   ├── cron/      # Cron job definitions
│                   └── d5-lp-consolidated.py
├── scripts/                     # Global Hermes scripts (root-level)
│   ├── cmc-watchlist.py
│   ├── d5-lp-consolidated.py (symlink? or separate copy?)
│   └── ...
├── cron/                        # Global cron
└── logs/
```

## Key Variables

- `HERMES_HOME` (env): `/root/.hermes/profiles/yoyo`
- `os.path.expanduser("~")`: `/root/.hermes/profiles/yoyo/home` (the runtime shell HOME)
- `HOME_SCRIPTS_DIR` (computed): `os.path.join(HERMES_HOME, "home", ".hermes", "scripts")`
  - Result: `/root/.hermes/profiles/yoyo/home/.hermes/scripts`

## Path Resolution Pattern

```python
import os

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")

def hermes_path(filename: str) -> str:
    return os.path.join(HOME_SCRIPTS_DIR, filename)

# State files live here:
STATE_FILE = hermes_path(".d5-lp-state.json")          # Debounce + LP tracking state
CM C_STATE_FILE = hermes_path(".cmc-watchlist-state.json")  # CMC daily reset state
CONFIG_FILE = hermes_path(".lfj-aae-config.json")     # Position + milestone config
POSITION_TRACKER = hermes_path(".lfj-position-tracker.json")  # Entry price + IL tracking
```

## Verification

```python
import os
print("HERMES_HOME:", os.environ.get("HERMES_HOME"))
print("expanduser('~'):", os.path.expanduser("~"))
print("Scripts dir exists?", os.path.isdir(HOME_SCRIPTS_DIR))
```

Expected output on Hermes:
```
HERMES_HOME: /root/.hermes/profiles/yoyo
expanduser('~'): /root/.hermes/profiles/yoyo/home
Scripts dir exists? True
```

## Why Not `~/.hermes/scripts/`?

The vault location (`/root/vaults/gentech/03-Strategies/scripts/`) is version-controlled (Obsidian). Hermes runtime state must live inside the Hermes profile directory to be writable by the Hermes process and survive across cron runs. The `hermes_path()` indirection allows the same code to run from either the vault (development) or the Hermes profile (production) by relying on the environment variable.

## Files Observed (2026-05-02)

| File | Purpose | Location |
|------|---------|----------|
| `.lfj-aae-config.json` | Position range, milestones, DCA, quiet hours | `/root/.hermes/profiles/yoyo/home/.hermes/scripts/` |
| `.d5-lp-state.json` | Debounce timestamps, last check time | same |
| `.cmc-watchlist-state.json` | Daily CMC last prices, date reset | same |
| `.lfj-position-tracker.json` | Entry AVAX price for IL calculation | same |
| `d5-lp-consolidated.py` | Pre-consolidation LP monitor | same |
| `d5-milestone-tracker.py.tmp` | Post-consolidation unified script (pending rename) | `/root/vaults/gentech/03-Strategies/scripts/` |

## Gotcha Checklist

- [ ] State file paths use `hermes_path()`, not hardcoded `/root` or `~`
- [ ] Directory existence check before first write (mkdir -p style)
- [ ] Config file loaded from `hermes_path()` not vault path when running in Hermes
- [ ] Cron job `command` field references script path relative to executing context (verify whether Hermes cron uses profile scripts dir or vault scripts dir)
- [ ] Permissions: State files must be writable by Hermes process user (root)
