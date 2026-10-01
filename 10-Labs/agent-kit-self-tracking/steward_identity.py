#!/usr/bin/env python3
"""steward_identity — single source of truth for WHO this treasury belongs to.

WHY THIS EXISTS
---------------
The wallet address was hardcoded in ~42 scripts. That is fine for one person and
catastrophic for a fleet: if a second operator (a cousin, a collaborator) runs
any of those scripts with their own config, the script still signs for the FIRST
person's wallet. That is how funds move to the wrong place — not a crash, a
silent success against the wrong treasury.

THE RULE
--------
Never hardcode a wallet. Import it. Then PROVE the signing key matches it:

    from steward_identity import signer, wallet
    acct = signer()          # raises IdentityMismatch if key != configured wallet

`signer()` refuses to return a key whose derived address does not match the
configured wallet. A mismatched identity is a hard stop, never a warning —
a warning would just get scrolled past at 3am in a cron log.

Resolution order (so one machine can host several treasuries):
    STEWARD_WALLET     env  -> highest priority (per-profile isolation)
    treasury_config.json    -> the operator's own config
"""
import json
import os

from web3 import Web3

DEFAULT_KEY_PATH = "/root/.blockrun/almanak-steward-key"
_HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_CANDIDATES = [
    os.path.join(_HERE, "treasury_config.json"),
    "/root/.hermes/profiles/gentech-treasury/scripts/treasury_config.json",
]

# Treasury state files that must also follow the configured wallet. Kept here so
# a second operator does not inherit the first operator's history.
STATE_MARKERS = ("wallet", "address")

# ─────────────────────────────────────────────────────────────────────────────
# TENANT BOUNDARY — the wiring (2026-09-22)
#
# tenant_guard.py could always refuse correctly, but NOTHING CALLED IT, so the boundary
# was a tested library rather than an enforced one. This is the wiring, and it is placed
# HERE on purpose: `signer()` is the only way this system can move capital, so a check
# inside it cannot be forgotten by the next script someone writes. A boundary that relies
# on every call site remembering is not a boundary — it is a convention, and conventions
# drift silently at 3am in a cron log.
#
# The tenant is DERIVED from the signing wallet, then verified against the registry.
# Deriving it means a box cannot claim a tenant it does not hold keys for; verifying it
# means an unregistered wallet is REFUSED rather than quietly becoming a tenant of its own.
# ─────────────────────────────────────────────────────────────────────────────
TENANT_REGISTRY = os.path.join(_HERE, "tenants.json")
TENANT_REGISTRY_FALLBACKS = (
    TENANT_REGISTRY,
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json",
)


def _tenants():
    """Read the tenant registry, or refuse. A missing registry is never a permissive default."""
    for p in TENANT_REGISTRY_FALLBACKS:
        try:
            with open(p) as f:
                return json.load(f) or {}
        except Exception:
            continue
    raise IdentityMismatch(
        f"cannot read the tenant registry (looked in {TENANT_REGISTRY_FALLBACKS}) — "
        "refusing to sign without knowing whose treasury this is.")


def tenant():
    """Which tenant this box IS. Declared by STEWARD_TENANT, else derived from the wallet.

    Derivation is the default because it cannot be spoofed: a box can only claim a tenant
    whose wallet it can actually sign as. An explicit STEWARD_TENANT that disagrees with the
    wallet is a hard stop, not a preference.
    """
    reg = _tenants().get("tenants") or {}
    w = wallet().lower()

    declared = os.environ.get("STEWARD_TENANT", "").strip()
    if declared:
        t = reg.get(declared)
        if not t:
            raise IdentityMismatch(
                f"STEWARD_TENANT={declared!r} is not in the registry — refusing to sign.")
        if (t.get("wallet") or "").lower() != w:
            raise IdentityMismatch(
                f"TENANT BOUNDARY VIOLATION: this box declares tenant {declared!r} but signs "
                f"as {wallet()}, which is not that tenant's registered wallet. Refusing — "
                "signing here would act on the wrong treasury.")
        return declared

    # match on wallet regardless of status, so a proposed-but-keyed tenant gets the
    # right refusal from assert_tenant rather than a confusing "unknown wallet"
    matches = [n for n, t in reg.items() if (t.get("wallet") or "").lower() == w]
    if not matches:
        raise IdentityMismatch(
            f"signing wallet {wallet()} is not registered as ANY tenant. An unregistered "
            "wallet is an error, not a tenant of its own — add it to tenants.json "
            "deliberately before it can move capital.")
    if len(matches) > 1:
        raise IdentityMismatch(
            f"wallet {wallet()} is registered to several tenants {matches} — ambiguous, refusing.")
    return matches[0]


