#!/usr/bin/env bash
# test-hq-backup-update.sh — the eight cases, as INVOCATIONS rather than a report.
#
# WHY THIS FILE EXISTS
#   The first version of this work reported eight tests that had been run by hand. HQ's note
#   (2026-09-28): "the negative control is not re-runnable by the next reader without editing
#   your constants — the one thing an alarm-fires test should never require." Exactly right:
#   a test you must EDIT THE SUBJECT to run is a test that will not be run. `--ref` makes the
#   negative control a flag rather than a file edit, and the safety assertion still applies, so
#   pointing it at `main` is REFUSED rather than dangerous.
#
# SAFETY: every case is non-mutating by construction — dry-runs, refusals, and interval
#   deferrals. The suite never pushes the backup ref and never touches `main`. The one case
#   that would push (the real run) is asserted by SOURCE INSPECTION instead, so running this
#   file cannot move a ref.
#
# Usage: scripts/test-hq-backup-update.sh          -> prints PASS/FAIL per case, exit 0 if all pass

set -uo pipefail
VAULT=/root/vaults/gentech
SCRIPT="$VAULT/scripts/hq-backup-update.py"
CANON="$VAULT/10-Labs/agent-kit-self-tracking/hq-backup-update.py"
PY=python3
PASS=0; FAIL=0
ok(){ printf '  ✅ PASS  %s\n' "$1"; PASS=$((PASS+1)); }
no(){ printf '  ❌ FAIL  %s\n      %s\n' "$1" "${2:-}"; FAIL=$((FAIL+1)); }
run(){ ( cd "$VAULT" && timeout 200 $PY "$@" ); }   # NOTE: no pipe — see case 7

# ── CODE-ONLY EXTRACTION — the fix for a CLASS of test bug, applied to every grep below ──
# A grep over the whole file matches PROSE. Two of these tests false-failed on the docstrings
# that explain the very defect they check for (addition 10 matched the retired flag's story;
# case 6b matched `STOPPED_NOT_FAST_FORWARD` in the comment about the previous version). A
# pattern that matches text is not a check on code. So: strip comments and docstrings ONCE,
# and grep the result. This is the same defect the tests exist to catch, one level up.
CODEFILE=$(mktemp)
$PY - "$SCRIPT" > "$CODEFILE" <<'PYEOF'
import ast, sys
src = open(sys.argv[1]).read()
tree = ast.parse(src)
drop = set()
for node in ast.walk(tree):
    # every docstring (module, class, function)
    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
           and isinstance(body[0].value.value, str):
            d = body[0]
            for ln in range(d.lineno, (d.end_lineno or d.lineno) + 1):
                drop.add(ln)
    # every inline comment
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
       and isinstance(node.value.value, str) and not isinstance(getattr(node, "parent", None), type(None)):
        pass
lines = src.splitlines()
for i, line in enumerate(lines, 1):
    if i in drop:
        continue
    code = line.split("#", 1)[0] if not line.lstrip().startswith("#") else ""
    if code.strip():
        print(f"{i}:{code}")
PYEOF
# fallback: if AST stripping failed, use the raw file (fail LOUD rather than silently pass)
if [ ! -s "$CODEFILE" ]; then
  echo "  ⚠️  code-only extraction produced nothing — falling back to the raw file"
  cp "$SCRIPT" "$CODEFILE"
fi
codegrep(){ grep "$@" "$CODEFILE"; }
# `|| true`, not `|| echo 0`: on zero matches `grep -c` already prints "0" and exits 1, so `echo 0`
# appended a SECOND line and the variable became "0\n0" — which makes `[ "$x" -ge 3 ]` an arithmetic
# error. A count that cannot produce a clean zero cannot produce a clean signal.
codecount(){ grep -c "$1" "$CODEFILE" 2>/dev/null || true; }

