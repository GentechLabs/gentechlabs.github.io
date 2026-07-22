"""
GenTech Agent Kit — PixelRAG Integration Module
=================================================
Wraps PixelRAG's visual search capabilities for AI agents.
Provides screenshot capture, visual search, and tile retrieval
as reusable tool functions.

Two modes:
  1. **pixelshot** — render any URL to screenshot tiles (local, CDP backend)
  2. **PixelRAG Search API** — search 8.28M Wikipedia pages by text or image

Usage:
  from pixelrag_agent_tool import PixelRAGClient

  client = PixelRAGClient()

  # Screenshot a page
  tiles = client.screenshot("https://gentechlabs.net")
  print(tiles[0])  # Path to tile directory

  # Search by text
  results = client.search("What is x402 protocol?")
  for hit in results:
      print(f"{hit.score:.3f} {hit.url}")

  # Search by image (visual similarity)
  results = client.search_by_image("path/to/screenshot.jpg")
  for hit in results:
      print(f"{hit.score:.3f} {hit.url}")

  # Fetch a tile image from search results
  tile_path = client.fetch_tile(hit)
"""

import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Configuration ──────────────────────────────────────────────────────

PIXELRAG_API_URL = "https://pixelrag.ai/api"
PIXELRAG_SEARCH_URL = f"{PIXELRAG_API_URL}/search"
PIXELRAG_TILE_URL = f"{PIXELRAG_API_URL}/tile"

# Path to the pixelrag venv (for clean env execution)
PIXELRAG_VENV_PYTHON = r"C:\Users\jhitm\Desktop\GenTech_Agency\pixelrag-demo\.venv\Scripts\python.exe"


# ── Data Types ────────────────────────────────────────────────────────

@dataclass
class SearchHit:
    """A single search result from PixelRAG."""
    score: float
    url: str
    article_id: int
    tile_index: int
    chunk_index: int
    y_offset: int = 0
    tile_height: int = 1024
    path: str = ""
    article_pages: str = ""
    image_base64: Optional[str] = None


@dataclass
class ScreenshotResult:
    """Result of a pixelshot capture."""
    url: str
    tile_dir: Path
    tile_count: int
    tiles: list = field(default_factory=list)
    complete: bool = False


# ── PixelRAG Client ────────────────────────────────────────────────────