def assert_tenant_boundary():
    """The hard stop. Refuses unless this box is an ACTIVE tenant signing as its own wallet.

    tenant_guard is imported lazily because it imports this module — importing at module
    scope would be circular. The check is deliberately NOT swallowed: if the guard cannot be
    loaded, signing stops. A boundary that silently disables itself when its dependency is
    missing is worse than no boundary, because it reads as protection.
    """
    import sys as _sys
    if _HERE not in _sys.path:
        _sys.path.insert(0, _HERE)
    from tenant_guard import assert_tenant  # raises ImportError loudly if absent
    return assert_tenant(tenant())



class IdentityMismatch(RuntimeError):
    """Raised when the signer does not match the configured treasury wallet."""


def state_path(directory, stem, suffix="json"):
    """Per-tenant state file path: `<directory>/.<stem>-<tenant>.<suffix>`.

    WHY THIS EXISTS (2026-09-28)
    ----------------------------
    Every other state file in this system carries its tenant — `.posture-{t}.json`,
    `.fee-ledger-{t}.json`, `.cascade-state-{t}.json`, `.steward-wallet-baseline-{t}.json` —
    but `.compound-ledger.json` and `.farm-snapshot.json` were UNSURFIXED and shared by the
    whole box. With one book that is harmless. With two it is a silent corruption: the farm
    report OVERWRITES the snapshot every run, and auto_compound APPENDS to the ledger, so
    whichever tenant ran last erased or inherited the other's history. Nobody would see an
    error — just a report describing a book that is half the wrong person.

    Kept here, beside `wallet()`, because the question "whose state is this?" has exactly one
    answer in this system and it is the same answer as "whose wallet is this?".

    Falls back to the un-suffixed name when the identity cannot be resolved, so a box whose
    registry is unreadable reads the legacy file rather than raising on a path lookup. That
    fallback is deliberately the OLD name: it cannot silently create a fresh empty file that
    reads as "no history".
    """
    try:
        t = tenant()
    except IdentityMismatch:
        return os.path.join(directory, f".{stem}.{suffix}")
    return os.path.join(directory, f".{stem}-{t}.{suffix}")


