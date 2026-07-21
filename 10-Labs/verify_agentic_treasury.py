#!/usr/bin/env python3
"""
Agentic Treasury Spec — Verification Script
Validates that 10-Labs/agentic-treasury-spec.md is complete and consistent.
Checks: section presence, contract interfaces, Q402 tool mapping, cross-references.
"""

import re
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).parent / "agentic-treasury-spec.md"

# ── Required Sections ──────────────────────────────────────────────────────

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Architecture Overview",
    "Pillar 1: Yield Brain (AAE)",
    "Pillar 2: Payment Router (x402 Mesh)",
    "Pillar 3: P2P Causes (Funding Platform)",
    "Smart Contract Interfaces",
    "x402 / Q402 Integration Points",
    "Agent Interaction Flows",
    "Implementation Phases",
    "Risk Analysis",
    "Appendix: Q402 Tool Reference",
]

# ── Required Contract Interfaces ───────────────────────────────────────────

REQUIRED_INTERFACES = [
    "IYieldBrain",
    "IPaymentRouter",
    "IP2PCauses",
]

REQUIRED_FUNCTIONS = {
    "IYieldBrain": ["deposit", "withdraw", "rebalance", "setEnforcement", "getAgentPortfolio"],
    "IPaymentRouter": ["selectRoute", "routePayment", "quoteRoute"],
    "IP2PCauses": ["createCause", "contribute", "createEscrow", "completeMilestone", "disputeMilestone", "cancelCause", "getContributorReputation"],
}

# ── Required Q402 Tools ───────────────────────────────────────────────────

REQUIRED_Q402_TOOLS = [
    "q402_yield_reserves",
    "q402_yield_deposit",
    "q402_yield_withdraw",
    "q402_request_create",
    "q402_request_pay",
    "q402_escrow_create",
    "q402_escrow_lock",
    "q402_escrow_release",
]

# ── Required Cross-References ──────────────────────────────────────────────

REQUIRED_REFERENCES = [
    "AAE-Six-Layer-Architecture.md",
    "AAE-Layers-Overview.md",
    "x402-AAE-Integration-Map.md",
    "x402-multi-facilitator-example",
    "p2p_causes.py",
    "aae_deploy_flow.py",
    "agent-rug-2.0-spec.md",
]

# ── Required Architecture Elements ─────────────────────────────────────────

REQUIRED_ARCH_ELEMENTS = [
    "AAE Layer 6",
    "Enforcement",
    "CDP",
    "GoPlausible",
    "Q402",
    "Bazaar",
    "ERC-8004",
    "EIP-3009",
    "gasless",
    "multi-facilitator",
    "two-phase consent",
    "recipient allowlist",
    "max amount",
    "milestone",
    "escrow",
    "arbiter",
]

# ── Required Implementation Phases ─────────────────────────────────────────

REQUIRED_PHASES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]

# ── Required Risk Categories ───────────────────────────────────────────────

REQUIRED_RISK_CATEGORIES = [
    "Smart Contract Risks",
    "Economic Risks",
    "Operational Risks",
]


def read_spec() -> str:
    """Read the spec file."""
    if not SPEC_PATH.exists():
        print(f"❌ SPEC NOT FOUND: {SPEC_PATH}")
        sys.exit(1)
    return SPEC_PATH.read_text(encoding="utf-8")


def check_sections(text: str) -> list[str]:
    """Check that all required sections exist."""
    errors = []
    for section in REQUIRED_SECTIONS:
        # Check for section header with optional numbering (## 1. Section Name)
        pattern = re.compile(
            r'^#{2,3}\s+\d*\.?\s*' + re.escape(section), re.MULTILINE
        )
        if not pattern.search(text):
            errors.append(f"Missing section: '{section}'")
    return errors


def check_interfaces(text: str) -> list[str]:
    """Check that all required contract interfaces and functions exist."""
    errors = []
    for iface in REQUIRED_INTERFACES:
        if iface not in text:
            errors.append(f"Missing interface: '{iface}'")
            continue
        for func in REQUIRED_FUNCTIONS[iface]:
            if func not in text:
                errors.append(f"Missing function '{func}' in interface '{iface}'")
    return errors


def check_q402_tools(text: str) -> list[str]:
    """Check that all required Q402 tools are documented."""
    errors = []
    for tool in REQUIRED_Q402_TOOLS:
        if tool not in text:
            errors.append(f"Missing Q402 tool: '{tool}'")
    return errors


def check_references(text: str) -> list[str]:
    """Check that all required cross-references exist."""
    errors = []
    for ref in REQUIRED_REFERENCES:
        if ref not in text:
            errors.append(f"Missing reference: '{ref}'")
    return errors


def check_architecture_elements(text: str) -> list[str]:
    """Check that all required architecture elements are mentioned."""
    errors = []
    for elem in REQUIRED_ARCH_ELEMENTS:
        if elem.lower() not in text.lower():
            errors.append(f"Missing architecture element: '{elem}'")
    return errors


