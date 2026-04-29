"""
DMOB A2A Server — Proof of Concept
===================================
Exposes DMOB's security audit capabilities via the A2A protocol.
Other agents can discover, delegate tasks to, and receive results from DMOB.

Usage:
    .venv/bin/python server.py
    # Server runs at http://localhost:8383
    # Agent Card: http://localhost:8383/.well-known/agent-card.json
"""

import asyncio
import contextlib
import json
import logging
import time
import uuid

from fastapi import FastAPI
import uvicorn

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentProvider,
    AgentSkill,
    Part,
    Task,
    TaskState,
    TaskStatus,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dmob-a2a")


# ─── Agent Card ───────────────────────────────────────────────────────────────
# This is what other agents see when they discover us.

AGENT_CARD = AgentCard(
    name="DMOB",
    description=(
        "Security audit agent for smart contracts. Specializes in Solidity "
        "vulnerability analysis, gas optimization, and DeFi protocol review. "
        "Part of the Gentech agent ecosystem."
    ),
    version="0.1.0",
    provider=AgentProvider(
        organization="Gentech Labs",
        url="https://gentech.dev",
    ),
    documentation_url="https://gentech.dev/docs/dmob",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=True,
        extended_agent_card=False,
    ),
    default_input_modes=["text/plain", "application/json"],
    default_output_modes=["text/plain", "application/json"],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="1.0",
            url="http://localhost:8383/a2a",
        ),
        AgentInterface(
            protocol_binding="HTTP+JSON",
            protocol_version="1.0",
            url="http://localhost:8383/a2a",
        ),
    ],
    skills=[
        AgentSkill(
            id="solidity_audit",
            name="Solidity Smart Contract Audit",
            description="Full security audit of Solidity contracts. Checks for known vulnerabilities, access control issues, reentrancy, overflow, and gas inefficiencies.",
            tags=["solidity", "security", "audit", "smart-contract", "evm"],
            examples=[
                "Audit this contract for vulnerabilities: [contract code]",
                "Review 0x1234...abcd on Base for security issues",
            ],
            input_modes=["text/plain", "application/json"],
            output_modes=["application/json"],
        ),
        AgentSkill(
            id="gas_optimization",
            name="Gas Optimization Review",
            description="Analyze Solidity contracts for gas optimization opportunities. Suggests concrete code changes.",
            tags=["solidity", "gas", "optimization", "evm"],
            examples=[
                "Optimize gas for this contract: [contract code]",
                "Find gas waste in my DeFi protocol",
            ],
            input_modes=["text/plain", "application/json"],
            output_modes=["application/json"],
        ),
        AgentSkill(
            id="vulnerability_scan",
            name="Known Vulnerability Scanner",
            description="Scan a contract address against known vulnerability databases and recent advisories.",
            tags=["vulnerability", "scan", "security", "cve"],
            examples=[
                "Scan 0x1234...abcd for known vulnerabilities",
                "Check this contract against recent advisories",
            ],
            input_modes=["text/plain", "application/json"],
            output_modes=["application/json"],
        ),
        AgentSkill(
            id="protocol_review",
            name="DeFi Protocol Architecture Review",
            description="Review DeFi protocol design for economic security, attack vectors, and game theory issues.",
            tags=["defi", "protocol", "architecture", "game-theory", "economic-security"],
            examples=[
                "Review this lending protocol design for attack vectors",
                "Analyze the game theory of this staking mechanism",
            ],
            input_modes=["text/plain", "application/json"],
            output_modes=["application/json"],
        ),
    ],
)


# ─── Agent Executor ───────────────────────────────────────────────────────────
# The actual work logic. In production this would call Hermes/LLM.
# For the PoC, we simulate audit work and return structured results.

