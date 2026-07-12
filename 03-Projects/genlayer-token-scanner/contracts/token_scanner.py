# { "Depends": "py-genlayer:test" }

"""
Token Scanner — GenLayer Intelligent Contract
===============================================
On-chain token risk assessment using GoPlus API + LLM analysis.
Scans any EVM token address, returns a 0-100 risk score with labeled risk factors.

Part of GenLayer Builder Program — Intelligent Contract Templates.
Built by GenTech Labs.

Usage:
    Deploy via GenLayer CLI, then call scan_token(token_address) from frontend or CLI.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from genlayer import *


# ─── Storage Models ───────────────────────────────────────────────────────────

@allow_storage
@dataclass
class TokenAssessment:
    token_address: str
    token_name: str
    token_symbol: str
    risk_score: int            # 0-100 (100 = safest)
    risk_level: str            # LOW / MEDIUM / HIGH / CRITICAL
    risk_factors: DynArray[str]
    honeypot: bool
    open_source: bool
    owner_can_change_balance: bool
    can_take_back_liquidity: bool
    hidden_owner: bool
    selfdestruct: bool
    is_proxy: bool
    malicious_behavior: bool
    slippage_modifiable: bool
    is_blacklisted: bool
    holder_count: int
    total_supply: str
    scanner_agent: str
    scan_timestamp: int
    source_url: str


@allow_storage
@dataclass
class ScanRequest:
    requester: Address
    token_address: str
    timestamp: int
    resolved: bool


# ─── Risk Weight Constants ────────────────────────────────────────────────────

RISK_WEIGHTS = {
    "honeypot":              0.20,
    "open_source":           0.10,  # inverted: NOT open source = risky
    "owner_change_balance":  0.10,
    "take_back_liquidity":   0.12,
    "hidden_owner":          0.10,
    "selfdestruct":          0.08,
    "external_call":         0.05,
    "is_proxy":              0.05,
    "malicious_behavior":    0.10,
    "slippage_modifiable":   0.05,
    "is_blacklisted":        0.05,
}


# ─── Main Contract ────────────────────────────────────────────────────────────

class TokenScanner(gl.Contract):
    """On-chain token risk scanner using GoPlus API + LLM analysis."""

    # Storage: address → latest assessment
    assessments: TreeMap[Address, TokenAssessment]
    # Storage: address → list of all assessment timestamps
    scan_history: TreeMap[Address, DynArray[int]]
    # Storage: authorized scanner agents
    authorized_agents: TreeMap[Address, bool]
    # Total scans performed
    total_scans: u256

    def __init__(self):
        self.total_scans = 0

    # ─── Internal: Fetch GoPlus Data ──────────────────────────────────────

    def _fetch_goplus_data(self, token_address: str) -> dict:
        """
        Fetch token security data from GoPlus API via web access.
        Returns raw GoPlus response dict.
        """
        url = f"https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses={token_address}"

        def fetch_data() -> str:
            response = gl.nondet.web.get(url)
            return response.text

        raw_text = gl.eq_principle.strict_eq(fetch_data)
        data = json.loads(raw_text)

        if data.get("code") != 1:
            raise Exception(f"GoPlus API error: {data.get('message', 'unknown')}")

        result = data.get("result", {}).get(token_address.lower(), {})
        if not result:
            # Try case-insensitive match
            for key, val in data.get("result", {}).items():
                if token_address.lower().endswith(key) or key.endswith(token_address.lower()):
                    result = val
                    break

        if not result:
            raise Exception(f"No data found for token: {token_address}")

        return result

    # ─── Internal: LLM Risk Analysis ──────────────────────────────────────

    def _analyze_risk(self, raw_data: dict, token_address: str) -> dict:
        """
        Use LLM to analyze GoPlus data and extract structured risk assessment.
        Returns dict with risk_score, risk_level, risk_factors, and metadata.
        """
        # Build a concise summary for the LLM
        security_summary = json.dumps({
            "is_honeypot": raw_data.get("is_honeypot", "0"),
            "is_open_source": raw_data.get("is_open_source", "0"),
            "owner_change_balance": raw_data.get("owner_change_balance", "0"),
            "can_take_back_liquidity": raw_data.get("can_take_back_liquidity", "0"),
            "hidden_owner": raw_data.get("hidden_owner", "0"),
            "selfdestruct": raw_data.get("selfdestruct", "0"),
            "external_call": raw_data.get("external_call", "0"),
            "is_proxy": raw_data.get("is_proxy", "0"),
            "malicious_behavior": raw_data.get("malicious_behavior", "0"),
            "slippage_modifiable": raw_data.get("slippage_modifiable", "0"),
            "is_blacklisted": raw_data.get("is_blacklisted", "0"),
            "holder_count": raw_data.get("holder_count", "0"),
            "total_supply": raw_data.get("total_supply", "0"),
            "token_name": raw_data.get("token_name", "Unknown"),
            "token_symbol": raw_data.get("token_symbol", "???"),
            "owner_address": raw_data.get("owner_address", "unknown"),
            "creation_time": raw_data.get("creation_time", "0"),
        }, indent=2)

        prompt = f"""
