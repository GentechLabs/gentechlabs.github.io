#!/bin/bash
# sync-treasury-scripts.sh — propagate vault (source of truth) → repos + profile.
#
# WHY: the treasury's cron ring runs scripts from THREE locations:
#   - /root/vaults/gentech/10-Labs/agent-kit-self-tracking/   (SOURCE OF TRUTH)
#   - /root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/  (watchdog runs this)
#   - /root/.hermes/profiles/gentech-treasury/scripts/        (wrappers + some)
# When the vault is edited, the repos copy the watchdog runs does NOT update
# automatically — that's how the fee-ledger bug happened (old LFJ-only version
# kept running). This script syncs vault → repos + profile and verifies md5.
#
# Usage: bash sync-treasury-scripts.sh [--commit]
#   --commit  also git-commit the repos copy (so the GitHub Pages repo stays current)

set -euo pipefail

VAULT="/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
REPOS="/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking"
PROFILE="/root/.hermes/profiles/gentech-treasury/scripts"

# The treasury scripts that must stay in sync (vault is canonical).
SCRIPTS=(
  avax_rpc.py
  steward_rebalance.py
  # ── POSTURE + ITS TESTS (2026-09-26) ──────────────────────────────────────────────────────────
  # posture.py is the decision layer: all six layers in, ONE posture out. It must be in the
  # manifest or it never reaches the machine that runs it — and its two regression tests must ride
  # with it, so the refusal (an unreadable layer does not vote) and the width bounds cannot be
  # broken again without a failure.
  posture.py
  fed-event-tracker.py
  steward-macro-watch.sh
  test_rangebound.py
  test_adaptive_width.py
  test_rescue_gate.sh
  test_no_ceiling.py
  test_shape_classifier.py
  constitution_trace.py
  steward_action_log.py
  test_action_log.py
  test_action_log_finality.py
  test_shape_of_mass.py
  test_tenant_isolation.py
  test_mid_rebalance_guard.py
  test_state_path_tenant.py
  test_hub_theme.py
  test_hub_no_position.py
  run-tests.sh
  test_cron_health_no_recursion.py
  test_cron_health_fleet_self_exemption.py
  test_calendar_freshness.py
  test_shape_deadlock.py
  test_shape_verdict_render.js
  test_earnings_render.js
  steward_fee_ledger.py
  auto_compound.py
  steward_farm_report.py
  discover_positions.py
  blackhole_cl_adapter.py
  steward_execute.py
  steward_state.py
  steward_progress.py
  # Yield-rainbow feed writer. It existed ONLY in the profile, so it drifted out of
  # management entirely — the council reads its output for the LP Position member, and it
  # was publishing positionUsd 0.0 (FLAT) while our funded LFJ position was live.
  yield-rainbow.py
  # Pool catalog + fee ranking (bookmarks and the ranking must travel together: the
  # ranker reads pool-catalog.json, so shipping one without the other mis-ranks).
  pool-fee-rank.py
  pool-fee-rank.sh
  pool-catalog.py
  pool-catalog.json
  # Scenario planners — read-only, but they must be runnable from the executed copy.
  lunch-scenario.py
  strategy_desk.py
  vfat_blackhole.py
  treasury_config.json
  blackhole_fee_reader.py
  treasury_self_audit.py
  treasury_truth.py
  value_timeline.py
  # Volatility/stability reading + the what-to-rebalance-to verdict (Jordan, 2026-09-23):
  # volatile -> bid-ask, stable -> curve, run far -> propose exiting the pool to hold the asset.
  # Registered here on creation — a new file that is not in the manifest never reaches the
  # executed copy, so it looks like it was written and does nothing.
  volatility_tracker.py
  instrument_contract.py
  # Either farm it or get out (Jordan, 2026-09-23): measures the SPEED of a move in
  # sigma/hour so a grind (farm it) is never confused with a cascade (exit to stables).
  cascade_guard.py
  # The vault must never sit unpushed (Jordan, 2026-09-23): the write gate DEFERS a push when
  # the 20/hr budget is spent and nothing retried it, so a deferred push was simply forgotten.
  vault_push_drain.py
  vault-push-drain.sh
  # How wide should the band be? (Jordan, 2026-09-23, approved): coverage vs realized vol,
  # chase rate, chase cost -- the three numbers that decide whether the width is enough.
  width_advisor.py
  # What is the position actually EARNING? (Jordan, 2026-09-23: "Fee efficiency should be
  # zero") -- LFJ compounds fees into the bins, so earnings had no reader at all.
  fee_ledger.py
  fee-ledger.sh
  # ── PAUSE-SAFETY (Jordan, 2026-09-24) ────────────────────────────────────────────────────
  # "If you ever pause the watchdog to fix something. Consider withdrawing from the pool and
  # switching to usdc as a safety precaution." Pausing the watchdog removes the ONLY thing
  # managing the book -- what remains is an unmanaged directional position. That happened:
  # the watchdog was paused nine hours on 2026-09-24 and the pullback ran through the books.
  # --report is the default because Jordan's word was "consider": the tool makes the choice
  # INFORMED rather than making it automatically.
  pause_safety.py
  # ── TRANSITIONS, NOT CLASSIFIERS (Jordan, 2026-09-24) ───────────────────────────────────
  # "For a long time we've talked about how to predict different scenarios and what to do in
  # different scenarios. But we never talk about going from bullish to bearish... I think our
  # ideas work better as transitions." Scenarios become STATES, moves become TRANSITIONS with
  # their own licence, and a jump that is not an edge is WALKED as a ladder.
  transition_map.py
  gas_reserve.py
  gas_topup.py
  watchdog_breaker.py
  agent_lock.py
  mutual-aid-policy.json
  test_gas_topup.py
  test_gas_on_redeploy.py
  test_sync_integrity.py
  test_phased_gas.py
  test_lfj_exit_reserve.py
  test_quiet_hours_windows.py
  test_gas_from_receipts.py
  test_pause_safety_lock.py
  daily_fee_ledger.py
  steward_consistency.py
  test_steward_consistency.py
  test_posture_atomic.py
  test_watchdog_breaker.py
  test_wallet_lock.py
  test_gas_affordability.py
  test_completions_structure.py
  # ── A FAILED READ IS NOT A REAL ZERO (2026-09-27) ──────────────────────────────────────
  # The Sunday report printed a PYTHON CRASH as if it were the state of the world
  # ("unsupported format string passed to NoneType.__format__"), masking a WORKING chain
  # read behind an age-parse failure. Four false-value defects sat under it: no User-Agent
  # on the RPC call (publicnode answers a bare urllib POST with 403 while answering the same
  # request WITH a UA -- and avax_rpc.url() probes WITH a UA, certifying the one host the
  # caller could not use), fromisoformat() on an epoch float, a refusal path that formatted
  # the missing age with {:.1f}, and _deployed_usd() reading a schema key that had MOVED
  # (so an unreadable treasury printed as "TREASURY IS FLAT"). The test proves BOTH
  # directions -- stale abstains AND fresh still fires -- or it is not a fix. An
  # unenrolled test is a claim, not a check.
  test_freshness_and_deploy_read.py
  # ── THE GAS FLOOR'S TEST TRAVELS WITH THE FLOOR (Jordan, 2026-09-25) ────────────────────
  # gas_reserve.py is the ONE floor the no-idle rule must respect; its test is what proves the
  # floor still fires ABOVE / BELOW / AT the boundary. An unenrolled test is a claim, not a
  # check (bug class #10, sync-list coverage): if this file does not travel, every deploy path
  # in the profile could be gating on a floor nobody can verify.
  test-gas-floor.py
  cron_health.py
  cron-health.sh
  # ── FLEET CRON HEALTH STANDARD (Jordan, 2026-09-25) ──────────────────────────────────────
  # "we should also add that to the agent kit as like a standard for cron jobs. And then we
  # should have that go to every cron job for all groups ... what the intent of the cron job
  # is, and when something is not working, we troubleshoot and we fix it."
  # The one-profile sentinel generalized. Three files that must travel TOGETHER:
  #   cron_health_fleet.py  — reads every profile's ring, heals by re-firing once, speaks
  #                           only what healing could not fix; UNKNOWN + exit 2 when it
  #                           cannot read a job list (never reports false health).
  #   cron-health-fleet.sh  — the no_agent wrapper registered in all four profiles (30m).
  #   cron-intents.json     — the INTENT registry: what each job is FOR, so a failure is
  #                           triaged against purpose instead of an opaque error string.
  # A wrapper whose script is missing, or a tool whose registry did not travel, is exactly
  # the "written and does nothing" failure this manifest exists to prevent. Enrol all three.
  cron_health_fleet.py
  cron-health-fleet.sh
  cron-intents.json
  # Keep the hub following the chain (Jordan, 2026-09-23): it was on NO cron, so the page
  # only refreshed when a human ran it -- the "10-15 minute grace" Jordan was granting was
  # actually unbounded.
  defi-hub-refresh.sh
  # THE HUB'S TIMEOUT BUDGET IS A CONTRACT BETWEEN TWO FILES, so its test must travel or the
  # contract is unverifiable in the profile. Measured 2026-09-28: the wrapper's `timeout 280` sat
  # BELOW the collector's hardcoded inner `timeout=300`, so the graceful-degradation branch could
  # never fire and a slow run died with a bare rc=124 — after 88-97% of the envelope was already
  # consumed on GOOD runs (246-272s of 280s). Fixed (outer 600s / inner 240s) and pinned here for
  # both directions: the invariant, the worst case across all ACTIVE tenants, and two negative
  # controls that must go RED. An unenrolled test is a claim, not a check.
  test_defi_hub_timeout_budget.py
  pin_loss.py
  reconcile_recenter.py
  find_lfj_bins.py
  wallet_forensics.py
  wallet_timeline.py
  who_is_trading.py
  tx_cost_forensics.py
  decode_and_deposits.py
  lfj_postmortem.py
  # ── LFJ EXECUTORS, added 2026-09-21 ─────────────────────────────────────
  # WHY: the manifest carried only the LFJ REPORTERS (postmortem, rehearsal, truth,
  # fee-decode) and omitted every file that actually MOVES MONEY. The sync printed
  # "Done. Vault is source of truth" while the executed copies of these four stayed
  # stale -- so a fix to the deploy logic could be written, synced, reported as
  # landed, and never run. That is the false-success family: a mechanism reporting
  # success while doing nothing. An executor that is not in the manifest is not
  # deployable, no matter what the sync says.
  lfj_bid_deploy.py
  gta_avax_lp_execute.py
  lfj-curve-deploy.sh
  lfj_recenter.py
  steward_hold.py
  lfj_exit.py
  # ── lfj_shapes.py: THE GEOMETRY TABLE, added 2026-09-25 ─────────────────────────────────
  # WHY: every deploy path resolves its width law from this file, but it was NOT in the
  # manifest -- so the vault copy could be corrected while the executed copy stayed stale, and
  # the fix would read as landed and never run. Found exactly that way today: a new classifier
  # (shape_of_bins) was added to the vault copy, the sync printed "Done. Vault is source of
  # truth", and the profile copy still had the old md5 -- lfj_recenter's _held_shape would have
  # hit AttributeError and silently fallen back to the gap test that causes the churn, with the
  # sync reporting success. A file a money path IMPORTS is a money path.
  lfj_shapes.py
  verify_black_emissions.py
  find_correct_router.py
  security_sentinel.py
  value_now.py
  apply_audit_fixes.py
  fix_stranded_black.py
  add_approval_check.py
  reconcile_black_accrual.py
  # ── Trade-Mode executor cluster, added 2026-09-11 ────────────────────────
  # WHY: gta_executor.py lived ONLY in the profile and carried the fresh-scan
  # truth guard (ARB_STATE_MAX_AGE_H) that the vault copy had never received.
  # sync-treasury-scripts.sh runs VAULT -> repos+profile, so an unlisted file is
  # never protected: a profile-only revision is silently authoritative and the
  # vault "source of truth" rots. Same shape as the Aug 23 frozen-scan and the
  # Sep 11 arb-log defects — a reader/writer pointing at the wrong copy.
  gta_executor.py
  # Test suites must be enrolled too: test_gta_executor.py existed ONLY in the
  # profile and had silently rotted against two shipped changes (the mode gate
  # and the fresh-scan truth guard), so it reported 4 "failures" that were
  # really fixture drift. A test that cannot run against the vault copy cannot
  # protect the vault copy. Same bug class #10 (sync-list coverage).
  test_gta_executor.py
  # Two more suites with the same gap, found by auditing every test-*.py in the vault against
  # this manifest (2026-09-24). test_steward_progress.py was in the REPO but not the PROFILE,
  # and test_steward_rebalance.py was in neither — so the vault copies were unverifiable and
  # the executed copies unprotected. Enrolling a suite is what makes its green light mean
  # something; an unenrolled test is a claim, not a check.
  test_steward_progress.py
  test_steward_rebalance.py
  gated-executor.sh
  gated-run.sh
  capital_gate.py
  gta-arb-monitor.py
  auto-compound.sh
  benchmark-feeds.py
  staking_benchmark.py
  lfj_fee_attribution.py
  challenger.py
  clarity-mode-watch.sh
  gated-deposit-watchdog.sh
  gated-heartbeat.sh
  gated-watchdog.sh
  steward-watchdog.sh
  handoff-watcher.py
  # swap_readiness.py — answers "is this lag or a real divergence?" before acting.
  # Added the moment it was written: a cron-executed script outside the sync list has no
  # single source of truth, and this one is meant to be run BY hand while diagnosing.
  swap_readiness.py
  prewake_context_save.py
  regime-watch.sh
  security-sentinel-watch.sh
  self-audit-watch.sh
  steward-buylist.py
  steward-council.py
  steward-farm-report.sh
  strategy-desk.sh
  weekly-fed-council.py
  agent-network-weekly.sh
  agent_network_scan.py
  clarity-mode.py
  gated-lp-monitor.sh
  lp-monitor-v2.py
  regime_classifier.py
  reprobe_models.py
  steward_macro_scheduler.py
  prove_swap_route.py
  add_to_position.py
  prove_increase_staked.py
  quote_swap_routes.py
  find_real_swapper.py
  test_swap_leg.py
  coq_rail_check.py
  coq_definitive.py
  coq_farm_econ.py
  coq_gauge_emissions.py
  link_rail_check.py
  link_blackhole_econ.py
  steward-buylist-overrides.json
  coq_weekly_dca.py
  # coq-dca-weekly.sh was DELETED 2026-09-12 (commit a6c838267) and replaced by the dip-aware daily
  # accumulator below. Its manifest line outlived it by 16 days. Because the loop treated a missing
  # file as a warning and still exited 0, this phantom entry produced a GREEN deploy every run while
  # the COQ capital path deployed with one fewer file than the manifest claimed — the "written and
  # does nothing" class, in the deploy layer. Removed here; the loop now exits 1 on any phantom so
  # this cannot recur. Do not re-add without restoring the file.
  coq_accumulator.py
  coq_avax_correlation.py
  coq-accumulator-daily.sh
  rebalance_swap.py
  revoke_router_approval.py
  deploy_lp_curve.py
  gta_hl_execute.py
  gta_solana_leg.py
  # LIVE EVM->Solana bridge quotes (deBridge DLN), fail-closed. solana_homebase.py
  # imports this for a real quote; it must be on sys.path wherever that runs.
  bridge_quote.py
  revoke_stale_approvals.py
  steward_selfheal.py
  steward_identity.py
  migrate_identity.py
  add_identity_check.py
  link_definitive.py
  refresh_state_capital.py
  link_gauge_econ.py
  link_gauge_verify.py
  link_funding_check.py
  compound_cost.py
  meteora_tao_monitor.py
  feegrowth_watch.py
  feegrowth-watch.sh
  # ── Provider canary, added 2026-09-13 ────────────────────────────────────
  # WHY: both inference providers (Nous Portal balance, Ollama Cloud weekly
  # limit) went dead at once and nothing surfaced it — neither provider exposes
  # a usage/quota/billing endpoint, so a real minimal completion is the only
  # honest probe. Silent-until-change watchdog; alerts on provider change.
  provider_canary.py
  provider-canary.sh
  # ── Arb-log signal sources, enrolled 2026-09-14 ──────────────────────────
  # WHY: cross_venue_scanner.py was NEVER enrolled, so its copies could diverge
  # freely and nothing protected it. It is the writer that produced 45
  # fabricated cross-venue rows from an impostor DEX pair (symbol match, not
  # identity — see Treasury/arb-log/CORRECTIONS.md, Correction 3). Same shape
  # as bug class #10 (sync-list coverage): a cron-executed script outside the
  # sync list has no single source of truth.
  # These live in Treasury/scripts, so they are mirrored by the dedicated
  # block below the main loop, not by this array.
  # ── Exit suite, enrolled 2026-09-15 ──────────────────────────────────────
  # WHY: Jordan (Sep 15) — "the same way we built the bridge to go platform to
  # platform, we need a plan for EXITING liquidity per platform." On Sep 15 an
  # orchestrator-authorized exit had NO rehearsed path and had to be built on
  # the fly mid-withdrawal. Every future exit runs this synced path.
  gta_full_exit.py
  exit-rails.json
  capital-guard-rails.json
  wallets.json
  capital-guard.py
  approvals.json
  # ── BLACK health tracker (Jordan Sep 15: "track BLACK and see what it looks
  # like if BLACK collapses") ──────────────────────────────────────────────
  black_health.py
  # re-entry pairing (Jordan Sep 15): rainbow x farm
  reentry_yield.py
  reentry-watch.sh
  # Yield Farm Report — cross-rail venue comparison (Jordan Sep 15)
  agentic-treasury-report.py
  agentic-treasury-report.sh
  arc_rail.py
  # venue/rail compatibility matrix — canonical copy lives here so the sync tracks
  # it (the 10-Labs/ copy is the working original; this is the synced one)
  venue-compat.py
  # post-event council monitor — was PROFILE-ONLY (not in vault/git) until Sep 16;
  # a profile rebuild would have killed the post-event council entirely
  post-event-monitor.py
  # SEC/CFTC rulemaking watch (Jordan Sep 16) — the post-CLARITY framework
  sec-cftc-watch.py
  sec-cftc-watch.sh
  # buy-list cron wrapper: enforces the 7am-9pm ET window (Jordan Sep 16)
  buylist-cron.sh
  # deposit watchdog — was PROFILE-ONLY (not in vault/git) until Sep 16; the cron was
  # switched onto it today (ungated), so a profile rebuild would have lost the fix
  steward-deposit-watchdog.sh
  # Fed/regulator SPEECH watch (Jordan Sep 16) — the layer between the calendar (dates)
  # and the Federal Register (documents): statements, speeches, testimony, minutes
  fed-watch.py
  fed-watch.sh
  discover-news-sources.py
  # yield-rail-finder — NOT enrolled before Sep 16, which is exactly why the vault copy
  # drifted 11 days behind the profile and ended up pointing at a DEAD data path
  yield-rail-finder.py
  yield-rail-finder-cron.sh
  # ── Exit modes + the mode module, enrolled 2026-09-17 ────────────────────
  # WHY treasury_state.py MUST be here: it is the SHARED BRAIN — every cron job
  # reads the treasury mode through it. It was NOT enrolled, so the vault copy and
  # the executed copy could silently disagree about what modes EXIST. Adding HOLD
  # to the vault changed nothing in production until this line existed: the profile
  # copy still read MODES={"YIELD_FARM","TRADE","DRY_POWDER"}, meaning a treasury
  # legitimately holding the token would have been reported as YIELD_FARM — a
  # holder wearing a farmer's label. Same bug class as the Aug 23 frozen scan and
  # the Sep 16 dup sweep: the unenrolled file is the one that drifts.
  treasury_state.py
  # exit_plan.py turns (rail, exit_mode) into the exact exit sequence. Jordan asked
  # (Sep 17) for exits that can land in "just holding the token", not only in cash.
  exit_plan.py
  # A test that cannot run against the vault copy cannot protect the vault copy.
  test-treasury-modes.py
  # ── HOLD-mode intelligence, enrolled 2026-09-17 ──────────────────────────
  # Jordan defined the HOLD discipline: hold ONLY when monthly AND weekly are both
  # bullish AND real momentum exists AND holding beats the fee income given up.
  # "we don't want to say oh, we're bullish and we're going up when we're normally
  # just steady."  hold_trigger.py is that gate; it defaults to FARM.
  hold_trigger.py
  # The rotation loop Jordan named on 2026-09-26: hold while rising, read the DECAY SIGNS
  # that arrive BEFORE the band breaks (fast-leg rollover, failed high, lost directional
  # edge), and say when to re-enter the pool. It asks the gates on a SCHEDULE — hold_trigger
  # was only ever asked from inside lfj_recenter's out-of-range branch, so mid-range the
  # question went unasked and the loop only ran one way.
  # READ-ONLY: no wallet, no tx path anywhere in it. Silence doctrine — speaks only when
  # the read changes.
  momentum_watch.py
  # What a held position can DO — live liquid-staking / lending rates rather than
  # suggestions, so HOLD is not assumed to be idle.
  hold-yield-options.py
  # Gas is an operational input, and it is NOT a constraint on Avalanche
  # (a full exit costs ~0.000027 AVAX). Recorded so nobody re-invents a hard gate.
  gas_runway.py
  verify-gas-cost.py
  # LFJ Liquidity Book is a DIFFERENT POSITION MODEL from Black Hole CL — bin IDs not ticks,
  # shapes not ranges, single-sided allowed, and a fee law that surges with volatility. FOUR
  # WAVAX/USDC pairs exist in the factory and three are liquidity-free decoys that quote a
  # confident wrong price, so "which pair" is a safety question, not a detail. This rehearses
  # every one of those before any capital moves. READ-ONLY: eth_call only.
  lfj-bin-rehearsal.py
  # Every outbound transfer goes through this: address length + checksum, the NATIVE-vs-bridged
  # USDC assertion (Avalanche has TWO contracts called USDC and the wrong one is unrecoverable),
  # gas quote, an eth_call simulation, and a read-back verification. A broadcast is not a delivery.
  steward-send-usdc.py
  steward-send-native.py
  test_mutual_aid.py
  lfj-addliquidity-dryrun.py
  # The buy list carried hand-written yield notes that had drifted (AVAX still claimed Blackhole
  # 216%% / 27%% fee core). These two go and MEASURE instead: rails finds every venue for each
  # buy-list asset in the full DefiLlama universe, verify tests each headline against its own
  # 7d/30d history because a one-day spike annualised looks exactly like a real yield.
  buylist-yield-rails.py
  buylist-yield-verify.py
  # Jordan (Sep 18): "on chain data is king always king". This names the SOURCE of every number that
  # drives a decision — CHAIN (definitive) vs AGGREGATOR (discovery only, must be reproduced) vs
  # CONFIG (a label, never a fact) — and flags the scripts that are config-only, where the number
  # cannot have updated itself. Strips comments/docstrings first: a check that fires on the prose
  # describing a fixed bug is as useless as one that cannot recognise a pass.
  data-provenance-audit.py
  # The SEC/CFTC watcher's second half (Jordan, Sep 18): benefit + recommended action + the running
  # note the Sunday council reads. THE TEXT is fact, THE CHAIR is judgment and says so. Allowed to
  # conclude "this does not reach us" — a watcher that cannot say that trains its reader to skim.
  regulatory-benefit.py
  # A test that cannot run against the executed copy cannot protect it. This one pins
  # the three defects found in this watcher on 2026-09-21 (UK spelling missed,
  # comment windows silently capped at 8, Sunday note re-appending identical reads)
  # and was verified to FAIL on the pre-fix code before being enrolled.
  test-regulatory-watch.py
  # Pins the carry-reader defect found 2026-09-23: _read_regulatory_carry() break-ed out of
  # its scan at the FIRST carry block and then sliced out[-3:], so it always returned the
  # oldest block. The comment said "the last one wins"; the code did the opposite, and every
  # update appended after 2026-09-18 was unreachable by the Sunday council. The reader now
  # takes an injectable path so this test exercises the REAL function rather than a copy of
  # its logic — a duplicated parser passes whether or not the real one is fixed.
  test-fed-council-carry.py
   # Stocks vs crypto: do they bull together or take turns? (Jordan, Sep 18 — on Ondo's
   # tokenized-stocks post). Measures correlation, rolling correlation, and the divergence
   # windows. Equities via api.nasdaq.com, crypto via Coinbase. Named sources, READ-ONLY.
   stock-vs-crypto-cycle.py
   # Stooq client: solves Stooq's JS hashcash challenge before fetching CSVs, and RAISES on
   # failure so a blocked fetch can never be mistaken for 'this ticker has no history'.
   stooq-client.py
   # Ranks pools by CHAIN-MEASURED fees: factories -> pools -> TVL from balances ->
   # 24h of Swap events -> fees -> APR. READ-ONLY. Replaces the aggregator's number, because LFJ's
   # went 90.7% -> 7.85% when measured on swaps that actually happened.
   chain-fee-rank.py
  # The ranker's own regression suite. Enrolled 2026-09-24: it lived only in the vault, so
  # the copy the cron actually runs was never covered by the check that exists to protect it —
  # the same enrollment gap recorded at line ~128 for test_gta_executor.py, repeated. Worse, its
  # "fresh measurement still pays" assertion was pinned to the literal "$0.3", a substring that
  # matched only while capital sat near $139.55: when the ranker started reading real capital
  # ($121.46) the cell became "$0.2995", and the suite FAILED while the ranker was correct. A
  # check wired to the wallet's SIZE cannot report on the ranker's BEHAVIOUR. The expected value
  # is now computed from a pinned book, so the light means what it says.
  test-pool-fee-rank.py
   # LFJ WAVAX/USDC reconciled on-chain: enumerates every Liquidity Book from the factory,
   # reads reserves + fee params, and flags the empty decoys. Chain is the source of truth.
   lfj-truth.py
   # Decodes REAL fee revenue from LB Swap events (fees are in the log). Guards against
   # reporting a total that cannot be true — an absurd number is a signal, not an output.
   lfj-fee-decode.py
   # Measures the buy list's actual state: up 30d/90d, down 365d, and how far each sits
   # from its high. Tells 'buying strength' apart from 'cycle turn' — the two read
   # identically on a 30-day chart. READ-ONLY.
   buylist-state.py
   # Shared helper imported by the buy list and other cron scripts. It lived ONLY in the
   # profile scripts dir, so the vault copy could not run standalone — closing that gap.
   quiet_hours.py
   # Hourly snapshot of our LFJ claim so a real 24h fee rate can exist. Enrolled 2026-09-22:
  # it lived only in the profile, and the wrapper's 2>&1>/dev/null destroyed the cause of a
  # failure (a Cloudflare 1015 read as an anonymous "exit 1").
  lfj_fee_measure.py
  lfj-fee-snapshot.sh
  # Refreshes the chain-fee measurement cache that the treasury report reads. A cache
   # nobody refreshes is just a slower way to be wrong — and the report refuses one
   # older than 12h. Mirrors the cache back to the vault so both copies agree.
   chain-fee-refresh.sh
   # DEV vs INVEST — two separate axes. Jordan: 'developers have to separate working
   # on projects versus investing in projects, two different things.' ALGO is the proof:
   # MODERATE to build on, PRICE BET ONLY to hold. Missing data is labelled UNKNOWN.
   dev-vs-invest.py
   # ── Tenant boundary layer, enrolled 2026-09-22 ───────────────────────────
   # WHY: tenant_guard.py, tenants.json, speakers.json and autonomy-model.json all
   # existed in the VAULT but were NEVER in this manifest, so they never reached the
   # profile — which is a large part of why the guards were unwired: the code that
   # would call them could not import them. The guard is only real if it ships.
   # steward_identity.signer() now asserts the tenant boundary before returning a key,
   # so every signing path inherits the check without opting in.
   tenant_guard.py
   tenants.json
   speakers.json
   autonomy-model.json
   # steward_heartbeat.py was NOT enrolled, so the vault copy could never reach the
   # profile — the vault silently diverged while the profile kept running the old
   # hardcoded wallet. Found 2026-09-22 while wiring the tenant boundary.
   steward_heartbeat.py
   # ── LFJ family gap, closed 2026-09-22 ────────────────────────────────────
   # Both of these existed in the vault and never reached the profile. fee_efficiency.py
   # is the module the 10-minute low-efficiency trigger reads, and lfj_swap_leg.py is the
   # executor that funds a curve's bid leg — the exact step a curve re-center needs. A
   # script the loop depends on but which never ships is a loop that cannot run.
   fee_efficiency.py
   lfj_swap_leg.py
   # Jordan 2026-09-22 reversed the self-custody-only posture for collaborators: "I think
   # it's okay if you create the wallet and the key pair for them, but just keep it separate."
   provision_tenant_wallet.py
   # The leaderboard values each tenant in its OWN process; it is the report the fleet reads
   # to see whose capital is working hardest.
   yield_leaderboard.py
   yield-leaderboard.sh
   # Per-person DeFi hubs: each tenant gets its OWN data file and its OWN page, so a collaborator
   # has a link that can only ever show their own pool. Jordan 2026-09-22: "so we have our own
   # links to check our own pools."
   defi_hub_index.py
  defi_hub_data.py
   # ── THE UPTIME / DUTY-CYCLE STAT (Jordan, 2026-09-25) ────────────────────────────────────
   # "add the amount of hours that we've been active inside the pool between each rebalance...
   #  that would also show us the benefits of what we're doing versus doing it manually."
   # ENROLLED AT CREATION TIME, ON PURPOSE. Not being in this manifest is not a soft failure —
   # the file simply never reaches the profile, defi_hub_data.py's import falls into its
   # try/except, and BOTH pages would render UNKNOWN forever with nothing in the logs to say why.
   # A silent UNKNOWN that looks like a data outage is worse than a crash. This is the trap that
   # has bitten this project three times; the entry goes in with the file, never after it.
   duty_cycle.py
   # ── COMPOUNDING IS THE HEADLINE (Jordan, 2026-09-25) ──────────────────────────────────────
   # "instead of showing how much work in capital that we have in the pool Why don't we instead
   #  talk about how much is being auto compounded back into the bins or back into Our LP"
   # defi_hub_data.py imports this inside a try/except, so a file that does NOT travel does not
   # crash the build -- it makes BOTH pages render UNKNOWN forever with nothing in the log to say
   # why. That is the exact enrolment trap this manifest names twice above (duty_cycle.py, and
   # lfj_shapes.py): the import falls into the except and the silence looks like a data outage.
   # A module the hub imports IS the hub. Enrolled with the file, never after it.
   compound_status.py
   # DEFAULT per-tenant check: every tenant was deployed by lfj_bid_deploy.py, so the inverted-ask
   # bug is never a one-tenant defect. Jordan 2026-09-22: "By default check both of our pages for
   # the same bug."
   leg_orientation_check.py
  # REGRESSION TESTS ship with the code they guard. test_leg_orientation.py exists because the
  # leg-orientation detector raised a FALSE "inverted" on a correct book three times in one day —
  # each cut was only ever exercised against the live hub, so the person who found the bug was
  # Jordan, on his own page. A guard file that is not synced is a guard that does not exist on the
  # machine that runs it.
  test_leg_orientation.py
  test_verify_ratio.py
    # ── OFF-BOX BASELINE (2026-09-28) ──────────────────────────────────────────────────────────────
    # Fast-forwards HQ's backup ref so the restore point stays close to HEAD while the vault
    # main push is blocked by the fork. NEVER main, NEVER force, hourly, silent on success.
    # If the update is not a fast-forward it STOPS loudly — that state is an alarm, not an obstacle.
    # A baseline that decays, not a safety net. THE MERGE CLOSES THE GAP; no snapshot does.
    hq-backup-update.py
    # ── CASE-COLLISION CHECK (2026-09-28) ──────────────────────────────────────────────────────────
    # Case-only path collisions break on case-insensitive clients (macOS/Windows): only one path
    # appears and WHICH one is not deterministic. Checks FILE and DIRECTORY levels — a file-path
    # scan cannot see a Games/ vs games/ collision. Exits 1 only when content DIFFERS (real risk).
    case-collisions.py
    # ── the updater's own tests (2026-09-28). The negative control is a FLAG (--ref main),
    # not a file edit, because a test you must edit the subject to run is a test nobody runs.
    test-hq-backup-update.sh
    # ── FAIL-CLOSED cap check (2026-09-28): an ENABLED class (allowTypes) whose file exceeds
    # Obsidian Sync's 5MB per-file cap is SILENTLY never uploaded while the client reports
    # "Fully synced". `allowTypes` widened from [image,pdf] to [image,pdf,audio,video] tonight,
    # which widens that silent surface. Exits 2 when it cannot measure — never a pass.
    enabled-class-oversize.py
    # ── RETRACTION SWEEP (2026-09-28, Pixel's discipline): a correction applied to the NEXT note
    # and not swept back through the EARLIER one leaves a stale figure answering first, unmarked.
    # Retracted figures live in retractions.json as DATA, not as a literal here — adding one is a
    # config line. Reports only; never edits prose.
    retraction-sweep.py
    retractions.json
    # ── ACCUMULATION TRACE (2026-09-28): the provider's `size` op is UNREACHABLE (zero callers, no
    # CLI route, no module exports, WebSocket+HKDF handshake). This measures the accumulation the
    # LOCAL table can see — uid high-water minus live rows — because the question a limit is
    # charged on is accumulation, not the live present. Named limits in the output, not hidden.
    sync-accumulation.py
    # ── SYNC HEALTH FROM THE SIZE COLUMN (2026-09-28, HQ's idea, corrected): the constant +28 B
    # server-vs-disk offset is ciphertext overhead, so a file off that offset has diverged. Three
    # corrections, each measured: an empty file expects 0 (no payload, no nonce/tag); the
    # UNSUPPORTED class can NEVER sync so its divergence is expected, not a fault (0 .json
    # transfers vs 3,412 .md); and the SIGN separates a pending upload from a stale tree.
    sync-health.py
)

