#!/bin/bash
# auto-compound.sh — cron wrapper for the Steward Auto-Compound Engine.
# Single source of truth lives in the vault (no script copies to diverge).
exec python3 /root/vaults/gentech/10-Labs/agent-kit-self-tracking/auto_compound.py