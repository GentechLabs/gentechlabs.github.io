"""End-to-end demo of the GenTech Agent Memory layer on CockroachDB.

Shows the full lifecycle: write episodic + semantic memories, semantic search,
consolidation (sleep), and stats. Run against a live local CockroachDB.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import db  # noqa: E402
from src.memory import AgentMemory  # noqa: E402


def main() -> None:
    conn = db.connect()
    db.init_schema(conn)
    mem = AgentMemory(conn, "demo-agent")

    print("=== GenTech Agent Memory on CockroachDB ===\n")

    # Episodic memories (what happened)
    mem.write("episodic", "User asked how to bridge USDC from Base to Avalanche", 0.6)
    mem.write("episodic", "User reported the arcade tennis game loads slowly", 0.5)
    mem.write("episodic", "User asked about stablecoin yield on Base", 0.7)

    # Semantic memories (facts)
    mem.write("semantic", "The treasury rebalances stablecoin LP on Base", 0.8)
    mem.write("semantic", "The x402 gateway accepts Base USDC payments", 0.8)
    mem.write("semantic", "The arcade serves the tennis game at the root path", 0.7)

    print("Wrote 6 memories (3 episodic, 3 semantic).\n")

    # Semantic search
    print("--- Semantic search: 'how to move money across chains' ---")
    for r in mem.search("how to move money across chains", limit=3):
        print(f"  [{r['similarity']:.3f}] {r['content']}")

    print("\n--- Recent episodic ---")
    for r in mem.recent("episodic", limit=3):
        print(f"  {r['content']}")

    # Consolidation (sleep)
    print("\n--- Consolidate (sleep) ---")
    n = mem.consolidate(threshold_days=7)
    print(f"  Consolidated {n} old episodic memories into a semantic summary.")

    print("\n--- Stats ---")
    print(f"  {mem.stats()}")

    print("\nDone. Memory layer verified against live CockroachDB.")


if __name__ == "__main__":
    main()
