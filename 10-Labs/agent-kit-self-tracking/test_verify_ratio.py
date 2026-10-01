"""Prove _verify_ratio DISCRIMINATES: on-target vs off-target vs unreadable.
A check that cannot fail is not a check."""
import sys, io, contextlib
sys.path.insert(0, "/root/vaults/gentech/10-Labs/agent-kit-self-tracking")
from lfj_recenter import _verify_ratio

class FakeTok:
    def __init__(self, raw): self._raw = raw
    @property
    def functions(self): return self
    def balanceOf(self, me): return self
    def call(self): return self._raw

def run(u_raw, w_raw, px, target):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        a, ok = _verify_ratio(None, FakeTok(u_raw), FakeTok(w_raw), "0x0", target, {"avax_usd": px})
    return a, ok, out.getvalue()

CASES = [
    # (desc, usdc_raw, wavax_raw, price, target, expect_on_target)
    ("70/30 CORRECT (jordan now)",   43_240_000, int(9.36e18), 10.94, 0.70, True),
    ("98.8/1.2 INVERTED (jordan 11:33)", 143_820_000, int(0.156e18), 10.94, 0.70, False),
    ("76/24 (dadrian now)",           21_360_000, int(0.62e18),  10.94, 0.70, False),
    ("exactly 50/50 vs 0.70 target",  73_000_000, int(6.67e18),  10.94, 0.70, False),
]
print(f"  {'case':<38} {'achieved ask':>13} {'on_target':>10}  verdict")
print("  " + "-"*76)
bad = 0
for desc, u, w, px, tgt, exp in CASES:
    a, ok, _ = run(u, w, px, tgt)
    good = (ok == exp)
    if not good: bad += 1
    print(f"  {desc:<38} {a*100:>12.1f}% {str(ok):>10}  {'OK' if good else 'FAIL — MISCLASSIFIED'}")

# unreadable must NOT read as on-target
a, ok, txt = run(0, 0, 0, 0.70)
print(f"  {'no price / both zero':<38} {'—':>13} {str(ok):>10}  "
      f"{'OK' if ok is None else 'FAIL — reported a verdict on an unreadable read'}")

print()
print(f"  RESULT: {'PASS' if bad == 0 and a is None else 'FAIL'}")
