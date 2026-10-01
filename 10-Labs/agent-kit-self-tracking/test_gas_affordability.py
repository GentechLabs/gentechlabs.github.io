#!/usr/bin/env python3
"""Guard the gas precondition: the floor is POLICY (rescuable), affordability is PHYSICS.

Jordan, 2026-09-27, after his book sat stranded for five hours: *"the biggest thing I'm worried
about is sitting with low efficiency for too long and not acting."* He was right, and this is the
gate that was supposed to prevent it.

THE FAILURE THIS GUARDS. `_gas_precondition` collapsed two different questions into ONE gate:

    ok, why = GR.gate(info, cost_avax=need_avax, action="re-center", bypass=rescue)

`bypass=rescue` skipped the FLOOR — correct, the reserve exists for repairs — but because the
two questions shared one call it ALSO skipped "can this cycle FINISH?". So the rescue withdrew a
DEPLOYED book it could not re-deploy:

    Web3RPCError: insufficient funds for gas * price + value:
        balance 4584049209086108, tx cost 6620230615071780

...and then repeated the same doomed rescue every 10 minutes for hours, burning gas against a
shrinking balance while the capital sat in the wallet earning nothing — the exact state the
rescue exists to fix, held open BY the rescue.

THE RULE:
  * FLOOR          `balance - cost >= reserve`  -> POLICY.  A rescue may override it.
  * AFFORDABILITY  `balance >= cost`            -> PHYSICS. No flag can override it.

WHY THE BALANCE IS STUBBED. The interesting case is a wallet that cannot pay, and a live wallet
cannot be made poor on demand. A stub lets the test prove the refusal WITHOUT depending on the
current balance — which matters, because the first version of this test passed by accident: it ran
against a healthy wallet and its verdict logic was inverted, so it "failed" a correct gate. A test
that only ever sees one balance proves nothing about the boundary.

WHY THE STUB MUST PASS `gas_price` EXPLICITLY. gas_reserve reads `w3.eth.gas_price`. A naive
`__getattr__` delegation forwards that to the Web3 object, which has no such attribute, and every
case then returns UNMEASURABLE — which is a refusal, so a broken stub looks like a passing gate.
The first stub written here did exactly that and reported 8/8 refusals for a gate that was fine.
The stub is checked (section 0) before any result from it is believed.

Run: python3 test_gas_affordability.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("STEWARD_TENANT", "jordan")
os.environ.setdefault("STEWARD_WALLET", "0x572ABd6461BED2258615E6b99c585Ab7c5d05037")

from web3 import Web3                                                      # noqa: E402
import gas_reserve as G                                                    # noqa: E402
import lfj_recenter as R                                                   # noqa: E402

ok = 0
fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}  {detail}")


REAL = Web3(Web3.HTTPProvider("https://avalanche-c-chain-rpc.publicnode.com",
                              request_kwargs={"timeout": 25}))
ME = R._steward_wallet()
GP = REAL.eth.gas_price


class StubEth:
    def __init__(self, real, bal_wei):
        object.__setattr__(self, "_r", real)
        object.__setattr__(self, "_b", int(bal_wei))

    def __getattr__(self, n):
        if n == "get_balance":
            return lambda a: self._b
        if n == "gas_price":
            return GP
        return getattr(self._r, n)


class StubW3:
    def __init__(self, real, bal_avax):
        object.__setattr__(self, "eth", StubEth(real, int(bal_avax * 1e18)))
        object.__setattr__(self, "_r", real)

    def __getattr__(self, n):
        if n == "gas_price":
            return GP
        return getattr(self._r, n)


NEED = (G.RECENTER_GAS * GP) / 1e18        # what the gate charges for a full recenter
FLOOR = G.reserve_info(tenant="jordan", w3=REAL)["reserve_avax"]

print("")
print(f"  full recenter needs {NEED:.8f} AVAX  (RECENTER_GAS {G.RECENTER_GAS:,} @ {GP / 1e9:.4f} gwei)")
print(f"  the floor is         {FLOOR:.8f} AVAX")

print("")
print("  ── 0. THE STUB ITSELF IS SOUND (a broken stub fakes a passing gate) ────")
s = StubW3(REAL, 0.5)
check("the stub reports the balance it was given", s.eth.get_balance(ME) == int(0.5 * 1e18))
check("the stub passes gas_price through (else every case is UNMEASURABLE)",
      s.eth.gas_price == GP and s.gas_price == GP)
ok_probe, why_probe = R._gas_precondition(StubW3(REAL, 0.10), ME, rescue=False)
check("a clearly-funded stub is NOT refused as UNMEASURABLE",
      "UNMEASURABLE" not in (why_probe or ""),
      f"stub is broken: {why_probe[:90]}")

print("")
print("  ── 1. THE STRANDED STATE IS REFUSED — WITH AND WITHOUT --rescue ───────")
# This is the exact balance jordan's wallet held while the loop burned gas. Before the fix the
# rescue was allowed here, which is precisely how the book got withdrawn and left idle.
ok_n, why_n = R._gas_precondition(StubW3(REAL, 0.00298), ME, rescue=False)
ok_r, why_r = R._gas_precondition(StubW3(REAL, 0.00298), ME, rescue=True)
check("stranded + normal  -> REFUSED", not ok_n, why_n[:80])
check("stranded + --rescue -> REFUSED (affordability is physics)", not ok_r, why_r[:80])
check("the refusal names CANNOT FINISH, not the floor",
      "CANNOT FINISH" in (why_r or ""), why_r[:90])
check("the refusal says --rescue cannot override affordability",
      "never affordability" in (why_r or ""), why_r[:110])

print("")
print("  ── 2. BOTH SIDES OF THE AFFORDABILITY BOUNDARY ────────────────────────")
below = NEED * 0.9
above = NEED * 1.5
ob_n, ob_w = R._gas_precondition(StubW3(REAL, below), ME, rescue=False)
ob_r, ob_w = R._gas_precondition(StubW3(REAL, below), ME, rescue=True)
check("just BELOW one cycle + normal  -> REFUSED", not ob_n)
check("just BELOW one cycle + --rescue -> REFUSED", not ob_r)
# NOTE: the message is ob_w, not ob_r. The first version of this line tested the BOOLEAN
# (`"CANNOT FINISH" in (ob_r or "")`), which is always False, so a correct gate was reported as a
# failure — the same wrong-variable mistake this file warns about elsewhere. Read the MESSAGE.
check("just-below reason is CANNOT FINISH", "CANNOT FINISH" in (ob_w or ""), str(ob_w)[:90])
oa_n, oa_w = R._gas_precondition(StubW3(REAL, above), ME, rescue=False)
oa_r, oa_w = R._gas_precondition(StubW3(REAL, above), ME, rescue=True)
check("above one cycle + normal -> refused ONLY by the floor",
      (not oa_n) and "FLOOR" in (oa_w or "").upper(), oa_w[:90])
check("above one cycle + --rescue -> ALLOWED (the floor is the only thing gating it)",
      oa_r, oa_w[:90])
check("and the rescue says it did NOT gate the floor",
      "RESCUE" in (oa_w or "").upper(), oa_w[:90])

print("")
print("  ── 3. AN UNREADABLE CHAIN STILL FAILS CLOSED ──────────────────────────")


class DeadW3:
    def __init__(self):
        object.__setattr__(self, "eth", self)

    def __getattr__(self, n):
        if n == "get_balance":
            return lambda a: (_ for _ in ()).throw(ConnectionError("rpc down"))
        raise ConnectionError("rpc down")


d_ok, d_why = R._gas_precondition(DeadW3(), ME, rescue=True)
check("an unreadable chain REFUSES even with --rescue", not d_ok)
check("and says UNMEASURABLE rather than guessing", "UNMEASURABLE" in (d_why or ""), d_why[:90])

print("")
print("  ── 4. THE LIVE WALLET: WHATEVER IT IS, THE VERDICT MUST BE CONSISTENT ─")
live = REAL.eth.get_balance(ME) / 1e18
l_ok, l_why = R._gas_precondition(REAL, ME, rescue=False)
can_afford = live >= NEED
print(f"      live balance {live:.8f} AVAX, can afford a cycle: {can_afford}")
if not can_afford:
    check("live: cannot afford -> refused for AFFORDABILITY, not the floor",
          (not l_ok) and "CANNOT FINISH" in (l_why or ""), l_why[:90])
else:
    check("live: can afford -> the floor alone decides", "FLOOR" in (l_why or "").upper(),
          l_why[:90])

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
