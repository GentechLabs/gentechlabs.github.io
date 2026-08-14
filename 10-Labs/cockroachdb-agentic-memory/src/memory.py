"""Agentic memory store: write, retrieve, semantic-search, consolidate, forget.

Implements the three memory types an agent needs:
- episodic:   what happened (event records)
- semantic:   facts / knowledge extracted from experience
- procedural: how to do things (skills / workflows)

Semantic retrieval uses CockroachDB's distributed vector indexing (pgvector
HNSW) so embeddings scale without a separate vector store.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Optional

import psycopg

from . import db

# A tiny deterministic embedding for the demo/test path. In production this is
# replaced by a real embedding model (e.g. an AWS Bedrock Titan embedding or a
# local sentence-transformer). We keep a pluggable embed() so the storage layer
# is model-agnostic.
def _default_embed(text: str, dim: int = 384) -> list[float]:
    """Deterministic bag-of-characters embedding (demo/test only)."""
    vec = [0.0] * dim
    for i, ch in enumerate(text):
        vec[(ord(ch) * 31 + i) % dim] += 1.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


class AgentMemory:
    def __init__(
        self,
        conn: psycopg.Connection,
        agent_id: str,
        embed: Optional[callable] = None,
    ):
        self.conn = conn
        self.agent_id = agent_id
        self.embed = embed or _default_embed

    # ---- write -----------------------------------------------------------
    def write(
        self,
        memory_type: str,
        content: str,
        importance: float = 0.5,
        metadata: Optional[dict] = None,
    ) -> str:
        """Store a memory with its embedding. Returns the memory id."""
        emb = self.embed(content)
        mid = str(uuid.uuid4())
        emb_str = "[" + ",".join(f"{v:.6f}" for v in emb) + "]"
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_memory
                    (id, agent_id, memory_type, content, embedding, importance, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (mid, self.agent_id, memory_type, content, emb_str, importance,
                 json.dumps(metadata) if metadata else None),
            )
            cur.execute(
                """
                INSERT INTO memory_events (agent_id, event_type, memory_id, detail)
                VALUES (%s, 'write', %s, %s)
                """,
                (self.agent_id, mid, json.dumps({"type": memory_type})),
            )
        self.conn.commit()
        return mid

    # ---- retrieve --------------------------------------------------------
    def get(self, memory_id: str) -> Optional[dict]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM agent_memory WHERE id = %s AND agent_id = %s",
                (memory_id, self.agent_id),
            )
            row = cur.fetchone()
            if row:
                self._touch(memory_id)
            return row

    def _touch(self, memory_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE agent_memory
                SET last_accessed = now(), access_count = access_count + 1
                WHERE id = %s
                """,
                (memory_id,),
            )
        self.conn.commit()

    def recent(self, memory_type: Optional[str] = None, limit: int = 20) -> list[dict]:
        """Most recent memories (episodic recall)."""
        q = "SELECT * FROM agent_memory WHERE agent_id = %s"
        params: list[Any] = [self.agent_id]
        if memory_type:
            q += " AND memory_type = %s"
            params.append(memory_type)
        q += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        with self.conn.cursor() as cur:
            cur.execute(q, params)
            return cur.fetchall()

    def search(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 5,
        min_importance: float = 0.0,
    ) -> list[dict]:
        """Semantic (vector) search over the agent's memories."""
        emb = self.embed(query)
        emb_str = "[" + ",".join(f"{v:.6f}" for v in emb) + "]"
        q = """
            SELECT *, 1 - (embedding <=> %s::vector) AS similarity
            FROM agent_memory
            WHERE agent_id = %s AND importance >= %s
        """
        params: list[Any] = [emb_str, self.agent_id, min_importance]
        if memory_type:
            q += " AND memory_type = %s"
            params.append(memory_type)
        q += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params += [emb_str, limit]
        with self.conn.cursor() as cur:
            cur.execute(q, params)
            return cur.fetchall()

    # ---- consolidation / forgetting --------------------------------------
    def consolidate(self, threshold_days: int = 7) -> int:
        """Merge low-importance episodic memories into a semantic summary.

        Returns the number of memories consolidated. This is the 'sleep'
        step — turns raw events into durable knowledge.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, content FROM agent_memory
                WHERE agent_id = %s AND memory_type = 'episodic'
                  AND importance < 0.4
                  AND created_at < now() - (%s * interval '1 day')
                """,
                (self.agent_id, threshold_days),
            )
            old = cur.fetchall()
            if not old:
                return 0
            summary = " | ".join(r["content"] for r in old[:50])
            emb = self.embed(summary)
            emb_str = "[" + ",".join(f"{v:.6f}" for v in emb) + "]"
            sid = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO agent_memory
                    (id, agent_id, memory_type, content, embedding, importance, metadata)
                VALUES (%s, %s, 'semantic', %s, %s, 0.6, %s)
                """,
                (sid, self.agent_id, summary, emb_str,
                 json.dumps({"consolidated_from": len(old)})),
            )
            cur.execute(
                "DELETE FROM agent_memory WHERE id = ANY(%s)",
                ([r["id"] for r in old],),
            )
            cur.execute(
                """
                INSERT INTO memory_events (agent_id, event_type, memory_id, detail)
                VALUES (%s, 'consolidate', %s, %s)
                """,
                (self.agent_id, sid, json.dumps({"merged": len(old)})),
            )
        self.conn.commit()
        return len(old)

    def forget(self, memory_id: str) -> bool:
        """Delete a single memory (privacy / correction)."""
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM agent_memory WHERE id = %s AND agent_id = %s",
                (memory_id, self.agent_id),
            )
            deleted = cur.rowcount
            if deleted:
                cur.execute(
                    """
                    INSERT INTO memory_events (agent_id, event_type, memory_id)
                    VALUES (%s, 'forget', %s)
                    """,
                    (self.agent_id, memory_id),
                )
        self.conn.commit()
        return bool(deleted)

    def stats(self) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT memory_type, count(*) AS n
                FROM agent_memory WHERE agent_id = %s GROUP BY memory_type
                """,
                (self.agent_id,),
            )
            by_type = {r["memory_type"]: r["n"] for r in cur.fetchall()}
        return {"agent_id": self.agent_id, "by_type": by_type, "total": sum(by_type.values())}
