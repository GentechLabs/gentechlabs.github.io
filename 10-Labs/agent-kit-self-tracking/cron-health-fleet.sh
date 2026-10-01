#!/usr/bin/env bash
# Cron Health Sentinel — FLEET standard (see skill: cron-health-standard).
#
# HEAL BEFORE SPEAKING: re-fire every failed SCRIPT job once; a silent successful retry
# is the ideal outcome. SPEAK ONLY about what healing could not fix.
# SILENT WHEN THE FLEET IS HEALTHY; NEVER SILENT WHEN IT CANNOT TELL (UNKNOWN exits 2).
#
# Runs from the profile's own scripts dir so `--script` resolves inside it.
cd "$(dirname "$0")" || exit 0
python3 cron_health_fleet.py --heal --quiet-unless-bad 2>&1
