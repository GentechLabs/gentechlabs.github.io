#!/bin/bash
# Steward Deposit Watchdog wrapper — runs the Steward's deposit-detection +
# milestone progress in quiet mode. Silent until new money arrives in a treasury
# wallet; then it reports rank / % toward the next milestone / estimated fees.
#
# ── PER-TENANT (Jordan, 2026-09-26) ──────────────────────────────────────────────────────────────
# This ran ONE pass against ONE wallet (treasury_config.json → Jordan's), so a collaborator's
# deposit was invisible — and a deposit is the ONLY thing Jordan's cousin does with this treasury
# ("He just wants to put money in it"). --all-tenants sweeps every ACTIVE tenant in the registry as
# a separate process with its own wallet and its own baseline file, so one tenant's state can never
# become another's number. Each tenant also has its deposit checked against its own capital ceiling
# before the arrival is reported as good news.
exec python3 /root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/steward_progress.py --watchdog --all-tenants
