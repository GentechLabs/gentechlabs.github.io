# Solana SBF Dependency Pinning Reference

## The Problem

Solana CLI 2.1.x ships `cargo-build-sbf` with bundled cargo 1.79.0 (platform-tools v1.43). This cargo:
- Cannot parse `Cargo.lock` version 4 (needs `-Znext-lockfile-bump`, nightly feature)
- Cannot compile crates using `edition2024` (needs rustc ≥ 1.86)
- Cannot download crates whose manifests use `edition2024`

System cargo (rustup 1.85+) generates v4 lockfiles and resolves to latest crate versions — many of which now require edition2024.

## The Fix (Step by Step)

### 1. Generate lockfile with pinned Rust 1.85.0

```bash
rm -f Cargo.lock
RUSTUP_TOOLCHAIN=1.85.0-x86_64-unknown-linux-gnu cargo generate-lockfile
```

This produces a v3 lockfile (Rust 1.85 default). If you used system cargo (1.95+), fix manually:
```bash
sed -i 's/^version = 4$/version = 3/' Cargo.lock
```

### 2. Pin edition2024 offenders

Run these in order — each downgrade may reveal the next:

```bash
# indexmap: toml_edit 0.25+ requires ^2.13, but 2.13+ uses edition2024
# Fix: downgrade proc-macro-crate first to pull in older toml_edit
cargo update proc-macro-crate@3.5.0 --precise 3.1.0
cargo update indexmap@2.14.0 --precise 2.7.1

# blake3: v1.8+ pulls digest 0.11 → ctutils 0.4 → cmov 0.5 (edition2024)
cargo update blake3@1.8.5 --precise 1.5.5

# unicode-segmentation: v1.13+ requires rustc 1.85
cargo update unicode-segmentation@1.13.2 --precise 1.12.0
```

### 3. Verify clean

```bash
grep -c "edition2024" Cargo.lock   # should be 0
head -3 Cargo.lock                  # should show "version = 3"
```

### 4. Build

```bash
cargo-build-sbf  # or: anchor build --no-idl
```

## Known Offending Crates (as of May 2026)

| Crate | Bad Version | Safe Version | Why |
|-------|-------------|--------------|-----|
| indexmap | ≥ 2.13.0 | 2.7.1 | toml_edit 0.25+ requires ^2.13 |
| blake3 | ≥ 1.8.0 | 1.5.5 | digest 0.11 → ctutils → cmov (edition2024) |
| unicode-segmentation | ≥ 1.13.0 | 1.12.0 | requires rustc 1.85 |
| cmov | ≥ 0.5.0 | (removed by blake3 pin) | edition2024 |
| hashbrown | 0.15.2+ | 0.15.2 (exact, forced by solana-security-txt) | usually OK if indexmap pinned |

## Alternative: Use Solana 3.x

Solana CLI 3.x ships platform-tools v1.52 with cargo ~1.95, which handles edition2024 natively. But:
- Requires Anchor 1.0.x (not 0.30.x)
- Platform-tools may not auto-download in all environments
- If using Anchor 0.30.x, stick with Solana 2.1.x + pinning

## IDL Generation Workaround

`anchor build` (full) tries to build IDL by compiling programs with the host compiler. If your program depends on `ark-bn254` (via `solana-zk-token-sdk`), the `MontFp!` macro panics.

**Workaround:** Build without IDL, use pre-existing IDLs:
```bash
anchor build --no-idl
# Programs compile to .so successfully
# IDL JSON + TS types can be copied from a previous build or vault
```

The IDL is only needed for TypeScript client type generation — it doesn't affect on-chain behavior.
