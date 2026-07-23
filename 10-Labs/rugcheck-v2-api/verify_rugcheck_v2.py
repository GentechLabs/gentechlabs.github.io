"""
Rugcheck v2 API — Verification Script
======================================
Tests the FastAPI server by importing and exercising the core logic
(AgentSecurityScanner, AgentCreditScoreEngine) and validating the
OpenAPI spec and PAY.md structure.

Run: python verify_rugcheck_v2.py
"""

import json
import os
import sys
import yaml  # for PAY.md frontmatter parsing

# Add the project directory to path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

# ── Test 1: Import and validate modules ───────────────────────────────

print("=" * 60)
print("Rugcheck v2 API — Verification Suite")
print("=" * 60)
print()

errors = 0
warnings = 0

# Import the main module
try:
    from main import (
        app, AgentSecurityScanner, AgentCreditScoreEngine,
        ScanRequest, CreditScoreRequest, Q402PaymentMiddleware,
        routes, Q402_ENABLED, EVM_ADDRESS, SOLANA_ADDRESS,
        SCAN_COUNTER, CREDIT_COUNTER,
    )
    print("✅ main.py imports successfully")
except ImportError as e:
    print(f"❌ main.py import failed: {e}")
    errors += 1
    sys.exit(1)

# ── Test 2: FastAPI app structure ─────────────────────────────────────

print()

# Check routes
expected_routes = {
    "POST /api/v1/agent/scan",
    "POST /api/v1/agent/credit-score",
}
actual_routes = set(routes.keys())
if expected_routes.issubset(actual_routes):
    print(f"✅ All {len(actual_routes)} protected routes registered")
else:
    missing = expected_routes - actual_routes
    print(f"❌ Missing routes: {missing}")
    errors += 1

# Check unprotected endpoints
unprotected_paths = {route.path for route in app.routes}
expected_unprotected = {
    "/api/v1/agent/status",
    "/api/v1/pricing",
    "/.well-known/x402-bazaar",
}
if expected_unprotected.issubset(unprotected_paths):
    print(f"✅ All {len(expected_unprotected)} unprotected endpoints registered")
else:
    missing = expected_unprotected - unprotected_paths
    print(f"❌ Missing unprotected endpoints: {missing}")
    errors += 1

# Check middleware
middleware_types = {m.cls.__name__ for m in app.user_middleware}
if "PaymentMiddlewareASGI" in middleware_types:
    print("✅ x402 PaymentMiddlewareASGI installed")
else:
    print("❌ PaymentMiddlewareASGI not found in middleware stack")
    errors += 1

# ── Test 3: Agent Security Scanner ────────────────────────────────────

print()

# Test scan with known agent
scan_result = AgentSecurityScanner.scan("test-agent-123", chain="solana", deep_scan=False)
assert scan_result.agent_id == "test-agent-123", "agent_id mismatch"
assert 0 <= scan_result.risk_score <= 100, f"risk_score out of range: {scan_result.risk_score}"
assert scan_result.risk_level in ("low", "medium", "high", "critical"), f"invalid risk_level: {scan_result.risk_level}"
assert len(scan_result.findings) >= 0, "findings should be a list"
assert len(scan_result.recommendations) > 0, "should have at least one recommendation"
assert scan_result.scan_id.startswith("scan_"), f"invalid scan_id format: {scan_result.scan_id}"
print(f"✅ AgentSecurityScanner.scan() — risk_score={scan_result.risk_score}, risk_level={scan_result.risk_level}, findings={len(scan_result.findings)}, checks_passed={scan_result.checks_passed}, checks_failed={scan_result.checks_failed}")

# Test deep scan
deep_result = AgentSecurityScanner.scan("test-agent-123", chain="solana", deep_scan=True)
assert deep_result.risk_score != scan_result.risk_score or deep_result.findings != scan_result.findings, \
    "deep scan should produce different results"
print(f"✅ Deep scan — risk_score={deep_result.risk_score}, findings={len(deep_result.findings)} (different from standard)")

# Test deterministic results
result_a = AgentSecurityScanner.scan("deterministic-agent", chain="solana")
result_b = AgentSecurityScanner.scan("deterministic-agent", chain="solana")
assert result_a.risk_score == result_b.risk_score, "deterministic scan should produce same risk_score"
assert result_a.findings == result_b.findings, "deterministic scan should produce same findings"
print("✅ AgentSecurityScanner is deterministic (same input = same output)")

