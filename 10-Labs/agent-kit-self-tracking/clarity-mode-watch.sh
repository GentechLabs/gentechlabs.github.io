#!/bin/bash
# Wrapper for the CLARITY mode-change watch. The cron `script` field is a bare
# path (no args), so we wrap the --watch call here. Exits 0 always; prints the
# mode-change report ONLY when the mode actually shifts (clarity-mode.py --watch
# handles the silent-when-unchanged logic).
cd "$(dirname "$0")"
exec python3 clarity-mode.py --watch