echo "=== Syncing vault → repos + profile ==="
# ── A SKIPPED FILE IS A FAILED DEPLOY, NOT A COMPLETED ONE (fixed 2026-09-28) ─────────────────
# This loop used to say "⚠️ missing in vault — skipping", continue, and still print
# "Done. Vault is source of truth; repos + profile now match." — then exit 0. So a manifest line
# whose file did not exist produced a GREEN deploy while a live cron kept executing the OLD copy.
#
# That is not hypothetical: it nearly happened to `test_cron_health_no_recursion.py`, which sat
# UNTRACKED in the working tree while this manifest already referenced it. A fresh sync from a
# clean checkout would have skipped it, reported success, and left the cron sentinel's regression
# test permanently undeployed - the file that proves the fork-bomb cannot recur, silently absent,
# with a green light on top. (HQ caught it and committed the file; this line is why it mattered.)
#
# An unenrolled test is a claim, not a check. A skipped manifest entry is a claim, not a deploy.
SKIPPED=()
for f in "${SCRIPTS[@]}"; do
  if [ ! -f "$VAULT/$f" ]; then
    echo "  ❌ $f missing in vault — NOT deployed"
    SKIPPED+=("$f")
    continue
  fi
  # ── PRESERVE THE MODE, OR A SCRIPT DEPLOYS NON-EXECUTABLE (fixed 2026-09-23) ──────────
  # Plain `cp` drops the execute bit: a 755 script in the vault landed as 644 in the profile
  # and every runner got "Permission denied". The deploy silently degraded the artifact — the
  # same family as everything else that day, one layer down in the pipeline.
  #
  # ── ATOMIC REPLACE, OR A LIVE CRON READS A HALF-WRITTEN SCRIPT (fixed 2026-09-26) ─────
  # `cp` TRUNCATES the destination and then writes into it. The window is microseconds, but
  # this repo runs a FIVE-MINUTE cron that executes these exact files, and the cost of losing
  # that race is not a bad number — it is a dead runner. Measured: at 10:48:37 the watchdog
  # died mid-run with
  #     line 210: syntax error near unexpected token `elif'
  # while every copy of the file on disk was byte-identical, md5-verified and `bash -n` clean
  # BOTH before and after. The file was never broken; bash read it while cp was mid-write.
  # The failure was transient, self-healing and therefore nearly invisible — the worst kind,
  # because the next one will land on the WITHDRAW path instead of the reporter.
  # Fix: write to a temp file in the SAME directory, then `mv` it into place. rename(2) is
  # atomic within a filesystem, so a reader sees either the whole old file or the whole new
  # one, and never a torn one. `install -m` would also work but would not preserve the mode
  # the 2026-09-23 fix above exists to protect.
  _atomic_cp() {
    _src="$1"; _dst="$2"
    _tmp="$(dirname "$_dst")/.sync.$$.$(basename "$_dst")"
    if cp -p "$_src" "$_tmp" 2>/dev/null && mv -f "$_tmp" "$_dst"; then
      return 0
    fi
    rm -f "$_tmp" 2>/dev/null
    return 1
  }
  _atomic_cp "$VAULT/$f" "$REPOS/$f"
  _atomic_cp "$VAULT/$f" "$PROFILE/$f"
  # verify md5 across all three
  v=$(md5sum "$VAULT/$f" | awk '{print $1}')
  r=$(md5sum "$REPOS/$f" | awk '{print $1}')
  p=$(md5sum "$PROFILE/$f" | awk '{print $1}')
  if [ "$v" = "$r" ] && [ "$r" = "$p" ]; then
    echo "  ✅ $f synced (md5 $v)"
  else
    echo "  ❌ $f DIVERGED after sync!"
  fi
