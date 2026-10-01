#!/usr/bin/env python3
"""Apply the self-audit findings to the VAULT copies (source of truth).

Fixes:
  A. success-before-status in the swap + approve paths (real false-positive bug)
  B. self-audit checker: look BACKWARD for a status guard (kills false positives)
     and skip known EOAs / other-chain token addresses (kills noise)
  C. sync-treasury-scripts.sh: cover the new forensics + audit files
Idempotent.
"""
import pathlib, re

V = pathlib.Path('/root/vaults/gentech/10-Labs/agent-kit-self-tracking')
A = V / 'blackhole_cl_adapter.py'
ok = []

# ── A1. swap: print ✅ only after status check ──────────────────────────
s = A.read_text()
old = '''        print(f"  ✅ swapped: {h.hex()} status={rcpt['status']}")
        if rcpt['status'] != 1:
            print("  ❌ swap REVERTED", file=sys.stderr)
            return {"ok": False, "stage": "swap"}'''
new = '''        if rcpt['status'] != 1:
            print(f"  ❌ swap REVERTED: {h.hex()} status={rcpt['status']}", file=sys.stderr)
            return {"ok": False, "stage": "swap"}
        print(f"  ✅ swapped: {h.hex()} status={rcpt['status']}")'''
if old in s:
    s = s.replace(old, new, 1); ok.append('swap: status check before ✅')

# ── A2. generic approve in the mint path ────────────────────────────────
old2 = '''                print(f"  ✅ {name} approved: {h.hex()} status={rcpt['status']}")
            else:
                print(f"  ✅ {name} already approved")'''
new2 = '''                if rcpt['status'] != 1:
                    print(f"  ❌ {name} approve REVERTED: {h.hex()} status={rcpt['status']}",
                          file=sys.stderr)
                    sys.exit(1)
                print(f"  ✅ {name} approved: {h.hex()} status={rcpt['status']}")
            else:
                print(f"  ✅ {name} already approved")'''
if old2 in s:
    s = s.replace(old2, new2, 1); ok.append('mint-approve: status check before ✅')

# ── A3. re-stake / gauge approve paths: verify before ✅ ────────────────
for pat, label in [
    ('        print(f"  ✅ gauge approved: {h.hex()} status={rcpt[\'status\']}")',
     'gauge-approve'),
    ('    print(f"  ✅ re-staked: {h.hex()} status={rcpt[\'status\']}")', 're-stake'),
]:
    if pat in s:
        indent = pat[:len(pat) - len(pat.lstrip())]
        chk = (f'{indent}if rcpt["status"] != 1:\n'
               f'{indent}    print(f"  ❌ {label} REVERTED: {{h.hex()}} status={{rcpt[\'status\']}}", file=sys.stderr)\n'
               f'{indent}    return False, None\n')
        s = s.replace(pat, chk + pat, 1)
        ok.append(f'{label}: status check before ✅')

A.write_text(s)

# ── B. self-audit checker improvements ──────────────────────────────────
S = V / 'treasury_self_audit.py'
t = S.read_text()

old_chk = '''            # look ahead up to 8 lines for a real status check
            window = "\\n".join(lines[i + 1:i + 9])
            guarded = bool(re.search(r"status['\\"]?\\]?\\s*!=\\s*1|status\\s*!=\\s*1", window))'''
new_chk = '''            # a guard may sit BEFORE the print (preferred) or shortly after.
            # Checking only forward produced false positives on correctly
            # ordered code, so scan both directions.
            before = "\\n".join(lines[max(0, i - 6):i])
            after = "\\n".join(lines[i + 1:i + 9])
            guarded = bool(re.search(r"status['\\"]?\\]?\\s*!=\\s*1|status\\s*!=\\s*1", before + after))'''
if old_chk in t:
    t = t.replace(old_chk, new_chk, 1); ok.append('checker: status guard scanned both ways')

old_addr = '''def check_addresses():
    seen = set()
    for f in CORE:
        src = read(f)
        for a in re.findall(r"0x[a-fA-F0-9]{40}", src):
            if a.lower() in seen:
                continue
            seen.add(a.lower())
            code = rpc("eth_getCode", [a, "latest"])'''
new_addr = '''# Addresses that are legitimately NOT contracts on Avalanche:
#  - our own wallet (an EOA by definition)
#  - token addresses belonging to OTHER chains (base/ethereum/arbitrum maps)
SKIP_ADDRS = {"0x572abd6461bed2258615e6b99c585ab7c5d05037"}
OTHER_CHAIN_HINTS = ("base", "ethereum", "arbitrum", "optimism", "polygon")


def check_addresses():
    seen = set()
    for f in CORE:
        src = read(f)
        lines = src.splitlines()
        for a in re.findall(r"0x[a-fA-F0-9]{40}", src):
            if a.lower() in seen or a.lower() in SKIP_ADDRS:
                continue
            seen.add(a.lower())
            # skip if the address sits near another chain's name (token map)
            near = False
            for i, ln in enumerate(lines):
                if a in ln:
                    ctx = " ".join(lines[max(0, i - 6):i + 3]).lower()
                    if any(h in ctx for h in OTHER_CHAIN_HINTS):
                        near = True
                        break
            if near:
                continue
            code = rpc("eth_getCode", [a, "latest"])'''
if old_addr in t:
    t = t.replace(old_addr, new_addr, 1); ok.append('checker: skip wallet + other-chain tokens')

# index-selection: recognise the explicit "different tid" fallback as valid
old_idx = '''            ctx = src[max(0, m.start() - 900):m.start()]
            ranked = "liq > best_liq" in ctx or "best_liq" in ctx'''
new_idx = '''            ctx = src[max(0, m.start() - 900):m.start()]
            # valid when it ranks by liquidity, OR when it is the explicit
            # "find a DIFFERENT tokenId" fallback after a re-mint (it compares
            # against token_id, which the ranked selector already chose).
            ranked = ("liq > best_liq" in ctx or "best_liq" in ctx
                      or "tid != token_id" in src[m.start():m.start() + 200])'''
if old_idx in t:
    t = t.replace(old_idx, new_idx, 1); ok.append('checker: accept re-mint fallback')

S.write_text(t)

# ── C. sync script coverage ─────────────────────────────────────────────
SY = pathlib.Path('/root/vaults/gentech/scripts/sync-treasury-scripts.sh')
y = SY.read_text()
add_files = ['blackhole_fee_reader.py', 'treasury_self_audit.py', 'treasury_truth.py',
             'value_timeline.py', 'pin_loss.py', 'reconcile_recenter.py',
             'find_lfj_bins.py', 'wallet_forensics.py', 'wallet_timeline.py',
             'who_is_trading.py', 'tx_cost_forensics.py', 'decode_and_deposits.py',
             'lfj_postmortem.py', 'verify_black_emissions.py', 'find_correct_router.py']
missing = [f for f in add_files if f not in y]
if missing:
    block = "\n".join(f"  {f}" for f in missing)
    y = y.replace("  treasury_config.json\n)", f"  treasury_config.json\n{block}\n)", 1)
    SY.write_text(y)
    ok.append(f'sync script: added {len(missing)} files')

print('applied:')
for x in ok:
    print('  -', x)
if not ok:
    print('  (nothing to do)')
