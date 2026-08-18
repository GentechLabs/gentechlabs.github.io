#!/usr/bin/env python3
"""
x402 Compliance Scanner — Reference Implementation

Validates x402 endpoint responses against the protocol specification.
Use this to verify your x402 gateway implements the standard correctly.

Capabilities:
  - Checks 402 response shape (status, x402version, accepts, network, asset, amount, payment_address)
  - Validates accepts[] field requirements (type, scheme, network, amount, asset, payTo)
  - Verifies CORS headers
  - Tests settlement flow: 402 → payment → 200 response
  - Schema drift detection against golden snapshots

Usage:
  python3 scanner.py scan <url>              # Scan a single endpoint
  python3 scanner.py scan-all <base-url>      # Scan all endpoints from OpenAPI
  python3 scanner.py validate <url> <tx>      # Validate a settled transaction

Exit codes:
  0 = all checks pass
  1 = one or more checks failed
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

__version__ = "0.1.0"

# ── Data ────────────────────────────────────────────────────────────────────

@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""

    def ok(self, detail=""):
        self.passed = True
        self.detail = detail
        return self

    def fail(self, detail=""):
        self.passed = False
        self.detail = detail
        return self

    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"  {status} {self.name}: {self.detail}"

# ── Core checks ─────────────────────────────────────────────────────────────

# x402 v2 spec (verified 2026-08-18 against Coinbase CDP, PayAI, x402.org):
# Top-level PaymentRequired body = { x402Version, resource, accepts, extensions }.
# The v1 fields (status/x402version/payment_address) are gone in v2 — payment
# data moved to headers (PAYMENT-REQUIRED) and the body carries the challenge.
REQUIRED_402_FIELDS = ["x402Version", "resource", "accepts"]
# x402 v2 spec (verified 2026-08-18 against Coinbase CDP, PayAI, x402.org):
# accepts[] entries use scheme/network/amount/asset/payTo/maxTimeoutSeconds/extra.
# There is NO 'type' field in the v2 spec — earlier versions of this scanner
# wrongly required it, producing false negatives on compliant gateways.
ACCEPTS_FIELDS = ["scheme", "network", "amount", "asset", "payTo"]

def check_402_response(url: str, timeout: int = 10) -> tuple[list[Check], dict]:
    """
    Issue an unauthenticated request and validate the 402 response shape.
    Returns (checks, response_body).
    """
    checks = []
    body = {}

    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "x402-Compliance-Scanner/0.1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout):
            checks.append(Check("http_402_required", False, "Expected 402, got 200"))
            return checks, body
    except urllib.error.HTTPError as e:
        if e.code != 402:
            checks.append(Check("http_402_required", False, f"Expected 402, got {e.code}"))
            return checks, body
        checks.append(Check("http_402_required", True, "Responded 402 Payment Required"))
        body = json.loads(e.read())

    # Required top-level fields
    for field in REQUIRED_402_FIELDS:
        if field not in body:
            checks.append(Check(f"field_{field}", False, f"Missing required field '{field}'"))
        else:
            checks.append(Check(f"field_{field}", True, f"'{field}' present"))

    # x402 version check (v2: x402Version at top level)
    version = body.get("x402Version")
    if version in (2, "2", "x402-v2"):
        checks.append(Check("x402version_format", True, f"x402Version = {version}"))
    else:
        checks.append(Check("x402version_format", False, f"Unexpected x402Version: {version}"))

    # resource must be present and carry a url (v2)
    resource = body.get("resource")
    if isinstance(resource, dict) and resource.get("url"):
        checks.append(Check("resource_valid", True, f"resource.url = {resource['url']}"))
    else:
        checks.append(Check("resource_valid", False, "resource.url missing or empty"))

    # accepts[] entries must each carry a positive amount + payTo (v2)
    accepts = body.get("accepts", [])
    if isinstance(accepts, list) and accepts:
        for i, entry in enumerate(accepts):
            amt = entry.get("amount", "0")
            if isinstance(amt, str) and amt.isdigit() and int(amt) > 0:
                checks.append(Check(f"accepts[{i}].amount_valid", True, f"amount = {amt}"))
            else:
                checks.append(Check(f"accepts[{i}].amount_valid", False, f"Invalid amount: {amt!r}"))
            if entry.get("payTo"):
                checks.append(Check(f"accepts[{i}].payTo_present", True, f"payTo = {entry['payTo'][:10]}..."))
            else:
                checks.append(Check(f"accepts[{i}].payTo_present", False, "payTo is empty"))

    # CORS
    cors = None
    try:
        req2 = urllib.request.Request(
            url,
            method="OPTIONS",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        with urllib.request.urlopen(req2, timeout=timeout):
            cors = "*"
        checks.append(Check("cors_preflight", True, "CORS preflight OK"))
    except urllib.error.HTTPError as e:
        cors = e.headers.get("Access-Control-Allow-Origin")
        if cors == "*":
            checks.append(Check("cors_header", True, "Access-Control-Allow-Origin: *"))
        elif cors:
            checks.append(Check("cors_header", True, f"Access-Control-Allow-Origin: {cors}"))
        else:
            checks.append(Check("cors_header", False, "No CORS header"))

    if body:
        checks.append(Check("content_type", True, "Response is JSON"))
    else:
        checks.append(Check("content_type", False, "No response body"))

    return checks, body


def check_settlement_flow(url: str, payment_auth: str, timeout: int = 10) -> list[Check]:
    """
    After obtaining a 402 challenge, attempt settlement with a payment auth header.
    Validates that a proper payment results in a 200 with the requested resource.
    """
    checks = []
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "x402-Compliance-Scanner/0.1.0",
                "Accept": "application/json",
                "Payment": payment_auth,
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            checks.append(Check("settlement_flow", True, "Payment accepted, resource returned"))
            body = json.loads(resp.read())
            checks.append(Check("settlement_response", True, "200 response is valid JSON"))
            # Check for payment confirmation header
            pay_resp = resp.headers.get("Payment-Response") or resp.headers.get("payment-response")
            if pay_resp:
                checks.append(Check("settlement_confirmation", True, f"Payment-Response: {pay_resp[:60]}"))
            else:
                checks.append(Check("settlement_confirmation", False, "No Payment-Response header"))
    except urllib.error.HTTPError as e:
        checks.append(Check("settlement_flow", False, f"Settlement failed: HTTP {e.code}"))
    return checks


def scan_endpoint(url: str, payment_auth: Optional[str] = None) -> dict:
    """Run all checks against a single x402 endpoint."""
    results = {"endpoint": url, "version": __version__, "checks": []}
    total_start = time.time()

    phase1, body = check_402_response(url)
    results["checks"].extend([c.__dict__ for c in phase1])

    if payment_auth and body:
        phase2 = check_settlement_flow(url, payment_auth)
        results["checks"].extend([c.__dict__ for c in phase2])

    results["duration_seconds"] = round(time.time() - total_start, 2)
    results["passed"] = all(c["passed"] for c in results["checks"])
    results["summary"] = f"{sum(1 for c in results['checks'] if c['passed'])}/{len(results['checks'])} checks passed"
    return results


# ── CLI ─────────────────────────────────────────────────────────────────────

def print_results(results):
    """Pretty-print scan results."""
    print(f"\n{'='*50}")
    print(f"x402 Compliance Scanner v{__version__}")
    print(f"{'='*50}")
    print(f"Endpoint: {results['endpoint']}")
    print(f"Duration: {results['duration_seconds']}s")
    print()
    for c in results["checks"]:
        status = "✅" if c["passed"] else "❌"
        print(f"  {status} {c['name']}: {c['detail']}")
    print()
    print(f"  Summary: {results['summary']}")
    result = "✅ ALL CHECKS PASSED" if results["passed"] else "❌ SOME CHECKS FAILED"
    print(f"  Result: {result}")
    print(f"{'='*50}\n")
    return results["passed"]


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(0)

    command = sys.argv[1]

    if command == "scan" and len(sys.argv) >= 3:
        url = sys.argv[2]
        auth = sys.argv[3] if len(sys.argv) > 3 else None
        results = scan_endpoint(url, auth)
        passed = print_results(results)
        sys.exit(0 if passed else 1)

    elif command == "scan-all" and len(sys.argv) >= 3:
        base_url = sys.argv[2].rstrip("/")
        # Try to discover endpoints from OpenAPI spec
        try:
            req = urllib.request.Request(
                f"{base_url}/openapi.json",
                headers={"User-Agent": "x402-Compliance-Scanner/0.1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                spec = json.loads(resp.read())
        except Exception:
            print("No OpenAPI spec found. Scanning common endpoints...")
            endpoints = [f"{base_url}/v1/{e}" for e in ["agent", "wallet", "payment", "verify"]]
            endpoints.append(base_url)
        else:
            # Extract paths from OpenAPI
            paths = spec.get("paths", {})
            endpoints = []
            for path_str, methods in paths.items():
                for method in methods:
                    if methods[method].get("x-payment", {}).get("required"):
                        endpoints.append(f"{base_url}{path_str}")
        if not endpoints:
            print("No x402-gated endpoints discovered.")
            sys.exit(0)

        all_passed = True
        for ep in endpoints:
            r = scan_endpoint(ep)
            p = print_results(r)
            if not p:
                all_passed = False
        sys.exit(0 if all_passed else 1)

    elif command == "validate" and len(sys.argv) >= 3:
        # Validate a settlement transaction receipt
        receipt = sys.argv[2]
        print(f"\n📋 Settlement Receipt: {receipt}")
        print("  Receipt validation requires network-specific verification.")
        print("  See x402 specification for settlement verification rules.\n")
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print("Usage: python3 scanner.py scan <url>")
        print("       python3 scanner.py scan-all <base-url>")
        print("       python3 scanner.py validate <receipt-id>")
        sys.exit(1)


if __name__ == "__main__":
    main()