def check_phases(text: str) -> list[str]:
    """Check that all implementation phases exist."""
    errors = []
    for phase in REQUIRED_PHASES:
        if phase not in text:
            errors.append(f"Missing implementation phase: '{phase}'")
    return errors


def check_risk_categories(text: str) -> list[str]:
    """Check that all required risk categories exist."""
    errors = []
    for cat in REQUIRED_RISK_CATEGORIES:
        if cat not in text:
            errors.append(f"Missing risk category: '{cat}'")
    return errors


def check_ascii_diagrams(text: str) -> list[str]:
    """Check that ASCII architecture diagrams exist."""
    errors = []
    # Look for box-drawing characters
    if '┌' not in text or '┐' not in text or '│' not in text:
        errors.append("Missing ASCII architecture diagram (box-drawing chars)")
    return errors


def check_code_blocks(text: str) -> list[str]:
    """Check that Solidity and Python code blocks exist."""
    errors = []
    if '```solidity' not in text:
        errors.append("Missing Solidity code blocks")
    if '```python' not in text:
        errors.append("Missing Python code blocks")
    if '```json' not in text:
        errors.append("Missing JSON code blocks")
    return errors


def check_flow_descriptions(text: str) -> list[str]:
    """Check that agent interaction flows are documented."""
    errors = []
    required_flows = [
        "Yield Optimization Flow",
        "Payment Routing Flow",
        "P2P Funding Flow",
    ]
    for flow in required_flows:
        if flow not in text:
            errors.append(f"Missing agent interaction flow: '{flow}'")
    return errors


def check_emergency_procedures(text: str) -> list[str]:
    """Check that emergency procedures exist."""
    errors = []
    if "Emergency Procedures" not in text:
        errors.append("Missing Emergency Procedures section")
    return errors


def check_tool_reference_table(text: str) -> list[str]:
    """Check that the Q402 tool reference appendix has tables."""
    errors = []
    # Look for markdown tables (lines with |---| or |---|---|)
    if not re.search(r'^\|[-]+\|', text, re.MULTILINE):
        errors.append("Missing markdown tables in tool reference")
    return errors


def main():
    print(f"🔍 Verifying: {SPEC_PATH}")
    print(f"   Size: {SPEC_PATH.stat().st_size:,} bytes\n")

    text = read_spec()

    all_errors = []
    all_errors.extend(check_sections(text))
    all_errors.extend(check_interfaces(text))
    all_errors.extend(check_q402_tools(text))
    all_errors.extend(check_references(text))
    all_errors.extend(check_architecture_elements(text))
    all_errors.extend(check_phases(text))
    all_errors.extend(check_risk_categories(text))
    all_errors.extend(check_ascii_diagrams(text))
    all_errors.extend(check_code_blocks(text))
    all_errors.extend(check_flow_descriptions(text))
    all_errors.extend(check_emergency_procedures(text))
    all_errors.extend(check_tool_reference_table(text))

    # ── Summary ──────────────────────────────────────────────────────────
    total_checks = (
        len(REQUIRED_SECTIONS)
        + len(REQUIRED_INTERFACES) + sum(len(v) for v in REQUIRED_FUNCTIONS.values())
        + len(REQUIRED_Q402_TOOLS)
        + len(REQUIRED_REFERENCES)
        + len(REQUIRED_ARCH_ELEMENTS)
        + len(REQUIRED_PHASES)
        + len(REQUIRED_RISK_CATEGORIES)
        + 4  # ascii diagrams, code blocks, flows, emergency
    )

    if not all_errors:
        print(f"✅ ALL {total_checks} CHECKS PASSED")
        print(f"   Sections: {len(REQUIRED_SECTIONS)}/{len(REQUIRED_SECTIONS)}")
        print(f"   Interfaces: {len(REQUIRED_INTERFACES)}/{len(REQUIRED_INTERFACES)}")
        print(f"   Q402 Tools: {len(REQUIRED_Q402_TOOLS)}/{len(REQUIRED_Q402_TOOLS)}")
        print(f"   References: {len(REQUIRED_REFERENCES)}/{len(REQUIRED_REFERENCES)}")
        print(f"   Arch Elements: {len(REQUIRED_ARCH_ELEMENTS)}/{len(REQUIRED_ARCH_ELEMENTS)}")
        print(f"   Phases: {len(REQUIRED_PHASES)}/{len(REQUIRED_PHASES)}")
        print(f"   Risk Categories: {len(REQUIRED_RISK_CATEGORIES)}/{len(REQUIRED_RISK_CATEGORIES)}")
        print(f"   Diagrams: ✅ | Code Blocks: ✅ | Flows: ✅ | Emergency: ✅")
        return 0
    else:
        print(f"❌ {len(all_errors)} FAILURES FOUND:\n")
        for err in all_errors:
            print(f"   • {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
