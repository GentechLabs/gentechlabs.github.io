#!/bin/bash
# gated-lp-monitor.sh — run LP Monitor v2 only when the treasury has capital.
exec bash "$(dirname "${BASH_SOURCE[0]}")/gated-run.sh" lp-monitor-v2.py
