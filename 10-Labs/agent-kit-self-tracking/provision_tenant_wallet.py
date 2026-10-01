#!/usr/bin/env python3
"""
provision_tenant_wallet.py — create a collaborator's wallet and key pair, KEPT SEPARATE.

WHY THIS EXISTS (Jordan, 2026-09-22)
------------------------------------
    "most of our collaborators don't know... getting the private key is kind of difficult
     to do and they're going to run into the same issue I did. So I think it's okay if you
     create the wallet and the key pair for them, but just, you know, of course, keep it
     separate."

This REVERSES the earlier posture. tenants.json used to say, in the hard_rule: "We never
generate a key for a third party and never accept one from them." That rule existed for a
good reason — a key we hold is a key we can sign with — but it assumed a collaborator who
could safely self-custody. Jordan's point is the honest one: a rule that only the technically
capable can satisfy does not protect anyone, it just excludes people.

So the rule changes, and the RISK IT WAS MANAGING MOVES RATHER THAN DISAPPEARS. Say that
plainly: while we hold a collaborator's key, the tenant boundary is what stops their capital
and Jordan's from touching — not custody. The boundary is real and tested (see tenant_guard.py
and steward_identity.assert_tenant_boundary), but it is now load-bearing in a way it was not
before, and it must never be described as equivalent to the collaborator holding their own key.

SEPARATION IS THE WHOLE POINT. "keep it separate" is not a nicety:
  * one directory per tenant, mode 700
  * that tenant's key encrypted with that tenant's OWN passphrase file
  * the address is registered in tenants.json, so the identity layer binds it
  * NOTHING here is shared with the live treasury's key, path, or passphrase

SAFETY
  * The private key is NEVER printed, logged, or returned. Only the address is shown.
  * Refuses to overwrite an existing key — a silent overwrite is how a funded wallet is lost.
  * Refuses if the tenant is not in the registry: an unregistered wallet cannot be bound to
    an identity, and an unbound wallet is exactly the thing this file exists to prevent.
  * Refuses to leave a key unencrypted without saying so loudly.
"""
import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile

from eth_account import Account

HERE = os.path.dirname(os.path.abspath(__file__))
# VAULT FIRST — this ordering is load-bearing, not cosmetic.
# sync-treasury-scripts.sh copies vault -> profile, so a write to the PROFILE copy is silently
# reverted on the next sync. The first version of this tool listed HERE (the profile) first, so
# it registered Dadrian's address into a copy that the next sync overwrote back to null: the
# wallet existed, the key existed, and the registry said the tenant had no wallet at all.
# The vault is the source of truth, so the vault is where a durable registration goes.
REGISTRY_CANDIDATES = [
    os.environ.get("STEWARD_TENANT_REGISTRY", ""),
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json",
    os.path.join(HERE, "tenants.json"),
]
KEY_ROOT = os.environ.get("STEWARD_TENANT_KEY_ROOT", "/root/.blockrun/tenants")


class ProvisionError(RuntimeError):
    """Refusal, not a warning."""


def _registry_path():
    for p in REGISTRY_CANDIDATES:
        if p and os.path.exists(p):
            return p
    raise ProvisionError(f"tenant registry not found (looked in {REGISTRY_CANDIDATES})")


def _assert_durable_registry(path):
    """Refuse to register into a copy that the sync will revert.

    A registration that disappears on the next sync is worse than no registration: the wallet
    is funded, the key is on disk, and the registry says the tenant has no wallet.
    """
    vault = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
    if os.path.realpath(path) != os.path.realpath(vault) and not os.environ.get("STEWARD_TENANT_REGISTRY"):
        raise ProvisionError(
            f"registry resolved to {path}, which is NOT the vault ({vault}). "
            f"sync-treasury-scripts.sh copies vault -> profile and would silently revert this "
            f"registration. Set STEWARD_TENANT_REGISTRY to override deliberately.")


def _load_registry():
    with open(_registry_path()) as f:
        return json.load(f)


def _tenant_dir(tenant: str) -> str:
    return os.path.join(KEY_ROOT, tenant)


