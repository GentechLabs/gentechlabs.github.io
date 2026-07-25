#!/usr/bin/env python3
"""
Unity Agent — Agent-friendly wrapper for Unity CLI.
Maps Unity CLI commands to structured JSON that agents can pipe into decision loops.

Usage:
    python unity-agent.py install 6000.2.10f1
    python unity-agent.py editors
    python unity-agent.py eval "return Application.version;"
    python unity-agent.py command scan-scene --verbose
    python unity-agent.py pipeline install --project path/to/project
    python unity-agent.py doctor
"""

import json
import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def find_unity():
    """Find the unity CLI binary."""
    unity = shutil.which("unity")
    if unity:
        return unity
    # Common Windows paths
    for p in [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Unity" / "cli" / "unity.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Unity" / "cli" / "unity.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Unity" / "cli" / "unity.exe",
    ]:
        if p.exists():
            return str(p)
    return None


def run_unity(args, timeout=120):
    """Run a unity CLI command and return structured result."""
    unity = find_unity()
    if not unity:
        return {"error": "Unity CLI not found. Install: see SKILL.md for instructions.", "found": False}

    cmd = [unity] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        # Try to parse as JSON if requested
        parsed = None
        if "--format json" in " ".join(args) or "-f json" in " ".join(args):
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError:
                pass

        return {
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "stdout": output,
            "stderr": error,
            "parsed_json": parsed,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s", "command": " ".join(cmd)}
    except FileNotFoundError:
        return {"error": "Unity CLI binary not executable", "command": " ".join(cmd)}


def main():
    parser = argparse.ArgumentParser(description="Unity Agent — Agent-friendly Unity CLI wrapper")
    parser.add_argument("action", nargs="?", help="Action: install, editors, eval, command, pipeline, doctor, modules, open, help")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments passed to unity CLI")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--timeout", type=int, default=120, help="Command timeout in seconds")
    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    # Build unity CLI arguments
    unity_args = []
    action = args.action

    if action == "help":
        unity_args = ["--help"]
    elif action == "editors":
        unity_args = ["editors", "--format", "json"]
    elif action == "doctor":
        unity_args = ["doctor"]
    elif action == "install":
        # unity install <version> [--modules ...]
        unity_args = ["install"] + args.args
        if "--accept-eula" not in unity_args:
            unity_args.append("--accept-eula")
        if "--yes" not in unity_args:
            unity_args.append("--yes")
    elif action == "eval":
        # unity command eval "<expression>"
        expr = " ".join(args.args) if args.args else ""
        if not expr:
            # Read from stdin
            expr = sys.stdin.read().strip()
        unity_args = ["command", "eval", expr, "--format", "json"]
    elif action == "command":
        # unity command <name> [--args...]
        unity_args = ["command"] + args.args
    elif action == "pipeline":
        # unity pipeline <subcommand> [--args...]
        unity_args = ["pipeline"] + args.args
    elif action == "modules":
        # unity modules <subcommand> [--args...]
        unity_args = ["modules"] + args.args
    elif action == "open":
        # unity open <project-path>
        unity_args = ["open"] + args.args
    else:
        # Pass through unknown actions
        unity_args = [action] + args.args

    result = run_unity(unity_args, timeout=args.timeout)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)
        if not result["success"]:
            print(f"⚠️  Command exited with code {result['exit_code']}")
        if result["stdout"]:
            print(result["stdout"])
        if result["stderr"]:
            print(f"stderr: {result['stderr']}", file=sys.stderr)

    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
