#!/usr/bin/env python3
"""Regression test for the hub theme palettes in defi_hub_data.py.

WHY THIS EXISTS
---------------
The hub palette is 12 CSS variables consumed by 32 `var(--)` uses. A theme is a palette swap, which
is free and cheap to ship — and therefore cheap to ship WRONG. Two failure modes are silent:

  1. **An incomplete palette.** A missing variable leaves the page using an undefined CSS var, which
     renders as NO COLOUR AT ALL (transparent/black) rather than as an error. Nothing raises.
  2. **A theme that repurposes the semantic colours.** `--good/--warn/--bad` are load-bearing: they
     colour real in-range / out-of-range / exit states. A palette that tints them for decoration
     makes a losing book look fine, or a healthy one look broken. That is the exact class of defect
     this whole system exists to prevent — a surface implying something its data does not say.

So the rule this test pins: **a theme changes the MOOD of the surface, never the MEANING of a
signal.** Every palette must be complete, and `good/warn/bad` must be byte-identical across all of
them. It also pins the fallback direction, because a partial theme must degrade to the full house
palette rather than to a half-dressed page.

Run:  python3 test_hub_theme.py
Exit: 0 = properties hold, 1 = violated.
"""
import importlib.util
import types
import os
import re
import sys

SCRIPTS = "/root/.hermes/profiles/gentech-treasury/scripts"
SRC = os.path.join(SCRIPTS, "defi_hub_data.py")
sys.path.insert(0, SCRIPTS)

PASS, FAIL = [], []

REQUIRED = ("bg", "card", "card2", "line", "txt", "dim",
            "good", "warn", "bad", "accent", "wax", "usd")
SEMANTIC = ("good", "warn", "bad")


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


def vars_of(block):
    """Parse `--name:#rrggbb` pairs out of a :root block."""
    return {k: v.lower() for k, v in re.findall(r"--([a-z0-9]+)\s*:\s*(#[0-9a-fA-F]{6})", block)}


# ── LOAD FROM SOURCE, NEVER FROM .pyc ──────────────────────────────────────────────────────────
# Python validates a cached .pyc on (source mtime, source size) ONLY. A probe that plants a fault
# and restores it can change NEITHER: an edit like "#2fd07f" -> "#e08a2e" is the same 7 characters,
# and plant+restore inside one second keeps the same mtime. So a .pyc compiled from the PLANTED
# file validates as current for the clean one, and the test silently reads the plant.
#
# Measured 2026-09-28: this test reported a semantic violation AFTER the source had been restored,
# and the fault was real — in the stale bytecode. Compiling the source text directly makes the
# result a fact about the file on disk, which is the only thing a test may assert.
_src_text = open(SRC).read()
m = types.ModuleType("dhd_theme")
# `__file__` must be set BEFORE exec: the module resolves sibling paths from it, and without it
# the exec'd body raises NameError at import time (measured — this exact mistake).
m.__file__ = SRC
m.__dict__["__file__"] = SRC
exec(compile(_src_text, SRC, "exec"), m.__dict__)

print("═══ hub theme palettes ═══")

check("a THEMES table exists", isinstance(getattr(m, "THEMES", None), dict) and m.THEMES)
check("an ACTIVE_THEME is named", isinstance(getattr(m, "ACTIVE_THEME", None), str) and m.ACTIVE_THEME)
check("ACTIVE_THEME is a real palette",
      m.ACTIVE_THEME in m.THEMES, f"ACTIVE_THEME={m.ACTIVE_THEME!r} not in {list(m.THEMES)}")

base = vars_of(m.theme_root("default"))
check("the default palette is complete", len(base) == len(REQUIRED),
      f"got {len(base)} vars: {sorted(base)}")

# ── 1. THE SEMANTIC RULE: mood may change, meaning may not ─────────────────────────────────────
for name in sorted(m.THEMES):
    v = vars_of(m.theme_root(name))
    check(f"{name}: palette is complete ({len(REQUIRED)} vars)",
          all(k in v for k in REQUIRED),
          f"missing: {sorted(set(REQUIRED) - set(v))}")
    same_sem = all(v.get(k) == base.get(k) for k in SEMANTIC)
    check(f"{name}: good/warn/bad identical to the house default  (MUST NOT be repurposed)",
          same_sem,
          f"good={v.get('good')} warn={v.get('warn')} bad={v.get('bad')} vs "
          f"{[base.get(k) for k in SEMANTIC]}")

# ── 2. A theme must actually theme something (a palette identical to default is a no-op) ───────
for name in sorted(m.THEMES):
    if name == "default":
        continue
    v = vars_of(m.theme_root(name))
    check(f"{name}: differs from default in a visual dimension",
          any(v.get(k) != base.get(k) for k in ("bg", "card", "card2", "line", "txt", "dim", "accent")),
          "palette is byte-identical to default — the theme would render as no change")

# ── 3. FALLBACK SAFETY: an unknown/partial theme must degrade to a COMPLETE palette ────────────
for probe in ("nonsense", "", None, "UPT0BER", "uptober ", 0, [], {}):
    try:
        v = vars_of(m.theme_root(probe))
    except Exception as e:
        check(f"theme_root({probe!r}) does not raise", False, f"{type(e).__name__}: {e}")
        continue
    check(f"theme_root({probe!r}) degrades to a complete palette", len(v) == len(REQUIRED),
          f"got {len(v)} vars — a missing var renders as NO COLOUR, not an error")

# ── 4. A partial palette must inherit the house value for the keys it omits ───────────────────
_partial = dict(m.THEMES.get("default", {}))
saved = getattr(m, "THEMES", {}).get("__partial_probe__")
m.THEMES["__partial_probe__"] = {"bg": "#123456"}          # only one key, deliberately
try:
    pv = vars_of(m.theme_root("__partial_probe__"))
    check("a partial palette inherits the house values for omitted keys",
          len(pv) == len(REQUIRED) and pv.get("bg") == "#123456"
          and all(pv.get(k) == base.get(k) for k in SEMANTIC),
          f"got {len(pv)} vars; bg={pv.get('bg')}")
finally:
    if saved is None:
        m.THEMES.pop("__partial_probe__", None)
    else:
        m.THEMES["__partial_probe__"] = saved

# ── 5. THE SLOT IS ACTUALLY WIRED (a palette nobody injects is not a theme) ───────────────────
src = open(SRC).read()
check("the page template has a __THEME_ROOT__ slot",
      "__THEME_ROOT__" in src, "template still carries a hardcoded :root block")
check("the hardcoded palette is gone from the template",
      "--bg:#080a0d" not in src.split("def theme_root")[0].replace('"bg": "#080a0d"', ""),
      "a literal palette is still baked into PAGE — the slot would be decorative")
check("write_pages substitutes the slot",
      '__THEME_ROOT__", theme_root()' in src.replace(" ", "").replace("\n", "")
      or "theme_root()" in src.split("def write_pages")[-1][:600],
      "write_pages does not call theme_root() — pages would render with an empty :root")

print()
if FAIL:
    print(f"  ❌ {len(FAIL)} FAILED: {', '.join(FAIL)}")
    sys.exit(1)
print(f"  ✅ all {len(PASS)} hub-theme properties hold")
sys.exit(0)