# ── FUNCTION-SCOPED EXTRACTION — a clause labelled "read by <function>" must measure THAT function ──
# Case 4's `in_assert` was a literal COPY of `refs` (both were `codecount NEVER_TOUCH`), so the clause
# "read by assert_target_safe" could NOT fail independently. MEASURED: a subject whose assert function
# reads NEVER_TOUCH zero times but which carries two unrelated NEVER_TOUCH references elsewhere still
# PASSED case 4 — because `refs >= 3` was satisfied by the unrelated uses. The protection was a global
# threshold wearing the name of a specific clause: the same defect as case 3, one level over.
ASSERTFN=$(mktemp)
$PY - "$SCRIPT" > "$ASSERTFN" <<'PYEOF'
import ast, sys
src = open(sys.argv[1]).read(); lines = src.splitlines()
for n in ast.walk(ast.parse(src)):
    if isinstance(n, ast.FunctionDef) and n.name == "assert_target_safe":
        # EXCLUDE THE FUNCTION'S OWN DOCSTRING. A count that includes prose measures TEXT, not code —
        # the same defect this suite exists to catch, one level further in. The guard's docstring
        # DISCUSSES NEVER_TOUCH, so counting it would keep the clause satisfied while the code
        # stopped reading the constant.
        skip = set()
        b = n.body
        if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
           and isinstance(b[0].value.value, str):
            d = b[0]
            skip = set(range(d.lineno, (d.end_lineno or d.lineno) + 1))
        for i in range(n.lineno, (n.end_lineno or n.lineno) + 1):
            if i in skip:
                continue
            code = lines[i-1].split("#", 1)[0] if not lines[i-1].lstrip().startswith("#") else ""
            if code.strip():
                print(f"{i}:{code}")
PYEOF
# FAIL LOUD: if the guard's body cannot be extracted, case 4's clause is unevaluable. A missing
# function must not read as a satisfied one.
if [ ! -s "$ASSERTFN" ]; then
  echo "  ❌ assert_target_safe body could not be extracted — refusing to report a vacuous PASS"
  exit 1
fi

echo "  === test-hq-backup-update.sh — 8 cases + 2 additions ==="
echo "  subject: $SCRIPT"
echo "  md5: $(md5sum "$SCRIPT" | cut -c1-12)"
echo

# ── case 1: dry-run reports WOULD_PUSH (or CURRENT) and moves nothing ───────────────────
before=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
out=$(run "$SCRIPT" --dry-run --now 2>&1)
after=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
if echo "$out" | grep -qE "would fast-forward|CURRENT|up to date" && [ "$before" = "$after" ]; then
  ok "case 1 — dry-run reports and moves nothing (backup $(printf %.12s "$before"))"
else
  no "case 1 — dry-run" "out=$(echo "$out" | tail -2) before=$before after=$after"
fi

# ── case 2: --json emits valid JSON with a status ──────────────────────────────────────
out=$(run "$SCRIPT" --json --dry-run --now 2>&1 | tail -1)
if echo "$out" | $PY -c "import json,sys; d=json.load(sys.stdin); assert d.get('status'); print(d['status'])" >/dev/null 2>&1; then
  ok "case 2 — --json parses and carries a status ($(echo "$out" | $PY -c 'import json,sys;print(json.load(sys.stdin)["status"])'))"
else
  no "case 2 — --json" "raw=$(echo "$out" | head -c 120)"
fi

# ── case 3: the push target is BUILT from {ref}, VALIDATED by the named guard, then USED ──
#  (v1 of this case grep'd for a literal refspec and false-failed: the push uses the VARIABLE,
#   which is the whole point. Assert the ORDER of construction -> validation -> use instead.)
built=$(codecount 'refspec = f"HEAD:refs/heads/{ref}"')
used=$(codecount 'git push {remote} {refspec}')
pushes=$(codecount "git push")
# FIXED 2026-09-28 (gentech HQ, announced): this pattern matched the DEFINITION at L74 as well as the
# call, so `head -1` returned the def and case 3 could NOT FAIL — measured with the call deleted
# entirely, case 3 still PASSED. Point it at the CALL SITE only, as case 6b already does.
guardline=$(codegrep -n "problem = assert_target_safe\|assert_target_safe(refspec, ref)" | grep -v "def " | head -1 | cut -d: -f1)
pushline=$(codegrep -n "git push" | head -1 | cut -d: -f1)
if [ "$built" -ge 1 ] && [ "$used" -eq 1 ] && [ "$pushes" -eq 1 ] \
   && [ -n "$guardline" ] && [ -n "$pushline" ] && [ "$guardline" -lt "$pushline" ]; then
  ok "case 3 — refspec built from {ref} (L$built), validated by assert_target_safe (L$guardline) BEFORE use (L$pushline); 1 push in file, 0 to main"
else
  no "case 3 — push target" "built=$built used=$used pushes=$pushes guardline=$guardline pushline=$pushline"
fi

