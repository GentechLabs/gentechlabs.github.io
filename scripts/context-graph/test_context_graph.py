#!/usr/bin/env python3
"""
test_context_graph.py — tests for the repo-context graph toolkit (repo_map.py,
repo_map_check.py, blast_radius.py).

Builds a tiny throwaway fixture repo, runs the full pipeline, and asserts the
three borrowed Graft primitives behave. Pure stdlib. Run with `pytest` or
`python3 test_context_graph.py`.

USAGE:
    python3 test_context_graph.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_MAP = os.path.join(HERE, "repo_map.py")
REPO_MAP_CHECK = os.path.join(HERE, "repo_map_check.py")
BLAST = os.path.join(HERE, "blast_radius.py")


FIXTURE = {
    "main.py": '"""Entry point. Boots the app, calls worker.run()."""\nfrom worker import run\nfrom utils import parse\ndef main():\n    cfg = parse("x")\n    run(cfg)\n    return cfg\n',
    "worker.py": '"""Worker subsystem. Orchestrates jobs using utils."""\nfrom utils import parse\nimport secrets\ndef run(cfg):\n    tid = secrets.token_hex(16)\n    return tid\n',
    "utils.py": '"""Utils subsystem. Parsing + hashing helpers."""\nimport hashlib\nimport re\n_SAFE = re.compile(r"[A-Za-z0-9]+")\ndef parse(raw):\n    if not _SAFE.match(raw):\n        raise ValueError("bad")\n    return hashlib.sha256(raw.encode()).hexdigest()\n',
    "solo.py": '"""Standalone module, no siblings."""\ndef ping():\n    return "pong"\n',
    "web/index.js": 'import { boot } from "./app.js";\nexport function start() { boot(); }\n',
    "web/app.js": 'export function boot() { return "up"; }\n',
}


def _make_fixture():
    d = tempfile.mkdtemp(prefix="ctxgrtest-")
    for name, content in FIXTURE.items():
        path = os.path.join(d, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return d


def _run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def test_build_map():
    d = _make_fixture()
    try:
        r = _run([sys.executable, REPO_MAP, d], d)
        assert r.returncode == 0, r.stderr
        out = os.path.join(d, ".repo-map")
        assert os.path.exists(os.path.join(out, "repo-map.md"))
        assert os.path.exists(os.path.join(out, "graph.json"))
        assert os.path.exists(os.path.join(out, "fingerprint.json"))
        with open(os.path.join(out, "graph.json")) as f:
            g = json.load(f)
        # 6 files (4 py + 2 js), subsystems from top-level dirs + file stems
        assert len(g["files"]) == 6, g["files"]
        # worker depends on utils; utils depends on nothing in-repo
        assert "utils" in g["files"]["worker.py"]["depends_on"]
        assert g["files"]["utils.py"]["depends_on"] == []
        # JS same-dir import resolved
        assert "app" in g["files"]["web/index.js"]["depends_on"], g["files"]["web/index.js"]
        # used_by: utils is used by main + worker; app used by web/index
        assert "utils" in g["used_by"]
        assert set(g["used_by"]["utils"]) == {"main.py", "worker.py"}
        assert "web/app.js" in g["used_by"].get("app", []) or "app" in g["used_by"]
        # JS blast-radius resolves app → index
        r = _run([sys.executable, BLAST, d, "web/app.js"], d)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "web/index.js" in r.stdout
    finally:
        shutil.rmtree(d)


def test_staleness():
    d = _make_fixture()
    try:
        _run([sys.executable, REPO_MAP, d], d)
        # fresh
        r = _run([sys.executable, REPO_MAP_CHECK, d], d)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "FRESH" in r.stdout
        # drift
        with open(os.path.join(d, "utils.py"), "a") as f:
            f.write("\n# touched\n")
        r = _run([sys.executable, REPO_MAP_CHECK, d], d)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "DRIFTED" in r.stdout
        assert "utils.py" in r.stdout
        # auto-rebuild restores freshness
        r = _run([sys.executable, REPO_MAP_CHECK, d, "--rebuild"], d)
        assert r.returncode == 0, r.stdout + r.stderr
        r = _run([sys.executable, REPO_MAP_CHECK, d], d)
        assert r.returncode == 0
    finally:
        shutil.rmtree(d)


def test_blast_radius():
    d = _make_fixture()
    try:
        _run([sys.executable, REPO_MAP, d], d)
        # who depends on utils.py → main + worker
        r = _run([sys.executable, BLAST, d, "utils.py"], d)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "main.py" in r.stdout and "worker.py" in r.stdout
        # transitive closure from utils → includes main (via worker)
        r = _run([sys.executable, BLAST, d, "utils.py", "--transitive"], d)
        assert r.returncode == 0
        assert "main.py" in r.stdout
        # unknown target → exit 2
        r = _run([sys.executable, BLAST, d, "nope.py"], d)
        assert r.returncode == 2
    finally:
        shutil.rmtree(d)


if __name__ == "__main__":
    tests = [test_build_map, test_staleness, test_blast_radius]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(1 if fails else 0)
