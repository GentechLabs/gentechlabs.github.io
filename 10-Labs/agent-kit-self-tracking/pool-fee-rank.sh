#!/bin/bash
# Pool Fee Rank — wrapper for the ranking job.
#
# Jordan (2026-09-18): "the cron Job should check the pools we talked about getting into
# based on fee generation" and "A way to bookmark favorites or catalog the ones you use".
#
# Runs the fee ranking (which reads pool-catalog.json and marks each row with its catalog
# status) and appends the catalog view so the decisions travel with the numbers.
#
# Read-only. Moves no capital, touches no position.
exec python3 /root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/pool-fee-rank.py
