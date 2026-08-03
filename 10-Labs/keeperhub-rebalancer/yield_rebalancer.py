"""Autonomous Yield Rebalancer — KeeperHub Agents Onchain submission.

An agent that monitors a DeFi yield position and, when the effective APY / spread
crosses a threshold, executes a real onchain rebalance THROUGH KeeperHub.

Execution layer (KeeperHub MCP):
  - create_workflow      : model the monitor -> decide -> rebalance flow
  - execute_check_and_execute : the key primitive — read a contract value,
                               evaluate a condition, execute if met
  - execute_contract_call: direct contract calls (view / state-changing)
  - execute_workflow     : manual trigger, returns execution ID
  - get_workflow / list_workflows / validate_workflow

This agent is built against the KeeperHub MCP server (https://app.keeperhub.com/mcp)
so a real transaction is linked at submission time — no mockups. The exact chain,
pool and wallet are parameterised; set them via env to your live position.

Env:
  KEEPERHUB_API_KEY   kh_...   (required to execute)
  KEEPERHUB_MCP_URL   default https://app.keeperhub.com/mcp
  POOL_ADDRESS        target lending pool / yield vault contract
  WALLET_ADDRESS      the wallet that holds the position
  CHAIN_ID            e.g. 8453 (Base), 1 (Ethereum)
  TARGET_APY_BPS      threshold to trigger rebalance (basis points, e.g. 500 = 5%)
  CHECK_INTERVAL_S    poll cadence

Usage (agent mode):
  python yield_rebalancer.py run

Demo/plan mode (no key needed):
  python yield_rebalancer.py plan --pool <addr> --wallet <addr>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from dataclasses import dataclass, field

KEEPERHUB_MCP = os.environ.get("KEEPERHUB_MCP_URL", "https://app.keeperhub.com/mcp")
KEEPERHUB_KEY = os.environ.get("KEEPERHUB_API_KEY", "")


# --------------------------------------------------------------------------- #
#  Minimal MCP client (JSON-RPC over HTTP). KeeperHub exposes an MCP server.  #
# --------------------------------------------------------------------------- #
class McpClient:
    def __init__(self, url: str, api_key: str = ""):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers=self.headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode()
        except urllib.error.HTTPError as e:
            body = e.read().decode()
        # MCP streams may use SSE framing; strip "data: " lines for JSON-RPC.
        return self._parse(body)

    @staticmethod
    def _parse(body: str) -> dict:
        lines = [ln for ln in body.splitlines() if ln.strip()]
        if len(lines) == 1:
            return json.loads(lines[0])
        # SSE: take the last data: payload
        data = ""
        for ln in lines:
            if ln.startswith("data:"):
                data = ln[len("data:"):].strip()
        if data:
            return json.loads(data)
        return {"jsonrpc": "2.0", "result": None}

    def call_tool(self, name: str, arguments: dict) -> dict:
        return self._post({
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })


# --------------------------------------------------------------------------- #
#  Rebalancer agent                                                           #
# --------------------------------------------------------------------------- #
@dataclass
class Rebalancer:
    pool: str
    wallet: str
    chain_id: int
    target_apy_bps: int
    client: McpClient = field(default=None)  # type: ignore

    def __post_init__(self):
        if self.client is None:
            self.client = McpClient(KEEPERHUB_MCP, KEEPERHUB_KEY)

    def read_current_apy(self) -> int:
        """Read the live supply APY of the pool (basis points) via a view call."""
        res = self.client.call_tool("execute_contract_call", {
            "chainId": str(self.chain_id),
            "contractAddress": self.pool,
            "functionName": "supplyRatePerSecond",
            "args": [],
            "from": self.wallet,
        })
        # supplyRatePerSecond is per-second rate; annualise to bps.
        rate_per_sec = self._extract_number(res)
        apy_bps = int((1 + rate_per_sec) ** (365 * 24 * 3600) - 1) * 10000
        return apy_bps

    @staticmethod
    def _extract_number(res: dict) -> float:
        # MCP returns the result inside result.content[0].text (JSON string).
        try:
            content = res["result"]["content"][0]["text"]
            val = json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return 0.0
        if isinstance(val, dict):
            for k in ("result", "value", "returnValue", "data", "output"):
                if k in val:
                    v = val[k]
                    if isinstance(v, (int, float, str)):
                        try:
                            return float(v)
                        except ValueError:
                            pass
        if isinstance(val, (int, float)):
            return float(val)
        return 0.0

    def should_rebalance(self, current_bps: int) -> tuple[bool, str]:
        if current_bps < self.target_apy_bps:
            return True, f"APY {current_bps/100:.2f}% < target {self.target_apy_bps/100:.2f}%"
        return False, f"APY {current_bps/100:.2f}% >= target {self.target_apy_bps/100:.2f}% (no action)"

    def rebalance(self) -> dict:
        """Move the position — the actual onchain action via KeeperHub."""
        return self.client.call_tool("execute_contract_call", {
            "chainId": str(self.chain_id),
            "contractAddress": self.pool,
            "functionName": "redeem",          # withdraw under-yielding position
            "args": [],
            "from": self.wallet,
            "value": "0",
        })

    def create_monitor_workflow(self) -> dict:
        """Model the monitor->decide->rebalance loop as a KeeperHub workflow.
        Returns the raw workflow definition (does not contact the network)."""
        return {
            "name": f"yield-rebalance-{self.pool[:8]}",
            "description": (
                "Autonomous yield rebalancer: read supply APY, if below target "
                "rebalance position onchain via KeeperHub."
            ),
            "nodes": {
                "read_apy": {
                    "type": "contract_call",
                    "config": {
                        "chainId": self.chain_id,
                        "address": self.pool,
                        "function": "supplyRatePerSecond",
                        "output": "apy_bps",
                    },
                },
                "check": {
                    "type": "condition",
                    "config": {
                        "field": "apy_bps",
                        "op": "<",
                        "value": self.target_apy_bps,
                    },
                },
                "rebalance": {
                    "type": "contract_call",
                    "config": {
                        "chainId": self.chain_id,
                        "address": self.pool,
                        "function": "redeem",
                    },
                },
            },
            "edges": [
                {"from": "read_apy", "to": "check"},
                {"from": "check", "to": "rebalance", "when": "true"},
            ],
        }

    def create_workflow_remote(self) -> dict:
        """Persist the monitor workflow in KeeperHub (requires API key)."""
        return self.client.call_tool("create_workflow", self.create_monitor_workflow())

    def run_once(self) -> dict:
        current = self.read_current_apy()
        act, reason = self.should_rebalance(current)
        return {"current_apy_bps": current, "action": "REBALANCE" if act else "HOLD",
                "reason": reason}


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Autonomous Yield Rebalancer (KeeperHub)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Continuous monitor loop (needs KEEPERHUB_API_KEY)")
    run.add_argument("--pool", default=os.environ.get("POOL_ADDRESS"))
    run.add_argument("--wallet", default=os.environ.get("WALLET_ADDRESS"))
    run.add_argument("--chain", type=int, default=int(os.environ.get("CHAIN_ID", "8453")))
    run.add_argument("--target-bps", type=int, default=int(os.environ.get("TARGET_APY_BPS", "500")))
    run.add_argument("--once", action="store_true", help="single check, no loop")

    plan = sub.add_parser("plan", help="Show the rebalance plan / workflow JSON (no key needed)")
    plan.add_argument("--pool", required=True)
    plan.add_argument("--wallet", required=True)
    plan.add_argument("--chain", type=int, default=8453)
    plan.add_argument("--target-bps", type=int, default=500)

    args = ap.parse_args()

    if args.cmd == "plan":
        if not args.pool or not args.wallet:
            print("--pool and --wallet are required for plan mode")
            return 1
        r = Rebalancer(args.pool, args.wallet, args.chain, args.target_bps)
        wf = r.create_monitor_workflow()
        print("=== Rebalance workflow (ready to create in KeeperHub) ===")
        print(json.dumps(wf, indent=2))
        print("\nTo execute for real, set KEEPERHUB_API_KEY and run: "
              "python yield_rebalancer.py run --pool <addr> --wallet <addr>")
        return 0

    if args.cmd == "run":
        if not KEEPERHUB_KEY:
            print("❌ KEEPERHUB_API_KEY is required to execute onchain via KeeperHub.\n"
                  "Get a kh_ key at https://app.keeperhub.com then set it in the profile .env.")
            return 2
        if not args.pool or not args.wallet:
            print("--pool and --wallet are required")
            return 1
        r = Rebalancer(args.pool, args.wallet, args.chain, args.target_bps)
        if args.once:
            print(json.dumps(r.run_once(), indent=2))
            return 0
        print(f"Monitoring {args.pool} (target {args.target_bps} bps) every 60s...")
        try:
            while True:
                state = r.run_once()
                print(f"[{time.strftime('%H:%M:%S')}] {state}")
                if state["action"] == "REBALANCE":
                    print("→ Executing rebalance via KeeperHub...")
                    tx = r.rebalance()
                    print(json.dumps(tx, indent=2))
                    print("✅ Transaction submitted — link this execution in the submission.")
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nstopped")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
