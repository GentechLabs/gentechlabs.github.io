# BPF Toolchain Compatibility Notes

Solana CLI ships with platform-tools containing an older rustc (~1.79.0-dev). This creates compatibility issues with modern crate dependencies.

## Known Incompatible Dependencies

| Package | Min Rustc | Fix |
|---------|-----------|-----|
| `unicode-segmentation >= 1.13` | 1.85.0 | `cargo update unicode-segmentation@1.13.2 --precise 1.11.0` |

## Diagnosis

Build error pattern:
```
error: rustc 1.79.0-dev is not supported by the following package:
  <package>@<version> requires rustc <min-version>
```

## Fix

```bash
# Pin to the last version supporting rustc 1.79.0
cargo update <package>@<current-version> --precise <compatible-version>

# Then rebuild
cargo-build-sbf --manifest-path programs/<name>/Cargo.toml
```

## Anchor CLI Compatibility Matrix

| Anchor CLI | anchor-lang | Status on Rust 1.95 | Notes |
|------------|-------------|---------------------|-------|
| 0.30.1 | 0.30.1 | ❌ Fails (time crate) | Use cargo-build-sbf directly |
| 1.0.1 | 0.30.1 | ⚠️ Panics | Version mismatch panic |
| 1.0.1 | 1.0.1 | ✅ Works | Match versions |

**Rule:** When Anchor CLI can't build, fall back to `cargo-build-sbf` for compilation verification. IDL generation requires a working Anchor CLI.
