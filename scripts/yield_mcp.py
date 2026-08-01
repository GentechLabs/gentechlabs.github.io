#!/usr/bin/env python3
"""Yield.xyz MCP client — GTA yield intelligence layer.

Talks JSON-RPC (MCP streamable-HTTP) to https://mcp.yield.xyz/mcp.
No API key required. Read tools are currently free; write/action tools may
return an x402 PAYMENT-REQUIRED header — surfaced as YieldPaymentRequired.

Usage:
    python3 yield_mcp.py top --min-tvl 10000000 --limit 10
    python3 yield_mcp.py top --network base --type vault
    python3 yield_mcp.py risk <yield_id>
    python3 yield_mcp.py networks
"""
from __future__ import annotations

import argparse
import json
import logging
import urllib.error
import urllib.request
from typing import Any

ENDPOINT = "https://mcp.yield.xyz/mcp"
TIMEOUT = 30
MAX_ID_LEN = 200

log = logging.getLogger("yield_mcp")


class YieldMCPError(RuntimeError):
    """Transport or protocol failure talking to the Yield.xyz MCP server."""


class YieldPaymentRequired(YieldMCPError):
    """Server demanded x402 payment for this tool call."""


def _sanitize(value: str, limit: int = MAX_ID_LEN) -> str:
    """Bound length and strip newlines so untrusted ids can't forge logs."""
    return str(value)[:limit].replace("\n", "").replace("\r", "")


class YieldMCP:
    def __init__(self, endpoint: str = ENDPOINT, timeout: int = TIMEOUT) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._id = 0

    # ---- transport -------------------------------------------------
    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            payload["params"] = params
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode()
        except urllib.error.HTTPError as exc:
            if exc.code == 402:
                raise YieldPaymentRequired(
                    "Yield.xyz requires x402 payment for %s" % _sanitize(method, 64)
                ) from exc
            log.error("HTTP error calling %r", _sanitize(method, 64), exc_info=True)
            raise YieldMCPError("Yield.xyz MCP request failed") from exc
        except Exception as exc:  # network/timeout
            log.error("Transport error calling %r", _sanitize(method, 64), exc_info=True)
            raise YieldMCPError("Yield.xyz MCP request failed") from exc

        # streamable-HTTP may answer as SSE
        if raw.lstrip().startswith("event:") or raw.lstrip().startswith("data:"):
            for line in raw.splitlines():
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    break
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise YieldMCPError("Malformed JSON-RPC response") from exc
        if "error" in doc:
            raise YieldMCPError("MCP error: %s" % _sanitize(json.dumps(doc["error"]), 300))
        return doc.get("result", {})

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        result = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        for block in result.get("content", []):
            if block.get("type") == "text":
                text = block.get("text", "")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
        return result

    # ---- convenience ------------------------------------------------
    def list_tools(self) -> list[str]:
        return [t["name"] for t in self._rpc("tools/list").get("tools", [])]

    def networks(self) -> Any:
        return self.call_tool("networks_get_all")

    def yields(
        self,
        networks: list[str] | None = None,
        types: list[str] | None = None,
        providers: list[str] | None = None,
        token: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "rewardRateDesc",
    ) -> list[dict[str, Any]]:
        """Server-side filtered opportunity list (yields_get_all schema)."""
        args: dict[str, Any] = {"limit": max(1, min(limit, 200)), "offset": offset, "sort": sort}
        if networks:
            args["networks"] = [_sanitize(n, 40) for n in networks]
        if types:
            args["types"] = [_sanitize(t, 40) for t in types]
        if providers:
            args["providers"] = [_sanitize(p, 40) for p in providers]
        if token:
            args["token"] = _sanitize(token, 64)
        if search:
            args["search"] = _sanitize(search, 120)
        data = self.call_tool("yields_get_all", args)
        return data.get("items", []) if isinstance(data, dict) else []

    def risk(self, yield_id: str) -> Any:
        return self.call_tool("yields_get_risk", {"yieldId": _sanitize(yield_id)})

    def tvl_history(self, yield_id: str) -> Any:
        return self.call_tool("yields_get_tvl_history", {"yieldId": _sanitize(yield_id)})


def rank(items: list[dict], min_tvl: float = 0.0, min_apy: float = 0.0) -> list[dict]:
    """Filter + sort opportunities by reward rate, skipping unhealthy ones."""
    out = []
    for it in items:
        if it.get("deprecated") or it.get("underMaintenance"):
            continue
        if not (it.get("status") or {}).get("enter", False):
            continue
        try:
            tvl = float(it.get("tvlUsd") or 0)
            apy = float(it.get("rewardRate") or 0)
        except (TypeError, ValueError):
            continue
        if tvl < min_tvl or apy < min_apy:
            continue
        out.append(it)
    return sorted(out, key=lambda x: float(x.get("rewardRate") or 0), reverse=True)


def _fmt(items: list[dict]) -> str:
    lines = []
    for it in items:
        apy = float(it.get("rewardRate") or 0) * 100
        tvl = float(it.get("tvlUsd") or 0)
        lines.append(
            f"{apy:6.2f}%  ${tvl/1e6:9.2f}M  {it.get('network',''):<10} "
            f"{it.get('tokenSymbol',''):<8} {it.get('providerId',''):<12} "
            f"{it.get('type','')}"
        )
    return "\n".join(lines) or "(no matches)"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Yield.xyz MCP client")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("top")
    t.add_argument("--network")
    t.add_argument("--type", dest="ytype")
    t.add_argument("--token")
    t.add_argument("--limit", type=int, default=20)
    t.add_argument("--min-tvl", type=float, default=0.0)
    t.add_argument("--min-apy", type=float, default=0.0)
    r = sub.add_parser("risk")
    r.add_argument("yield_id")
    sub.add_parser("networks")
    sub.add_parser("tools")
    a = p.parse_args()

    c = YieldMCP()
    try:
        if a.cmd == "tools":
            print("\n".join(c.list_tools()))
        elif a.cmd == "networks":
            print(json.dumps(c.networks(), indent=2)[:4000])
        elif a.cmd == "risk":
            print(json.dumps(c.risk(a.yield_id), indent=2)[:4000])
        else:
            items = c.yields(
                networks=[a.network] if a.network else None,
                types=[a.ytype] if a.ytype else None,
                token=a.token,
                limit=max(a.limit, 50),
            )
            print(_fmt(rank(items, a.min_tvl, a.min_apy)[: a.limit]))
    except YieldMCPError as exc:
        log.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
