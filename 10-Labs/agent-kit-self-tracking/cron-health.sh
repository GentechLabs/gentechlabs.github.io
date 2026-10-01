#!/usr/bin/env bash
# Cron Health Sentinel — self-healing fleet check.
# Jordan, 2026-09-25: "the cron jobs could fail... they don't really report anything or try
# to fix the problem... I usually have to ask afterward." This retries once, then speaks.
# SILENT UNLESS SOMETHING BROKE (silence doctrine: quiet unless something changed).
cd /root/.hermes/profiles/gentech-treasury/scripts || exit 0
python3 cron_health.py --heal --quiet-unless-bad 2>&1
