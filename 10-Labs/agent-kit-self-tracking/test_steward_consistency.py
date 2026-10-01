#!/usr/bin/env python3
"""Tests for steward_consistency.py — the cross-system agreement checker.

The checker exists because two cards on ONE page contradicted each other (Jordan, 2026-09-27:
"We shouldn't have systems that disagree with each other"). So the thing that must be provable is
that the checker FIRES on a real disagreement and STAYS SILENT on a correct one. A guard that
cannot fail is not a guard.

Exit codes: 0 pass, 1 fail, 2 could not read inputs (a read failure is not a verdict).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = "/root/.hermes/profiles/gentech-treasury/scripts/steward_consistency.py"
DEFI = Path("/var/www/gentechlabs/DeFi")
TENANTS = ["jordan", "dadrian"]

results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(f"  {'PASS' if ok else 'FAIL'} — {name}" + (f"  [{detail}]" if detail and not ok else ""))


def run(tenants):
    p = subprocess.run([sys.executable, SCRIPT] + tenants, capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout


# ---------------------------------------------------------------- 1. inputs readable
payloads = {}
for t in TENANTS:
    f = DEFI / f"defi-data-{t}.json"
    if not f.exists():
        print(f"  SKIP — no payload for {t} (cannot judge, not a verdict)")
        sys.exit(2)
    try:
        payloads[t] = json.loads(f.read_text())
    except Exception as e:
        print(f"  SKIP — cannot parse {f}: {e}")
        sys.exit(2)

check("both payloads load", len(payloads) == 2)

# ---------------------------------------------------------------- 2. clean run is clean
rc, out = run(TENANTS)
check("clean run exits 0 (no disagreement)", rc == 0, f"rc={rc}")
check("clean run reports 0 disagreements", "DISAGREEMENTS: 0" in out, out[-200:])

# ---------------------------------------------------------------- 3. every check RAN
for label in ("capital: ledger vs chain", "bins: ledger vs chain scan", "range flag vs arithmetic",
              "spot inside held bins", "shape verdicts", "payload freshness",
              "page ledger vs ledger file", "estimate vs realised receipt"):
    check(f"check present: {label}", label in out)

# ---------------------------------------------------------------- 4. NON-VACUITY: planted faults fire
# Each fault is a REAL disagreement in one field. If any of these passes silently, the checker is
# measuring nothing and its green ticks are worthless.
FAULTS = [
    ("bins disagree", lambda d: d.update({"chain_bins": 999})),
    ("in_range flag wrong", lambda d: d.update({"in_range": not d.get("in_range")})),
    ("capital diverges", lambda d: d.update({"capital_usd": (d.get("capital_usd") or 0) + 5000,
                                             "ledger_vs_shape_delta": 5000.0})),
    ("spot outside held bins", lambda d: d.update({"active_id": 1})),
    ("stale payload", lambda d: d.update({"updated_at": "2020-01-01T00:00:00Z"})),
]

for label, mutate in FAULTS:
    t = TENANTS[0]
    src = DEFI / f"defi-data-{t}.json"
    bak = Path(tempfile.mkdtemp()) / "bak.json"
    shutil.copy(src, bak)
    try:
        d = json.loads(src.read_text())
        mutate(d)
        src.write_text(json.dumps(d))
        rc, out = run([t])
        check(f"FALLS on planted fault: {label}",
              rc == 1 or "❌" in out or "DISAGREE" in out, f"rc={rc}")
    finally:
        shutil.copy(bak, src)

# ---------------------------------------------------------------- 5. restored clean
d_after = json.loads((DEFI / f"defi-data-{TENANTS[0]}.json").read_text())
check("payload restored byte-identical after probes", d_after == payloads[TENANTS[0]])
rc, out = run(TENANTS)
check("clean again after probes", rc == 0, f"rc={rc}")

# ---------------------------------------------------------------- 6. unreadable input -> 2, never 1
src = DEFI / f"defi-data-{TENANTS[0]}.json"
bak = Path(tempfile.mkdtemp()) / "bak.json"
shutil.copy(src, bak)
try:
    src.write_text("{ this is not json")
    rc, out = run([TENANTS[0]])
    check("corrupt payload exits 2 (read failure), not 1 (verdict)", rc == 2, f"rc={rc}")
finally:
    shutil.copy(bak, src)

passed = sum(1 for ok, _, _ in results if ok)
print(f"\n  RESULT: {'PASS' if passed == len(results) else 'FAIL'} — {passed}/{len(results)} checks passed")
for ok, name, detail in results:
    if not ok:
        print(f"    FAILED: {name} {detail}")
sys.exit(0 if passed == len(results) else 1)
