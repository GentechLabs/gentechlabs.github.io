#!/bin/bash
# gated-heartbeat.sh — run Steward Position Heartbeat only when the treasury has capital.
exec bash "$(dirname "${BASH_SOURCE[0]}")/gated-run.sh" steward-heartbeat.sh
