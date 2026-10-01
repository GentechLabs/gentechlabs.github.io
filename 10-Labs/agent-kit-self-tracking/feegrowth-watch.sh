#!/usr/bin/env bash
# Wrapper for the fee-growth watcher.
#
# Why: the cron `script` field takes a FILENAME, not a command line. Passing
# "feegrowth_watch.py --quiet" made the scheduler look for a file literally
# named that (cron 612c41051805 failed with "Script not found"). Arguments must
# live in a wrapper like this one.
exec /usr/bin/env python3 "$(dirname "$0")/feegrowth_watch.py" --quiet