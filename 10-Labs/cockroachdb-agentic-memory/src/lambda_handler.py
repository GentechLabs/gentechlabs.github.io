"""AWS Lambda handler — the '1+ AWS service' requirement.

This module is the deployment entrypoint for the agentic memory layer on AWS
Lambda. It exposes a JSON-RPC-ish API over the memory store so any agent can
call it via an HTTP gateway (API Gateway / Lambda URL).

Deployment (serverless.yml or SAM):
  handler: src.lambda_handler.handler
  environment:
    COCKROACH_DSN: postgresql://<user>@<host>:26257/<db>?sslmode=verify-full
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from typing import Any

from . import db
from .memory import AgentMemory

# Connection is cached across warm invocations (Lambda execution context reuse).
_conn = None


def _json_default(o):
    if isinstance(o, uuid.UUID):
        return str(o)
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def _dumps(obj) -> str:
    return json.dumps(obj, default=_json_default)


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = db.connect()
    return _conn


def handler(event: dict, context: Any = None) -> dict:
    """Lambda entrypoint. event = {"operation": ..., "payload": {...}}."""
    try:
        conn = _get_conn()
        body = event.get("body") or event
        if isinstance(body, str):
            body = json.loads(body)
        op = body.get("operation", "health")
        payload = body.get("payload", {})
        agent_id = payload.get("agent_id", "default-agent")
        mem = AgentMemory(conn, agent_id)

        if op == "health":
            result = db.health(conn)
        elif op == "write":
            mid = mem.write(
                payload["memory_type"], payload["content"],
                importance=payload.get("importance", 0.5),
                metadata=payload.get("metadata"),
            )
            result = {"memory_id": mid}
        elif op == "search":
            result = {
                "results": mem.search(
                    payload["query"],
                    memory_type=payload.get("memory_type"),
                    limit=payload.get("limit", 5),
                )
            }
        elif op == "recent":
            result = {"results": mem.recent(payload.get("memory_type"), payload.get("limit", 20))}
        elif op == "consolidate":
            result = {"consolidated": mem.consolidate(payload.get("threshold_days", 7))}
        elif op == "forget":
            result = {"deleted": mem.forget(payload["memory_id"])}
        elif op == "stats":
            result = mem.stats()
        else:
            return {"statusCode": 400, "body": _dumps({"error": f"unknown op {op}"})}

        return {"statusCode": 200, "body": _dumps(result)}
    except Exception as exc:  # noqa: BLE001
        return {"statusCode": 500, "body": _dumps({"error": str(exc)})}
