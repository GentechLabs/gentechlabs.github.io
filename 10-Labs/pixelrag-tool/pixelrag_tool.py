"""
PixelRAG Agent Kit Tool — Visual search for agents.
Screenshots web pages, embeds them visually, and searches over images.
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

PIXELRAG_VENV = os.path.join(os.path.dirname(__file__), "..", "10-Labs", ".venv-pixelrag", "Scripts", "python.exe")
PIXELRAG_DIR = os.path.join(os.path.dirname(__file__), "..", "10-Labs", "pixelrag-index")
os.makedirs(PIXELRAG_DIR, exist_ok=True)


def _run_pixelrag(args: list[str], timeout: int = 120) -> dict:
    """Run a pixelrag command and return result."""
    cmd = [PIXELRAG_VENV, "-m", "pixelrag"] + args
    env = {**os.environ, "PYTHONPATH": ""}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return {"success": r.returncode == 0, "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}


def screenshot_page(url: str, output_dir: str = None) -> dict:
    """Capture a web page as tiled screenshots for visual search."""
    out = output_dir or os.path.join(PIXELRAG_DIR, "captures")
    os.makedirs(out, exist_ok=True)
    cmd = [str(PIXELRAG_VENV), "-m", "pixelrag_render.render", "--output", out, "--backend", "cdp", "--viewport-width", "875", url]
    env = {**os.environ, "PYTHONPATH": ""}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        # Find the tile dir
        tile_dirs = list(Path(out).glob("*.png.tiles"))
        return {
            "success": r.returncode == 0,
            "tile_dir": str(tile_dirs[0]) if tile_dirs else None,
            "output": r.stdout[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}


def search_visual(query: str, index_dir: str = None) -> dict:
    """Search the visual index for pages matching a query."""
    idx = index_dir or os.path.join(PIXELRAG_DIR, "index")
    if not os.path.exists(idx):
        return {"success": False, "error": "No index built yet. Run build_index() first."}
    result = _run_pixelrag(["serve", "--index-dir", idx, "--query", query])
    return result


def build_index(source_dir: str = None) -> dict:
    """Build a FAISS index from captured tiles."""
    src = source_dir or os.path.join(PIXELRAG_DIR, "captures")
    out = os.path.join(PIXELRAG_DIR, "index")
    os.makedirs(out, exist_ok=True)

    # Chunk
    r1 = _run_pixelrag(["chunk", "--tiles-dir", src, "--workers", "4"])
    if not r1["success"]:
        return r1

    # Embed
    shards = list(Path(src).glob("shard_*"))
    if not shards:
        return {"success": False, "error": "No shards found after chunking"}

    for shard in shards:
        r2 = _run_pixelrag(["embed", "--shard-dir", str(shard), "--output-dir", out, "--backend", "direct_gpu", "--batch-size", "32"])
        if not r2["success"]:
            return r2

    # Build index
    r3 = _run_pixelrag(["build-index", "--embeddings-dir", out, "--output-dir", out])
    return r3


def status() -> dict:
    """Check PixelRAG status."""
    return {
        "installed": os.path.exists(PIXELRAG_VENV),
        "index_dir": PIXELRAG_DIR,
        "captures_dir": os.path.join(PIXELRAG_DIR, "captures"),
        "index_exists": os.path.exists(os.path.join(PIXELRAG_DIR, "index")),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PixelRAG Agent Kit Tool")
    parser.add_argument("action", choices=["screenshot", "search", "build", "status"])
    parser.add_argument("--url", help="URL to screenshot")
    parser.add_argument("--query", help="Search query")
    args = parser.parse_args()

    if args.action == "status":
        print(json.dumps(status(), indent=2))
    elif args.action == "screenshot":
        if not args.url: print("Usage: pixelrag_tool.py screenshot --url https://..."); sys.exit(1)
        print(json.dumps(screenshot_page(args.url), indent=2))
    elif args.action == "search":
        if not args.query: print("Usage: pixelrag_tool.py search --query 'text'"); sys.exit(1)
        print(json.dumps(search_visual(args.query), indent=2))
    elif args.action == "build":
        print(json.dumps(build_index(), indent=2))