class PixelRAGClient:
    """
    Client for PixelRAG visual search and screenshot capture.

    Two capabilities:
    - **screenshot()** — renders any URL to screenshot tiles via local CDP
    - **search()** — queries the hosted PixelRAG index (8.28M Wikipedia pages)
    - **search_by_image()** — visual similarity search using an image
    - **fetch_tile()** — downloads a tile image from search results
    """

    def __init__(self, pixelshot_python: str = PIXELRAG_VENV_PYTHON):
        self.pixelshot_python = pixelshot_python
        self._check_pixelshot()

    def _check_pixelshot(self):
        """Verify pixelshot is available."""
        if not os.path.isfile(self.pixelshot_python):
            raise RuntimeError(
                f"PixelRAG venv not found at {self.pixelshot_python}. "
                "Run: cd pixelrag-demo && uv venv --python 3.12 && uv pip install pixelrag pillow"
            )

    def _run_pixelshot(self, url: str, output_dir: str) -> dict:
        """Run pixelshot CLI via the clean venv."""
        env = {k: v for k, v in os.environ.items() if 'hermes' not in k.lower()}
        env.pop('PYTHONPATH', None)

        cmd = [
            self.pixelshot_python, '-m', 'pixelrag_render.render',
            url, '--output', output_dir, '--workers', '1'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

        if result.returncode != 0:
            # Check if it actually produced output despite non-zero exit
            tiles_dir = None
            for line in result.stdout.split('\n'):
                if '.png.tiles' in line:
                    tiles_dir = line.strip()
                    break

            if not tiles_dir:
                raise RuntimeError(
                    f"pixelshot failed: {result.stderr[:500]}"
                )

        # Parse output for tile directory
        tiles_dir = None
        for line in result.stdout.split('\n'):
            if '.png.tiles' in line:
                tiles_dir = line.strip()
                break

        if not tiles_dir:
            # Try to find it in the output directory
            out_path = Path(output_dir)
            tile_dirs = list(out_path.glob("*.png.tiles"))
            if tile_dirs:
                tiles_dir = str(tile_dirs[0])

        if not tiles_dir:
            return {"url": url, "tile_dir": None, "tile_count": 0, "tiles": [], "complete": False}

        tile_path = Path(tiles_dir)
        tiles_json = tile_path / "tiles.json"
        tile_files = sorted(tile_path.glob("tile_*.jpg"))

        metadata = {}
        if tiles_json.exists():
            with open(tiles_json) as f:
                metadata = json.load(f)

        return {
            "url": url,
            "tile_dir": str(tile_path),
            "tile_count": len(tile_files),
            "tiles": [str(t) for t in tile_files],
            "complete": metadata.get("complete", False),
        }

    # ── Screenshot Capture ────────────────────────────────────────────

    def screenshot(self, url: str, output_dir: Optional[str] = None) -> ScreenshotResult:
        """
        Render a URL to screenshot tiles.

        Args:
            url: The URL to screenshot
            output_dir: Output directory (default: temp dir)

        Returns:
            ScreenshotResult with tile paths and metadata
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="pixelshot_")

        result = self._run_pixelshot(url, output_dir)

        return ScreenshotResult(
            url=result["url"],
            tile_dir=Path(result["tile_dir"]) if result["tile_dir"] else None,
            tile_count=result["tile_count"],
            tiles=result["tiles"],
            complete=result["complete"],
        )

    # ── Text Search ───────────────────────────────────────────────────

    def search(self, query: str, n_docs: int = 5) -> list[SearchHit]:
        """
        Search the PixelRAG index by text query.

        Args:
            query: Natural language query (e.g. "What is the capital of France?")
            n_docs: Number of results to return (default: 5)

        Returns:
            List of SearchHit objects sorted by relevance
        """
        payload = json.dumps({
            "queries": [{"text": query}],
            "n_docs": n_docs,
        }).encode()

        req = urllib.request.Request(
            PIXELRAG_SEARCH_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            raise RuntimeError(f"PixelRAG search failed: {e}")

        hits = []
        for r in data.get("results", []):
            for h in r.get("hits", []):
                hits.append(SearchHit(
                    score=h.get("score", 0),
                    url=h.get("url", ""),
                    article_id=h.get("article_id", 0),
                    tile_index=h.get("tile_index", 0),
                    chunk_index=h.get("chunk_index", 0),
                    y_offset=h.get("y_offset", 0),
                    tile_height=h.get("tile_height", 1024),
                    path=h.get("path", ""),
                    article_pages=h.get("article_pages", ""),
                    image_base64=h.get("image_base64"),
                ))

        # Sort by score descending
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits

    # ── Image Search ──────────────────────────────────────────────────

    def search_by_image(self, image_path: str, text: Optional[str] = None, n_docs: int = 5) -> list[SearchHit]:
        """
        Search the PixelRAG index by image (visual similarity).

        Args:
            image_path: Path to a local image file
            text: Optional text query to combine with image (hybrid search)
            n_docs: Number of results to return (default: 5)

        Returns:
            List of SearchHit objects sorted by visual similarity
        """
        # Read and base64-encode the image
        with open(image_path, "rb") as f:
            import base64
            b64 = base64.b64encode(f.read()).decode()

        query = {"image": b64}
        if text:
            query["text"] = text

        payload = json.dumps({
            "queries": [query],
            "n_docs": n_docs,
        }).encode()

        req = urllib.request.Request(
            PIXELRAG_SEARCH_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            raise RuntimeError(f"PixelRAG image search failed: {e}")

        hits = []
        for r in data.get("results", []):
            for h in r.get("hits", []):
                hits.append(SearchHit(
                    score=h.get("score", 0),
                    url=h.get("url", ""),
                    article_id=h.get("article_id", 0),
                    tile_index=h.get("tile_index", 0),
                    chunk_index=h.get("chunk_index", 0),
                    y_offset=h.get("y_offset", 0),
                    tile_height=h.get("tile_height", 1024),
                    path=h.get("path", ""),
                    article_pages=h.get("article_pages", ""),
                    image_base64=h.get("image_base64"),
                ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits

    # ── Tile Fetching ─────────────────────────────────────────────────

    def fetch_tile(self, hit: SearchHit, output_path: Optional[str] = None) -> str:
        """
        Download a tile image from a search hit.

        Args:
            hit: A SearchHit from search() or search_by_image()
            output_path: Where to save the tile (default: temp file)

        Returns:
            Path to the downloaded tile image
        """
        tile_url = f"{PIXELRAG_TILE_URL}/{hit.article_id}/{hit.tile_index}/{hit.chunk_index}"

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".png")

        try:
            urllib.request.urlretrieve(tile_url, output_path)
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to fetch tile: {e}")

        return output_path

    # ── Research Workflow ────────────────────────────────────────────

    def research(self, query: str, n_docs: int = 3) -> list[dict]:
        """
        Full research workflow: search + fetch tiles.

        Args:
            query: Natural language query
            n_docs: Number of results to fetch

        Returns:
            List of dicts with url, score, and local tile path
        """
        hits = self.search(query, n_docs=n_docs)
        results = []

        for hit in hits:
            tile_path = self.fetch_tile(hit)
            results.append({
                "url": hit.url,
                "score": hit.score,
                "tile_path": tile_path,
                "article_id": hit.article_id,
            })

        return results


# ── Quick Test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=== GenTech Agent Kit — PixelRAG Module ===")
    print()

    client = PixelRAGClient()

    # 1. Text search
    print("1. Text search: 'What is x402 protocol?'")
    hits = client.search("What is x402 protocol?", n_docs=3)
    for h in hits:
        print(f"   [{h.score:.3f}] {h.url}")
    print()

    # 2. Visual search (Mario)
    print("2. Text search: 'Mario jumping over a pipe'")
    hits = client.search("Mario jumping over a pipe", n_docs=3)
    for h in hits:
        print(f"   [{h.score:.3f}] {h.url}")
    print()

    # 3. Screenshot a page
    print("3. Screenshot: gentechlabs.net")
    result = client.screenshot("https://gentechlabs.net")
    if result.tile_dir:
        print(f"   Tile dir: {result.tile_dir}")
        print(f"   Tiles: {result.tile_count}")
    else:
        print("   ❌ Screenshot failed")
    print()

    # 4. Research workflow
    print("4. Research: 'What is the capital of France?'")
    research = client.research("What is the capital of France?", n_docs=2)
    for r in research:
        print(f"   [{r['score']:.3f}] {r['url']} → {r['tile_path']}")
    print()

    print("=== All tests complete ===")
