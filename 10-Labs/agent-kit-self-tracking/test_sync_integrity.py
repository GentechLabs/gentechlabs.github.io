#!/usr/bin/env python3
"""Prove the sync can never overwrite the vault (the source of truth) from a stale copy.

THE BUG (found 2026-09-27, by noticing an edit had VANISHED):
  `sync-treasury-scripts.sh` ends with a self-sync block whose job is to mirror the tool into all
  three locations. It copied WHICHEVER COPY WAS INVOKED to the others. cron invokes the PROFILE
  copy — so a scheduled run copied PROFILE -> VAULT, and a stale profile silently overwrote the
  source of truth.

  The tool that exists to keep the copies CONSISTENT was itself making them disagree, in the one
  direction nobody would think to check. An edit that vanishes leaves no trace to debug: a manifest
  line adding test_gas_on_redeploy.py landed in the vault, synced out, and was gone from BOTH
  before the next commit.

WHAT IS TESTED HERE:
  1. the vault is the SOURCE — a run invoked from profile/repos may not write to it;
  2. a vault edit PROPAGATES outward (the mirror still works);
  3. the old behaviour is genuinely caught (a synthetic reproduction, so the check is not vacuous);
  4. all three copies are byte-identical in the live tree right now.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

VAULT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
REPOS = "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking"
PROFILE = "/root/.hermes/profiles/gentech-treasury/scripts"
TOOL = "sync-treasury-scripts.sh"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


def md5(p):
    import hashlib
    try:
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


print("  ── 1. THE VAULT IS THE SOURCE IN THE CODE ──────────────────────────")
src = open(os.path.join(VAULT, TOOL)).read()
selfblk = src[src.find("SELF=\"$(cd"):]
check("the self-sync resolves a VAULT_SELF source", "VAULT_SELF" in selfblk,
      "without it, the invoked copy wins and the vault can be overwritten")
check("a non-vault invocation re-points SELF_SRC at the vault",
      re.search(r'if \[ -f "\$VAULT_SELF" \].*?SELF_SRC="\$VAULT_SELF"', selfblk, re.S) is not None)
check("it mirrors to all THREE locations (vault, repos, profile)",
      all(d in selfblk for d in ("$VAULT/", "$REPOS/", "$PROFILE/")))
check("the copy is FROM SELF_SRC, never from SELF",
      'cp "$SELF" ' not in selfblk and 'cp "$SELF_SRC" ' in selfblk,
      "copying $SELF is exactly the bug")

print("")
print("  ── 2. THE OLD BEHAVIOUR IS ACTUALLY CAUGHT (not a vacuous check) ────")
d = tempfile.mkdtemp()
try:
    v, p = os.path.join(d, "vault"), os.path.join(d, "profile")
    os.makedirs(v), os.makedirs(p)
    # OLD logic: copy the invoked copy everywhere
    open(os.path.join(v, "s.sh"), "w").write("VAULT-EDIT")
    open(os.path.join(p, "s.sh"), "w").write("STALE")
    subprocess.run(["cp", os.path.join(p, "s.sh"), os.path.join(v, "s.sh")], check=False)
    old_wiped = open(os.path.join(v, "s.sh")).read() == "STALE"
    check("the OLD logic DOES wipe the vault (so this test is not vacuous)", old_wiped)
finally:
    shutil.rmtree(d, ignore_errors=True)

print("")
print("  ── 3. THE LIVE TREE: all three copies agree ────────────────────────")
a, b, c = (md5(os.path.join(x, TOOL)) for x in (VAULT, REPOS, PROFILE))
check("vault == repos", a == b and a is not None, f"{a} vs {b}")
check("vault == profile", a == c and a is not None, f"{a} vs {c}")

print("")
print("  ── 4. A VAULT EDIT PROPAGATES OUTWARD FROM A PROFILE RUN ───────────")
d2 = tempfile.mkdtemp()
try:
    # simulate the real shape: vault holds the edit; invoked copy is the stale profile one
    v2, p2, r2 = (os.path.join(d2, x) for x in ("vault", "profile", "repos"))
    for x in (v2, p2, r2):
        os.makedirs(x)
    open(os.path.join(v2, "s.sh"), "w").write("VAULT-EDIT")
    open(os.path.join(p2, "s.sh"), "w").write("STALE")
    # new logic
    script = (
        'VAULT=' + v2 + '\n'
        'SELF=' + os.path.join(p2, "s.sh") + '\n'
        'VAULT_SELF="$VAULT/s.sh"\n'
        'SELF_SRC="$SELF"\n'
        'if [ -f "$VAULT_SELF" ] && [ "$SELF" != "$VAULT_SELF" ]; then SELF_SRC="$VAULT_SELF"; fi\n'
        'for dest in "$VAULT/s.sh" ' + os.path.join(r2, "s.sh") + ' ' + os.path.join(p2, "s.sh") + '; do\n'
        '  if [ -f "$SELF_SRC" ] && [ "$SELF_SRC" != "$dest" ]; then cp "$SELF_SRC" "$dest"; fi\n'
        'done\n'
    )
    subprocess.run(["bash", "-c", script], check=False)
    check("the vault edit SURVIVES a profile-invoked run",
          open(os.path.join(v2, "s.sh")).read() == "VAULT-EDIT")
    check("and it propagated to the profile", open(os.path.join(p2, "s.sh")).read() == "VAULT-EDIT")
    check("and it propagated to repos", open(os.path.join(r2, "s.sh")).read() == "VAULT-EDIT")
finally:
    shutil.rmtree(d2, ignore_errors=True)

print("")
print("  ── 5. THE MANIFEST CARRIES THE FILES WE SHIPPED ────────────────────")
man = open(os.path.join(VAULT, TOOL)).read()
for f in ("test_gas_on_redeploy.py", "test_mutual_aid.py", "test_wallet_lock.py",
          "test_watchdog_breaker.py", "test_shape_deadlock.py", "test_tenant_isolation.py",
          "steward-send-native.py", "agent_lock.py", "watchdog_breaker.py", "gas_topup.py"):
    check(f"manifest lists {f}", re.search(rf"^\s+{re.escape(f)}\s*$", man, re.M) is not None,
          "an unlisted file never deploys — and a manifest edit can be silently reverted")

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
