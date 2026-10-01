#!/usr/bin/env python3
"""
case-collisions.py — find paths that differ ONLY by letter case, and say whether they are SAFE.

WHY THIS EXISTS
  Obsidian Sync is case-insensitive on some clients and not others: on Jordan's macOS/Windows
  clients only ONE of two case-variant paths appears, and WHICH one is not deterministic. So a
  case collision is not merely untidy — the vault can render differently on two machines, and a
  client that clobbers one path with the other loses whatever was in the loser.

  Found 2026-09-28: HQ found the pair in Treasury/ by hand. It was missed by a first-pass scan
  because **that scan's unit was the FILE PATH** — so a collision between two DIRECTORY names
  (`Games/` vs `games/`) was invisible to it, even though both were tracked. This checks BOTH
  levels, because "the unit of the check decides what the check can see."

WHAT IT REPORTS
  Two classes, and the distinction is the whole point:
    - IDENTICAL  same content (md5) -> a DUPLICATE. Safe to dedupe; a clobber loses nothing.
    - DIFFERING  content differs      -> a RISK. A case-insensitive client silently loses one.
  Only DIFFERING is an alarm; IDENTICAL is housekeeping. Reporting them as one list is how a
  harmless duplicate gets triaged as an emergency, and how a real risk gets triaged as tidy-up.

SELF-REPORTING (the rule: the instrument must print its window)
  It prints the repo, the tracked-file count, and the number of distinct directories examined,
  every run — so a reader can see what it actually looked at rather than what it was asked about.

EXIT
  0  no collisions, or only IDENTICAL ones
  1  at least one DIFFERING collision (the alarm path — a client will lose data)

Usage: case-collisions.py [--json] [--repo PATH]
"""

import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys


def git_files(repo):
    p = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True, text=True)
    return [f for f in p.stdout.split("\0") if f]