class DmobExecutor(AgentExecutor):
    """DMOB's A2A task executor."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id
        context_id = context.context_id
        updater = TaskUpdater(event_queue, task_id, context_id)

        logger.info(f"Received task {task_id}")

        # 1. Acknowledge submission
        await updater.submit()

        # 2. Start working
        thinking_msg = updater.new_agent_message(
            parts=[Part(text="🔍 Analyzing request...")]
        )
        await updater.start_work(message=thinking_msg)

        # 3. Parse the request
        user_input = context.get_user_input()
        skill_id = self._detect_skill(user_input)

        logger.info(f"Task {task_id}: detected skill={skill_id}")

        # 4. Execute the appropriate skill
        try:
            result = await self._execute_skill(skill_id, user_input, task_id)
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await updater.failed(message=updater.new_agent_message(
                parts=[Part(text=f"Audit failed: {str(e)}")]
            ))
            return

        # 5. Emit progress update
        progress_msg = updater.new_agent_message(
            parts=[Part(text=f"✅ Audit complete. Delivering {skill_id} report...")]
        )
        await updater.update_status(
            state=TaskState.TASK_STATE_WORKING,
            message=progress_msg,
        )

        # 6. Add the result as an artifact
        await updater.add_artifact(
            parts=[Part(text=json.dumps(result, indent=2))],
            name=f"{skill_id}_report",
            description=f"DMOB {skill_id} audit report",
            last_chunk=True,
        )

        # 7. Complete
        await updater.complete()
        logger.info(f"Task {task_id} completed")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel()

    def _detect_skill(self, user_input: str) -> str:
        """Detect which skill the user is requesting."""
        lower = user_input.lower()
        if any(kw in lower for kw in ["audit", "security", "vulnerability", "exploit"]):
            return "solidity_audit"
        elif any(kw in lower for kw in ["gas", "optimize", "efficiency"]):
            return "gas_optimization"
        elif any(kw in lower for kw in ["scan", "known", "advisory", "cve"]):
            return "vulnerability_scan"
        elif any(kw in lower for kw in ["protocol", "defi", "architecture", "game theory"]):
            return "protocol_review"
        return "solidity_audit"  # default

    async def _execute_skill(self, skill_id: str, user_input: str, task_id: str) -> dict:
        """Execute a skill and return structured results."""
        # Simulate processing time
        await asyncio.sleep(1.0)

        base = {
            "task_id": task_id,
            "agent": "DMOB",
            "skill": skill_id,
            "timestamp": time.time(),
            "version": "0.1.0",
        }

        if skill_id == "solidity_audit":
            return {
                **base,
                "status": "completed",
                "severity_summary": {
                    "critical": 0,
                    "high": 1,
                    "medium": 3,
                    "low": 5,
                    "informational": 8,
                },
                "findings": [
                    {
                        "id": "DMOB-001",
                        "severity": "high",
                        "title": "Unchecked external call return value",
                        "location": "Line 142",
                        "description": "The contract does not check the return value of the external call to the price oracle. A failed oracle call would be treated as success.",
                        "recommendation": "Use OpenZeppelin's Address.sendValue() or check return value explicitly.",
                        "gas_impact": "negligible",
                        "cwe": "CWE-252",
                    },
                    {
                        "id": "DMOB-002",
                        "severity": "medium",
                        "title": "Floating pragma version",
                        "location": "Line 2",
                        "description": "Contract uses pragma solidity ^0.8.19. Should be pinned to a specific version.",
                        "recommendation": "Pin to pragma solidity 0.8.24;",
                        "gas_impact": "none",
                    },
                    {
                        "id": "DMOB-003",
                        "severity": "medium",
                        "title": "Centralization risk: owner can pause indefinitely",
                        "location": "Line 89",
                        "description": "The owner can pause the contract with no timelock or expiry.",
                        "recommendation": "Add a timelock (48h minimum) and maximum pause duration.",
                        "gas_impact": "none",
                    },
                ],
                "gas_optimization_score": 72,
                "overall_risk": "medium",
                "audit_agent": "DMOB v0.1.0",
            }

        elif skill_id == "gas_optimization":
            return {
                **base,
                "status": "completed",
                "current_gas_estimate": 245000,
                "optimized_gas_estimate": 187000,
                "savings_percent": 23.7,
                "optimizations": [
                    {
                        "location": "Line 56-78",
                        "issue": "Storage reads in loop",
                        "fix": "Cache storage variables in memory before loop",
                        "gas_saved": 2400,
                        "priority": "high",
                    },
                    {
                        "location": "Line 120",
                        "issue": "Unnecessary SafeMath usage (Solidity >=0.8)",
                        "fix": "Remove SafeMath library, use native overflow checks",
                        "gas_saved": 800,
                        "priority": "medium",
                    },
                ],
            }

        elif skill_id == "vulnerability_scan":
            return {
                **base,
                "status": "completed",
                "contracts_scanned": 1,
                "known_vulnerabilities": [],
                "advisory_matches": [
                    {
                        "advisory_id": "GENTECH-2026-0042",
                        "title": "Oracle manipulation in TWAP-based pricing",
                        "relevance": "low",
                        "description": "If contract uses TWAP oracles, check for manipulation vectors.",
                    }
                ],
                "risk_score": "B+",
            }

        elif skill_id == "protocol_review":
            return {
                **base,
                "status": "completed",
                "attack_vectors": [
                    {
                        "vector": "Flash loan governance attack",
                        "risk": "medium",
                        "description": "Governance token can be acquired via flash loan to pass proposals.",
                        "mitigation": "Add snapshot-based voting with 48h delay.",
                    },
                    {
                        "vector": "Oracle front-running",
                        "risk": "high",
                        "description": "Price updates can be front-run by MEV bots.",
                        "mitigation": "Use commit-reveal scheme or Chainlink Functions for pricing.",
                    },
                ],
                "game_theory_score": 68,
                "economic_security_score": 71,
            }

        return {**base, "status": "completed", "message": "Skill executed"}


# ─── Server ───────────────────────────────────────────────────────────────────

async def main():
    task_store = InMemoryTaskStore()
    executor = DmobExecutor()

    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        agent_card=AGENT_CARD,
    )

    app = FastAPI(title="DMOB A2A Server", version="0.1.0")

    # Mount A2A routes (these return lists of Route objects)
    app.routes.extend(create_agent_card_routes(agent_card=AGENT_CARD))
    app.routes.extend(create_jsonrpc_routes(handler, rpc_url="/a2a"))
    app.routes.extend(create_rest_routes(handler, path_prefix="/a2a"))

    @app.get("/health")
    async def health():
        return {"status": "ok", "agent": "DMOB", "version": "0.1.0"}

    logger.info("🚀 DMOB A2A Server starting on http://localhost:8383")
    logger.info("📋 Agent Card: http://localhost:8383/.well-known/agent-card.json")
    logger.info("🔗 A2A JSON-RPC: http://localhost:8383/a2a")
    logger.info("🔗 A2A REST: http://localhost:8383/a2a/")

    config = uvicorn.Config(app, host="0.0.0.0", port=8383, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