# ── case 4: the never-touch constant is READ, not merely declared (HQ's (a)) ───────────
#  The v1 guard was declared and referenced ZERO times: the protection that held was the
#  hardcoded refspec, and the NAMED guard was inert. Assert the name is read by the two
#  places that matter — the safety assertion and the ancestor query.
#  FIXED 2026-09-28 (treasury, announced): `in_assert` used to be `codecount NEVER_TOUCH` — the
#  SAME command as `refs` — so the clause "read by assert_target_safe" could not fail on its own.
#  MEASURED: a subject whose assert body reads NEVER_TOUCH zero times, carrying two unrelated
#  NEVER_TOUCH references, still PASSED via the `refs >= 3` threshold. It now counts in the
#  function's OWN body, so the clause fails when the guard stops reading the constant.
refs=$(codecount "NEVER_TOUCH")
in_assert=$(grep -c "NEVER_TOUCH" "$ASSERTFN" 2>/dev/null || true)
in_query=$(codecount "merge-base --is-ancestor {remote}/{NEVER_TOUCH}")
if [ "$refs" -ge 3 ] && [ "$in_assert" -ge 1 ] && [ "$in_query" -ge 1 ]; then
  ok "case 4 — NEVER_TOUCH referenced $refs times: read by assert_target_safe ($in_assert) and the ancestor query ($in_query). No longer inert."
else
  no "case 4 — NEVER_TOUCH inert" "refs=$refs in_assert=$in_assert in_query=$in_query (a declared-but-unread guard is not a guard)"
fi

# ── case 5: TOO_SOON — the hourly interval holds, exit 0, SILENT ───────────────────────
before=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
run "$SCRIPT" >/tmp/hbu_t5.out 2>&1; rc=$?
after=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
if [ "$rc" -eq 0 ] && [ "$before" = "$after" ] && [ ! -s /tmp/hbu_t5.out ]; then
  ok "case 5 — interval holds: exit 0, silent, backup unchanged"
elif [ "$rc" -eq 0 ] && [ "$before" = "$after" ]; then
  ok "case 5 — interval: exit 0, backup unchanged (output present: $(head -c 60 /tmp/hbu_t5.out))"
else
  no "case 5 — interval" "rc=$rc before=$before after=$after out=$(head -c 80 /tmp/hbu_t5.out)"
fi