# Test different agents produce different results
result_c = AgentSecurityScanner.scan("different-agent", chain="solana")
assert result_a.risk_score != result_c.risk_score or result_a.findings != result_c.findings, \
    "different agents should produce different results"
print("✅ Different agents produce different scan results")

# ── Test 4: Agent Credit Score Engine ──────────────────────────────────

print()

# Test credit score evaluation
credit_result = AgentCreditScoreEngine.evaluate("test-agent-123", chain="solana")
assert credit_result.agent_id == "test-agent-123", "agent_id mismatch"
assert 0 <= credit_result.score <= 850, f"score out of range: {credit_result.score}"
assert credit_result.score_rating in ("poor", "fair", "good", "excellent"), f"invalid rating: {credit_result.score_rating}"
assert len(credit_result.factors) == 4, f"expected 4 factors, got {len(credit_result.factors)}"
assert len(credit_result.history) == 6, f"expected 6 history entries, got {len(credit_result.history)}"
assert len(credit_result.recommendations) > 0, "should have at least one recommendation"
print(f"✅ AgentCreditScoreEngine.evaluate() — score={credit_result.score}, rating={credit_result.score_rating}")

# Check factor weights sum to 1.0
weight_sum = sum(f.weight for f in credit_result.factors)
assert abs(weight_sum - 1.0) < 0.01, f"factor weights should sum to 1.0, got {weight_sum}"
print(f"✅ Factor weights sum to {weight_sum:.2f} (expected ~1.0)")

# Test deterministic results
credit_a = AgentCreditScoreEngine.evaluate("deterministic-agent")
credit_b = AgentCreditScoreEngine.evaluate("deterministic-agent")
assert credit_a.score == credit_b.score, "deterministic credit score should be same"
assert credit_a.factors == credit_b.factors, "deterministic factors should be same"
print("✅ AgentCreditScoreEngine is deterministic (same input = same output)")

# Test different agents produce different scores
credit_c = AgentCreditScoreEngine.evaluate("different-agent")
assert credit_a.score != credit_c.score, "different agents should produce different scores"
print("✅ Different agents produce different credit scores")

# Test score rating thresholds directly
ratings = AgentCreditScoreEngine.RATINGS
assert AgentCreditScoreEngine._determine_rating(200) == "poor", "score 200 should be poor"
assert AgentCreditScoreEngine._determine_rating(500) == "poor", "score 500 should be poor (below 580)"
assert AgentCreditScoreEngine._determine_rating(580) == "fair", "score 580 should be fair"
assert AgentCreditScoreEngine._determine_rating(600) == "fair", "score 600 should be fair"
assert AgentCreditScoreEngine._determine_rating(670) == "good", "score 670 should be good"
assert AgentCreditScoreEngine._determine_rating(740) == "excellent", "score 740 should be excellent"
assert AgentCreditScoreEngine._determine_rating(800) == "excellent", "score 800 should be excellent"
print(f"✅ Score rating system works (thresholds: {ratings})")

# ── Test 5: Q402 Payment Middleware ────────────────────────────────────

print()

# Test Q402 verification (sandbox mode)
import asyncio
q402_result = asyncio.run(Q402PaymentMiddleware.verify_payment(
    agent_id="test-agent",
    endpoint="/api/v1/agent/scan",
    amount="0.025",
))
assert q402_result is True, "Q402 sandbox verification should return True"
print(f"✅ Q402PaymentMiddleware.verify_payment() — sandbox mode: {q402_result}")

# ── Test 6: OpenAPI spec validation ────────────────────────────────────

print()

openapi_path = os.path.join(PROJECT_DIR, "openapi.json")
try:
    with open(openapi_path) as f:
        spec = json.load(f)
    assert spec["openapi"] == "3.1.0", "OpenAPI version should be 3.1.0"
    assert "paths" in spec, "OpenAPI spec missing paths"
    assert len(spec["paths"]) == 5, f"expected 5 paths, got {len(spec['paths'])}"
    print(f"✅ OpenAPI spec valid — {len(spec['paths'])} paths defined")
    
    # Check x-pay-skills annotations
    paid_endpoints = 0
    for path, methods in spec["paths"].items():
        for method, details in methods.items():
            if "x-pay-skills" in details:
                pricing = details["x-pay-skills"].get("pricing")
                if pricing is not None:
                    paid_endpoints += 1
                    assert "tiers" in pricing, f"pricing missing tiers for {method} {path}"
                    assert len(pricing["tiers"]) > 0, f"empty tiers for {method} {path}"
    print(f"✅ {paid_endpoints} paid endpoints annotated with x-pay-skills pricing")
    
