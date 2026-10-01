#!/bin/bash
# self-audit-watch.sh — run the treasury self-audit; speak ONLY when something changed.
#
# Jordan Sep 11 2026: "what if you decided to run an audit yourself... that's
# self-evolution or self-healing territory... you guys can catch things that
# need an audit before I do."
#
# Silence doctrine: this job is quiet unless it FINDS something new. It keeps a
# fingerprint of the finding set so a standing (known) issue doesn't re-alert
# every run, but a NEW class of bug speaks up immediately.
set -uo pipefail
SC="/root/.hermes/profiles/gentech-treasury/scripts"
STATE="$SC/.self-audit-state.json"

OUT=$(cd "$SC" && timeout 300 python3 treasury_self_audit.py --json 2>/dev/null)
RC=$?

python3 - "$OUT" "$STATE" "$RC" <<'PY'
import json, sys, hashlib, os, time

raw, state_path, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
try:
    data = json.loads(raw)
except Exception:
    # audit itself failed to run — that IS a finding worth one alert
    print("⚠️  Steward self-audit could not run (no JSON output).")
    sys.exit(0)

findings = data.get("findings", [])
# only HIGH/MED are alert-worthy; INFO is informational
alertable = [f for f in findings if f.get("sev") in ("HIGH", "MED")]
sig = hashlib.md5(json.dumps(
    sorted(f"{f['class']}:{f['where']}" for f in alertable)
).encode()).hexdigest()[:12]

prev = {}
if os.path.exists(state_path):
    try:
        prev = json.load(open(state_path))
    except Exception:
        prev = {}

if sig == prev.get("sig"):
    # nothing changed — stay silent (silence doctrine)
    sys.exit(0)

json.dump({"sig": sig, "ts": time.time(),
           "classes": sorted({f["class"] for f in alertable})},
          open(state_path, "w"))

if not alertable:
    if prev.get("sig"):
        print("✅ Steward self-audit: all clear — previously flagged issues are resolved.")
    sys.exit(0)

print("🔍 STEWARD SELF-AUDIT — new findings\n")
for f in alertable:
    print(f"  [{f['sev']}] {f['class']} · {f['where']}")
    print(f"      {f['msg']}")
    if f.get("fix"):
        print(f"      fix: {f['fix']}")
print(f"\n{len(alertable)} issue(s) need attention.")
PY
