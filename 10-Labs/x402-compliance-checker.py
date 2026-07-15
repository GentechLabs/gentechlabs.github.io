#!/usr/bin/env python3
"""
x402 Compliance Checker — v0.1.0
Scan any API endpoint for x402 v2 spec compliance.
Reports what's missing/wrong and generates fixes.

Usage:
  python3 x402-check.py https://api.example.com/endpoint
  python3 x402-check.py https://api.example.com --full  # scans .well-known/x402 too
"""

import json
import sys
import os
import base64
import urllib.request
import urllib.error
import ssl
from typing import Optional

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS = f"{GREEN}✅ PASS{RESET}"
FAIL = f"{RED}❌ FAIL{RESET}"
WARN = f"{YELLOW}⚠️  WARN{RESET}"

def fetch_url(url: str, timeout: int = 10) -> tuple[int, dict, str, dict]:
    """Fetch URL, return (status_code, headers_dict, body_text, parsed_json_or_empty)"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "x402-compliance-checker/0.1")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        body = resp.read().decode("utf-8", errors="replace")
        headers = dict(resp.headers)
        status = resp.status
        parsed = {}
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            pass
        return status, headers, body, parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        headers = dict(e.headers)
        status = e.code
        parsed = {}
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            pass
        return status, headers, body, parsed
    except Exception as e:
        return 0, {}, str(e), {}

def check_payment_required_header(headers: dict) -> list:
    """Check the Payment-Required header format"""
    results = []
    
    # Check header exists (case-insensitive)
    pr_header = None
    for k, v in headers.items():
        if k.lower() == "payment-required":
            pr_header = v
            break
    
    if not pr_header:
        results.append((FAIL, "Payment-Required header missing entirely"))
        return results
    
    results.append((PASS, "Payment-Required header present"))
    
    # Decode base64
    try:
        decoded = base64.b64decode(pr_header).decode("utf-8")
        pr_data = json.loads(decoded)
        results.append((PASS, "Payment-Required header is valid base64 JSON"))
    except Exception:
        results.append((FAIL, "Payment-Required header is NOT valid base64 JSON"))
        return results
    
    # Check x402Version
    version = pr_data.get("x402Version")
    if version == 2:
        results.append((PASS, "x402Version is 2"))
    elif version is None:
        results.append((FAIL, "Missing x402Version field"))
    else:
        results.append((FAIL, f"x402Version should be 2, got {version}"))
    
    # Check error field
    if "error" in pr_data:
        results.append((PASS, "error field present"))
    else:
        results.append((WARN, "Missing error field (recommended)"))
    
    # Check resource block
    resource = pr_data.get("resource")
    if resource:
        results.append((PASS, "resource block present"))
        for field in ["url", "description", "mimeType", "serviceName"]:
            if field in resource:
                results.append((PASS, f"  resource.{field} present"))
            else:
                results.append((WARN, f"  Missing resource.{field} (recommended)"))
    else:
        results.append((WARN, "Missing resource block (recommended)"))
    
    # Check accepts array
    accepts = pr_data.get("accepts", [])
    if not accepts:
        results.append((FAIL, "accepts array is empty or missing"))
        return results
    
    results.append((PASS, f"accepts array has {len(accepts)} item(s)"))
    
    for i, acc in enumerate(accepts):
        prefix = f"  accepts[{i}]."
        # scheme
        if acc.get("scheme") == "exact":
            results.append((PASS, f"{prefix}scheme is 'exact'"))
        elif "scheme" not in acc:
            results.append((FAIL, f"{prefix}Missing scheme field"))
            if "type" in acc:
                results.append((WARN, f"{prefix}Uses 'type' instead of 'scheme' (should be 'exact')"))
        else:
            results.append((FAIL, f"{prefix}scheme should be 'exact', got '{acc['scheme']}'"))
        
        # network
        if acc.get("network"):
            results.append((PASS, f"{prefix}network present: {acc['network']}"))
        else:
            results.append((FAIL, f"{prefix}Missing network"))
        
        # amount
        if "amount" in acc:
            if isinstance(acc["amount"], str) and acc["amount"].isdigit():
                results.append((PASS, f"{prefix}amount is string-digit: {acc['amount']}"))
            elif isinstance(acc["amount"], (int, float)):
                results.append((WARN, f"{prefix}amount should be string, got number: {acc['amount']}"))
            else:
                results.append((FAIL, f"{prefix}amount invalid format"))
        else:
            results.append((FAIL, f"{prefix}Missing amount"))
        
        # asset
        asset = acc.get("asset", "")
        if asset:
            is_lower = asset == asset.lower()
            if len(asset) == 42 and asset.startswith("0x"):
                results.append((PASS, f"{prefix}asset is EVM address"))
                if is_lower:
                    results.append((PASS, f"{prefix}  → lowercase hex ✓"))
                else:
                    results.append((WARN, f"{prefix}  → should be lowercase hex"))
            elif len(asset) > 30:
                results.append((PASS, f"{prefix}asset is Solana/base58 address"))
            else:
                results.append((PASS, f"{prefix}asset present"))
        else:
            results.append((FAIL, f"{prefix}Missing asset"))
        
        # payTo (NOT payment_address)
        if "payTo" in acc:
            results.append((PASS, f"{prefix}uses payTo (correct v2 field)"))
        elif "payment_address" in acc:
            results.append((FAIL, f"{prefix}uses 'payment_address' instead of 'payTo'"))
            results.append((WARN, f"{prefix}  → v2 spec requires 'payTo', not 'payment_address'"))
        else:
            results.append((FAIL, f"{prefix}Missing payTo"))
        
        # maxTimeoutSeconds
        if "maxTimeoutSeconds" in acc:
            results.append((PASS, f"{prefix}maxTimeoutSeconds present"))
        else:
            results.append((WARN, f"{prefix}Missing maxTimeoutSeconds (recommended)"))
    
    return results


def check_402_response_body(body_parsed: dict) -> list:
    """Check the 402 response body JSON"""
    results = []
    
    if not body_parsed:
        results.append((WARN, "Response body is not JSON"))
        return results
    
    # Check for x402version in body
    if body_parsed.get("x402version"):
        results.append((PASS, f"Body has x402version: {body_parsed['x402version']}"))
    
    # Check for accepts in body  
    if body_parsed.get("accepts"):
        results.append((PASS, "Body has accepts array"))
    
    if body_parsed.get("network"):
        results.append((PASS, "Body has network field"))
    
    if body_parsed.get("asset"):
        results.append((PASS, "Body has asset field"))
    
    if body_parsed.get("amount"):
        results.append((PASS, "Body has amount field"))
    
    if body_parsed.get("payment_address") or body_parsed.get("payTo"):
        results.append((PASS, "Body has payment address field"))
    
    if body_parsed.get("instructions"):
        results.append((PASS, "Body has instructions block"))
        instr = body_parsed["instructions"]
        for field in ["protocol", "header", "encoding", "proofStructure"]:
            if field in instr:
                results.append((PASS, f"  instructions.{field} present"))
            else:
                results.append((WARN, f"  Missing instructions.{field}"))
    
    return results


def check_well_known_x402(base_url: str) -> list:
    """Check /.well-known/x402 endpoint"""
    results = []
    
    wk_url = f"{base_url.rstrip('/')}/.well-known/x402"
    status, headers, body, parsed = fetch_url(wk_url)
    
    if status == 404:
        results.append((FAIL, "/.well-known/x402 returns 404 — NOT PRESENT"))
        return results
    
    if status >= 500:
        results.append((FAIL, f"/.well-known/x402 returned {status} — server error"))
        return results
    
    if status != 200:
        results.append((WARN, f"/.well-known/x402 returned status {status}"))
    
    if not parsed:
        results.append((FAIL, "/.well-known/x402 body is not valid JSON"))
        return results
    
    results.append((PASS, "/.well-known/x402 endpoint exists and returns JSON"))
    
    # Check version
    if parsed.get("version") == 1:
        results.append((PASS, "discovery version is 1"))
    else:
        results.append((WARN, f"discovery version should be 1, got {parsed.get('version')}"))
    
    # Check resources
    resources = parsed.get("resources", [])
    if resources:
        results.append((PASS, f"resources array with {len(resources)} item(s)"))
    else:
        results.append((FAIL, "resources array missing or empty"))
    
    # Check resourceDetails
    details = parsed.get("resourceDetails", [])
    if details:
        results.append((PASS, f"resourceDetails has {len(details)} item(s)"))
        if details[0].get("url") and details[0].get("price") is not None:
            results.append((PASS, "resourceDetails[0] has url + price"))
        missing = [f for f in ["url", "name", "description", "price"] if f not in details[0]]
        if missing:
            results.append((WARN, f"resourceDetails[0] missing fields: {missing}"))
    else:
        results.append((WARN, "Missing resourceDetails (recommended)"))
    
    # Check baseGateway
    gw = parsed.get("baseGateway")
    if gw:
        results.append((PASS, "baseGateway block present"))
        for field in ["enabled", "network", "asset", "payTo", "gatewayUrl", "discoveryUrl", "openapiUrl"]:
            if field in gw:
                results.append((PASS, f"  baseGateway.{field} present"))
            else:
                results.append((WARN, f"  Missing baseGateway.{field}"))
    else:
        results.append((WARN, "Missing baseGateway block (recommended)"))
    
    return results


def check_status_code(status: int) -> list:
    """Check that the endpoint returns 402"""
    results = []
    if status == 402:
        results.append((PASS, f"HTTP status is 402 (Payment Required)"))
    elif status == 200:
        results.append((WARN, "HTTP status is 200 — endpoint may not have x402 paywall"))
        results.append((WARN, "  → Ensure x402 middleware runs before request validation"))
    else:
        results.append((WARN, f"HTTP status is {status} (expected 402)"))
    return results


def scan_endpoint(url: str) -> dict:
    """Full scan of a single endpoint"""
    print(f"\n{BOLD}{CYAN}═══ Scanning: {url} {RESET}")
    print("─" * 60)
    
    status, headers, body, parsed = fetch_url(url)
    
    results = {"status": [], "header": [], "body": [], "well_known": []}
    
    # 1. Check HTTP status
    results["status"] = check_status_code(status)
    
    # 2. Check Payment-Required header
    results["header"] = check_payment_required_header(headers)
    
    # 3. Check response body
    results["body"] = check_402_response_body(parsed)
    
    return results


def scan_discovery(base_url: str) -> list:
    """Scan /.well-known/x402"""
    print(f"\n{BOLD}{CYAN}═══ Well-Known Discovery: {base_url.rstrip('/')}/.well-known/x402 {RESET}")
    print("─" * 60)
    return check_well_known_x402(base_url)


def print_results(category: str, results: list):
    if not results:
        return
    print(f"\n  {BOLD}{category}{RESET}")
    for icon, msg in results:
        print(f"    {icon} {msg}")


def generate_fixes(results: dict, base_url: str) -> str:
    """Generate a summary of fixes needed"""
    fixes = []
    has_issues = False
    
    for cat, items in results.items():
        for icon, msg in items:
            if icon == FAIL:
                has_issues = True
                fixes.append(msg)
    
    if not has_issues:
        return ""
    
    output = f"\n{BOLD}{YELLOW}═══ FIXES NEEDED {RESET}\n"
    output += "─" * 60 + "\n"
    
    # Generate .well-known/x402 template if needed
    if any("404" in m or "missing" in m.lower() or "Missing" in m for _, m in results.get("header", []) + results.get("body", [])):
        output += f"\n{YELLOW}📋 /.well-known/x402 template:{RESET}\n"
        output += f"""```json
{{
  "version": 1,
  "resources": ["{base_url.rstrip('/')}/your-endpoint"],
  "resourceDetails": [
    {{
      "url": "{base_url.rstrip('/')}/your-endpoint",
      "name": "Your API",
      "description": "Paid endpoint",
      "price": 0.005
    }}
  ],
  "baseGateway": {{
    "enabled": true,
    "network": "eip155:8453",
    "networkLabel": "Base Mainnet",
    "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "assetLabel": "USDC",
    "payTo": "your-wallet-address",
    "gatewayUrl": "{base_url.rstrip('/')}",
    "discoveryUrl": "{base_url.rstrip('/')}/.well-known/x402",
    "openapiUrl": "{base_url.rstrip('/')}/openapi.json"
  }}
}}
```"""
    
    # Fix fields that use wrong names
    if any("payment_address" in m for _, m in results.get("header", [])):
        output += f"\n{YELLOW}🔧 Field rename needed:{RESET}\n"
        output += "  Replace 'payment_address' with 'payTo' in your Payment-Required header\n"
    
    if any("scheme" in m and "type" in m for _, m in results.get("header", [])):
        output += f"\n{YELLOW}🔧 Scheme field needed:{RESET}\n"
        output += "  Replace 'type' with 'scheme' in accepts[] and set it to 'exact'\n"
    
    if any("lowercase" in m for _, m in results.get("header", [])):
        output += f"\n{YELLOW}🔧 Address case fix:{RESET}\n"
        output += "  Normalize EVM asset addresses to lowercase hex\n"
    
    if any("number" in m for _, m in results.get("header", [])):
        output += f"\n{YELLOW}🔧 Amount format fix:{RESET}\n"
        output += "  Change amount fields from number to string (e.g. \"5000\" not 5000)\n"
    
    return output


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <url> [--full]")
        print(f"  --full    Also check /.well-known/x402 and /openapi.json")
        sys.exit(1)
    
    url = sys.argv[1]
    full = "--full" in sys.argv
    
    # Parse base URL
    base_url = url
    if "/" in url and url.count("/") >= 3:
        # Try to extract base
        parts = url.split("/")
        base_url = "/".join(parts[:3])  # https://host.com
    
    # Scan endpoint
    results = scan_endpoint(url)
    
    # Print per-category
    print_results("HTTP Status", results["status"])
    print_results("Payment-Required Header", results["header"])
    print_results("402 Response Body", results["body"])
    
    # Full scan
    if full:
        wk_results = scan_discovery(base_url)
        results["well_known"] = wk_results
        print_results("Discovery Endpoint", wk_results)
    
    # Generate fixes
    fixes = generate_fixes(results, base_url)
    if fixes:
        print(fixes)
    else:
        print(f"\n{GREEN}{BOLD}═══ FULLY COMPLIANT 🎉{RESET}")
    
    # Summary
    total_checks = sum(len(v) for v in results.values())
    passes = sum(1 for v in results.values() for icon, _ in v if icon == PASS)
    fails = sum(1 for v in results.values() for icon, _ in v if icon == FAIL)
    warns = sum(1 for v in results.values() for icon, _ in v if icon == WARN)
    
    print(f"\n{BOLD}Summary:{RESET} {GREEN}{passes} passed{RESET}, {RED}{fails} failed{RESET}, {YELLOW}{warns} warnings{RESET} ({total_checks} total checks)")
    
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
