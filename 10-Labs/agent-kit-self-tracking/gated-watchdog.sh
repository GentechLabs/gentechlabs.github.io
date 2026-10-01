#!/bin/bash
# gated-watchdog.sh — run Steward Position Watchdog only when the treasury has capital.
exec bash "$(dirname "${BASH_SOURCE[0]}")/gated-run.sh" steward-watchdog.sh