done

# ── Treasury/scripts members (different vault dir than the loop above) ─────
# cross_venue_scanner.py, arb_log.py and wire_arb_log.py are cron-executed
# signal sources that live in Treasury/scripts. The main loop resolves every
# path under $VAULT (the agent-kit dir), so enroll them here against their own
# vault source. Verified md5 across vault source and profile after copy.
TSRC="/root/vaults/gentech/Treasury/scripts"
# solana_homebase.py: its action_bridge() was the STUB that tranche2_demo printed as a working
# bridge. It was never enrolled here, so the vault copy and the profile copy diverged — I fixed
# the vault copy, ran it, and got the OLD stub string back from the stale profile duplicate.
# Enrolling it is the permanent fix for that class: a file that runs from two places must be
# synced, or a fix to one copy silently misses the other.
for f in cross_venue_scanner.py arb_log.py wire_arb_log.py solana_homebase.py tranche2_demo.py; do
  if [ ! -f "$TSRC/$f" ]; then
    echo "  ⚠️  $f missing in Treasury/scripts — skipping"
    continue
  fi
  cp -p "$TSRC/$f" "$REPOS/$f" 2>/dev/null || true
  cp -p "$TSRC/$f" "$PROFILE/$f"
  v=$(md5sum "$TSRC/$f" | awk '{print $1}')
  p=$(md5sum "$PROFILE/$f" | awk '{print $1}')
  if [ "$v" = "$p" ]; then
    echo "  ✅ $f synced from Treasury/scripts (md5 $v)"
  else
    echo "  ❌ $f DIVERGED after sync!"
  fi
