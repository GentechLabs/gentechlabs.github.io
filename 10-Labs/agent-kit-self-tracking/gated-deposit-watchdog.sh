#!/bin/bash
# gated-deposit-watchdog.sh — run Steward Deposit Watchdog only when the treasury has capital.
exec bash "$(dirname "${BASH_SOURCE[0]}")/gated-run.sh" steward-deposit-watchdog.sh