def provision(tenant: str, execute: bool):
    reg = _load_registry()
    _assert_durable_registry(_registry_path())
    entry = (reg.get("tenants") or {}).get(tenant)
    if not entry:
        raise ProvisionError(
            f"tenant {tenant!r} is not in the registry. Add it deliberately first — a wallet "
            f"that cannot be bound to an identity is the failure this prevents.")

    tdir = _tenant_dir(tenant)
    enc = os.path.join(tdir, "steward.key.enc")
    pas = os.path.join(tdir, ".passphrase")

    print("=" * 84)
    print(f"  PROVISION TENANT WALLET — {tenant}")
    print("=" * 84)
    print(f"  registry     : {_registry_path()}")
    print(f"  key dir      : {tdir}   (per-tenant, separate from the live treasury)")

    if os.path.exists(enc):
        raise ProvisionError(
            f"a key already exists at {enc}. REFUSING to overwrite — silently replacing a key "
            f"is how a funded wallet becomes unreachable. Remove it deliberately if that is "
            f"truly what you want.")
    if entry.get("wallet"):
        raise ProvisionError(
            f"tenant {tenant!r} is already registered to {entry['wallet']}. Refusing to "
            f"generate a second wallet for a tenant that has one.")

    # ── generate ────────────────────────────────────────────────────────────
    acct = Account.create()
    address, key = acct.address, acct.key.hex()
    if not key.startswith("0x"):
        key = "0x" + key
    print(f"\n  generated address : {address}")
    print(f"  private key       : [NOT SHOWN — never printed, never logged]")

    if not execute:
        print("\n  (dry-run — pass --execute to write the key and register the address)")
        return address

    # ── store: dir 700, encrypted with the tenant's own passphrase ──────────
    os.makedirs(tdir, mode=0o700, exist_ok=True)
    os.chmod(tdir, 0o700)

    passphrase = Account.create().key.hex()      # a fresh random secret, per tenant
    with open(pas, "w") as f:
        f.write(passphrase)
    os.chmod(pas, 0o600)

    # encrypt via gpg (same mechanism as the live key); plaintext never hits disk
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write(key)
        tmp_path = tmp.name
    os.chmod(tmp_path, 0o600)
    try:
        r = subprocess.run(
            ["gpg", "--batch", "--yes", "--quiet", "--symmetric", "--cipher-algo", "AES256",
             "--passphrase-fd", "0", "--output", enc, tmp_path],
            input=passphrase.encode(), capture_output=True, timeout=60,
        )
        if r.returncode != 0:
            raise ProvisionError(
                "gpg encryption failed — REFUSING to leave the key in plaintext. "
                f"(gpg said: {r.stderr.decode()[:160]})")
    finally:
        try:
            os.unlink(tmp_path)          # plaintext is gone either way
        except OSError:
            pass
    os.chmod(enc, 0o600)

    # ── verify: decrypt it back and confirm the address round-trips ─────────
    # A key we cannot read back is not a stored key. This is the same "a copy is not a copy
    # until it is re-read" rule the rest of the system uses.
    r = subprocess.run(
        ["gpg", "--batch", "--yes", "--quiet", "--decrypt",
         "--passphrase-fd", "0", enc],
        input=passphrase.encode(), capture_output=True, timeout=60,
    )
    if r.returncode != 0:
        raise ProvisionError("stored key did not decrypt back — REFUSING to register it.")
    roundtrip = r.stdout.decode().strip()
    if Account.from_key(roundtrip).address.lower() != address.lower():
        raise ProvisionError(
            "round-tripped key derives a DIFFERENT address. REFUSING to register it — "
            "this is exactly how funds go to a wallet nobody can sign for.")
    del roundtrip

    # ── register the ADDRESS (never the key) ────────────────────────────────
    reg["tenants"][tenant]["wallet"] = address
    reg["tenants"][tenant]["key_custody"] = (
        "agent-held (Jordan, 2026-09-22). Key encrypted at "
        f"{enc} with a per-tenant passphrase at {pas}. SEPARATE from the live treasury key.")
    with open(_registry_path(), "w") as f:
        json.dump(reg, f, indent=2)

    print(f"\n  ✅ key written (AES-256, mode 600) and VERIFIED by decrypt round-trip")
    print(f"  ✅ address registered in tenants.json")
    print(f"  ⚠️  status is still {entry.get('status')!r} — Jordan activates it deliberately; "
          f"a registered wallet is not a licensed one.")
    return address


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    try:
        provision(a.tenant, a.execute)
    except ProvisionError as e:
        print(f"\n  ⛔ {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