done

if [ "${1:-}" = "--commit" ]; then
  echo "=== Committing repos copy ==="
  cd "$REPOS"
  git add -A
  git commit -m "auto: sync treasury scripts from vault $(date -u +%Y-%m-%dT%H:%MZ)" >/dev/null 2>&1 || echo "  (nothing to commit)"
  git push origin main >/dev/null 2>&1 || echo "  ⚠️  push failed (check remote)"
fi

# ── Self-sync ──────────────────────────────────────────────────────────────
# This script lives in scripts/ but syncs VAULT -> repos+profile, so it cannot
# protect itself through the normal loop. Mirror it into all three locations so
# the invariant "every enrolled file has a vault copy" actually holds — without
# this, the self-audit correctly reports it as enrolled-but-missing and the
# whole sync tool becomes the one file nobody can trust.
#
# ── BUT THE VAULT IS THE SOURCE OF TRUTH, INCLUDING FOR THIS SCRIPT ──────────────────────────
# (fixed 2026-09-27 — this block was overwriting the source of truth with a stale copy)
#
# It used to copy whichever copy was INVOKED to all three locations. cron invokes the PROFILE
# copy, so a scheduled run copied PROFILE -> VAULT: a stale profile silently overwrote the vault.
# The tool that exists to keep the copies CONSISTENT was itself the thing making them disagree,
# and it did it in the one direction nobody would think to check.
#
# MEASURED, not theorised: an edit adding test_gas_on_redeploy.py to the manifest landed in the
# vault, synced out to the profile, and was GONE from BOTH before the next commit — because a cron
# self-sync wrote the profile's older copy back over the vault. An edit that vanishes leaves no
# trace to debug; the only reason it was caught is that the file was checked afterwards.
#
# So: the VAULT copy is the source. It propagates to repos + profile. A copy that is not the vault
# may never write to the vault.
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
VAULT_SELF="$VAULT/$(basename "$0")"
SELF_SRC="$SELF"
if [ -f "$VAULT_SELF" ] && [ "$SELF" != "$VAULT_SELF" ]; then
    # invoked from repos/ or profile/ — the vault still wins, never the other way round
    SELF_SRC="$VAULT_SELF"
