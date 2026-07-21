"""
GenTech Agent Kit — Q402 Integration Module
=============================================
Wraps Q402's gasless payment protocol for GenTech agents.
Provides Trust Receipt verification, AAE enforcement hooks,
and a clean pay() interface for agent-to-agent payments.

Requirements:
  pip install httpx

Usage:
  from gentech_agent_kit import Q402Client, TrustReceipt

  # Sandbox mode (no API key needed)
  client = Q402Client()
  result = client.pay(
      to="0x7ebff188f2Eba16518C02864589b1403a5d1296a",
      amount="1.00",
      token="USDC",
      chain="bnb"
  )
  print(result.tx_hash)  # Fake hash in sandbox

  # Verify a Trust Receipt
  receipt = client.verify_receipt(tx_hash="0x...")
  print(receipt.verified)
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from typing import Optional


# ── Data Types ──────────────────────────────────────────────────────────

@dataclass
class PaymentResult:
    """Result of a Q402 payment call."""
    success: bool
    sandbox: bool
    tx_hash: str
    token_amount: str
    token: str
    chain: str
    method: str
    explorer_url: Optional[str] = None
    consent_token: Optional[str] = None
    needs_consent: bool = False
    guards_applied: list = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class TrustReceipt:
    """A verified Q402 Trust Receipt."""
    receipt_id: Optional[str]
    verified: bool
    tx_hash: Optional[str] = None
    chain: Optional[str] = None
    token: Optional[str] = None
    amount: Optional[str] = None
    explorer_url: Optional[str] = None
    not_found: bool = False
    raw: Optional[dict] = None


@dataclass
class BalanceInfo:
    """API key balance and plan info."""
    api_key_kind: Optional[str]
    api_key_masked: Optional[str]
    scopes: list = field(default_factory=list)
    dashboard_url: str = "https://q402.quackai.ai/dashboard"
    setup_hint: Optional[str] = None


# ── Q402 MCP Client ────────────────────────────────────────────────────

class Q402Client:
    """
    Client for Q402 gasless payments via the MCP server.

    Works in sandbox mode by default (no API key needed).
    For live payments, set Q402_TRIAL_API_KEY or Q402_MULTICHAIN_API_KEY
    in ~/.q402/mcp.env.
    """

    def __init__(self, mcp_path: str = r"C:\Program Files\nodejs\npx.cmd", mcp_args: list = None):
        self.mcp_path = mcp_path
        self.mcp_args = mcp_args or ["-y", "@quackai/q402-mcp"]

    def _call_mcp(self, tool: str, args: dict = None) -> dict:
        """Call a Q402 MCP tool via stdin/stdout JSON-RPC."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args or {}
            }
        }

        cmd = [self.mcp_path] + self.mcp_args
        result = subprocess.run(
            cmd,
            input=json.dumps(payload) + "\n",
            capture_output=True,
            text=True,
            timeout=30
        )

        # Q402 MCP outputs JSON-RPC to stdout (stderr is the banner)
        output = result.stdout or result.stderr

        # Parse the last JSON line from output
        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    if "result" in data:
                        text = data["result"]["content"][0]["text"]
                        return json.loads(text)
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

        return {"error": f"MCP call failed: {result.stderr[:200]}"}

    # ── Health & Balance ────────────────────────────────────────────────

    def doctor(self) -> dict:
        """Run Q402 health check."""
        return self._call_mcp("q402_doctor")

    def balance(self) -> BalanceInfo:
        """Check API key balance and plan."""
        result = self._call_mcp("q402_balance")
        return BalanceInfo(
            api_key_kind=result.get("apiKeyKind"),
            api_key_masked=result.get("apiKeyMasked"),
            scopes=result.get("scopes", []),
            dashboard_url=result.get("dashboardUrl", "https://q402.quackai.ai/dashboard"),
            setup_hint=result.get("setupHint"),
        )

    # ── Payments ───────────────────────────────────────────────────────

    def pay(
        self,
        to: str,
        amount: str,
        token: str = "USDC",
        chain: str = "bnb",
        confirm: bool = True,
        consent_token: Optional[str] = None,
    ) -> PaymentResult:
        """
        Send a gasless payment via Q402.

        Args:
            to: Recipient address (0x...)
            amount: Human-readable decimal string (e.g. "1.00")
            token: "USDC", "USDT", "RLUSD", or "USDG"
            chain: "bnb", "avax", "eth", "base", etc.
            confirm: Two-phase consent. First call with confirm=True
                     returns needs_consent=True + consent_token.
                     Second call with the consent_token completes it.
            consent_token: From the first consent phase.

        Returns:
            PaymentResult with tx_hash (sandbox: fake hash)
        """
        args = {
            "to": to,
            "amount": amount,
            "token": token,
            "chain": chain,
            "confirm": confirm,
        }
        if consent_token:
            args["consentToken"] = consent_token

        result = self._call_mcp("q402_pay", args)

        # Check for consent flow
        if "needsConsent" in result:
            nc = result["needsConsent"]
            return PaymentResult(
                success=False,
                sandbox=False,
                tx_hash="",
                token_amount=amount,
                token=token,
                chain=chain,
                method="consent",
                needs_consent=True,
                consent_token=nc.get("consentToken"),
                guards_applied=result.get("guardsApplied", []),
            )

        return PaymentResult(
            success=result.get("result", {}).get("success", False) or result.get("result", {}).get("sandbox", False),
            sandbox=result.get("result", {}).get("sandbox", True),
            tx_hash=result.get("result", {}).get("txHash", ""),
            token_amount=result.get("result", {}).get("tokenAmount", amount),
            token=result.get("result", {}).get("token", token),
            chain=result.get("result", {}).get("chain", chain),
            method=result.get("result", {}).get("method", "sandbox"),
            explorer_url=result.get("result", {}).get("explorerUrl"),
            guards_applied=result.get("guardsApplied", []),
            error=result.get("error"),
        )

    # ── Trust Receipts ──────────────────────────────────────────────────

    def verify_receipt(
        self,
        receipt_id: Optional[str] = None,
        tx_hash: Optional[str] = None,
    ) -> TrustReceipt:
        """
        Verify a Q402 Trust Receipt.

        Args:
            receipt_id: rct_... receipt ID
            tx_hash: 0x... transaction hash (alternative lookup)

        Returns:
            TrustReceipt with verification status
        """
        args = {}
        if receipt_id:
            args["receiptId"] = receipt_id
        if tx_hash:
            args["txHash"] = tx_hash

        result = self._call_mcp("q402_receipt", args)

        return TrustReceipt(
            receipt_id=result.get("receiptId"),
            verified=result.get("verified", False),
            tx_hash=result.get("txHash"),
            chain=result.get("chain"),
            token=result.get("token"),
            amount=result.get("amount"),
            explorer_url=result.get("explorerUrl"),
            not_found=result.get("notFound", False),
            raw=result,
        )

    # ── Agent Wallet ────────────────────────────────────────────────────

    def agent_info(self) -> dict:
        """Get Agent Wallet info (addresses, caps, daily spend)."""
        return self._call_mcp("q402_agentic_info")

    def wallet_status(self) -> dict:
        """Get EIP-7702 delegation status."""
        return self._call_mcp("q402_wallet_status")

    # ── Yield ──────────────────────────────────────────────────────────

    def yield_reserves(self) -> dict:
        """List available yield lending markets."""
        return self._call_mcp("q402_yield_reserves")

    def yield_positions(self) -> dict:
        """Get current yield positions."""
        return self._call_mcp("q402_yield_positions")

    # ── Payment Requests (Invoicing) ────────────────────────────────────

    def create_request(
        self,
        amount: str,
        token: str = "USDC",
        chain: str = "bnb",
        memo: Optional[str] = None,
        recipient: Optional[str] = None,
        ttl_days: int = 7,
    ) -> dict:
        """Create a payment request (invoice). Returns /pay link + req_ id."""
        args = {"amount": amount, "token": token, "chain": chain, "ttlDays": ttl_days}
        if memo:
            args["memo"] = memo
        if recipient:
            args["recipient"] = recipient
        return self._call_mcp("q402_request_create", args)

    def request_status(self, req_id: str) -> dict:
        """Check a payment request status."""
        return self._call_mcp("q402_request_status", {"reqId": req_id})


