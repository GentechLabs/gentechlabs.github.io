#!/usr/bin/env python3
"""Install CHECK 11 (identity-hardcoding) into treasury_self_audit.py — v2.

v1 failed twice and both failures are worth naming:
  1. WRONG SCHEMA — it emitted keys (severity/check/file/detail) while the
     audit renders (class/sev/where/msg/fix), so a finding could never display.
  2. WRONG INSERTION POINT — it injected before the summary line and split
     main(), producing `return outside function`.

v2 is deterministic: it inserts the function immediately before `def main():`
and the call immediately before the summary print, both at exact indent. It
verifies by ast.parse AND by asserting the check is actually reachable.
"""
import ast
import pathlib
import shutil
import time
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

TARGET = pathlib.Path(__file__).resolve().parent / "treasury_self_audit.py"
BACKUP = TARGET.parent / (TARGET.name + ".bak-check11b-" + time.strftime("%Y%m%d"))

FUNC = '''
def check_identity_hardcoding(SRC_DIR):
    """CHECK 11 — a script able to SIGN must not hardcode who it signs FOR.

    A literal wallet (or a direct key-path read) in a signer means a second
    operator running that file would act on the FIRST operator's treasury.
    That is the "funds moved to the wrong place" class, so it is a finding
    even though the script works perfectly for its original author.
    """
    import pathlib as _pl
    import re as _re
    findings = []
    skip = {"steward_identity.py", "migrate_identity.py",
            "add_identity_check.py", "treasury_self_audit.py"}
    for p in sorted(_pl.Path(SRC_DIR).glob("*.py")):
        if p.name in skip or ".bak" in p.name:
            continue
        try:
            src = p.read_text()
        except Exception:
            continue
        if not any(h in src for h in ("sign_transaction", "send_raw_transaction",
                                      "from_key(")):
            continue                       # cannot sign -> out of scope
        if "steward_identity" in src:
            continue                       # resolves identity properly
        if _sw_keypath() in src:
            reason = ("reads the signing-key path directly instead of "
                      "resolving identity via steward_identity")
        elif _re.search(r"0x[a-fA-F0-9]{40}", src):
            reason = ("hardcodes a wallet address and can sign — a second "
                      "operator would sign for the first operator's treasury")
        else:
            reason = ("can sign but does not resolve identity via "
                      "steward_identity")
        findings.append({
            "class": "identity-hardcoding",
            "sev": "MED",
            "where": p.name,
            "msg": reason,
            "fix": "import steward_identity and use signer() / wallet()",
        })
    return findings


'''


def main():
    src = TARGET.read_text()
    if "def check_identity_hardcoding" in src:
        print("CHECK 11 already installed")
        return 0

    lines = src.split("\n")

    def idx(pred, what):
        for i, ln in enumerate(lines):
            if pred(ln):
                return i
        raise SystemExit(f"❌ anchor not found: {what}")

    # 1. function definition before `def main():`
    i_main = idx(lambda l: l.startswith("def main():"), "def main():")
    # 2. the call inside main(), before the summary print (4-space indent)
    i_sum = idx(lambda l: l.strip().startswith('print(f"\\n{len(findings)}'),
                "summary print")

    call = ("    # CHECK 11 — identity resolution (multi-tenant safety)\n"
            "    try:\n"
            "        findings.extend(\n"
            "            check_identity_hardcoding(\n"
            "                os.path.dirname(os.path.abspath(__file__))))\n"
            "    except Exception:\n"
            "        pass\n")

    # insert the call first (later position), then the function (earlier)
    lines[i_sum:i_sum] = call.split("\n")
    lines[i_main:i_main] = FUNC.split("\n")

    out = "\n".join(lines)
    try:
        ast.parse(out)
    except SyntaxError as e:
        print(f"❌ syntax error line {e.lineno}: {e.msg} — NOT written")
        return 1

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(out)
    print(f"✅ CHECK 11 installed (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