# ── case 6: NEGATIVE CONTROL — the guard REFUSES --ref main, with ITS OWN reason ────────
#  v2 asserted the status was IN A SET, so a DIFFERENT refusal satisfied it: the FF query
#  returned STOPPED_NOT_FAST_FORWARD for main and the test passed while the guard was
#  unreachable (HQ, 2026-09-28). Asserting a status is in a set is not asserting WHICH guard
#  produced it. This asserts the exact status AND that the guard's own reason is printed.
main_before=$(timeout 60 git -C "$VAULT" ls-remote vault main | cut -f1)
bk_before=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
out=$(run "$SCRIPT" --json --now --ref main 2>&1 | tail -1)
txt=$(run "$SCRIPT" --now --ref main 2>&1)
main_after=$(timeout 60 git -C "$VAULT" ls-remote vault main | cut -f1)
bk_after=$(timeout 60 git -C "$VAULT" ls-remote vault hq-backup-20260928 | cut -f1)
status=$(echo "$out" | $PY -c "import json,sys;print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "UNPARSED")
if [ "$main_before" = "$main_after" ] && [ "$bk_before" = "$bk_after" ] \
   && [ "$status" = "STOPPED_UNSAFE_REFSPEC" ] \
   && echo "$txt" | grep -q "never-touch ref"; then
  ok "case 6 — negative control: --ref main -> $status via THE GUARD (its own reason printed); main AND backup untouched"
else
  no "case 6 — negative control" "status=$status (want STOPPED_UNSAFE_REFSPEC — a set-membership test let the FF query pass for it) reason_printed=$(echo "$txt" | grep -c 'never-touch ref') main=$main_before->$main_after bk=$bk_before->$bk_after"
fi

# ── case 6b: REACHABILITY — the guard is called BEFORE any other return can mask it ──────
#  Order is necessary and not sufficient (HQ, 2026-09-28). v2 had the call before the push and
#  still could not fire, because the FF query returned first. Reachability is about whether
#  CONTROL ARRIVES, so assert the call precedes every other `return` in main() that can fire
#  first — the interval, the fetch, and the FF query.
# the extract prefixes line numbers, so '^def main' cannot anchor — match the definition itself
mainln=$(codegrep -n 'def main():' | head -1 | cut -d: -f1)
guardln=$(codegrep -n 'problem = assert_target_safe' | head -1 | cut -d: -f1)
intervalln=$(codegrep -n 'TOO_SOON' | head -1 | cut -d: -f1)
fetchln=$(codegrep -n 'FETCH_FAILED' | head -1 | cut -d: -f1)
ffln=$(codegrep -n 'STOPPED_NOT_FAST_FORWARD' | head -1 | cut -d: -f1)
if [ -n "$guardln" ] && [ "$guardln" -gt "$mainln" ] \
   && [ "$guardln" -lt "$intervalln" ] && [ "$guardln" -lt "$fetchln" ] && [ "$guardln" -lt "$ffln" ]; then
  ok "case 6b — REACHABLE: assert_target_safe (L$guardln) precedes TOO_SOON (L$intervalln), FETCH_FAILED (L$fetchln) and the FF query (L$ffln) — no earlier return can mask it"
else
  no "case 6b — reachability" "guard=$guardln must be < interval=$intervalln fetch=$fetchln ff=$ffln (order is not reachability)"
fi

# ── case 6c: the guard must be REACHABLE, not merely ordered — prove it end to end ───────
#  The strongest form: run the exact CLI input whose firing case was hand-edited before.
if echo "$txt" | grep -q "refusing to push" && [ "$status" = "STOPPED_UNSAFE_REFSPEC" ]; then
  ok "case 6c — the guard FIRES FROM THE CLI: its firing case is now an invocation, not a hand-edit"
else
  no "case 6c — guard reachable from CLI" "the firing case still requires editing the subject"
fi

# ── case 7: exit codes captured WITHOUT a pipe (a refusal must not read as success) ────
run "$SCRIPT" --json --now --ref main >/tmp/hbu_t7.out 2>&1; rc=$?
if [ "$rc" -eq 1 ]; then
  ok "case 7 — refusal returns exit 1 when captured without a pipe (rc=$rc)"
else
  no "case 7 — exit code" "rc=$rc (expected 1; a refusal that reads as 0 is the worst bug in an alarm job)"
fi

# ── case 8: the backup is a real SNAPSHOT, not a hash echo (content, not hash) ─────────
if timeout 90 git -C "$VAULT" cat-file -e hq-backup-20260928:01-HANDOFFS/gentech-treasury-completions.md 2>/dev/null \
   || timeout 90 git -C "$VAULT" cat-file -e 8caed13ef1ae07584eafdcb10ef2805c3cc9b35f:01-HANDOFFS/gentech-treasury-completions.md 2>/dev/null; then
  ok "case 8 — backup tree reads a real file (a snapshot, not a hash echo)"
else
  no "case 8 — content" "cat-file could not read a known file from the backup tree"
fi

# ── addition 9: the four copies are one artifact (the drift surface HQ flagged) ────────
copies=(
  "$VAULT/scripts/hq-backup-update.py"
  "$VAULT/10-Labs/agent-kit-self-tracking/hq-backup-update.py"
  "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/hq-backup-update.py"
  "/root/.hermes/profiles/gentech-treasury/scripts/hq-backup-update.py"
)
uniq=$(for f in "${copies[@]}"; do test -f "$f" && md5sum "$f" | cut -d' ' -f1; done | sort -u | wc -l)
present=$(for f in "${copies[@]}"; do test -f "$f" && echo x; done | wc -l)
if [ "$uniq" -eq 1 ] && [ "$present" -eq 4 ]; then
  ok "addition 9 — all 4 copies present at ONE md5 ($(md5sum "${copies[0]}" | cut -c1-12)) — no drift today"
else
  no "addition 9 — copy drift" "present=$present/4 distinct_md5=$uniq"
fi

# ── addition 10: the retired word is gone from the CLI SURFACE (not from the file) ─────
#  (v1 grep'd the whole file and false-failed on the header, which legitimately EXPLAINS why
#   --force-run was withdrawn. The right surface is argparse: the header must keep the reason.)
surface=$(codegrep -E "add_argument" | grep -c "force")
now_flag=$(codecount 'add_argument("--now"')
if [ "$surface" -eq 0 ] && [ "$now_flag" -eq 1 ]; then
  ok "addition 10 — CLI has --now and zero force-named flags (the docstring may still explain why)"
else
  no "addition 10 — force wording on the CLI" "force_flags=$surface now_flag=$now_flag"
fi

echo
echo "  ────────────────────────────────────"
echo "  PASS $PASS   FAIL $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