You are a token security analyst. Analyze the following GoPlus security data for token {token_address}.

GoPlus Data:
{security_summary}

Calculate a risk score from 0 (extremely dangerous) to 100 (completely safe).

Risk weights:
- Honeypot: 20% (if detected, major red flag)
- Not open source: 10% (closed source = risky)
- Owner can change balance: 10%
- Can take back liquidity: 12%
- Hidden owner: 10%
- Self-destruct: 8%
- External call: 5%
- Is proxy: 5%
- Malicious behavior: 10%
- Slippage modifiable: 5%
- Blacklisted: 5%

Also consider: holder count, token age, supply distribution.

Respond in JSON only:
{{
    "risk_score": <int 0-100>,
    "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "token_name": "<name from data>",
    "token_symbol": "<symbol from data>",
    "risk_factors": ["<list of detected risk factors>"],
    "honeypot": <true|false>,
    "open_source": <true|false>,
    "owner_can_change_balance": <true|false>,
    "can_take_back_liquidity": <true|false>,
    "hidden_owner": <true|false>,
    "selfdestruct": <true|false>,
    "is_proxy": <true|false>,
    "malicious_behavior": <true|false>,
    "slippage_modifiable": <true|false>,
    "is_blacklisted": <true|false>,
    "holder_count": <int>,
    "total_supply": "<string>",
    "analysis": "<brief 1-2 sentence analysis>"
}}

