#!/bin/sh
# vault-push-drain.sh — run the vault push drain. (Jordan, 2026-09-23)
#
# The write gate DEFERS a push when the 20/hr budget is spent ("retry next tick") and exits
# non-zero. Nothing retried it, so a deferred push was forgotten until some later commit
# happened to carry it — and if the box died first, the vault (the fleet's memory) died with
# it. This runs the drain on a schedule so a deferred push is DELAYED, not lost.
#
# Silent unless something is genuinely wrong: the drain prints only when it lands work that
# had been stranded for hours, or when it cannot push for hours.
set -u
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPTS_DIR/vault_push_drain.py" "$@"
