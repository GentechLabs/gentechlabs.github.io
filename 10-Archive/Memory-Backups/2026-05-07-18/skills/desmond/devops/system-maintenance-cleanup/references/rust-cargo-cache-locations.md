# Rust/Cargo Cache Locations — Cleanup Guide

Cargo stores build artifacts and registry caches in predictable locations. These can accumulate quickly across multiple projects and agent profiles.

## Where Bloat Lives

### 1. Per-Project `target/` (LARGEST)
**Path pattern:** `<project>/target/`
**Size:** 500MB — 5GB per project (depends on dependencies)
**Content:** Compiled artifacts, debug symbols, incremental build cache
**Safe to delete?** ✅ YES — Cargo rebuilds on next `cargo build`
**How to delete:**
```bash
# Specific project
rm -rf /path/to/project/target

# All projects (aggressive)
find /root -type d -name 'target' -exec rm -rf {} + 2>/dev/null
```

### 2. Cargo Registry Source (SMALLER)
**Path:** `~/.cargo/registry/src/index.crates.io-*/`
**Size:** ~200–500MB
**Content:** Source code for all downloaded crates (extracted tarfiles)
**Safe to delete?** ✅ YES — Cargo re-downloads as needed
**How to delete:**
```bash
rm -rf ~/.cargo/registry/src
# Cargo will repopulate on next build (no network if crates cached)
```

### 3. Cargo Registry Cache (compressed)
**Path:** `~/.cargo/registry/cache/`
**Size:** ~100–300MB
**Content:** Compressed `.crate` files (downloaded from crates.io)
**Safe to delete?** ✅ YES — Cargo re-downloads
**How to delete:**
```bash
rm -rf ~/.cargo/registry/cache
```

### 4. Cargo Git Dependency Cache
**Path:** `~/.cargo/git/`
**Size:** Varies (depends on git dependencies)
**Content:** Cloned git repos for dependencies
**Safe to delete?** ⚠️ CONDITIONAL — if network available, Cargo re-clones. If offline, may lose access.
**Recommendation:** Keep unless disk space critical.

### 5. Hermes Agent-Specific Cargo (BLOAT MAGNET)
Common locations across profiles:
- `/root/.hermes/profiles/dmob/home/.cargo/`
- `/root/.hermes/profiles/gentech/home/.cargo/`
- `/root/.hermes/profiles/yoyo/home/.cargo/`
- `/root/.hermes/profiles/desmond/home/.cargo/`

**Note:** Each agent profile maintains separate cargo registry + caches. This is redundant and can be safely cleared if the agent doesn't have active Rust builds in its own home directories.

---

## Recommended Cleanup Order

1. **Stop any running cargo builds** (to avoid corruption)
2. **Delete per-project `target/` dirs** (biggest wins)
3. **Clear registry src + cache** (medium win)
4. **Audit profile-specific `.cargo/` dirs** — clear if no active builds in that profile
5. **Verify with `du -sh ~/.cargo`** before and after

## Quick Clean (Single Command)

```bash
# Nuke all Rust build artifacts system-wide
find /root -type d -name 'target' -exec rm -rf {} + 2>/dev/null
rm -rf ~/.cargo/registry/src ~/.cargo/registry/cache
echo "Cargo caches cleared. Rebuild will occur on next cargo build."
```

## Pro-Tip: Cargo Clean with `-p`

If you want to keep some targets but not others:
```bash
cargo clean -p <specific-crate>  # removes only that package's artifacts
```

## Gotchas

- **Active builds:** Don't delete `target/` while `cargo build` is running.
- **`cargo check --release`** still writes to `target/release/` — safe to delete after completion.
- **Hermes Kanban:** Local Rust binary at `/root/hermes-kanban` built from source; its `target/` can be safely removed (binary already installed).
- **Colosseum/Solana programs:** Anchor builds in `programs/<name>/target/` — these get rebuilt on `anchor build`. Safe to delete.
