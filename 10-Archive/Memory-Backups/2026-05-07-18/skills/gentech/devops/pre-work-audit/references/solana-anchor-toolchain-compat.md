# Solana/Anchor Build Environment Compatibility

## The Core Problem (as of May 2026)

Solana 1.18.x SBF toolchain ships **rustc 1.79.0-dev** with **Cargo ~1.75.0**. The current crates.io ecosystem has moved to `edition = "2024"` and Cargo lockfile v4 format. These are incompatible.

If you're building an Anchor 0.30.1 project on Solana 1.18.x, you WILL hit cascading build failures.

## Known Failure Modes

### 1. Cargo.lock v4 Incompatibility
- **Symptom:** `lock file version 4 requires -Znext-lockfile-bump`
- **Cause:** System cargo (1.95.0+) generates v4 lockfiles. SBF cargo (1.75.0) can't read them.
- **Fix:** Generate lockfile with `RUSTUP_TOOLCHAIN=stable`, then `sed -i 's/^version = 4$/version = 3/' Cargo.lock`
- **Pitfall:** `anchor build` regenerates the lockfile using system cargo, overwriting your fix. Either make the lockfile read-only (`chmod 444`) or use anchor-cli 0.30.1 (not 1.0.x).

### 2. edition2024 Crate Contamination
- **Symptom:** `feature edition2024 is required` from cargo 1.75.0
- **Cause:** Transitive deps have updated to crates using `edition = "2024"` on crates.io
- **Platform-tools Rust versions (confirmed May 2026):**
  - Agave 1.18.x → platform-tools 1.41 → rustc 1.75
  - Agave 2.1.x → platform-tools 1.43 → rustc 1.79
  - Agave 2.2.x → platform-tools 1.47 → rustc 1.84 (still < 1.85 needed for edition2024)
  - **None of the current stable Agave releases support edition2024**
- **Cascading pins needed (tested with Agave 2.2.14, May 2026):**
  ```bash
  # Pin ORDER matters — pin proc-macro-crate BEFORE toml_datetime
  cargo update -p blake3 --precise 1.5.5                    # removes cpufeatures 0.3.0
  cargo update -p proc-macro-crate@3.5.0 --precise 3.2.0    # removes toml_edit 0.25 + toml_datetime 1.1
  cargo update -p indexmap@2.14.0 --precise 2.13.0           # edition2024; toml_edit needs >= 2.13
  cargo update -p borsh@1.6.1 --precise 1.5.3                # removes newer borsh-derive chain
  cargo update -p unicode-segmentation@1.13.2 --precise 1.12.0  # requires rustc 1.85
  ```
- **Pitfall:** Don't try to pin `toml_datetime` directly — `toml_edit 0.25.x` requires `toml_datetime ^1.1.1` and cargo will refuse. Pin `proc-macro-crate` first to remove the entire chain.
- **Pitfall:** Don't pin `indexmap` below 2.13.0 — `toml_edit 0.25.x` requires `>= 2.13.0`.
- **Detection script:** Scan registry for `edition2024` in Cargo.toml, cross-reference with lockfile

### 3. proc-macro2 source_file() Removal
- **Symptom:** `no method named source_file found for struct proc_macro2::Span`
- **Cause:** anchor-syn 0.30.1 uses `source_file()` behind `#[cfg(procmacro2_semver_exempt)]`. Removed in proc-macro2 1.0.80+.
- **Fix:** Pin proc-macro2 to 1.0.79, BUT also pin serde_derive (< 1.0.200), quote (< 1.0.40), syn (< 2.0.60) — cascading.
- **Alternative:** Upgrade to Solana 2.0+ (newer platform-tools with rustc ≥ 1.85).

### 4. anchor-cli Version Mismatch
- **Symptom:** `anchor-lang version(0.30.1) and the current CLI version(1.0.1) don't match`
- **Cause:** `anchor build` with CLI 1.0.x regenerates Cargo.lock as v4, breaking SBF toolchain
- **Fix:** `avm install 0.30.1 && avm use 0.30.1`

## Recommended Approach

### Option A: Stay on Solana 1.18.x (compatibility pins)
```
1. avm install 0.30.1 && avm use 0.30.1
2. rm Cargo.lock
3. RUSTUP_TOOLCHAIN=stable cargo generate-lockfile
4. Apply all edition2024 pins (see list above)
5. sed -i 's/^version = 4$/version = 3/' Cargo.lock
6. chmod 444 Cargo.lock
7. anchor build
```
**Risk:** Pins drift as crates.io updates. Need to re-pin periodically.

### Option B: Upgrade to Solana 2.0+ (recommended)
```
1. agave-install init stable (or specific 2.x version)
2. Reinstall platform-tools (newer rustc ≥ 1.85)
3. Update anchor-lang dependency to match
4. Build normally
```
**Risk:** May require code changes for breaking Solana SDK changes.

### Option C: Get lockfile from original dev environment
If the project compiled successfully elsewhere, get THAT Cargo.lock. It has the right pins baked in.

## Verification After Build
```bash
# Check compiled programs exist
ls target/deploy/*.so

# Check keypairs exist
ls target/deploy/*-keypair.json

# Verify program IDs match Anchor.toml
solana program show <PROGRAM_ID> --url devnet
```

## Workaround: cargo-build-sbf When anchor build Fails on IDL

`anchor build` does two things: (1) compiles programs to `.so`, (2) generates IDL JSON. Step 2 often fails on older projects because IDL generation uses different deps.

If `anchor build` fails but programs seem to compile, **build each individually**:
```bash
for prog in program-a program-b program-c; do
    cargo-build-sbf --manifest-path "programs/$prog/Cargo.toml"
done
```
This skips IDL generation. The `.so` files appear in `target/deploy/`. IDLs can be hand-written for hackathon demos.

## Agave CLI Install Notes

The `anza.xyz/stable` installer sometimes returns a **minimal install** (missing `solana` binary). Pin a specific version:
```bash
# Preferred: pin to known-good version
sh -c "$(curl -sSfL https://release.anza.xyz/v2.2.14/install)"

# Avoid: "stable" may give partial installs on some systems
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
```

## Related
- `anchor build` with `--no-idl` skips IDL generation (avoids source_file() issue but loses IDL)
- SBF platform-tools installed at: `~/.cache/solana/v1.52/platform-tools/`
- If rustc binary missing: run `cd $SOLANA_SDK/sbf && bash scripts/install.sh`