def _from_env():
    w = os.environ.get("STEWARD_WALLET", "").strip()
    if w:
        return w
    # ── STEWARD_TENANT MUST RESOLVE ITS OWN WALLET (fixed 2026-09-27) ────────────────────────
    # `wallet()` consulted STEWARD_WALLET and then the PROFILE's treasury_config.json. It never
    # read STEWARD_TENANT. So a script that said "I am acting for dadrian" by setting only the
    # tenant label silently resolved the DEFAULT wallet and read JORDAN's book — no error, no
    # warning, a correct-looking number for the wrong person.
    #
    # Measured on the live books: `STEWARD_TENANT=dadrian fee_efficiency.py --tenant dadrian`
    # reported "ACTUAL deployed bins 8363337..8363348 (12 bins)" — jordan's twelve bins — and an
    # efficiency of 50.2% for dadrian, whose real book is 25 bins (8363326..8363352) scoring
    # 52.4%. `posture.py` had already been patched to export BOTH variables for this exact
    # reason; fee_efficiency, cascade_guard, auto_compound, gas_reserve and six others still
    # exported only the label. That is ten call sites sharing one latent bug.
    #
    # Fixing it HERE, at the resolver, is the only version that cannot be forgotten by the next
    # script someone writes. A per-tenant loop around a read that ignores the tenant label is not
    # per-tenant — it is one book wearing two names.
    #
    # Order is unchanged: an explicit STEWARD_WALLET still wins, so nothing that already works
    # moves. The registry only fills the gap that used to fall through to the default.
    t = os.environ.get("STEWARD_TENANT", "").strip()
    if not t:
        return None
    rec = (_tenants().get("tenants") or {}).get(t) or {}
    tw = str(rec.get("wallet") or "").strip()
    if tw:
        return tw
    # The tenant is known but carries no wallet (a tenant still being provisioned), or is not in
    # the registry at all. We cannot INVENT a wallet, and reading someone else's is worse than
    # saying so — make the fallback visible rather than silent.
    import sys as _sys
    print(f"  ⚠️  STEWARD_TENANT={t!r} has no wallet in the registry — falling back to the "
          f"configured default. If this read is per-tenant, the numbers belong to whoever that "
          f"default is, NOT to {t!r}.", file=_sys.stderr)
    return None


def _from_config():
    for path in CONFIG_CANDIDATES:
        try:
            with open(path) as f:
                w = (json.load(f) or {}).get("wallet")
            if w:
                return w, path
        except Exception:
            continue
    return None, None


def wallet_source():
    """Where the wallet came from — useful for audit output."""
    if os.environ.get("STEWARD_WALLET", "").strip():
        return "env:STEWARD_WALLET", None
    # _from_env() now also resolves a declared STEWARD_TENANT, so reporting "config:..." here
    # would name the wrong origin — an audit line that lies about provenance is worse than none.
    if os.environ.get("STEWARD_TENANT", "").strip() and _from_env():
        return "env:STEWARD_TENANT->registry", None
    w, path = _from_config()
    if w:
        return f"config:{path}", path
    return None, None


def wallet():
    """The configured treasury wallet (checksummed). Raises if unset."""
    w = _from_env()
    if not w:
        w, _ = _from_config()
    if not w:
        raise IdentityMismatch(
            "no treasury wallet configured — set STEWARD_WALLET or add "
            "'wallet' to treasury_config.json")
    return Web3.to_checksum_address(w)


def key_path():
    """Where the signing key lives. Tenant-aware, because a tenant's key is not Jordan's.

    Order: STEWARD_KEY_PATH (explicit wins) -> this tenant's own provisioned key -> the
    default. A tenant box that silently fell back to the DEFAULT path would sign as Jordan,
    which is the exact failure this module exists to prevent.
    """
    env = os.environ.get("STEWARD_KEY_PATH", "").strip()
    if env:
        return env
    try:
        t = tenant()
        cand = os.path.join("/root/.blockrun/tenants", t, "steward.key.enc")
        if os.path.exists(cand):
            return cand
    except IdentityMismatch:
        pass          # identity unresolvable — fall through; signer() will refuse properly
    return DEFAULT_KEY_PATH


