"""Tests for the CockroachDB agentic memory layer.

Run against a live local CockroachDB (docker):
    docker run -d --name cockroach-mem -p 26257:26257 -p 18080:8080 \
        cockroachdb/cockroach:v24.3.4 start-single-node --insecure \
        --store=type=mem,size=1GiB

    python -m pytest tests/ -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src import db  # noqa: E402
from src.memory import AgentMemory  # noqa: E402

DSN = os.environ.get("COCKROACH_DSN", "postgresql://root@localhost:26257/defaultdb?sslmode=disable")


@pytest.fixture(scope="module")
def conn():
    c = db.connect(DSN)
    db.init_schema(c)
    yield c
    c.close()


@pytest.fixture()
def mem(conn):
    m = AgentMemory(conn, "test-agent")
    # clean slate
    with conn.cursor() as cur:
        cur.execute("DELETE FROM agent_memory WHERE agent_id = %s", ("test-agent",))
        cur.execute("DELETE FROM memory_events WHERE agent_id = %s", ("test-agent",))
    conn.commit()
    return m


def test_health(conn):
    h = db.health(conn)
    assert h["status"] == "ok"
    assert "CockroachDB" in h["cockroach_version"]


def test_write_and_get(mem):
    mid = mem.write("episodic", "User asked about yield on Base", importance=0.7)
    row = mem.get(mid)
    assert row is not None
    assert row["content"] == "User asked about yield on Base"
    assert row["memory_type"] == "episodic"
    assert row["importance"] == 0.7


def test_recent_ordering(mem):
    mem.write("episodic", "first")
    mem.write("episodic", "second")
    recent = mem.recent("episodic")
    assert recent[0]["content"] == "second"
    assert recent[1]["content"] == "first"


def test_semantic_search(mem):
    mem.write("semantic", "The treasury rebalances stablecoin LP on Base", importance=0.8)
    mem.write("semantic", "The arcade serves the tennis game at the root path", importance=0.8)
    results = mem.search("stablecoin liquidity pool rebalancing", memory_type="semantic")
    assert results, "expected at least one result"
    # The relevant memory is retrieved with a positive similarity score.
    assert any("treasury rebalances" in r["content"] for r in results)
    assert all(r["similarity"] > 0.0 for r in results)


def test_search_respects_importance(mem):
    mem.write("semantic", "low importance fact", importance=0.1)
    results = mem.search("low importance fact", min_importance=0.5)
    assert results == []


def test_consolidate(mem):
    # old low-importance episodic memories
    with mem.conn.cursor() as cur:
        e1 = "[" + ",".join(f"{v:.6f}" for v in mem.embed("old event A")) + "]"
        e2 = "[" + ",".join(f"{v:.6f}" for v in mem.embed("old event B")) + "]"
        cur.execute(
            """
            INSERT INTO agent_memory (agent_id, memory_type, content, embedding, importance, created_at)
            VALUES (%s, 'episodic', 'old event A', %s, 0.2, now() - interval '10 days'),
                   (%s, 'episodic', 'old event B', %s, 0.2, now() - interval '10 days')
            """,
            ("test-agent", e1, "test-agent", e2),
        )
    mem.conn.commit()
    n = mem.consolidate(threshold_days=7)
    assert n == 2
    # a semantic summary now exists
    sem = mem.recent("semantic")
    assert any("old event" in s["content"] for s in sem)


def test_forget(mem):
    mid = mem.write("episodic", "sensitive data to remove")
    assert mem.forget(mid) is True
    assert mem.get(mid) is None
    assert mem.forget(mid) is False  # already gone


def test_stats(mem):
    mem.write("episodic", "e1")
    mem.write("semantic", "s1")
    s = mem.stats()
    assert s["total"] == 2
    assert s["by_type"]["episodic"] == 1
    assert s["by_type"]["semantic"] == 1


def test_lambda_handler(conn):
    from src.lambda_handler import handler
    # write via lambda
    r = handler({"operation": "write", "payload": {
        "agent_id": "lambda-agent", "memory_type": "semantic",
        "content": "lambda wrote this"}})
    assert r["statusCode"] == 200
    mid = __import__("json").loads(r["body"])["memory_id"]
    # search via lambda
    r2 = handler({"operation": "search", "payload": {
        "agent_id": "lambda-agent", "query": "lambda wrote"}})
    assert r2["statusCode"] == 200
    results = __import__("json").loads(r2["body"])["results"]
    assert any(x["content"] == "lambda wrote this" for x in results)
    # health
    r3 = handler({"operation": "health", "payload": {}})
    assert r3["statusCode"] == 200
    assert __import__("json").loads(r3["body"])["status"] == "ok"
