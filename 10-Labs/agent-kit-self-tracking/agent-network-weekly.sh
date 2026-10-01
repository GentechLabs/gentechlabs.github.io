#!/bin/bash
# Wrapper for the weekly agent-network top-20 scan. The cron `script` field is a
# bare path (no args), so we wrap the --weekly call here.
cd "$(dirname "$0")"
exec python3 agent_network_scan.py --weekly