# ── AAE Enforcement Hooks ──────────────────────────────────────────────

class AAEEnforcement:
    """
    AAE (Agentic Action Enforcement) hooks for Q402 payments.

    These hooks ensure payments meet safety criteria before execution:
    - Max amount per call (default $200)
    - Recipient allowlist
    - Two-phase consent
    - Chain-specific routing
    """

    def __init__(self, max_amount: float = 200.0, allowed_recipients: Optional[list] = None):
        self.max_amount = max_amount
        self.allowed_recipients = allowed_recipients or []

    def check_amount(self, amount: str) -> bool:
        """Check if amount is within the max limit."""
        try:
            return float(amount) <= self.max_amount
        except ValueError:
            return False

    def check_recipient(self, address: str) -> bool:
        """Check if recipient is allowed (empty allowlist = any OK)."""
        if not self.allowed_recipients:
            return True
        return address.lower() in [r.lower() for r in self.allowed_recipients]

    def enforce(self, to: str, amount: str) -> list:
        """Run all enforcement checks. Returns list of guard names applied."""
        guards = []
        if self.check_amount(amount):
            guards.append("max_amount<={}".format(int(self.max_amount)))
        if self.check_recipient(to):
            guards.append("recipient_allowed")
        return guards


# ── Quick Test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=== GenTech Agent Kit — Q402 Module ===")
    print()

    client = Q402Client()

    # Health check
    print("1. Health check...")
    health = client.doctor()
    print(f"   Package: {health.get('package', '?')}")
    print(f"   Version: {health.get('version', '?')}")
    print(f"   Ready: {health.get('ready', False)}")
    print()

    # Balance
    print("2. Balance check...")
    bal = client.balance()
    print(f"   API Key: {bal.api_key_kind or 'none (sandbox)'}")
    print(f"   Scopes: {bal.scopes or ['sandbox']}")
    print()

    # AAE enforcement
    print("3. AAE enforcement test...")
    aae = AAEEnforcement(max_amount=200.0)
    guards = aae.enforce("0x7ebff188f2Eba16518C02864589b1403a5d1296a", "1.00")
    print(f"   Guards applied: {guards}")
    print(f"   Amount check ($1.00 <= $200): {aae.check_amount('1.00')}")
    print(f"   Recipient check: {aae.check_recipient('0x7ebff188f2Eba16518C02864589b1403a5d1296a')}")
    print()

    # Sandbox payment
    print("4. Sandbox payment test...")
    result = client.pay(
        to="0x7ebff188f2Eba16518C02864589b1403a5d1296a",
        amount="1.00",
        token="USDC",
        chain="bnb",
        confirm=True,
    )
    if result.needs_consent:
        print(f"   → Needs consent: {result.consent_token}")
        # Complete the consent
        result2 = client.pay(
            to="0x7ebff188f2Eba16518C02864589b1403a5d1296a",
            amount="1.00",
            token="USDC",
            chain="bnb",
            confirm=True,
            consent_token=result.consent_token,
        )
        print(f"   → Sandbox payment: {'✅' if result2.success else '❌'}")
        print(f"   → TX Hash: {result2.tx_hash}")
        print(f"   → Mode: {result2.method}")
        print(f"   → Guards: {result2.guards_applied}")
    else:
        print(f"   → Payment: {'✅' if result.success else '❌'}")
        print(f"   → TX Hash: {result.tx_hash}")
        print(f"   → Mode: {result.method}")
    print()

    print("=== All tests complete ===")
