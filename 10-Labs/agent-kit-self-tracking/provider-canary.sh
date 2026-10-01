#!/usr/bin/env bash
# Wrapper for the provider canary.
#
# Why: the cron `script` field takes a FILENAME, not a command line (cron
# 612c41051805 failed with "Script not found" when args were passed inline).
# Arguments must live in a wrapper like this one.
#
# Silent-until-change: empty stdout = nothing delivered (--no-agent cron).
# Manual run with a verdict regardless of change:  provider-canary.sh --force
exec /usr/bin/env python3 "$(dirname "$0")/provider_canary.py" "$@"