def _read_key_material(path):
    """Read the signing key, DECRYPTING it when it is stored encrypted.

    Tenant keys are written AES-256 by provision_tenant_wallet.py. Until 2026-09-22 signer()
    read every key path as PLAINTEXT, so a collaborator's encrypted key was simply unreadable
    and their box could not sign at all — onboarding would have failed at the first
    transaction, after the wallet had already been funded. A stored key the signer cannot
    read is not a stored key.

    Passphrase resolution mirrors steward_key.py: env first, then the sibling .passphrase
    file. A missing passphrase REFUSES — it never falls back to anything, because a silent
    fallback turns encryption into decoration while still looking like security.
    """
    if not path.endswith(".enc"):
        return open(path).read().strip()

    pw = os.environ.get("STEWARD_KEY_PASSPHRASE", "").strip()
    if not pw:
        sib = os.path.join(os.path.dirname(path), ".passphrase")
        if os.path.exists(sib):
            mode = oct(os.stat(sib).st_mode)[-3:]
            if mode != "600":
                raise IdentityMismatch(
                    f"passphrase file {sib} has mode {mode}, expected 600. Refusing to use a "
                    f"world-readable passphrase — fix the permissions.")
            pw = open(sib).read().strip()
    if not pw:
        raise IdentityMismatch(
            f"key at {path} is encrypted but no passphrase was found. Set "
            f"STEWARD_KEY_PASSPHRASE or create {os.path.dirname(path)}/.passphrase (mode 600). "
            f"Refusing to fall back to anything.")

    import subprocess, tempfile
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        r = subprocess.run(
            ["gpg", "--batch", "--yes", "--quiet", "--decrypt",
             "--passphrase-fd", "0", "--output", tmp_path, path],
            input=pw.encode(), capture_output=True, timeout=30)
        if r.returncode != 0:
            # do NOT echo gpg's stderr — some modes can include key material
            raise IdentityMismatch(
                "decryption failed (wrong passphrase, or the key file is corrupt). Refusing.")
        return open(tmp_path).read().strip()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass



def signing_key():
    """The decrypted signing key, AFTER asserting the tenant boundary.

    PREFER signer(): it returns an Account and keeps the raw key inside this module. This exists
    for the handful of call sites that still do `Account.sign_transaction(tx, key)` and would
    otherwise open the key file themselves.

    WHY IT MATTERS: seven files in this directory read the key path directly and parsed it as
    PLAINTEXT. Two consequences, both real:
      1. A tenant's key is AES-256, so those paths raised UnicodeDecodeError - a collaborator's
         box could not sign AT ALL, and would have failed after the wallet was funded.
      2. Reading the key directly skipped the tenant boundary and the autonomy guard entirely.
         A guard every other path can walk around is decoration, not a boundary.
    One accessor, one place the boundary is asserted.
    """
    assert_tenant_boundary()
    return _read_key_material(key_path())


def signer(require_key=True):
    """Return the signing account, but ONLY if it matches the configured wallet.

    This is the guard that makes 'funds moved to the wrong place' structurally
    impossible for every script that uses it.
    """
    w3 = Web3()
    path = key_path()
    if not os.path.exists(path):
        if require_key:
            raise IdentityMismatch(
                f"no signing key at {path} — set STEWARD_KEY_PATH")
        return None
    try:
        acct = w3.eth.account.from_key(_read_key_material(path))
    except IdentityMismatch:
        raise
    except Exception as e:
        raise IdentityMismatch(f"unreadable signing key at {path}: {e}")

    want = wallet()
    if acct.address.lower() != want.lower():
        raise IdentityMismatch(
            "REFUSING TO SIGN — identity mismatch.\n"
            f"  signing key  : {acct.address}\n"
            f"  configured to: {want}\n"
            "  The key and the config disagree, so signing would act on the "
            "WRONG treasury. Fix STEWARD_WALLET / STEWARD_KEY_PATH first.")

    # TENANT BOUNDARY — checked BEFORE the key is handed back, so no signing path can
    # skip it. This is the wiring that turns tenant_guard from a tested library into an
    # enforced boundary: an ACTIVE tenant must sign as its OWN registered wallet.
    assert_tenant_boundary()
    return acct


def describe():
    """One-line human summary for audit/report output."""
    src, _ = wallet_source()
    try:
        w = wallet()
    except IdentityMismatch as e:
        return f"❌ {e}"
    try:
        acct = signer()
        ok = "✅ key matches" if acct else "⚠️ no key"
    except IdentityMismatch as e:
        ok = f"❌ MISMATCH — {str(e).splitlines()[0]}"
    return f"wallet {w} ({src}) · {ok}"


if __name__ == "__main__":
    print(describe())
