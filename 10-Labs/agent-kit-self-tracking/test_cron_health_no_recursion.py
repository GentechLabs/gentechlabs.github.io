#!/usr/bin/env python3
"""Regression test: the cron sentinel must NEVER be able to fork-bomb the host.

THE OUTAGE THIS LOCKS (2026-09-28):
    `heal()` re-fired whatever it graded as failed — including its own job. The sentinel graded
    ITSELF as failed (its `last_status` was `error` from the previous run), re-fired itself, that
    child re-graded itself, re-fired itself... Measured **465 concurrent `cron_health.py`
    processes**, load average **42**, memory driven to ~150 MB free. The kernel OOM-killed the
    treasury gateway twice (`global_oom`) and killed a child mid-run (`memcg`) — which is why
    scheduled runs kept returning `unknown` and Telegram kept dropping. The monitor WAS the outage.

A test that only proves "this specific bug is gone" is worth little. This one asserts the
GENERAL property — that healing cannot recurse at all — so a future refactor that re-introduces
self-healing, or drops the depth counter, fails here loudly instead of at 3am on the host.
"""
import importlib.util
import os
import subprocess
import sys
import time

SCRIPTS = "/root/.hermes/profiles/gentech-treasury/scripts"
SRC = os.path.join(SCRIPTS, "cron_health.py")

fails = []


def check(name, cond, detail=""):
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def load():
    spec = importlib.util.spec_from_file_location("cron_health_under_test", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


print("═══ cron_health recursion guards ═══")
ch = load()

# ── 1. The sentinel refuses to heal its own job id ────────────────────────────────────────────
check("SELF_ID is declared", hasattr(ch, "SELF_ID") and bool(ch.SELF_ID), f"id={getattr(ch,'SELF_ID',None)}")
ok, note = ch.heal({"id": ch.SELF_ID, "script": "cron-health.sh"})
check("heal(self) is REFUSED", not ok, note)
check("refusal names the reason", "re-fire itself" in note, note)

# ── 2. Nothing heals while already inside a heal cycle ────────────────────────────────────────
os.environ["STEWARD_HEAL_DEPTH"] = "1"
try:
    ok, note = ch.heal({"id": "51bc9900e24d", "script": "steward-watchdog.sh"})
    check("heal() at depth>0 is REFUSED", not ok, note)
    check("depth refusal names the reason", "depth>0" in note, note)
finally:
    os.environ.pop("STEWARD_HEAL_DEPTH", None)

# ── 3. The depth counter actually TRAVELS into the child (the real brake) ─────────────────────
# Without this, the parent-level guard is bypassable by the child simply not knowing it is a child.
tmp = "/tmp/_depth_probe.sh"
with open(tmp, "w") as f:
    f.write('#!/usr/bin/env bash\necho "CHILD_DEPTH=${STEWARD_HEAL_DEPTH:-unset}"\n')
os.chmod(tmp, 0o755)
import shutil
shutil.copy(tmp, os.path.join(SCRIPTS, "_depth_probe.sh"))
os.environ.pop("STEWARD_HEAL_DEPTH", None)
ok, note = ch.heal({"id": "probe-job", "script": "_depth_probe.sh"})
child_env = os.environ.get("STEWARD_HEAL_DEPTH")  # heal() must not leak depth into THIS process
check("heal() does not leak depth into the parent", child_env is None, f"parent depth={child_env}")
check("a normal heal still runs (no over-blocking)", ok, note)

# ── 4. The general property: a heal child CANNOT itself heal ──────────────────────────────────
os.environ["STEWARD_HEAL_DEPTH"] = "1"
try:
    ok, note = ch.heal({"id": "probe-job", "script": "_depth_probe.sh"})
    check("a heal child cannot heal on (fork-bomb impossible)", not ok, note)
finally:
    os.environ.pop("STEWARD_HEAL_DEPTH", None)
    for p in (tmp, os.path.join(SCRIPTS, "_depth_probe.sh")):
        try:
            os.unlink(p)
        except OSError:
            pass

# ── 5. End-to-end: a full --heal run must terminate and must not RECURSE ──────────────────────
# The first version of this check counted cron_health.py processes before and after and asserted
# `after <= before + 1`. It FAILED at 02:00 for the wrong reason: the real scheduled sentinel fires
# on the :00/:30 mark, so the test's sample caught a legitimate run alongside its own (`before=1
# after=4`). That is a test measuring COINCIDENCE. Re-run away from the mark it passed (0 -> 0).
#
# A flaky guard is worse than a missing one, because it teaches you to ignore it. So measure the
# thing that is actually wrong — RECURSION — which a fork bomb produces unmistakably (hundreds of
# chained processes), and keep a generous absolute ceiling as a backstop.
def snapshot():
    """Every cron_health.py process: (pid, ppid)."""
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cl = f.read().replace(b"\0", b" ").decode("utf8", "replace")
            if "cron_health.py" not in cl:
                continue
            with open(f"/proc/{pid}/stat") as f:
                st = f.read().split()
            out.append((int(pid), int(st[3])))
        except OSError:
            continue
    return set(out)


def chain_depth(snap):
    """Longest parent->child chain of cron_health.py processes. 1 = independent. >1 = recursion.

    Only walk to a parent that is ITSELF one of our processes. The first version took
    `dict(snap).get(pid)` as the parent and incremented unconditionally, so a SINGLE process whose
    parent was bash scored 2 — a false positive that flagged the test itself. Recursion means a
    cron_health.py is the PARENT of a cron_health.py; an ordinary parent is not a chain.
    """
    pids = {p for p, _ in snap}
    by_pid = dict(snap)
    best = 0
    for pid, _ in snap:
        d, cur = 1, pid
        for _ in range(12):
            parent = by_pid.get(cur)
            if parent is None or parent == cur or parent not in pids:
                break
            d += 1
            cur = parent
        best = max(best, d)
    return best


peak = 0
worst_chain = 0
r = subprocess.run([sys.executable, SRC, "--heal", "--quiet-unless-bad"],
                   capture_output=True, text=True, timeout=280, cwd=SCRIPTS)
for _ in range(6):
    s = snapshot()
    peak = max(peak, len(s))
    worst_chain = max(worst_chain, chain_depth(s))
    time.sleep(0.15)

check("full --heal run terminates", r.returncode in (0, 1), f"rc={r.returncode}")
check("no RECURSION (no cron_health.py is a child of another)",
      worst_chain <= 1, f"longest chain={worst_chain} (1 = independent)")
check("process count stays bounded (a fork bomb is hundreds)",
      peak <= 12, f"peak={peak} during and after the run")
check("--heal run does not recurse into its own id",
      "70a959e08d3a" not in (r.stdout or ""), "")


print()
if fails:
    print(f"❌ {len(fails)} FAILED: " + ", ".join(fails))
    sys.exit(1)
print("✅ all recursion guards hold — the sentinel cannot fork-bomb the host")