IMPORTANT: Respond ONLY with valid JSON. No other text.
"""
        def get_analysis() -> str:
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            return json.dumps(result, sort_keys=True)

        analysis_json = json.loads(gl.eq_principle.strict_eq(get_analysis))
        return analysis_json

    # ─── Internal: Calculate Deterministic Score ───────────────────────────

    def _calculate_deterministic_score(self, raw_data: dict) -> tuple:
        """
        Fallback deterministic scoring using weighted risk factors.
        Returns (score, level, risk_factors_list).
        """
        def _bool(val):
            return str(val) == "1"

        factors = {
            "honeypot":              _bool(raw_data.get("is_honeypot", 0)),
            "open_source":           _bool(raw_data.get("is_open_source", 0)),
            "owner_change_balance":  _bool(raw_data.get("owner_change_balance", 0)),
            "take_back_liquidity":   _bool(raw_data.get("can_take_back_liquidity", 0)),
            "hidden_owner":          _bool(raw_data.get("hidden_owner", 0)),
            "selfdestruct":          _bool(raw_data.get("selfdestruct", 0)),
            "external_call":         _bool(raw_data.get("external_call", 0)),
            "is_proxy":              _bool(raw_data.get("is_proxy", 0)),
            "malicious_behavior":    _bool(raw_data.get("malicious_behavior", 0)),
            "slippage_modifiable":   _bool(raw_data.get("slippage_modifiable", 0)),
            "is_blacklisted":        _bool(raw_data.get("is_blacklisted", 0)),
        }

        total_penalty = 0.0
        risk_factors = []

        for factor, weight in RISK_WEIGHTS.items():
            is_risky = factors.get(factor, False)
            if factor == "open_source":
                if not is_risky:
                    total_penalty += weight
                    risk_factors.append("closed_source")
            else:
                if is_risky:
                    total_penalty += weight
                    risk_factors.append(factor)

        score = max(0, min(100, int((1.0 - total_penalty) * 100)))

        if score >= 80:
            level = "LOW"
        elif score >= 60:
            level = "MEDIUM"
        elif score >= 40:
            level = "HIGH"
        else:
            level = "CRITICAL"

        return score, level, risk_factors

    # ─── Public: Scan Token ───────────────────────────────────────────────

    @gl.public.write
    def scan_token(self, token_address: str) -> dict:
        """
        Scan a token address for risk factors.
        Fetches GoPlus data, analyzes with LLM, stores result on-chain.

        Args:
            token_address: EVM token contract address (0x...)

        Returns:
            Assessment dict with risk_score, risk_level, and risk_factors.
        """
        # Step 1: Fetch GoPlus data
        raw_data = self._fetch_goplus_data(token_address)

        # Step 2: Try LLM analysis, fall back to deterministic
        try:
            analysis = self._analyze_risk(raw_data, token_address)
            risk_score = analysis.get("risk_score", 50)
            risk_level = analysis.get("risk_level", "MEDIUM")
            risk_factors = analysis.get("risk_factors", [])
            honeypot = analysis.get("honeypot", False)
            open_source = analysis.get("open_source", False)
            owner_change = analysis.get("owner_can_change_balance", False)
            take_liquidity = analysis.get("can_take_back_liquidity", False)
            hidden_owner = analysis.get("hidden_owner", False)
            selfdestruct = analysis.get("selfdestruct", False)
            is_proxy = analysis.get("is_proxy", False)
            malicious = analysis.get("malicious_behavior", False)
            slippage = analysis.get("slippage_modifiable", False)
            blacklisted = analysis.get("is_blacklisted", False)
            holder_count = analysis.get("holder_count", 0)
            total_supply = analysis.get("total_supply", "0")
            token_name = analysis.get("token_name", raw_data.get("token_name", "Unknown"))
            token_symbol = analysis.get("token_symbol", raw_data.get("token_symbol", "???"))
        except Exception:
            # Fallback to deterministic scoring
            risk_score, risk_level, risk_factors = self._calculate_deterministic_score(raw_data)
            honeypot = str(raw_data.get("is_honeypot", "0")) == "1"
            open_source = str(raw_data.get("is_open_source", "0")) == "1"
            owner_change = str(raw_data.get("owner_change_balance", "0")) == "1"
            take_liquidity = str(raw_data.get("can_take_back_liquidity", "0")) == "1"
            hidden_owner = str(raw_data.get("hidden_owner", "0")) == "1"
            selfdestruct = str(raw_data.get("selfdestruct", "0")) == "1"
            is_proxy = str(raw_data.get("is_proxy", "0")) == "1"
            malicious = str(raw_data.get("malicious_behavior", "0")) == "1"
            slippage = str(raw_data.get("slippage_modifiable", "0")) == "1"
            blacklisted = str(raw_data.get("is_blacklisted", "0")) == "1"
            holder_count = int(raw_data.get("holder_count", 0))
            total_supply = raw_data.get("total_supply", "0")
            token_name = raw_data.get("token_name", "Unknown")
            token_symbol = raw_data.get("token_symbol", "???")

        # Step 3: Store assessment on-chain
        timestamp = int(datetime.now().timestamp()) if hasattr(datetime, 'timestamp') else 0
        token_addr = Address(token_address)

        assessment = TokenAssessment(
            token_address=token_address,
            token_name=token_name,
            token_symbol=token_symbol,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=DynArray(risk_factors),
            honeypot=honeypot,
            open_source=open_source,
            owner_can_change_balance=owner_change,
            can_take_back_liquidity=take_liquidity,
            hidden_owner=hidden_owner,
            selfdestruct=selfdestruct,
            is_proxy=is_proxy,
            malicious_behavior=malicious,
            slippage_modifiable=slippage,
            is_blacklisted=blacklisted,
            holder_count=holder_count,
            total_supply=total_supply,
            scanner_agent="genlayer_token_scanner_v1",
            scan_timestamp=timestamp,
            source_url="https://api.gopluslabs.io",
        )

        self.assessments[token_addr] = assessment
        self.scan_history.get_or_insert_default(token_addr).append(timestamp)
        self.total_scans += 1

        # Step 4: Return result
        return {
            "token_address": token_address,
            "token_name": token_name,
            "token_symbol": token_symbol,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "holder_count": holder_count,
            "scan_number": int(self.total_scans),
        }

    # ─── Public: Batch Scan ───────────────────────────────────────────────

    @gl.public.write
    def scan_batch(self, token_addresses: DynArray[str]) -> DynArray[dict]:
        """
        Scan multiple tokens in a single transaction.
        Returns list of assessment summaries.

        Args:
            token_addresses: List of EVM token addresses to scan

        Returns:
            List of assessment dicts
        """
        results = []
        for addr in token_addresses:
            try:
                result = self.scan_token(addr)
                results.append(result)
            except Exception as e:
                results.append({
                    "token_address": addr,
                    "error": str(e),
                    "risk_score": 0,
                    "risk_level": "UNKNOWN",
                })
        return results

    # ─── Public Views ─────────────────────────────────────────────────────

    @gl.public.view
    def get_assessment(self, token_address: str) -> dict:
        """Get the latest risk assessment for a token."""
        token_addr = Address(token_address)
        if token_addr not in self.assessments:
            return {"error": "No assessment found for this token"}

        a = self.assessments[token_addr]
        return {
            "token_address": a.token_address,
            "token_name": a.token_name,
            "token_symbol": a.token_symbol,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "risk_factors": list(a.risk_factors),
            "honeypot": a.honeypot,
            "open_source": a.open_source,
            "owner_can_change_balance": a.owner_can_change_balance,
            "can_take_back_liquidity": a.can_take_back_liquidity,
            "hidden_owner": a.hidden_owner,
            "selfdestruct": a.selfdestruct,
            "is_proxy": a.is_proxy,
            "malicious_behavior": a.malicious_behavior,
            "slippage_modifiable": a.slippage_modifiable,
            "is_blacklisted": a.is_blacklisted,
            "holder_count": a.holder_count,
            "total_supply": a.total_supply,
            "scanner_agent": a.scanner_agent,
            "scan_timestamp": a.scan_timestamp,
            "source_url": a.source_url,
        }

    @gl.public.view
    def get_scan_count(self, token_address: str) -> int:
        """Get number of times a token has been scanned."""
        token_addr = Address(token_address)
        if token_addr not in self.scan_history:
            return 0
        return len(self.scan_history[token_addr])

    @gl.public.view
    def get_total_scans(self) -> int:
        """Get total number of scans performed by this contract."""
        return int(self.total_scans)

    @gl.public.view
    def is_safe(self, token_address: str) -> bool:
        """Quick check: is this token safe? (score >= 60)"""
        token_addr = Address(token_address)
        if token_addr not in self.assessments:
            return False
        return self.assessments[token_addr].risk_score >= 60

    @gl.public.view
    def is_honeypot(self, token_address: str) -> bool:
        """Quick check: is this token a honeypot?"""
        token_addr = Address(token_address)
        if token_addr not in self.assessments:
            return False
        return self.assessments[token_addr].honeypot

    @gl.public.view
    def get_risk_level(self, token_address: str) -> str:
        """Get risk level string for a token."""
        token_addr = Address(token_address)
        if token_addr not in self.assessments:
            return "NOT_SCANNED"
        return self.assessments[token_addr].risk_level

    @gl.public.view
    def get_all_assessments(self) -> dict:
        """Get all stored assessments. Returns token_address → assessment."""
        return {k.as_hex: {
            "token_name": v.token_name,
            "token_symbol": v.token_symbol,
            "risk_score": v.risk_score,
            "risk_level": v.risk_level,
            "risk_factors": list(v.risk_factors),
            "scan_timestamp": v.scan_timestamp,
        } for k, v in self.assessments.items()}
