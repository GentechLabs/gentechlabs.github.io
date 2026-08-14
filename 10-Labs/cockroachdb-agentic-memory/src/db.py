"""CockroachDB connection + schema management for the agentic memory layer."""
from __future__ import annotations

import os
from typing import Optional

import psycopg
from psycopg.rows import dict_row

DEFAULT_DSN = os.environ.get(
    "COCKROACH_DSN",
    "postgresql://root@localhost:26257/defaultdb?sslmode=disable",
)

# pgvector extension is bundled with CockroachDB (vector type + ivf index).
SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_memory (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id      STRING NOT NULL,
    memory_type   STRING NOT NULL,          -- 'episodic' | 'semantic' | 'procedural'
    content       STRING NOT NULL,
    embedding     VECTOR(384),
    importance    FLOAT8 NOT NULL DEFAULT 0.5,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT now(),
    access_count  INT8 NOT NULL DEFAULT 0,
    metadata      JSONB
);

CREATE INDEX IF NOT EXISTS idx_memory_agent_type
    ON agent_memory (agent_id, memory_type);

CREATE TABLE IF NOT EXISTS memory_events (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id   STRING NOT NULL,
    event_type STRING NOT NULL,             -- 'write' | 'read' | 'consolidate' | 'forget'
    memory_id  UUID,
    detail     JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

# Vector index: CockroachDB v24.3 exposes the pgvector type + operators but only
# 'prefix'/'inverted' access methods. ivfflat/hnsw arrive in later releases. We
# create the index when the access method exists and otherwise fall back to a
# sequential scan (correct at demo scale). The vector column + <=> operator are
# the distributed-vector-indexing capability.
_VECTOR_INDEX_SQL = {
    "ivfflat": (
        "CREATE INDEX IF NOT EXISTS idx_memory_embedding "
        "ON agent_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1)"
    ),
    "hnsw": (
        "CREATE INDEX IF NOT EXISTS idx_memory_embedding "
        "ON agent_memory USING hnsw (embedding vector_cosine_ops)"
    ),
}


def connect(dsn: Optional[str] = None) -> psycopg.Connection:
    """Open a connection to CockroachDB."""
    return psycopg.connect(dsn or DEFAULT_DSN, row_factory=dict_row)


def init_schema(conn: psycopg.Connection) -> None:
    """Create tables + indexes if they don't exist. Idempotent."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(SCHEMA)
        # Create the vector index only if the access method is available.
        cur.execute("SELECT amname FROM pg_am;")
        ams = {r["amname"] for r in cur.fetchall()}
        for am in ("ivfflat", "hnsw"):
            if am in ams:
                cur.execute(_VECTOR_INDEX_SQL[am])
                break
    conn.commit()


def health(conn: psycopg.Connection) -> dict:
    """Return a health/readiness payload (used by the Lambda handler)."""
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()["version"]
        cur.execute("SELECT count(*) AS n FROM agent_memory;")
        n = cur.fetchone()["n"]
    return {"status": "ok", "cockroach_version": version, "memory_rows": n}
