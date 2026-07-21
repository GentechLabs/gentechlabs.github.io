#!/usr/bin/env python3
"""
Agent Arcade Phase 1 — Spec Verification Script
================================================
Validates that the architecture spec at 10-Labs/agent-arcade-build-queue.md
covers all required components, has no structural issues, and is internally
consistent.

Usage:
    python verify_agent_arcade_spec.py
"""

import re
import sys
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

SPEC_PATH = Path(
    r"C:\Users\jhitm\Desktop\GenTech_Agency\gentech-vault-new"
    r"\10-Labs\agent-arcade-build-queue.md"
)

REQUIRED_SECTIONS = [
    "Architecture Overview",
    "Game Protocol",
    "x402",
    "Q402",
    "ARC",
    "Lobby",
    "Poker Cabinet",
    "Implementation Phases",
    "Risk Analysis",
    "Agent SDK",
    "Directory Structure",
    "Key Design Decisions",
    "Success Criteria",
]

REQUIRED_MCP_TOOLS = ["join", "act", "observe", "leave", "rebuy", "list_tables"]

REQUIRED_REFERENCES = [
    "gentech_strategy.py",
    "gentech-mcp-server.py",
    "gentech_agent_kit.py",
    "poker-arena",
]

REQUIRED_WEEKS = ["Week 1", "Week 2", "Week 3", "Week 4"]

# ── Checks ──────────────────────────────────────────────────────────────────

def read_spec() -> str:
    """Read the spec file."""
    if not SPEC_PATH.exists():
        print(f"❌ Spec file not found: {SPEC_PATH}")
        sys.exit(1)
    text = SPEC_PATH.read_text(encoding="utf-8")
    print(f"✅ Spec file found: {SPEC_PATH.name} ({len(text):,} bytes, {len(text.splitlines())} lines)")
    return text


def check_sections(text: str) -> list[str]:
    """Check that all required sections exist."""
    missing = []
    for section in REQUIRED_SECTIONS:
        # Check for section header (## or ###)
        pattern = rf"^#{{2,3}}\s+.*{re.escape(section)}.*$"
        if not re.search(pattern, text, re.MULTILINE):
            missing.append(section)
    return missing


def check_mcp_tools(text: str) -> list[str]:
    """Check that all required MCP tools are documented."""
    missing = []
    for tool in REQUIRED_MCP_TOOLS:
        if tool not in text:
            missing.append(tool)
    return missing


def check_references(text: str) -> list[str]:
    """Check that existing code references are mentioned."""
    missing = []
    for ref in REQUIRED_REFERENCES:
        if ref not in text:
            missing.append(ref)
    return missing


def check_weeks(text: str) -> list[str]:
    """Check that all 4 implementation weeks are present."""
    missing = []
    for week in REQUIRED_WEEKS:
        if week not in text:
            missing.append(week)
    return missing


def check_architecture_diagram(text: str) -> bool:
    """Check for ASCII architecture diagram."""
    # Look for box-drawing characters
    return bool(re.search(r'[┌┐└┘├┤┬┴┼│─]', text))


def check_payment_flow(text: str) -> bool:
    """Check for payment flow diagram."""
    return "x402 PAYMENT FLOW" in text or "402 challenge" in text


def check_token_spec(text: str) -> bool:
    """Check for ARC token specification table."""
    return "ARC" in text and "ERC-20" in text and "Base" in text


def check_lobby_mockup(text: str) -> bool:
    """Check for lobby UI mockup."""
    return "AGENT ARCADE" in text and "Connect Wallet" in text


def check_risk_table(text: str) -> bool:
    """Check for risk analysis table."""
    return "Probability" in text and "Impact" in text and "Mitigation" in text


def check_success_criteria(text: str) -> bool:
    """Check for success criteria with metrics."""
    return "Metric" in text and "Target" in text and "Measurement" in text


def check_code_snippets(text: str) -> bool:
    """Check for code blocks."""
    code_blocks = re.findall(r'```', text)
    return len(code_blocks) >= 4  # At least 2 code blocks (opening + closing)


def check_internal_consistency(text: str) -> list[str]:
    """Check for internal consistency issues."""
    issues = []

    # Check that MCP tools mentioned in protocol section match the tool list
    tool_section = re.search(r'### 2\.1 MCP Tool Definitions(.*?)###', text, re.DOTALL)
    if tool_section:
        section_text = tool_section.group(1)
        for tool in REQUIRED_MCP_TOOLS:
            if f'"name": "{tool}"' not in section_text:
                issues.append(f"MCP tool '{tool}' not found in tool definitions section")

    # Check that weeks mentioned in phases section match
    phase_section = re.search(r'## 7\. Implementation Phases(.*?)## 8\.', text, re.DOTALL)
    if phase_section:
        section_text = phase_section.group(1)
        for week in REQUIRED_WEEKS:
            if week not in section_text:
                issues.append(f"Implementation phase '{week}' not found in phases section")

    return issues