fi
# ── SELF-SYNC MUST BE ATOMIC, INCLUDING OVER THE RUNNING FILE (fixed 2026-09-30) ──────────────
# This loop copies the script onto itself when launched from its own location, and bash reads a
# running script INCREMENTALLY BY BYTE OFFSET. A plain `cp` truncates and rewrites the SAME inode,
# so bash resumes at a stale offset and executes whatever bytes now sit there -- which is why this
# script exited non-zero with a DIFFERENT mangled token each run (`ound: command not found`, then
# `.: filename argument required`, then `ds: command not found`, at moving line numbers) while the
# copying itself always completed.
#   A fixed line number and a stable message means a normal bug. A MOVING one means the interpreter
#   is reading a file that is shifting underneath it.
# THE FIX IS THE ATOMIC COPY THIS SCRIPT ALREADY USES EVERYWHERE ELSE: write a temp file and `mv`
# it into place. rename(2) swaps the DIRECTORY ENTRY while the running bash keeps its file
# descriptor on the OLD inode, so the executing script is never read mid-write and the destination
# still ends up current. An earlier version of this fix simply SKIPPED the running file, which
# stopped the corruption but FROZE the profile copy -- the very copy the cron launches.
for dest in "$VAULT/$(basename "$0")" "$REPOS/$(basename "$0")" "$PROFILE/$(basename "$0")"; do
    if [ -f "$SELF_SRC" ] && [ "$SELF_SRC" != "$dest" ]; then
        _atomic_cp "$SELF_SRC" "$dest" 2>/dev/null \
          && echo "  ✅ $(basename "$0") self-synced -> $dest"
    fi