def md5(repo, rel):
    h = hashlib.md5()
    try:
        with open(os.path.join(repo, rel), "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None          # unreadable: NOT the same as identical


def unexamined(repo):
    """Count the paths git will NOT hand us, and check tracked STUBS for misleading pointers.

    Added 2026-09-28 after HQ found the false-completeness: this scanner reads `git ls-files`, so an
    IGNORED directory is structurally invisible to it — `Gaming/` is 24 entries and 580K, gitignored,
    and appears in NO collision the tool can see. Two additions, both from their note:

      1. A window line for the half of the window NOT covered. One number, and it kills the
         false-completeness for every future case rather than for this one.
      2. A STUB-REDIRECT check, because the harm is not the missing collision — it is a reader
         following a pointer. `Games/.redirect.md` says "Contents moved to `Gaming/`", and the trap is
         that a case-insensitive resolver merges Games -> games and never reaches the target.

    SCOPING, and the first draft got this wrong in a way worth keeping: a loose version (any file
    containing "deprecated", any backticked token) produced **287 findings, almost all noise** prose
    like `pip install almanak`. A false alarm is worse than no check — it spends the trust the real
    finding needs. So a STUB is strictly defined: tiny, and its content is *only* a pointer.
        - size < 512 bytes                 (a redirect is a stub; a document is not)
        - a redirect PHRASE in the first 400 chars
        - the target is a SINGLE TOKEN naming a bare folder (no spaces, no slashes, no prose)
    """
    import re
    REDIRECT_PHRASES = ("moved to", "do not add", "no longer", "superseded by")
    # NOTE the optional trailing slash INSIDE the backticks: the real redirect reads
    # "Contents moved to `Gaming/`" — a pattern without `/?` matches nothing at all and the
    # check silently reports zero findings, which looks identical to a clean vault.
    TOKEN = re.compile(r"`([A-Za-z0-9][A-Za-z0-9._-]{0,48})/?`")

    out = {"ignored_dirs": 0, "untracked_dirs": 0, "stubs_examined": 0,
           "stubs_phrase_only": [], "stale_redirections": [], "resolved": []}
    for args, key in ((("--others", "--ignored", "--exclude-standard", "--directory"), "ignored_dirs"),
                      (("--others", "--exclude-standard", "--directory"), "untracked_dirs")):
        p = subprocess.run(["git", "ls-files", *args], cwd=repo, capture_output=True, text=True)
        out[key] = len([x for x in p.stdout.split("\n") if x.strip().endswith("/")])

    for f in git_files(repo):
        if not f.lower().endswith((".md", ".txt")):
            continue
        full = os.path.join(repo, f)
        try:
            if os.path.getsize(full) > 512:          # a redirect is a stub by definition
                continue
            text = open(full, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        head = text[:400].lower()
        if not any(ph in head for ph in REDIRECT_PHRASES):
            continue
        # a stub's body must be a pointer, not a discussion: very few words outside the pointer
        words = len([w for w in re.findall(r"[A-Za-z]{3,}", text)])
        if words > 40:
            continue
        # A "stub" with NO resolvable token is not a pointer at all. Counting it as examined
        # inflated the denominator and made the clean result harder to account for (HQ flagged the
        # 4-vs-3 discrepancy). Count only stubs that actually carry a checkable target.
        targets = [t.strip() for t in TOKEN.findall(text)]
        targets = [t for t in targets if t and not t.startswith(".")
                   and t.lower() not in ("true", "false", "none", "null")]
        if not targets:
            out["stubs_phrase_only"].append(f)      # phrase matched, but nothing to resolve
            continue
        out["stubs_examined"] += 1

        for t in targets:
            cand = os.path.join(repo, t)

            # ---- TWO SCOPES, because "resolves" is a question about a filesystem ----
            # The whole thread is about an OFF-BOX reader, and git cannot see inside an IGNORED
            # directory. `Gaming/` is on disk (24 entries, 580K) and 0 TRACKED, so a fresh clone
            # following this stub lands on NOTHING. Reporting one verdict hid that (HQ, 2026-09-28).
            on_disk = os.path.isdir(cand) and sum(len(fn) for _, _, fn in os.walk(cand)) > 0
            # in a clone == does git track ANY file beneath the target?
            p = subprocess.run(["git", "ls-files", "--", f"{t}/"], cwd=repo,
                               capture_output=True, text=True)
            in_clone = bool(p.stdout.strip())

            sib = [d for d in os.listdir(repo)
                   if os.path.isdir(os.path.join(repo, d)) and d != t and d.lower() == t.lower()]

            rec = {"file": f, "target": t, "on_disk": on_disk, "in_clone": in_clone}
            verdicts = []
            if not on_disk:
                verdicts.append("does NOT resolve on disk")
            if not in_clone:
                verdicts.append("does NOT resolve in a CLONE (target has no tracked files)")
            if sib:
                verdicts.append(f"case-sibling {sib} exists — a case-insensitive resolver would "
                                f"follow the WRONG one")
            if verdicts:
                rec["why"] = "; ".join(verdicts)
                out["stale_redirections"].append(rec)
            else:
                out["resolved"].append(rec)
    return out


def scan(repo):
    files = git_files(repo)

    # ---- level 1: file paths ---------------------------------------------------------
    by_lower = collections.defaultdict(list)
    for f in files:
        by_lower[f.lower()].append(f)
    file_coll = {k: v for k, v in by_lower.items() if len(v) > 1}

    # ---- level 2: DIRECTORY paths (the level a file-path scan cannot see) ------------
    dirs = set()
    for f in files:
        parts = f.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    dlow = collections.defaultdict(list)
    for d in dirs:
        dlow[d.lower()].append(d)
    dir_coll = {k: v for k, v in dlow.items() if len(v) > 1}

    def classify(paths, is_dir):
        if is_dir:
            # for directories, compare their contents wholesale
            def sig(d):
                hs = sorted(md5(repo, f) or "?" for f in files if f.startswith(d + "/"))
                return hashlib.md5("|".join(hs).encode()).hexdigest()
            sigs = {d: sig(d) for d in paths}
            verdict = "IDENTICAL" if len(set(sigs.values())) == 1 else "DIFFERING"
            return verdict, {d: (sigs[d] or "")[:12] for d in paths}
        sigs = {p: (md5(repo, p) or "") for p in paths}
        readable = [v for v in sigs.values() if v]
        verdict = "IDENTICAL" if len(sigs) == len(readable) and len(set(readable)) == 1 else "DIFFERING"
        return verdict, {p: (sigs[p] or "UNREADABLE")[:12] for p in paths}

    out = []
    for k, v in sorted(file_coll.items()):
        verdict, sigs = classify(v, is_dir=False)
        out.append({"level": "file", "key": k, "paths": v, "verdict": verdict, "md5": sigs})
    for k, v in sorted(dir_coll.items()):
        verdict, sigs = classify(v, is_dir=True)
        out.append({"level": "directory", "key": k, "paths": v, "verdict": verdict, "dirsig": sigs})

    return files, len(dirs), out


def main():
    ap = argparse.ArgumentParser(description="Find case-only path collisions; say if they are safe.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default="/root/vaults/gentech")
    a = ap.parse_args()

    files, ndirs, out = scan(a.repo)
    ux = unexamined(a.repo)
    differing = [c for c in out if c["verdict"] == "DIFFERING"]

    if a.json:
        print(json.dumps({"repo": a.repo, "tracked_files": len(files), "directories_examined": ndirs,
                          "collisions": out, "differing": len(differing),
                          "not_examined": ux}, indent=2))
    else:
        print(f"  === case-collision scan ===")
        print(f"  repo                 : {a.repo}")
        print(f"  WINDOW — tracked files examined   : {len(files)}")
        print(f"  WINDOW — directories examined     : {ndirs}   (file-path scans CANNOT see these)")
        print(f"  WINDOW — NOT examined             : {ux['ignored_dirs']} ignored dir(s), "
              f"{ux['untracked_dirs']} untracked dir(s)   <-- git ls-files cannot see inside these")
        print(f"  collisions found     : {len(out)}   (identical: {len(out)-len(differing)}, "
              f"DIFFERING: {len(differing)})")
        for c in out:
            flag = "⚠️  RISK" if c["verdict"] == "DIFFERING" else "safe"
            print(f"\n  [{c['level']}] {flag}  {c['key']}")
            for p in c["paths"]:
                print(f"      {p}")
            print(f"      -> {c['verdict']}: "
                  f"{'a clobber LOSES DATA — dedupe or rename' if c['verdict']=='DIFFERING' else 'a duplicate — nothing is lost, safe to dedupe'}")
        if not out:
            print("\n  ✅ no case collisions")

        # ---- redirects: TWO SCOPES, because a verdict about a pointer is scoped to a filesystem ----
        # count over ALL examined stubs, not just the ones that passed — a stub that FAILS one
        # scope can still pass the other, and that difference is the whole point of showing both.
        allrec = ux["resolved"] + ux["stale_redirections"]
        n_disk = sum(1 for r in allrec if r["on_disk"])
        n_clone = sum(1 for r in allrec if r["in_clone"])
        tot = len(allrec)
        print(f"\n  REDIRECT CHECK — {ux['stubs_examined']} stub(s) with a checkable target"
              + (f", {len(ux['stubs_phrase_only'])} phrase-only (no target to resolve)"
                 if ux["stubs_phrase_only"] else ""))
        if tot:
            print(f"      resolves on disk : {n_disk}/{tot}      <- the WORKING TREE")
            print(f"      resolves in a clone : {n_clone}/{tot}   <- the REPOSITORY (what an off-box reader gets)")
        for s in ux["stale_redirections"]:
            print(f"\n      ⚠️  {s['file']}")
            print(f"          -> `{s['target']}`")
            print(f"             {s['why']}")
        if not ux["stale_redirections"]:
            print(f"      ✅ every target resolves in BOTH scopes")

    return 1 if differing else 0


if __name__ == "__main__":
    sys.exit(main())