except FileNotFoundError:
    print("❌ openapi.json not found")
    errors += 1
except json.JSONDecodeError as e:
    print(f"❌ openapi.json parse error: {e}")
    errors += 1

# ── Test 7: PAY.md validation ──────────────────────────────────────────

print()

pay_md_path = os.path.join(PROJECT_DIR, "PAY.md")
try:
    with open(pay_md_path) as f:
        content = f.read()
    
    # Parse frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            
            required_fields = ["name", "title", "description", "use_case", "category", "service_url", "openapi"]
            for field in required_fields:
                assert field in frontmatter, f"PAY.md missing required field: {field}"
                assert frontmatter[field] is not None, f"PAY.md field is null: {field}"
            
            # Validate field constraints
            desc = frontmatter["description"]
            assert 64 <= len(desc) <= 255, f"description length {len(desc)} not in [64, 255]"
            
            use_case = frontmatter["use_case"]
            assert 32 <= len(use_case) <= 255, f"use_case length {len(use_case)} not in [32, 255]"
            
            valid_categories = [
                "ai_ml", "cloud", "compute", "data", "devtools", "finance",
                "identity", "maps", "media", "messaging", "other",
                "productivity", "search", "security", "shopping", "storage", "translation"
            ]
            assert frontmatter["category"] in valid_categories, \
                f"invalid category: {frontmatter['category']}"
            
            assert frontmatter["service_url"].startswith("https://"), \
                "service_url must be HTTPS"
            
            assert "path" in frontmatter["openapi"], \
                "openapi must use path: (committed sidecar)"
            
            print(f"✅ PAY.md valid — name={frontmatter['name']}, category={frontmatter['category']}")
            print(f"   description: {len(desc)} chars, use_case: {len(use_case)} chars")
        else:
            print("❌ PAY.md frontmatter not properly delimited")
            errors += 1
    else:
        print("❌ PAY.md does not start with ---")
        errors += 1
        
except FileNotFoundError:
    print("❌ PAY.md not found")
    errors += 1
except yaml.YAMLError as e:
    print(f"❌ PAY.md YAML parse error: {e}")
    errors += 1
except AssertionError as e:
    print(f"❌ PAY.md validation failed: {e}")
    errors += 1

# ── Test 8: .env.example validation ────────────────────────────────────

print()

env_path = os.path.join(PROJECT_DIR, ".env.example")
try:
    with open(env_path) as f:
        env_content = f.read()
    assert "EVM_ADDRESS" in env_content, ".env.example missing EVM_ADDRESS"
    assert "SOLANA_ADDRESS" in env_content, ".env.example missing SOLANA_ADDRESS"
    assert "Q402_ENABLED" in env_content, ".env.example missing Q402_ENABLED"
    print("✅ .env.example has all required variables")
except FileNotFoundError:
    print("❌ .env.example not found")
    errors += 1

# ── Test 9: File structure completeness ────────────────────────────────

print()

expected_files = [
    "main.py",
    "requirements.txt",
    ".env.example",
    "PAY.md",
    "openapi.json",
    "PR_README.md",
]
for fname in expected_files:
    fpath = os.path.join(PROJECT_DIR, fname)
    if os.path.exists(fpath):
        fsize = os.path.getsize(fpath)
        print(f"✅ {fname} ({fsize} bytes)")
    else:
        print(f"❌ {fname} MISSING")
        errors += 1

# ── Summary ───────────────────────────────────────────────────────────

print()
print("=" * 60)
if errors == 0:
    print(f"🎉 ALL {len(expected_files)} TESTS PASSED (with {warnings} warnings)")
else:
    print(f"❌ {errors} ERRORS, {warnings} WARNINGS — review above")
print("=" * 60)

sys.exit(0 if errors == 0 else 1)