done

# ── Runtime-state mirror (REVERSE direction on purpose) ───────────────────
# treasury-state.json is RUNTIME state written by the executor, not code. The
# normal loop is vault -> repos; for THIS ONE FILE the truth flows the other way.
# Syncing it vault->repos would CLOBBER the live state, and not syncing it left
# the vault mirror stale (it read TRADE while live read YIELD_FARM — the drift
# Jordan's trade-mode cron flagged). So: mirror live -> vault, and verify.
LIVE_STATE="/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json"
VAULT_STATE="$VAULT/treasury-state.json"
if [ -f "$LIVE_STATE" ]; then
  if ! cmp -s "$LIVE_STATE" "$VAULT_STATE"; then
    cp "$LIVE_STATE" "$VAULT_STATE" \
      && echo "  ✅ treasury-state.json mirrored live -> vault (runtime state)"
  fi
  # verify the mirror actually matches — a copy is not a copy until re-read
  if cmp -s "$LIVE_STATE" "$VAULT_STATE"; then
    echo "  ✅ state mirror in sync (mode=$(python3 -c "import json;print(json.load(open('$LIVE_STATE'))['mode'])" 2>/dev/null))"
  else
    echo "  ⚠️  STATE MIRROR STILL DRIFTED — check $VAULT_STATE"
  fi
fi

if [ ${#SKIPPED[@]} -gt 0 ]; then
  echo ""
  echo "❌ DEPLOY INCOMPLETE — ${#SKIPPED[@]} manifest file(s) did not exist in the vault, so the"
  echo "   profile is NOT in sync with the source of truth. A live cron may still be running the"
  echo "   previous copy of each one:"
  for f in "${SKIPPED[@]}"; do echo "     - $f"; done
  echo "   Fix: commit the file, or remove the line from this manifest. Do not ignore this."
  exit 1
fi

echo "=== Done. Vault is source of truth; repos + profile now match. ==="
  