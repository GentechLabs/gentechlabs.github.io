"""
Claim Evaluator — MCP registration + CLI demo.

Implements the Agent Kit tool shape:
    claim_evaluator.evaluate(claim, asset?)

and a small MCP server registration so the evaluator can be wired into the
kit server (spec A2). Run as a standalone demo with:

    python3 demo.py                          # BTC "crypto bottom is in"
    python3 demo.py "ETH breakout" ETH       # custom claim + asset

The MCP handler is intentionally thin: it parses args, calls evaluate(),
and returns the verdict JSON. It registers on the MCP tool surface used by
the agent kit (FastMCP-style). If the `mcp` package is not installed the
demo still runs — MCP registration is optional and guarded.
"""
import json
import sys
from typing import Any, Dict, Optional

from claim_evaluator import ClaimEvaluator

# ── Tool shape (agent-kit convention) ──────────────────────────────────

TOOL_NAME = "claim_evaluator.evaluate"


def evaluate_tool(claim: str, asset: Optional[str] = None) -> Dict[str, Any]:
    """MCP tool entrypoint: evaluate a market claim against kit layers."""
    ev = ClaimEvaluator()
    return ev.evaluate(claim, asset)


# ── Optional MCP registration (guarded) ────────────────────────────────

def register_mcp(server: Any = None) -> Any:
    """Attach the tool to an MCP server if one is provided.

    Works with any FastMCP-style server exposing `tool()` or `Tool()`.
    Returns the server unchanged. Never raises on missing MCP support.
    """
    if server is None:
        return server
    try:
        # FastMCP style: server.tool() decorator
        if hasattr(server, "tool"):

            @server.tool()
            def claim_evaluator_evaluate(
                claim: str,
                asset: Optional[str] = None,
            ) -> str:
                """Evaluate a market claim against the kit's data layers.

                Args:
                    claim: the directional market claim (e.g. "bottom is in").
                    asset: optional asset symbol (e.g. "BTC").
                Returns:
                    JSON verdict string with .verdict / .action / .layers.
                """
                return json.dumps(evaluate_tool(claim, asset))
            return server
    except Exception:
        # MCP optional — never break the import path without it.
        pass
    return server


# ── CLI demo ───────────────────────────────────────────────────────────

def main() -> None:
    claim = sys.argv[1] if len(sys.argv) > 1 else "crypto bottom is in"
    asset = sys.argv[2] if len(sys.argv) > 2 else "BTC"
    print(f"CLAIM: {claim!r}  |  ASSET: {asset}")
    print("-" * 60)
    result = evaluate_tool(claim, asset)
    print(json.dumps(result, indent=2, default=str))
    # Human-readable verdict line
    verdict = result.get("verdict")
    action = result.get("action")
    conf = result.get("confidence")
    print("-" * 60)
    print(f"=> VERDICT: {verdict}  |  ACTION: {action}  |  CONF: {conf}")


if __name__ == "__main__":
    main()
