"""Tests for Dry Powder Mode — Phase 2: Auto-Retreat to Swap."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dry_powder_defense import (
    DefenseState, SignalType, ShapeType,
    PositionState, DefenseConfig, SignalResult, ReEntryAssessment, RetreatLog,
    DryPowderDefense,
)


def assert_eq(actual, expected, msg=""):
    if actual != expected:
        print(f"  ❌ {msg or f'Expected {expected!r}, got {actual!r}'}")
        return False
    print(f"  ✅ {msg or f'{actual!r} == {expected!r}'}")
    return True

def assert_in(item, container, msg=""):
    if item not in container:
        print(f"  ❌ {msg or f'{item!r} not in {container!r}'}")
        return False
    print(f"  ✅ {msg or f'{item!r} found'}")
    return True

def assert_gt(a, b, msg=""):
    if not (a > b):
        print(f"  ❌ {msg or f'{a} <= {b}'}")
        return False
    print(f"  ✅ {msg or f'{a} > {b}'}")
    return True

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    print(f"\n{name}")
    result = fn()
    if result:
        passed += 1
    else:
        failed += 1
        print(f"  ❌ TEST FAILED")


# ── Tests ──────────────────────────────────────────────────────────

def test_initial_state():
    defense = DryPowderDefense(simulation=True)
    ok = assert_eq(defense.state, DefenseState.NORMAL, "Initial state = NORMAL")
    return ok

def test_normal_in_range():
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    state = defense.tick(pos, 6.5)
    ok = assert_eq(state, DefenseState.NORMAL, "In range → NORMAL")
    return ok

def test_normal_out_of_range():
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    state = defense.tick(pos, 7.5)
    ok = assert_eq(state, DefenseState.HOLD, "Out of range → HOLD")
    return ok

def test_hold_recovery():
    """Price re-enters range during hold window."""
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    # First tick: out of range → HOLD
    defense.tick(pos, 7.5)
    # Second tick: back in range → NORMAL
    state = defense.tick(pos, 6.5)
    ok = assert_eq(state, DefenseState.NORMAL, "Price returns → NORMAL")
    return ok

def test_hold_to_retreat():
    """Hold timer expires → retreat on next tick."""
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0  # Instant retreat
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    # First tick: out of range → HOLD
    state1 = defense.tick(pos, 7.5)
    ok = assert_eq(state1, DefenseState.HOLD, "First tick → HOLD")
    # Second tick: timer expired → retreat → SENTINEL
    state2 = defense.tick(pos, 7.5)
    ok &= assert_eq(state2, DefenseState.SENTINEL, "Second tick → SENTINEL (after retreat)")
    return ok

def test_retreat_logs_created():
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT → SENTINEL
    logs = defense.get_retreat_logs()
    ok = assert_eq(len(logs), 1, "1 retreat log created")
    ok &= assert_gt(logs[0].total_usd_before, 0, "Log has position value")
    ok &= assert_gt(logs[0].usdc_after, 0, "Log has USDC value")
    return ok

def test_retreat_logs_multiple():
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT 1
    defense.reset()
    defense.tick(pos, 5.0)  # → HOLD
    defense.tick(pos, 5.0)  # → RETREAT 2
    logs = defense.get_retreat_logs()
    ok = assert_eq(len(logs), 2, "2 retreat logs")
    return ok

def test_sentinel_stays():
    """In sentinel mode, stays in sentinel if signals are bad."""
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT → SENTINEL
    # Tick with bad signals
    signals = {
        "fear_and_greed": 20,
        "volume_ratio_24h": 0.1,
        "price_range_pct_2h": 5.0,
        "hours_to_next_event": 12,
    }
    state = defense.tick(pos, 7.5, signals)
    ok = assert_eq(state, DefenseState.SENTINEL, "Bad signals → stays SENTINEL")
    return ok

def test_sentinel_to_normal():
    """Good signals → re-enter → NORMAL."""
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT → SENTINEL
    # Tick with good signals
    signals = {
        "fear_and_greed": 50,
        "volume_ratio_24h": 1.0,
        "price_range_pct_2h": 1.0,
        "hours_to_next_event": 72,
    }
    state = defense.tick(pos, 7.5, signals)
    ok = assert_eq(state, DefenseState.NORMAL, "Good signals → re-enter → NORMAL")
    return ok

def test_assess_re_entry_all_good():
    defense = DryPowderDefense(simulation=True)
    signals = {
        "fear_and_greed": 50,
        "volume_ratio_24h": 1.0,
        "price_range_pct_2h": 1.0,
        "hours_to_next_event": 72,
    }
    assessment = defense.assess_re_entry(signals)
    ok = assert_eq(assessment.positive_count, 4, "All 4 signals positive")
    ok &= assert_eq(assessment.ready, True, "Ready for re-entry")
    return ok

def test_assess_re_entry_all_bad():
    defense = DryPowderDefense(simulation=True)
    signals = {
        "fear_and_greed": 20,
        "volume_ratio_24h": 0.1,
        "price_range_pct_2h": 5.0,
        "hours_to_next_event": 12,
    }
    assessment = defense.assess_re_entry(signals)
    ok = assert_eq(assessment.positive_count, 0, "0 signals positive")
    ok &= assert_eq(assessment.ready, False, "Not ready for re-entry")
    return ok

def test_assess_re_entry_partial():
    """2/4 signals positive → not ready (need 3/4 = 0.75)."""
    defense = DryPowderDefense(simulation=True)
    signals = {
        "fear_and_greed": 50,       # Good
        "volume_ratio_24h": 1.0,    # Good
        "price_range_pct_2h": 5.0,  # Bad
        "hours_to_next_event": 12,  # Bad
    }
    assessment = defense.assess_re_entry(signals)
    ok = assert_eq(assessment.positive_count, 2, "2/4 signals positive")
    ok &= assert_eq(assessment.ready, False, "Not ready (need 0.75)")
    return ok

def test_il_estimate_below_range():
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0, current_price=5.0)
    il = defense._estimate_impermanent_loss(pos)
    ok = assert_gt(il, 0, "IL > 0 when price below range")
    return ok

def test_il_estimate_above_range():
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0, current_price=8.0)
    il = defense._estimate_impermanent_loss(pos)
    ok = assert_gt(il, 0, "IL > 0 when price above range")
    return ok

def test_il_estimate_in_range():
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0, current_price=6.5)
    il = defense._estimate_impermanent_loss(pos)
    ok = assert_eq(il, 0.0, "IL = 0 when price in range")
    return ok

def test_il_estimate_capped():
    """IL should be capped at 10%."""
    defense = DryPowderDefense(simulation=True)
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0, current_price=1.0)
    il = defense._estimate_impermanent_loss(pos)
    ok = assert_eq(il, 10.0, "IL capped at 10%")
    return ok

def test_reset():
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT → SENTINEL
    ok = assert_eq(defense.state, DefenseState.SENTINEL, "State = SENTINEL after retreat")
    defense.reset()
    ok &= assert_eq(defense.state, DefenseState.NORMAL, "State = NORMAL after reset")
    return ok

def test_get_status():
    defense = DryPowderDefense(simulation=True)
    status = defense.get_status()
    ok = assert_eq(status["state"], "normal", "Status shows normal")
    ok &= assert_eq(status["retreats_executed"], 0, "0 retreats")
    return ok

def test_get_status_after_retreat():
    defense = DryPowderDefense(simulation=True)
    defense.config.retreat_timer_seconds = 0
    pos = PositionState(total_usd=100, range_low=6.0, range_high=7.0)
    defense.tick(pos, 7.5)  # → HOLD
    defense.tick(pos, 7.5)  # → RETREAT → SENTINEL
    status = defense.get_status()
    ok = assert_eq(status["state"], "sentinel", "Status shows sentinel")
    ok &= assert_eq(status["retreats_executed"], 1, "1 retreat")
    return ok

def test_config_defaults():
    config = DefenseConfig()
    ok = assert_eq(config.enabled, True, "Enabled by default")
    ok &= assert_eq(config.retreat_timer_seconds, 300, "5 min hold timer")
    ok &= assert_eq(config.sentinel_interval_minutes, 30, "30 min sentinel")
    ok &= assert_eq(config.re_entry_threshold, 0.75, "0.75 threshold")
    return ok

def test_config_custom():
    config = DefenseConfig(enabled=False, retreat_timer_seconds=600)
    ok = assert_eq(config.enabled, False, "Custom enabled")
    ok &= assert_eq(config.retreat_timer_seconds, 600, "Custom timer")
    return ok

def test_signal_result():
    sr = SignalResult(
        signal=SignalType.FEAR_AND_GREED,
        positive=True,
        value=50,
        threshold=35,
        weight=0.25,
        detail="Fear & Greed: 50 (need ≥ 35)",
    )
    ok = assert_eq(sr.positive, True, "Signal positive")
    ok &= assert_eq(sr.value, 50, "Signal value")
    return ok

def test_re_entry_assessment_score():
    assessment = ReEntryAssessment(threshold=0.75)
    assessment.signals = [
        SignalResult(SignalType.FEAR_AND_GREED, True, 50, 35, 0.25, ""),
        SignalResult(SignalType.VOLUME_STABILIZATION, True, 1.0, 0.5, 0.25, ""),
    ]
    ok = assert_eq(assessment.score, 0.5, "Score = 0.5 (2/4 signals)")
    return ok

def test_cli_simulate():
    import subprocess
    result = subprocess.run(
        [sys.executable, "dry_powder_defense.py", "simulate",
         "--price", "6.56", "--range-low", "6.40", "--range-high", "6.55",
         "--position-usd", "45.24", "--ticks", "3", "--price-drop", "0.05"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI simulate exits 0")
    ok &= assert_in("Starting defense", result.stdout, "Shows simulation start")
    return ok

def test_cli_assess():
    import subprocess
    result = subprocess.run(
        [sys.executable, "dry_powder_defense.py", "assess",
         "--fear-greed", "50", "--volume-ratio", "1.0",
         "--price-range", "1.5", "--hours-to-event", "72"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI assess exits 0")
    ok &= assert_in("Re-entry Assessment", result.stdout, "Shows assessment")
    return ok

def test_cli_status():
    import subprocess
    result = subprocess.run(
        [sys.executable, "dry_powder_defense.py", "status"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI status exits 0")
    ok &= assert_in("State:", result.stdout, "Shows state")
    return ok


# ── Run ────────────────────────────────────────────────────────────

tests = [
    ("Initial state = NORMAL", test_initial_state),
    ("In range → NORMAL", test_normal_in_range),
    ("Out of range → HOLD", test_normal_out_of_range),
    ("Hold recovery → NORMAL", test_hold_recovery),
    ("Hold timer → retreat", test_hold_to_retreat),
    ("Retreat logs created", test_retreat_logs_created),
    ("Multiple retreat logs", test_retreat_logs_multiple),
    ("Sentinel stays with bad signals", test_sentinel_stays),
    ("Sentinel → NORMAL with good signals", test_sentinel_to_normal),
    ("Re-entry assessment: all good", test_assess_re_entry_all_good),
    ("Re-entry assessment: all bad", test_assess_re_entry_all_bad),
    ("Re-entry assessment: partial", test_assess_re_entry_partial),
    ("IL estimate: below range", test_il_estimate_below_range),
    ("IL estimate: above range", test_il_estimate_above_range),
    ("IL estimate: in range", test_il_estimate_in_range),
    ("IL estimate: capped at 10%", test_il_estimate_capped),
    ("Reset to NORMAL", test_reset),
    ("Get status", test_get_status),
    ("Get status after retreat", test_get_status_after_retreat),
    ("Config defaults", test_config_defaults),
    ("Config custom", test_config_custom),
    ("Signal result", test_signal_result),
    ("Re-entry assessment score", test_re_entry_assessment_score),
    ("CLI simulate", test_cli_simulate),
    ("CLI assess", test_cli_assess),
    ("CLI status", test_cli_status),
]

for name, fn in tests:
    test(name, fn)

total = passed + failed
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
