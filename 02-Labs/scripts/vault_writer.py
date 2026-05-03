#!/usr/bin/env python3
"""Gentech Vault Atomic Writer — shared brain access utility."""

import os
import fcntl
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

VAULT_ROOT = Path(os.getenv("GENTECH_VAULT", "/root/vaults/gentech"))
LOCK_DIR = VAULT_ROOT / ".locks"
LOCK_DIR.mkdir(parents=True, exist_ok=True)

class VaultLock:
    """File-based lock for atomic vault writes."""

    def __init__(self, lock_name: str, timeout: int = 30):
        self.lockfile = LOCK_DIR / f"{lock_name}.lock"
        self.timeout = timeout
        self.fd = None

    def __enter__(self):
        start = time.time()
        while True:
            try:
                self.fd = self.lockfile.open("w")
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.fd.write(str(os.getpid()))
                self.fd.flush()
                return self
            except (IOError, BlockingIOError):
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"Could not acquire lock: {self.lockfile}")
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.fd.close()
            self.lockfile.unlink(missing_ok=True)


def vault_write(
    rel_path: str,
    content: str,
    author: str = "DMOB",
    group: str = "Labs",
    metadata: Optional[Dict[str, Any]] = None,
    mode: str = "append",  # append | overwrite
) -> Dict[str, Any]:
    """
    Atomically write to vault with audit trail.

    Args:
        rel_path: Path relative to vault root (e.g., '02-Labs/decisions.md')
        content: Markdown content to write
        author: Who/what is writing
        group: Group tag for lock namespacing
        metadata: Optional frontmatter fields
        mode: 'append' adds new entry, 'overwrite' replaces file

    Returns:
        Status dict with path, timestamp, bytes_written
    """
    abs_path = VAULT_ROOT / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)

    lock_name = f"{group}-{abs_path.name.split('.')[0]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    header = ""
    if metadata:
        header += "---\n"
        for k, v in metadata.items():
            header += f"{k}: {v}\n"
        header += "---\n\n"

    entry = f"""## {timestamp} — {author}

{content}

---\n"""

    with VaultLock(lock_name):
        if mode == "append" and abs_path.exists():
            existing = abs_path.read_text()
            # Avoid duplicate timestamps
            if timestamp not in existing:
                new_content = existing + "\n" + entry
            else:
                new_content = existing
        else:
            new_content = header + entry

        abs_path.write_text(new_content)

    return {
        "status": "ok",
        "path": str(abs_path.relative_to(VAULT_ROOT)),
        "timestamp": timestamp,
        "bytes_written": len(new_content),
        "mode": mode,
    }


def vault_read(rel_path: str, tail: int = 0) -> Dict[str, Any]:
    """
    Read vault file with optional tail (last N entries).

    Args:
        rel_path: Path relative to vault root
        tail: If > 0, return only last N entries (by '---' delimiter)

    Returns:
        Dict with content, line_count, entry_count
    """
    abs_path = VAULT_ROOT / rel_path
    if not abs_path.exists():
        return {"status": "not_found", "path": rel_path, "content": ""}

    content = abs_path.read_text()
    lines = content.splitlines()
    entries = [e for e in content.split("---\n") if e.strip()]

    result = {
        "status": "ok",
        "path": rel_path,
        "content": content,
        "line_count": len(lines),
        "entry_count": len(entries),
    }

    if tail > 0:
        result["tail_content"] = "---\n".join(entries[-tail:])
        result["tail_entries"] = min(tail, len(entries))

    return result


def vault_search(
    pattern: str,
    group: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Search vault files for a pattern (case-insensitive substring)."""
    matches = []
    root = VAULT_ROOT / (group or "")

    for filepath in root.rglob("*.md"):
        try:
            text = filepath.read_text()
            rel = str(filepath.relative_to(VAULT_ROOT))
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.lower() in line.lower():
                    matches.append({
                        "file": rel,
                        "line": i,
                        "context": line.strip(),
                    })
                    if len(matches) >= limit:
                        break
        except Exception:
            continue

    return {"status": "ok", "query": pattern, "matches": matches, "count": len(matches)}


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Gentech Vault Atomic Writer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Write
    w = sub.add_parser("write", help="Write to vault")
    w.add_argument("path")
    w.add_argument("--content", "-c", required=True)
    w.add_argument("--author", default="DMOB")
    w.add_argument("--group", default="Labs")
    w.add_argument("--mode", choices=["append", "overwrite"], default="append")

    # Read
    r = sub.add_parser("read", help="Read from vault")
    r.add_argument("path")
    r.add_argument("--tail", type=int, default=0)

    # Search
    s = sub.add_parser("search", help="Search vault")
    s.add_argument("pattern")
    s.add_argument("--group")
    s.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()

    try:
        if args.cmd == "write":
            meta = {"author": args.author, "group": args.group}
            result = vault_write(args.path, args.content, args.author, args.group, meta, args.mode)
            print(json.dumps(result, indent=2))
        elif args.cmd == "read":
            result = vault_read(args.path, args.tail)
            print(json.dumps(result, indent=2))
        elif args.cmd == "search":
            result = vault_search(args.pattern, args.group, args.limit)
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)