def check_ascii_art_quality(text: str) -> list[str]:
    """Check ASCII art for common issues."""
    issues = []
    lines = text.splitlines()
    in_ascii = False
    ascii_start = 0

    for i, line in enumerate(lines):
        if line.startswith("```") and in_ascii:
            in_ascii = False
        elif line.startswith("```"):
            in_ascii = True
            ascii_start = i
        elif in_ascii and any(c in line for c in '┌┐└┘├┤┬┴┼│─'):
            # Check for ragged right edges in box-drawing
            pass  # Would need more sophisticated analysis

    return issues


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Agent Arcade Phase 1 — Spec Verification")
    print("=" * 60)
    print()

    text = read_spec()
    print()

    # ── Section coverage ────────────────────────────────────────────────
    print("📋 Section Coverage:")
    missing = check_sections(text)
    if missing:
        for s in missing:
            print(f"  ❌ Missing section: {s}")
    else:
        print(f"  ✅ All {len(REQUIRED_SECTIONS)} required sections present")
    print()

    # ── MCP Tools ──────────────────────────────────────────────────────
    print("🔧 MCP Tool Definitions:")
    missing_tools = check_mcp_tools(text)
    if missing_tools:
        for t in missing_tools:
            print(f"  ❌ Missing tool: {t}")
    else:
        print(f"  ✅ All {len(REQUIRED_MCP_TOOLS)} MCP tools documented")
    print()

    # ── Code References ─────────────────────────────────────────────────
    print("📎 Existing Code References:")
    missing_refs = check_references(text)
    if missing_refs:
        for r in missing_refs:
            print(f"  ❌ Missing reference: {r}")
    else:
        print(f"  ✅ All {len(REQUIRED_REFERENCES)} code references present")
    print()

    # ── Implementation Phases ───────────────────────────────────────────
    print("📅 Implementation Phases:")
    missing_weeks = check_weeks(text)
    if missing_weeks:
        for w in missing_weeks:
            print(f"  ❌ Missing week: {w}")
    else:
        print(f"  ✅ All {len(REQUIRED_WEEKS)} implementation weeks present")
    print()

    # ── Architecture Diagram ────────────────────────────────────────────
    print("🏗️  Architecture Diagram:")
    if check_architecture_diagram(text):
        print("  ✅ ASCII architecture diagram present")
    else:
        print("  ❌ No ASCII architecture diagram found")
    print()

    # ── Payment Flow ────────────────────────────────────────────────────
    print("💰 Payment Flow:")
    if check_payment_flow(text):
        print("  ✅ x402/Q402 payment flow documented")
    else:
        print("  ❌ No payment flow documentation found")
    print()

    # ── Token Spec ──────────────────────────────────────────────────────
    print("🪙 ARC Token Specification:")
    if check_token_spec(text):
        print("  ✅ ARC token spec present (ERC-20 on Base)")
    else:
        print("  ❌ No ARC token specification found")
    print()

    # ── Lobby Mockup ────────────────────────────────────────────────────
    print("🕹️  Lobby UI Mockup:")
    if check_lobby_mockup(text):
        print("  ✅ ASCII lobby mockup present")
    else:
        print("  ❌ No lobby UI mockup found")
    print()

    # ── Risk Analysis ──────────────────────────────────────────────────
    print("⚠️  Risk Analysis:")
    if check_risk_table(text):
        print("  ✅ Risk analysis table present")
    else:
        print("  ❌ No risk analysis table found")
    print()

    # ── Success Criteria ────────────────────────────────────────────────
    print("🎯 Success Criteria:")
    if check_success_criteria(text):
        print("  ✅ Success criteria with metrics present")
    else:
        print("  ❌ No success criteria found")
    print()

    # ── Code Snippets ──────────────────────────────────────────────────
    print("💻 Code Snippets:")
    if check_code_snippets(text):
        print("  ✅ Code blocks present")
    else:
        print("  ❌ No code blocks found")
    print()

    # ── Internal Consistency ────────────────────────────────────────────
    print("🔗 Internal Consistency:")
    issues = check_internal_consistency(text)
    if issues:
        for i in issues:
            print(f"  ⚠️  {i}")
    else:
        print("  ✅ No consistency issues detected")
    print()

    # ── Summary ─────────────────────────────────────────────────────────
    print("=" * 60)
    total_checks = 12
    passed = 0
    failed = 0

    checks = [
        ("Sections", len(missing) == 0),
        ("MCP Tools", len(missing_tools) == 0),
        ("References", len(missing_refs) == 0),
        ("Weeks", len(missing_weeks) == 0),
        ("Arch Diagram", check_architecture_diagram(text)),
        ("Payment Flow", check_payment_flow(text)),
        ("Token Spec", check_token_spec(text)),
        ("Lobby Mockup", check_lobby_mockup(text)),
        ("Risk Analysis", check_risk_table(text)),
        ("Success Criteria", check_success_criteria(text)),
        ("Code Snippets", check_code_snippets(text)),
        ("Consistency", len(issues) == 0),
    ]

    for name, ok in checks:
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"  Results: {passed}/{total_checks} checks passed, {failed} failed")
    if failed == 0:
        print("  ✅ ALL CHECKS PASSED — Spec is complete and consistent")
    else:
        print(f"  ⚠️  {failed} check(s) failed — review above")
    print("=" * 60)


if __name__ == "__main__":
    main()
