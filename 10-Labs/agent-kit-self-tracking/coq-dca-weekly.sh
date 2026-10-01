#!/bin/bash
# Weekly COQ buy & hold DCA — Jordan's ruling Sep 12 2026.
# "$5/wk DCA starting Sun Sep 13" — spot accumulation, no LP, no IL.
#
# Silence doctrine: the script emits NOTHING unless something changed.
# First run while unfunded reports once, then stays quiet until it can buy.
# Funding: idle WAVAX only — it will NEVER touch farm position #3479882.
cd /root/.hermes/profiles/gentech-treasury/scripts || exit 0
python3 coq_weekly_dca.py --usd 5 --execute --quiet 2>&1
