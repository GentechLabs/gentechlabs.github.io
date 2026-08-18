#!/usr/bin/env python3
"""
Mastercard Innovation Challenge 2026 — LIVE STACK integration layer.

Turns the red/blue-team demo from SIMULATED into BACKED-BY-LIVE-TOOLING.

This module calls GenTech's real, deployed fraud/security services and
returns their actual output so the demo shows production data, not just
simulation:

  - RugCheck v2 (rugcheck.gentechlabs.net, localhost:8088)
      /v1/scan/{agent_id}   -> OWASP Agentic Top 10 full agent scan
      /v1/agent/{agent_id}  -> ERC-8004 identity + wallet reputation
  - Treasury Defender (localhost:8096)
      /demo/v1/defender/classify/{chain}/{token} -> token KNOWN/SUSPICIOUS

Every call is wrapped so that if a service is down, the demo degrades
gracefully to a clearly-labelled "simulated" fallback rather than crashing.
This is the honest "real data layer" — the same services that protect the
live treasury are the ones shown protecting the demo agent.

Run:  python3 live_stack.py --self-test
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ── service endpoints (local; the same services back the public gateways) ──
RUGCHECK_BASE = "http://localhost:8088"
DEFENDER_BASE = "http://localhost:8096"

# Real tokens used in the demo (Avalanche C-Chain, chainId 43114)
# USDC — a KNOWN, legitimate stablecoin (in Treasury Defender's known list)
USDC_AVAX = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
# A homoglyph USDC lookalike (the class Treasury Defender already caught live)
HOMOGLYPH_USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6F"

# A real agent address for the identity/scan demo (GenTech main treasury)
# Use the ERC-8004-registered GenTech agent so the demo shows a verified
# identity + credit score (agent 1770 = "GenTech Labs Agent", score 76.7/HIGH).
AGENT_ID = "1770"


@dataclass
class LiveScan:
    """Enriched result of a live agent scan + token classification."""

    agent_id: str
    owasp_score: Optional[float]
    owasp_level: Optional[str]
    owasp_checks: list[dict]
    erc8004_registered: bool
    wallet_reputation: Optional[float]
    token_status: Optional[str]
    token_reasons: list[str]
    source: str  # "live" | "simulated"
    credit_score: Optional[float] = None
    credit_level: Optional[str] = None
    fetched_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


def _get(url: str, timeout: float = 6.0) -> Optional[dict]:
    """GET a JSON endpoint; return None on any failure (service down)."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def scan_agent(agent_id: str = AGENT_ID) -> LiveScan:
    """Run a live full agent scan (OWASP Agentic Top 10) + identity check."""
    scan = _get(f"{RUGCHECK_BASE}/v1/scan/{agent_id}")
    ident = _get(f"{RUGCHECK_BASE}/v1/agent/{agent_id}")

    if scan is None and ident is None:
        return LiveScan(
            agent_id=agent_id,
            owasp_score=None,
            owasp_level=None,
            owasp_checks=[],
            erc8004_registered=False,
            wallet_reputation=None,
            token_status=None,
            token_reasons=["RugCheck service unreachable — simulated fallback"],
            source="simulated",
        )

    return LiveScan(
        agent_id=agent_id,
        owasp_score=scan.get("overall_score") if scan else None,
        owasp_level=scan.get("overall_level") if scan else None,
        owasp_checks=(scan.get("owasp_checks") or []) if scan else [],
        erc8004_registered=bool(ident and ident.get("erc8004_registered")),
        wallet_reputation=ident.get("wallet_reputation_score") if ident else None,
        credit_score=ident.get("overall_score") if ident else None,
        credit_level=ident.get("overall_level") if ident else None,
        token_status=None,
        token_reasons=[],
        source="live",
    )


def classify_token(chain_id: int = 43114, token: str = USDC_AVAX) -> dict:
    """Classify a token via Treasury Defender (KNOWN / SUSPICIOUS / UNKNOWN)."""
    data = _get(f"{DEFENDER_BASE}/demo/v1/defender/classify/{chain_id}/{token}")
    if data is None:
        return {
            "status": "UNKNOWN",
            "reasons": ["Treasury Defender unreachable — simulated fallback"],
            "source": "simulated",
        }
    data["source"] = "live"
    return data


def full_demo_payload(agent_id: str = AGENT_ID) -> dict:
    """Assemble the complete live-stack payload for the demo UI."""
    scan = scan_agent(agent_id)
    good = classify_token(43114, USDC_AVAX)
    bad = classify_token(43114, HOMOGLYPH_USDC)
    return {
        "agent_scan": scan.to_dict(),
        "token_known": good,
        "token_homoglyph": bad,
        "services": {
            "rugcheck": scan.source == "live",
            "treasury_defender": good.get("source") == "live",
        },
    }


def _self_test() -> int:
    print("🔍 LIVE STACK self-test\n")
    p = full_demo_payload()
    print(f"  agent_scan.source        : {p['agent_scan']['source']}")
    print(f"  agent_scan.owasp_score   : {p['agent_scan']['owasp_score']}")
    print(f"  agent_scan.owasp_level   : {p['agent_scan']['owasp_level']}")
    print(f"  agent_scan.erc8004       : {p['agent_scan']['erc8004_registered']}")
    print(f"  agent_scan.credit_score  : {p['agent_scan']['credit_score']} ({p['agent_scan']['credit_level']})")
    print(f"  token_known.status       : {p['token_known'].get('status')}")
    print(f"  token_homoglyph.status   : {p['token_homoglyph'].get('status')}")
    print(f"  services                 : {p['services']}")
    print("\n  ✅ self-test complete")
    return 0


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print(json.dumps(full_demo_payload(), indent=2))
