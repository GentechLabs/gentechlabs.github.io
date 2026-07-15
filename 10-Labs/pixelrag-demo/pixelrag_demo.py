"""
GenTech PixelRAG Demo — Visual Search Demo
============================================
Renders web pages as screenshot tiles and shows visual search results.
Demonstrates PixelRAG's ability to search by how a page LOOKS, not just text.

Usage:
    python pixelrag_demo.py --url https://ProtoJay4789.github.io/hub-vanito
    python pixelrag_demo.py --url https://ProtoJay4789.github.io --search "KAGE"
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# ── Config ──

PIXELRAG_DIR = Path(r"C:\Users\jhitm\Desktop\GenTech_Agency\PixelRAG")
VENV_PYTHON = PIXELRAG_DIR / ".venv" / "Scripts" / "python.exe"
OUTPUT_DIR = Path(r"C:\Users\jhitm\Desktop\GenTech_Agency\gentech-vault-new\10-Labs\pixelrag-demo")

# Demo URLs
DEMO_SITES = {
    "vanito": "https://ProtoJay4789.github.io/hub-vanito",
    "jordan": "https://ProtoJay4789.github.io",
    "gentech": "https://gentechlabs.net",
}


def render_page(url: str, name: str = None) -> Path:
    """Render a URL to screenshot tiles using PixelRAG."""
    if name is None:
        name = url.replace("https://", "").replace("/", "_").replace(".", "-")

    output = OUTPUT_DIR / name
    output.mkdir(parents=True, exist_ok=True)

    print(f"  Rendering {url}...")
    result = subprocess.run(
        [
            str(VENV_PYTHON), "-m", "pixelrag_render.render",
            url,
            "--output", str(output),
            "--backend", "cdp",
            "--workers", "1",
            "--tile-height", "1024",
        ],
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "PYTHONPATH": ""},
    )

    if result.returncode != 0:
        print(f"  ⚠️  Render stderr: {result.stderr.strip()[:200]}")

    # Find the tile directory
    tile_dirs = list(output.glob("*.tiles"))
    if tile_dirs:
        tile_dir = tile_dirs[0]
        tiles = list(tile_dir.glob("tile_*.jpg"))
        print(f"  ✅ {len(tiles)} tile(s) generated ({tile_dir.name})")
        return tile_dir
    else:
        print(f"  ⚠️  No tiles found in {output}")
        return None


def show_demo_summary(results: dict):
    """Print a summary of all rendered pages."""
    print("\n" + "=" * 60)
    print("  PIXELRAG DEMO — Visual Search Results")
    print("=" * 60)

    for name, info in results.items():
        status = "✅" if info["tiles"] else "❌"
        tile_count = len(info["tiles"]) if info["tiles"] else 0
        print(f"\n  {status} {name}: {info['url']}")
        print(f"     Tiles: {tile_count}")
        if info["tiles"]:
            first_tile = info["tiles"][0]
            size_kb = os.path.getsize(first_tile) / 1024
            print(f"     First tile: {first_tile.name} ({size_kb:.0f} KB)")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="GenTech PixelRAG Demo")
    parser.add_argument("--url", help="Single URL to render")
    parser.add_argument("--all", action="store_true", help="Render all demo sites")
    parser.add_argument("--search", help="Search term (visual search via API)")

    args = parser.parse_args()

    # Ensure output dir exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    if args.url:
        # Single URL
        tile_dir = render_page(args.url)
        tiles = sorted(tile_dir.glob("tile_*.jpg")) if tile_dir else []
        results[args.url] = {"url": args.url, "tiles": tiles}

    elif args.all:
        # All demo sites
        for name, url in DEMO_SITES.items():
            tile_dir = render_page(url, name)
            tiles = sorted(tile_dir.glob("tile_*.jpg")) if tile_dir else []
            results[name] = {"url": url, "tiles": tiles}

    else:
        # Default: render Vanito's Hub
        tile_dir = render_page(DEMO_SITES["vanito"], "vanito")
        tiles = sorted(tile_dir.glob("tile_*.jpg")) if tile_dir else []
        results["vanito"] = {"url": DEMO_SITES["vanito"], "tiles": tiles}

    show_demo_summary(results)

    # Save results as JSON for reference
    summary = {}
    for name, info in results.items():
        summary[name] = {
            "url": info["url"],
            "tile_count": len(info["tiles"]) if info["tiles"] else 0,
            "tiles": [str(t) for t in info["tiles"]] if info["tiles"] else [],
        }

    summary_path = OUTPUT_DIR / "demo-summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
