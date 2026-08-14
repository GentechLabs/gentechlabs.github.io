"""MCP-style server entrypoint for the agentic memory layer.

Exposes the memory store as MCP tools (memory_write, memory_search,
memory_recent, memory_consolidate, memory_forget, memory_stats) so any
MCP-capable agent (Claude Code, Cursor, etc.) can use CockroachDB as its
persistent memory. This mirrors the CockroachDB Cloud Managed MCP Server
pattern — agents connect over MCP, we back it with CockroachDB.

Run:  python -m src.mcp_server  (or via the mcp CLI)
"""
from __future__ import annotations

from . import db
from .memory import AgentMemory

_conn = None
_mem = None


def _get_mem(agent_id: str = "default-agent") -> AgentMemory:
    global _conn, _mem
    if _conn is None or _conn.closed:
        _conn = db.connect()
    if _mem is None or _mem.agent_id != agent_id:
        _mem = AgentMemory(_conn, agent_id)
    return _mem


def memory_write(memory_type: str, content: str, importance: float = 0.5, metadata: dict | None = None) -> str:
    return _get_mem().write(memory_type, content, importance, metadata)


def memory_search(query: str, memory_type: str | None = None, limit: int = 5) -> list[dict]:
    return _get_mem().search(query, memory_type, limit)


def memory_recent(memory_type: str | None = None, limit: int = 20) -> list[dict]:
    return _get_mem().recent(memory_type, limit)


def memory_consolidate(threshold_days: int = 7) -> int:
    return _get_mem().consolidate(threshold_days)


def memory_forget(memory_id: str) -> bool:
    return _get_mem().forget(memory_id)


def memory_stats() -> dict:
    return _get_mem().stats()


if __name__ == "__main__":
    # Minimal stdio MCP server (JSON-RPC over stdin/stdout).
    import sys

    def respond(obj: dict) -> None:
        sys.stdout.write(json_dumps(obj) + "\n")
        sys.stdout.flush()

    def json_dumps(o) -> str:
        import json
        return json.dumps(o)

    TOOLS = {
        "memory_write": memory_write,
        "memory_search": memory_search,
        "memory_recent": memory_recent,
        "memory_consolidate": memory_consolidate,
        "memory_forget": memory_forget,
        "memory_stats": memory_stats,
    }

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            import json
            req = json.loads(line)
            name = req.get("method", "")
            if name == "initialize":
                respond({"jsonrpc": "2.0", "id": req.get("id"),
                         "result": {"serverInfo": {"name": "gentech-agent-memory"},
                                    "capabilities": {"tools": {}}}})
            elif name == "tools/list":
                respond({"jsonrpc": "2.0", "id": req.get("id"),
                         "result": {"tools": [{"name": t, "description": t} for t in TOOLS]}})
            elif name == "tools/call":
                params = req.get("params", {})
                tool = params.get("name")
                args = params.get("arguments", {})
                if tool in TOOLS:
                    result = TOOLS[tool](**args)
                    respond({"jsonrpc": "2.0", "id": req.get("id"),
                             "result": {"content": [{"type": "text", "text": str(result)}]}})
                else:
                    respond({"jsonrpc": "2.0", "id": req.get("id"),
                             "error": {"code": -32601, "message": f"unknown tool {tool}"}})
            else:
                respond({"jsonrpc": "2.0", "id": req.get("id"),
                         "error": {"code": -32601, "message": f"unknown method {name}"}})
        except Exception as exc:  # noqa: BLE001
            respond({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}})
