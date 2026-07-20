"""Tests for GenTech Hub — P2P Causes + Flyer Factory."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

from p2p_causes import (
    Cause, Contribution, WalletReputation, ReputationTier,
    CauseStatus, FlyerStyle, FlyerFormat, FlyerSpec,
    P2PCausesEngine,
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

def assert_close(actual, expected, tolerance=0.01, msg=""):
    if abs(actual - expected) > tolerance:
        print(f"  ❌ {msg or f'{actual} != {expected} (tolerance {tolerance})'}")
        return False
    print(f"  ✅ {msg or f'{actual} ~= {expected}'}")
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

def test_create_cause():
    engine = P2PCausesEngine(simulation=True)
    cause = engine.create_cause(
        title="Save the Coral Reefs",
        story="We need funds to restore coral reefs in the Philippines.",
        creator_wallet="0xabc123",
        goal_amount_usd=5000,
        tags=["environment", "ocean", "philippines"],
    )
    ok = assert_in("cause-", cause.id, "Cause has ID")
    ok &= assert_eq(cause.title, "Save the Coral Reefs", "Title preserved")
    ok &= assert_eq(cause.status, CauseStatus.ACTIVE, "Status = ACTIVE")
    ok &= assert_eq(cause.raised_amount_usd, 0.0, "Starts at $0 raised")
    ok &= assert_eq(cause.progress_pct, 0.0, "Progress = 0%")
    return ok

def test_contribute():
    engine = P2PCausesEngine(simulation=True)
    cause = engine.create_cause("Test", "Test story", "0xcreator", 1000)
    contrib = engine.contribute("cause-1", "0xdonor", 100, "Great cause!")
    ok = assert_eq(contrib is not None, True, "Contribution succeeded")
    ok &= assert_eq(contrib.amount_usd, 100.0, "Amount preserved")
    ok &= assert_eq(contrib.message, "Great cause!", "Message preserved")
    # Check cause updated
    cause = engine.get_cause("cause-1")
    ok &= assert_eq(cause.raised_amount_usd, 100.0, "Raised amount updated")
    ok &= assert_eq(cause.contributor_count, 1, "Contributor count = 1")
    ok &= assert_close(cause.progress_pct, 10.0, msg="Progress = 10%")
    return ok

def test_contribute_fully_funds():
    engine = P2PCausesEngine(simulation=True)
    cause = engine.create_cause("Test", "Test", "0xcreator", 100)
    engine.contribute("cause-1", "0xdonor", 100)
    cause = engine.get_cause("cause-1")
    ok = assert_eq(cause.status, CauseStatus.FUNDED, "Status = FUNDED when goal met")
    ok &= assert_eq(cause.is_fully_funded, True, "is_fully_funded = True")
    return ok

def test_contribute_inactive_cause():
    engine = P2PCausesEngine(simulation=True)
    cause = engine.create_cause("Test", "Test", "0xcreator", 100)
    cause.status = CauseStatus.CANCELLED
    result = engine.contribute("cause-1", "0xdonor", 50)
    ok = assert_eq(result, None, "Contribution to cancelled cause fails")
    return ok

def test_contribute_nonexistent():
    engine = P2PCausesEngine(simulation=True)
    result = engine.contribute("nonexistent", "0xdonor", 50)
    ok = assert_eq(result, None, "Contribution to nonexistent cause fails")
    return ok

def test_contribute_zero_amount():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Test", "Test", "0xcreator", 100)
    result = engine.contribute("cause-1", "0xdonor", 0)
    ok = assert_eq(result, None, "Zero contribution fails")
    return ok

def test_list_causes():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Cause A", "Story A", "0x1", 100)
    engine.create_cause("Cause B", "Story B", "0x2", 200)
    engine.create_cause("Cause C", "Story C", "0x3", 300)
    causes = engine.list_causes()
    ok = assert_eq(len(causes), 3, "3 causes listed")
    return ok

def test_list_causes_by_status():
    engine = P2PCausesEngine(simulation=True)
    c1 = engine.create_cause("Active", "Active", "0x1", 100)
    c2 = engine.create_cause("Funded", "Funded", "0x2", 100)
    engine.contribute("cause-2", "0xdonor", 100)  # Funds it
    active = engine.list_causes(CauseStatus.ACTIVE)
    funded = engine.list_causes(CauseStatus.FUNDED)
    ok = assert_eq(len(active), 1, "1 active cause")
    ok &= assert_eq(len(funded), 1, "1 funded cause")
    return ok

def test_get_contributions():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Test", "Test", "0xcreator", 1000)
    engine.contribute("cause-1", "0xalice", 50)
    engine.contribute("cause-1", "0xbob", 75)
    contribs = engine.get_contributions("cause-1")
    ok = assert_eq(len(contribs), 2, "2 contributions")
    ok &= assert_eq(sum(c.amount_usd for c in contribs), 125.0, "Total = $125")
    return ok

def test_wallet_reputation_new():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Test", "Test", "0xnew", 100)
    rep = engine.get_reputation("0xnew")
    ok = assert_eq(rep is not None, True, "Reputation created")
    ok &= assert_eq(rep.tier, ReputationTier.NEW, "New wallet = NEW tier")
    return ok

def test_wallet_reputation_trusted():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("C1", "S1", "0xcreator", 100)
    engine.contribute("cause-1", "0xsupporter", 10)
    engine.contribute("cause-1", "0xsupporter", 10)
    rep = engine.get_reputation("0xsupporter")
    ok = assert_eq(rep.tier, ReputationTier.TRUSTED, "2 contributions = TRUSTED")
    return ok

def test_wallet_reputation_verified():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("C1", "S1", "0xcreator", 100)
    for i in range(6):
        engine.contribute("cause-1", "0xsupporter", 10)
    rep = engine.get_reputation("0xsupporter")
    ok = assert_eq(rep.tier, ReputationTier.VERIFIED, "6 contributions = VERIFIED")
    return ok

def test_wallet_reputation_core():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("C1", "S1", "0xcreator", 10000)  # High goal so it stays active
    for i in range(21):
        engine.contribute("cause-1", "0xsupporter", 10)
    rep = engine.get_reputation("0xsupporter")
    ok = assert_eq(rep.tier, ReputationTier.CORE, "21 contributions = CORE")
    return ok

def test_flyer_generation():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Save the Reefs", "Help restore coral reefs in the Philippines.",
                        "0xcreator", 5000, tags=["environment", "ocean"])
    engine.contribute("cause-1", "0xdonor", 500)
    html = engine.generate_flyer("cause-1", FlyerStyle.MODERN, FlyerFormat.POSTER)
    ok = assert_eq(html is not None, True, "Flyer generated")
    ok &= assert_in("Save the Reefs", html, "Title in flyer")
    ok &= assert_in("P2P Cause", html, "Badge in flyer")
    ok &= assert_in("500", html, "Raised amount in flyer")
    ok &= assert_in("5000", html, "Goal amount in flyer")
    ok &= assert_in("GenTech Labs", html, "Footer present")
    return ok

def test_flyer_styles():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Test", "Test", "0xcreator", 100)
    for style in FlyerStyle:
        html = engine.generate_flyer("cause-1", style, FlyerFormat.SQUARE)
        ok = assert_eq(html is not None, True, f"Flyer with {style.value} style")
        if not ok:
            return False
    return True

def test_flyer_formats():
    engine = P2PCausesEngine(simulation=True)
    engine.create_cause("Test", "Test", "0xcreator", 100)
    for fmt in FlyerFormat:
        html = engine.generate_flyer("cause-1", FlyerStyle.MODERN, fmt)
        ok = assert_eq(html is not None, True, f"Flyer with {fmt.value} format")
        if not ok:
            return False
    return True

def test_flyer_nonexistent_cause():
    engine = P2PCausesEngine(simulation=True)
    html = engine.generate_flyer("nonexistent")
    ok = assert_eq(html, None, "Nonexistent cause → None")
    return ok

def test_cause_remaining():
    cause = Cause(id="test", title="T", story="S", creator_wallet="0xw",
                  goal_amount_usd=1000, raised_amount_usd=300)
    ok = assert_eq(cause.remaining_usd, 700.0, "Remaining = $700")
    return ok

def test_cause_remaining_overfunded():
    cause = Cause(id="test", title="T", story="S", creator_wallet="0xw",
                  goal_amount_usd=1000, raised_amount_usd=1200)
    ok = assert_eq(cause.remaining_usd, 0.0, "Overfunded → remaining = $0")
    return ok

def test_cause_progress_100():
    cause = Cause(id="test", title="T", story="S", creator_wallet="0xw",
                  goal_amount_usd=1000, raised_amount_usd=2000)
    ok = assert_eq(cause.progress_pct, 100.0, "Overfunded → progress = 100%")
    return ok

def test_cause_zero_goal():
    cause = Cause(id="test", title="T", story="S", creator_wallet="0xw",
                  goal_amount_usd=0)
    ok = assert_eq(cause.progress_pct, 0.0, "Zero goal → progress = 0%")
    return ok

def test_reputation_recalculate():
    rep = WalletReputation(wallet="0xw", causes_supported=5, causes_created=1)
    rep.recalculate_tier()
    ok = assert_eq(rep.tier, ReputationTier.VERIFIED, "6 total → VERIFIED")
    return ok

def test_reputation_new_default():
    rep = WalletReputation(wallet="0xw")
    ok = assert_eq(rep.tier, ReputationTier.NEW, "Default tier = NEW")
    return ok

def test_cli_create():
    import subprocess
    result = subprocess.run(
        [sys.executable, "p2p_causes.py", "create",
         "--title", "Test Cause", "--story", "Test story",
         "--wallet", "0xabc", "--goal", "500"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI create exits 0")
    ok &= assert_in("Cause created", result.stdout, "CLI shows success")
    return ok

def test_cli_list():
    import subprocess
    result = subprocess.run(
        [sys.executable, "p2p_causes.py", "list"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI list exits 0")
    return ok

def test_cli_flyer():
    import subprocess
    # Create a cause and generate flyer in one script
    script = '''
import sys
sys.path.insert(0, "/root/vaults/gentech/10-Labs/p2p-causes")
from p2p_causes import P2PCausesEngine, FlyerStyle, FlyerFormat
engine = P2PCausesEngine(simulation=True)
cause = engine.create_cause("Flyer Test", "Test", "0xabc", 100)
html = engine.generate_flyer(cause.id, FlyerStyle.MODERN, FlyerFormat.POSTER)
with open("/tmp/test-flyer.html", "w") as f:
    f.write(html)
print("Flyer written to /tmp/test-flyer.html")
'''
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True,
    )
    ok = assert_eq(result.returncode, 0, "Flyer generation exits 0")
    ok &= assert_in("Flyer written", result.stdout, "Shows success")
    ok &= assert_eq(os.path.exists("/tmp/test-flyer.html"), True, "Flyer file exists")
    if os.path.exists("/tmp/test-flyer.html"):
        os.unlink("/tmp/test-flyer.html")
    return ok

def test_cli_reputation():
    import subprocess
    result = subprocess.run(
        [sys.executable, "p2p_causes.py", "reputation", "--wallet", "0xnew"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
    )
    ok = assert_eq(result.returncode, 0, "CLI reputation exits 0")
    return ok


# ── Run ────────────────────────────────────────────────────────────

tests = [
    ("Create cause", test_create_cause),
    ("Contribute to cause", test_contribute),
    ("Contribute fully funds", test_contribute_fully_funds),
    ("Contribute inactive cause", test_contribute_inactive_cause),
    ("Contribute nonexistent cause", test_contribute_nonexistent),
    ("Contribute zero amount", test_contribute_zero_amount),
    ("List causes", test_list_causes),
    ("List causes by status", test_list_causes_by_status),
    ("Get contributions", test_get_contributions),
    ("Wallet reputation: NEW", test_wallet_reputation_new),
    ("Wallet reputation: TRUSTED", test_wallet_reputation_trusted),
    ("Wallet reputation: VERIFIED", test_wallet_reputation_verified),
    ("Wallet reputation: CORE", test_wallet_reputation_core),
    ("Flyer generation", test_flyer_generation),
    ("Flyer all styles", test_flyer_styles),
    ("Flyer all formats", test_flyer_formats),
    ("Flyer nonexistent cause", test_flyer_nonexistent_cause),
    ("Cause remaining amount", test_cause_remaining),
    ("Cause remaining overfunded", test_cause_remaining_overfunded),
    ("Cause progress capped at 100%", test_cause_progress_100),
    ("Cause zero goal", test_cause_zero_goal),
    ("Reputation recalculate", test_reputation_recalculate),
    ("Reputation default tier", test_reputation_new_default),
    ("CLI create", test_cli_create),
    ("CLI list", test_cli_list),
    ("CLI flyer", test_cli_flyer),
    ("CLI reputation", test_cli_reputation),
]

for name, fn in tests:
    test(name, fn)

total = passed + failed
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
