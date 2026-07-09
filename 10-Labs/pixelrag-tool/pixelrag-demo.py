"""
PixelRAG Demo — GenTech Labs Visual Search Test
Run this on Forge's desktop (RTX 3070, CUDA).

What it does:
1. Captures screenshots of Vanito's Hub and Jordan's Hub
2. Builds a visual FAISS index
3. Runs sample queries to show visual search works

Usage:
  python pixelrag-demo.py

Requires:
  - pixelrag installed (pip install pixelrag[all])
  - CUDA GPU (RTX 3070+)
  - Node.js / Playwright for rendering (pixelrag handles this)
"""

import json, os, sys, time, subprocess
from pathlib import Path

DEMO_DIR = Path(__file__).parent / "demo-output"
DEMO_DIR.mkdir(exist_ok=True)

PAGE_DIR = DEMO_DIR / "captures"
INDEX_DIR = DEMO_DIR / "index"
RESULTS_DIR = DEMO_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# URLs to test — GenTech Live Pages
TEST_URLS = [
    ("Vanito's Hub", "https://ProtoJay4789.github.io/Vanito/"),
    ("Jordan's Hub", "https://ProtoJay4789.github.io/Jordan/"),
    ("GenTech Atlas", "https://ProtoJay4789.github.io/Games/GenTech-Atlas/"),
]

# Queries to run after indexing
TEST_QUERIES = [
    "music player",
    "DeFi dashboard",
    "travel companion Tokyo",
    "GenTech Atlas",
]

def step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

def run(cmd, timeout=120):
    print(f"  Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(f"  ⚠️  Exit code {r.returncode}")
        print(f"  stderr: {r.stderr[-500:]}")
    else:
        print(f"  ✅ OK")
    return r

def main():
    step("1. Capture screenshots of GenTech hub pages")
    for name, url in TEST_URLS:
        print(f"\n  📸 {name} — {url}")
        r = run([
            "python3", "-m", "pixelrag_render.render",
            "--output", str(PAGE_DIR),
            "--backend", "cdp",
            "--viewport-width", "875",
            url
        ])
        time.sleep(1)

    tile_count = len(list(PAGE_DIR.glob("*.png.tiles")))
    print(f"\n  📊 Total tile sets captured: {tile_count}")

    step("2. Chunk tiles into shards")
    run(["python3", "-m", "pixelrag", "chunk", "--tiles-dir", str(PAGE_DIR), "--workers", "4"])

    shards = list(PAGE_DIR.glob("shard_*"))
    print(f"  📦 Shards created: {len(shards)}")

    if not shards:
        print("  ❌ No shards — aborting.")
        sys.exit(1)

    step("3. Embed shards with GPU (Qwen3-VL-Embedding)")
    INDEX_DIR.mkdir(exist_ok=True)
    for shard in shards:
        run([
            "python3", "-m", "pixelrag", "embed",
            "--shard-dir", str(shard),
            "--output-dir", str(INDEX_DIR),
            "--backend", "direct_gpu",
            "--batch-size", "16"
        ])

    step("4. Build FAISS index")
    run([
        "python3", "-m", "pixelrag", "build-index",
        "--embeddings-dir", str(INDEX_DIR),
        "--output-dir", str(INDEX_DIR)
    ])

    step("5. Run test queries")
    for query in TEST_QUERIES:
        print(f"\n  🔍 Query: \"{query}\"")
        r = run([
            "python3", "-m", "pixelrag", "serve",
            "--index-dir", str(INDEX_DIR),
            "--query", query
        ])
        # Save results
        result_file = RESULTS_DIR / f"query-{query.replace(' ', '-')}.json"
        result_file.write_text(r.stdout)

    step("6. ✅ Demo Complete")
    print(f"\n  Results saved to: {RESULTS_DIR}")
    print(f"  Index location:   {INDEX_DIR}")
    print(f"  Raw captures:     {PAGE_DIR}")
    print(f"\n  Open results JSON files to see what PixelRAG found!")

if __name__ == "__main__":
    main()
