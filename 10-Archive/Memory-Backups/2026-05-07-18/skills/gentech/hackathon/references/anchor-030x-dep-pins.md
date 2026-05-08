# Anchor 0.30.x Dependency Pins for Platform-Tools ≤1.47

When building Anchor 0.30.x projects with Agave 2.2.x (platform-tools v1.47, Rust 1.84),
certain transitive dependencies have released versions requiring `edition = "2024"` which
the platform-tools Cargo cannot parse.

## The Fix

Run from project root after first failed `anchor build` or `cargo-build-sbf`:

```bash
# blake3 1.8.x → cpufeatures 0.3.0 (edition2024)
cargo update -p blake3 --precise 1.5.5

# proc-macro-crate 3.5.0 → toml_edit 0.25 → toml_datetime 1.1 (edition2024)
cargo update -p proc-macro-crate@3.5.0 --precise 3.2.0

# indexmap 2.14.0 (edition2024, but toml_edit needs >= 2.13)
cargo update -p indexmap@2.14.0 --precise 2.13.0

# borsh 1.6.x pulls newer transitive deps
cargo update -p borsh@1.6.1 --precise 1.5.3

# unicode-segmentation 1.13.x requires rustc 1.85
cargo update -p unicode-segmentation@1.13.2 --precise 1.12.0
```

## Order Matters

Pin `proc-macro-crate` BEFORE trying to pin `toml_datetime` directly —
cargo will refuse to downgrade `toml_datetime` while `toml_edit 0.25.x` requires it.

## Why These Specific Pins

| Dep | Bad Version | Pinned To | Pulled By | Why Bad |
|-----|-------------|-----------|-----------|---------|
| cpufeatures | 0.3.0 | (removed by blake3 pin) | blake3 1.8.x | edition2024 |
| toml_datetime | 1.1.1 | (removed by proc-macro-crate pin) | toml_edit 0.25.x | edition2024 |
| toml_edit | 0.25.11 | (removed by proc-macro-crate pin) | proc-macro-crate 3.5.x | depends on toml_datetime 1.1 |
| blake3 | 1.8.5 | 1.5.5 | solana-program | pulls cpufeatures 0.3.0 |
| proc-macro-crate | 3.5.0 | 3.2.0 | borsh-derive | pulls toml_edit 0.25 |
| indexmap | 2.14.0 | 2.13.0 | toml_edit (indirect) | edition2024 |
| borsh | 1.6.1 | 1.5.3 | solana-program | pulls newer borsh-derive |
| unicode-segmentation | 1.13.2 | 1.12.0 | (direct dep) | requires rustc 1.85 |

## Verification

After pinning:
```bash
cargo-build-sbf --manifest-path programs/<name>/Cargo.toml
# Should show "Finished `release` profile" without edition2024 errors
ls target/deploy/*.so  # Should exist
```

## Tested With

- Agave CLI 2.2.14 (platform-tools v1.47, cargo 1.84)
- Anchor CLI 0.30.1
- Rust 1.95.0 (host)
- solana-program 1.18.26
- anchor-lang 0.30.1
