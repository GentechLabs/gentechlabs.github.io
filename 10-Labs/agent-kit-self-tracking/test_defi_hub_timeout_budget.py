#!/usr/bin/env python3
"""test_defi_hub_timeout_budget.py — the inner timeout must be smaller than its envelope.

THE OUTAGE THIS PINS (2026-09-28, job dcb074a180d3)
---------------------------------------------------
`defi_hub_data.py::_run` used a hardcoded `timeout=300` while `defi-hub-refresh.sh` wrapped the
whole run in `timeout 280`. An inner guard ABOVE its outer limit can never fire: the shell always
wins. The job died with a bare rc=124 and the `TimeoutExpired` branch — written specifically so one
hung RPC degrades to "this tenant failed" instead of killing the page — never executed.

It was not a rare corner. Successful runs of that job measure 246-272s against the 280s cap, i.e.
88-97% of the envelope consumed on a GOOD run, so ordinary variance reached the cap.

WHAT IS ASSERTED (both directions)
----------------------------------
  1. COLLECT_TIMEOUT (inner) < the wrapper's `timeout` (outer).
  2. The worst case still fits: tenants x inner < outer. Otherwise the LAST tenant is always the
     one sacrificed, and which tenant that is depends on registry ordering.
  3. No hardcoded numeric timeout in the collector path that exceeds the envelope.
  4. NEGATIVE CONTROL: the test is shown to FAIL when the invariant is deliberately broken, so a
     green result means something. A test that cannot go red is a claim, not a check.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLLECTOR = os.path.join(HERE, "defi_hub_data.py")
WRAPPER = os.path.join(HERE, "defi-hub-refresh.sh")

fails = []


def check(label, ok, detail=""):
    print(("  ✅ " if ok else "  ❌ ") + label + (("  — " + detail) if detail else ""))
    if not ok:
        fails.append(label)


def live(path):
    """Strip comments/blank lines — measure CODE, not prose about code.

    The first version of this test grepped raw text and failed on `timeout=300` appearing inside the
    explanatory comment that documents the fix. Anchoring on prose measures prose.
    """
    out = []
    for line in open(path):
        s = line.split("#")[0].rstrip()
        if s.strip():
            out.append(s)
    return "\n".join(out)


def parse():
    c_raw = "\n".join(l for l in open(COLLECTOR) if "COLLECT_TIMEOUT" in l and l.strip().startswith("COLLECT_TIMEOUT"))
    inner = int(re.search(r"COLLECT_TIMEOUT\s*=\s*(\d+)", c_raw).group(1))
    # INTERPRETER-AGNOSTIC (fixed 2026-09-30). This pinned the literal token `python3`, so the
    # wrapper could not change WHICH interpreter it uses without breaking the test — and it had
    # to change, because Hermes' bundled python had no web3. A test that pins an expression
    # pins that expression's bugs: the property here is the TIMEOUT RELATION (inner < outer),
    # not the interpreter's name. Match any token between the timeout and the script.
    outer = int(re.search(r"timeout\s+(\d+)\s+\S.*defi_hub_data", live(WRAPPER)).group(1))
    n_tenants = len(re.findall(r"STEWARD_TENANT", live(COLLECTOR)))
    return inner, outer


def tenants_from_registry():
    """ACTIVE tenants, read from the SAME registry the collector uses.

    The first version of this test guessed a filename (`treasury-registry.json`) that does not exist,
    swallowed the exception, and returned a hardcoded fallback of 2 — a fallback constant read as a
    live measurement, which is the exact defect family this file exists to guard. It happened to
    produce the right number, which is the dangerous part: a wrong read that agrees with the truth
    teaches nothing and hides itself. Read REGISTRY out of the collector itself.
    """
    import json
    src = open(COLLECTOR).read()
    m = re.search(r'^REGISTRY\s*=\s*"([^"]+)"', src, re.M)
    if not m:
        raise AssertionError("cannot find REGISTRY in the collector — refusing to use a fallback")
    path = m.group(1)
    if not os.path.exists(path):
        raise AssertionError("REGISTRY does not exist: %s — refusing to use a fallback" % path)
    reg = json.load(open(path))
    n = sum(1 for t in (reg.get("tenants") or {}).values()
            if t.get("status") == "ACTIVE" and t.get("wallet"))
    print("  registry: %s  → %d ACTIVE tenant(s)" % (os.path.basename(path), n))
    return n


def run(inner, outer, n_tenants):
    """All assertions. Returns True if everything holds."""
    fails.clear()
    print("  inner (COLLECT_TIMEOUT) = %ds" % inner)
    print("  outer (wrapper timeout) = %ds" % outer)
    print()

    check("inner < outer  (the graceful branch is reachable)", inner < outer,
          "headroom %ds" % (outer - inner))

    worst = n_tenants * inner
    check("worst case fits: tenants x inner < outer", worst < outer,
          "%d tenants x %ds = %ds vs %ds" % (n_tenants, inner, worst, outer))

    # no hardcoded numeric timeout in the collector path that breaks the envelope
    bad = []
    for m in re.finditer(r"timeout\s*=\s*(\d+)", live(COLLECTOR)):
        v = int(m.group(1))
        if v >= outer:
            bad.append(v)
    check("no hardcoded timeout >= outer in the collector", not bad, str(bad))

    # sanity: a non-trivial envelope, so nobody 'fixes' this by setting both to 1
    check("envelope is sane (> 60s)", outer > 60, "%ds" % outer)

    return not fails


print("═══ defi hub timeout budget ═══")
inner, outer = parse()
n = tenants_from_registry()
ok = run(inner, outer, n)
print()

# ── NEGATIVE CONTROL: the test must go RED when the invariant is broken ────────────────────────
print("── negative control (must go RED) ──")
neg_ok = run(inner=900, outer=600, n_tenants=2)      # inner ABOVE outer — the original bug
print("  " + ("✅ control behaved: invariant violation is detected (RED as required)"
               if not neg_ok else "❌ control FAILED: a broken budget passed — this test is worthless"))
neg2_ok = run(inner=240, outer=300, n_tenants=2)     # worst case 480 > 300 — the subtle break
print("  " + ("✅ control behaved: worst-case overflow is detected (RED as required)"
               if not neg2_ok else "❌ control FAILED: an overflowing worst case passed"))
print()

if ok:
    print("✅ timeout budget holds — an inner guard smaller than its envelope, both directions proven")
    sys.exit(0)
print("❌ timeout budget VIOLATED — an inner guard cannot fire")
sys.exit(1)
