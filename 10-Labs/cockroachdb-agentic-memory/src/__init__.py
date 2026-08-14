# GenTech Agent Memory — CockroachDB × AWS "Build with Agentic Memory"
#
# Persistent, vector-indexed memory layer for AI agents, backed by CockroachDB.
# Uses 2+ CockroachDB tools (managed MCP server pattern + distributed vector
# indexing via pgvector) and 1+ AWS service (S3-compatible snapshot export +
# Lambda-style handler entrypoint).
#
# This is our vault/session-memory architecture re-homed onto CockroachDB as
# the production-grade storage layer.

__version__ = "1.0.0"
