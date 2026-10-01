#!/usr/bin/env python3
"""Migrate hardcoded treasury identity -> steward_identity resolver.

WHY: ~42 scripts hardcoded the wallet address, so a second operator running any
of them would still sign for the FIRST operator's treasury. This rewrites the
literals into resolver calls so identity comes from config/env, and adds a
startup assertion so a mismatch is a hard stop.

SAFETY: every rewrite is syntax-checked with ast.parse and REVERTED on failure —
a half-migrated script that signs transactions is worse than an unmigrated one.

Usage:
    python3 migrate_identity.py            # dry-run, report only
    python3 migrate_identity.py --execute
"""
import argparse
import ast
import pathlib
import re
import shutil
import time

HERE = pathlib.Path(__file__).resolve().parent

WALLET_LITERALS = ["0x572ABd6461BED2258615E6b99c585Ab7c5d05037"]
KEY_PATH_LITERALS = ["/root/.blockrun/almanak-steward-key"]

IMPORT_LINE = ("from steward_identity import (wallet as _sw_wallet, "
               "key_path as _sw_keypath)")
BACKUP_SUFFIX = ".bak-identity-20260912"


def needs_import(s):
    """True if `s` USES the resolver without importing it.

    Must be evaluated on the REWRITTEN text but keyed on the actual import
    statement — checking for the mere presence of '_sw_wallet' is wrong, since
    a successful rewrite puts that name in the file itself and would then look
    'already imported'.
    """
    uses = "_sw_wallet()" in s or "_sw_keypath()" in s
    has_import = "from steward_identity import" in s
    return uses and not has_import


def inject_import(s):
    """Insert the import after the last top-level import, else after docstring."""
    lines = s.split("\n")
    last_import = None
    for i, ln in enumerate(lines):
        if re.match(r"^(import |from )\S", ln):
            last_import = i
    if last_import is not None:
        lines.insert(last_import + 1, IMPORT_LINE)
        return "\n".join(lines)
    # no imports: place after shebang/docstring
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if lines[insert_at:insert_at + 1] and lines[insert_at].lstrip().startswith(('"""', "'''")):
        q = lines[insert_at].lstrip()[:3]
        if lines[insert_at].count(q) >= 2:
            insert_at += 1
        else:
            for j in range(insert_at + 1, len(lines)):
                if q in lines[j]:
                    insert_at = j + 1
                    break
    lines.insert(insert_at, "")
    lines.insert(insert_at + 1, IMPORT_LINE)
    return "\n".join(lines)


def rewrite(s):
    """Replace identity literals with resolver calls."""
    out = s
    for w in WALLET_LITERALS:
        out = re.sub(r'(["\'])' + re.escape(w) + r'\1', "_sw_wallet()", out)
    for k in KEY_PATH_LITERALS:
        out = out.replace(f'"{k}"', "_sw_keypath()").replace(f"'{k}'", "_sw_keypath()")
    return out


def already_migrated(s):
    return "_sw_wallet()" in s or "_sw_keypath()" in s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--dir", default=str(HERE))
    args = ap.parse_args()

    root = pathlib.Path(args.dir)
    files = sorted(p for p in root.glob("*.py")
                   if p.name not in {"migrate_identity.py", "steward_identity.py"})

    todo, skipped, failed = [], [], []
    for p in files:
        try:
            s = p.read_text()
        except Exception:
            continue
        if not any(w in s for w in WALLET_LITERALS) and \
           not any(k in s for k in KEY_PATH_LITERALS):
            continue
        if already_migrated(s):
            skipped.append((p.name, "already migrated"))
            continue
        new = rewrite(s)
        if needs_import(new):
            new = inject_import(new)
        try:
            ast.parse(new)
        except SyntaxError as e:
            failed.append((p.name, f"SyntaxError {e.lineno}: {e.msg}"))
            continue
        todo.append((p, new))

    print(f"=== IDENTITY MIGRATION — {len(todo)} to rewrite, "
          f"{len(skipped)} already done, {len(failed)} unusable ===")
    for name, why in failed:
        print(f"  ⚠️  skipped {name}: {why}")
    for name, why in skipped[:5]:
        print(f"  · {name}: {why}")
    for p, _ in todo:
        print(f"  → {p.name}")

    if not args.execute:
        print("\n[dry-run] re-run with --execute to write.")
        return 0

    done = 0
    for p, new in todo:
        shutil.copy2(p, str(p) + BACKUP_SUFFIX)
        p.write_text(new)
        written = p.read_text()
        try:
            ast.parse(written)
            # belt-and-braces: never leave a file using the resolver unimported
            if needs_import(written):
                raise SyntaxError("resolver used without import")
            done += 1
        except SyntaxError as e:
            shutil.copy2(str(p) + BACKUP_SUFFIX, p)
            print(f"  ❌ reverted {p.name} ({e})")
    print(f"\n✅ migrated {done}/{len(todo)} (backups: *{BACKUP_SUFFIX})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
