#!/usr/bin/env python3
"""
Agent Health Verification Script

Checks for discrepancies between Hermes agent processes (running) and
coordination board status (ONLINE/OFFLINE flags). Used during wrap-up
or mid-shift coordination checks when agent presence is in question.

Usage: python verify_agent_presence.py
Output: List of agents with mismatched state (process running but board OFFLINE)
"""

import subprocess
import os
from datetime import datetime

VAULT_ROOT = "/root/vaults/gentech"
COORD_BOARD = os.path.join(VAULT_ROOT, "11-Mess Hall", "agent-coordination-board.md")

def get_running_agents():
    """Return set of agent profile names with running hermes processes."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True, text=True
    )
    agents = set()
    for line in result.stdout.splitlines():
        if "hermes" in line and "profile" in line and "grep" not in line and "python" in line:
            # Extract profile name: --profile <name>
            parts = line.split()
            if "--profile" in parts:
                idx = parts.index("--profile")
                if idx + 1 < len(parts):
                    agents.add(parts[idx + 1])
    return agents

def get_board_status():
    """Parse agent-coordination-board.md and return {agent: status}."""
    status_map = {}
    if not os.path.exists(COORD_BOARD):
        return status_map
    with open(COORD_BOARD) as f:
        for line in f:
            if "|" in line and ("ONLINE" in line or "OFFLINE" in line):
                cells = [c.strip() for c in line.split("|")]
                # Expected: | Agent | Last Check-In | Current Task | Status | Notes |
                if len(cells) >= 4:
                    agent = cells[1]
                    status = cells[3]
                    if agent and status in ("ONLINE", "OFFLINE"):
                        status_map[agent] = status
    return status_map

def main():
    print("=== Agent Health Verification ===\n")
    running = get_running_agents()
    board = get_board_status()
    print(f"Running agents: {sorted(running)}")
    print(f"Board entries: {board}")

    mismatches = []
    for agent, status in board.items():
        if status == "OFFLINE" and agent in running:
            mismatches.append((agent, "board shows OFFLINE but process is RUNNING"))
        elif status == "ONLINE" and agent not in running:
            mismatches.append((agent, "board shows ONLINE but process NOT found"))

    if not mismatches:
        print("\n✅ No discrepancies detected — coordination board matches process state.")
    else:
        print("\n🚨 Discrepancies found:")
        for agent, reason in mismatches:
            print(f"  - {agent}: {reason}")
        print("\n→ ACTION: Agents must update their status on agent-coordination-board.md immediately.")
        print("  If process is running but board is OFFLINE → mark as ONLINE with timestamp.")
        print("  If process is dead but board is ONLINE → start agent or mark OFFLINE.")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
