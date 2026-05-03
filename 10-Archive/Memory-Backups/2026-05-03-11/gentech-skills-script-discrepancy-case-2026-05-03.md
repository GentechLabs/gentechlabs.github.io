# Script Output Discrepancy — LFJ Monitoring Suite

**Date**: 2026-05-03  
**Detected by**: YoYo during 4× daily report  
**Scripts involved**: `d5-master-cron.py`, `d5-milestone-summary.py`, `lp-position-reader.py`

---

## Symptom

Running two monitoring scripts on the same pool produced **substantially different position values** for the same timestamp:

| Script | Reported Position Value | Efficiency | Status |
|--------|----------------------|------------|--------|
| `d5-milestone-summary.py` | $83.92 | 38.2% | "Position Value: $83.92" |
| `d5-master-cron.py` | $138.92 | 66.3% | "Position Value: $138.92" |
| `lp-position-reader.py` | $134.94 (LP) + $0.88 (wallet) = **$135.82** | 38.2% | Ground truth (on-chain decoded) |

---

## Root Cause

The monitoring ecosystem has **three overlapping but independent scripts** that do not share state:

1. `d5-master-cron.py` — master consolidated report; uses its own state cache and may reflect pending DCA injection or stale snapshot.
2. `d5-milestone-summary.py` — human-narrative snapshot; uses a different config range source and simplified efficiency calc.
3. `lp-position-reader.py` — on-chain position decoder; queries the chain directly and returns verified balances.

No single source of truth exists across scripts; state files are fragmented across profiles (`~/.hermes/scripts/` vs `~/.hermes/profiles/yoyo/home/.hermes/scripts/`).

---

## Resolution Protocol (as executed)

1. **Run `lp-position-reader.py` first** — treat its output as ground truth for on-chain balances, active bin, and efficiency.
2. **Use `d5-master-cron.py` values** for watchlist prices and pool volume metrics (it aggregates CMC + DexScreener correctly).
3. **Ignore `d5-milestone-summary.py` numeric discrepancies**; use it only for narrative boilerplate.
4. **Vault entry numbers** must match `lp-position-reader.py` outputs exactly in the Balance fields.

Document the variance in the vault entry via an inline **Note** field if any script diverges by >$0.50 or efficiency differs by >5pp.

---

## Follow-up Actions (assigned)

| Owner | Task | Status |
|-------|------|--------|
| DMOB | Symlink state files across profiles: `~/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-*.json` ←→ `~/.hermes/scripts/` | Pending |
| YoYo | Reconcile milestone ladder: `d5-master-cron.py` hardcodes `$5/$20/$55/$200` while AAE config says `$3/$5/$8/$10/...` | Open |
| Desmond | Verify `d5-milestone-summary.py` reads config range from the same source as `d5-master-cron.py` | Open |

---

## Prevention

Before any vault update, **always run the trio** in order:
```bash
python3 lp-position-reader.py   # → use these numbers
python3 d5-master-cron.py       # → use watchlist + volume
# d5-milestone-summary.py only for templating
```

If any two sources disagree by more than rounding tolerance, log the discrepancy in the Green Room and defer vault update until resolved.
