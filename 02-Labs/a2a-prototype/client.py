"""
DMOB A2A Client — Test Script
==============================
Sends tasks to the DMOB A2A server and prints results.

Usage:
    # Start server first: .venv/bin/python server.py
    .venv/bin/python client.py
"""

import asyncio
import json
import httpx


BASE_URL = "http://localhost:8383"
A2A_URL = f"{BASE_URL}/a2a"


async def get_agent_card(client: httpx.AsyncClient):
    """Discover the agent's capabilities."""
    resp = await client.get(f"{BASE_URL}/.well-known/agent-card.json")
    card = resp.json()
    print("=" * 60)
    print("📋 AGENT CARD DISCOVERED")
    print("=" * 60)
    print(f"  Name:        {card.get('name')}")
    print(f"  Description: {card.get('description', '')[:80]}...")
    print(f"  Version:     {card.get('version')}")
    print(f"  Provider:    {card.get('provider', {}).get('organization')}")
    print()
    skills = card.get("skills", [])
    print(f"  Skills ({len(skills)}):")
    for s in skills:
        print(f"    • {s.get('name')}: {s.get('description', '')[:60]}...")
        print(f"      Tags: {', '.join(s.get('tags', []))}")
    print()
    interfaces = card.get("supportedInterfaces", [])
    print(f"  Interfaces ({len(interfaces)}):")
    for i in interfaces:
        print(f"    • {i.get('protocolBinding')}: {i.get('url')}")
    print()
    return card


async def send_task(client: httpx.AsyncClient, message: str, skill_name: str):
    """Send a task to the agent via JSON-RPC."""
    print("=" * 60)
    print(f"📨 SENDING TASK: {skill_name}")
    print(f"   Message: {message[:80]}...")
    print("=" * 60)

    # JSON-RPC request
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"text": message}],
            },
        },
    }

    resp = await client.post(A2A_URL, json=payload)
    result = resp.json()

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return result

    # Parse the result
    task = result.get("result", {})
    status = task.get("status", {})
    state = status.get("state", "unknown")

    print(f"\n📊 Task State: {state}")

    # Get artifacts
    artifacts = task.get("artifacts", [])
    if artifacts:
        for art in artifacts:
            name = art.get("name", "unnamed")
            parts = art.get("parts", [])
            print(f"\n📦 Artifact: {name}")
            for part in parts:
                text = part.get("text", "")
                try:
                    parsed = json.loads(text)
                    print(json.dumps(parsed, indent=2))
                except (json.JSONDecodeError, TypeError):
                    print(text)
    else:
        # Check for message
        history = task.get("history", [])
        for msg in history:
            for part in msg.get("parts", []):
                print(f"💬 {part.get('text', '')}")

    print()
    return result


async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Discover agent
        await get_agent_card(client)

        # 2. Solidity audit
        await send_task(
            client,
            "Audit this Solidity contract for security vulnerabilities:\n"
            "pragma solidity ^0.8.19;\n\n"
            "contract Vault {\n"
            "    mapping(address => uint256) public balances;\n"
            "    address public owner;\n"
            "    bool public paused;\n\n"
            "    function deposit() public payable {\n"
            "        require(!paused, 'Paused');\n"
            "        balances[msg.sender] += msg.value;\n"
            "    }\n\n"
            "    function withdraw(uint256 amount) public {\n"
            "        require(balances[msg.sender] >= amount);\n"
            "        (bool success, ) = msg.sender.call{value: amount}(\"\");\n"
            "        balances[msg.sender] -= amount;\n"
            "    }\n\n"
            "    function pause() public { require(msg.sender == owner); paused = true; }\n"
            "}",
            "solidity_audit",
        )

        # 3. Gas optimization
        await send_task(
            client,
            "Optimize gas for this contract with storage reads in loops",
            "gas_optimization",
        )

        # 4. Protocol review
        await send_task(
            client,
            "Review this lending protocol design for game theory attack vectors",
            "protocol_review",
        )

        print("=" * 60)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
