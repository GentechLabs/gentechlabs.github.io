"""Character locker: analyze a character reference sheet and produce a locked
look (coating + seed + palette) that is reused across every frame. This is the
core FrameForge differentiator — no character drift between shots.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CharacterLock:
    """A locked character configuration. Deterministic from the reference sheet."""

    name: str
    coating: str          # full inline character description (proven on KAGE)
    seed: int             # deterministic seed derived from the sheet
    palette: list[str]    # hex color palette
    source: str          # original reference sheet text
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "coating": self.coating,
            "seed": self.seed,
            "palette": self.palette,
            "source": self.source,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# Common color keywords -> hex, used to build a palette from a sheet.
_COLOR_MAP = {
    "red": "#c0392b", "crimson": "#8e1a1a", "scarlet": "#d32f2f",
    "blue": "#1f4e79", "navy": "#1a2a4a", "azure": "#2a6fb0",
    "green": "#2e7d32", "emerald": "#0f6b3f", "olive": "#6b8e23",
    "black": "#111111", "dark": "#1a1a1a", "charcoal": "#2b2b2b",
    "white": "#f5f5f5", "silver": "#c0c0c0", "gray": "#808080", "grey": "#808080",
    "gold": "#c9a227", "blonde": "#d9b36c", "yellow": "#f1c40f",
    "brown": "#6d4c2f", "tan": "#d2b48c", "bronze": "#a97142",
    "purple": "#6a3d9a", "violet": "#7d3c98", "magenta": "#c2185b",
    "orange": "#e67e22", "copper": "#b87333", "pink": "#e91e63",
    "teal": "#008080", "cyan": "#00bcd4", "maroon": "#800000",
    "steel": "#4682b4", "slate": "#708090", "ivory": "#fffff0",
    "cream": "#fffdd0", "pearl": "#f8f6f0", "ash": "#b2beb5",
}


def _extract_colors(text: str) -> list[str]:
    """Pull color keywords from the sheet text, in order of appearance."""
    found: list[str] = []
    for word in re.findall(r"[a-zA-Z]+", text.lower()):
        if word in _COLOR_MAP and word not in found:
            found.append(word)
    return [_COLOR_MAP[w] for w in found]


def _derive_seed(text: str) -> int:
    """Deterministic seed from the sheet content (stable across runs)."""
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def lock_character(name: str, reference_sheet: str) -> CharacterLock:
    """Analyze a character reference sheet and produce a locked look.

    The coating is the full inline description (the KAGE-proven pattern: every
    prompt carries the complete character description so the model never drifts).
    """
    sheet = reference_sheet.strip()
    if not sheet:
        raise ValueError("reference_sheet must not be empty")

    palette = _extract_colors(sheet)
    if not palette:
        # Fall back to a neutral studio palette rather than failing.
        palette = ["#1a1a1a", "#f5f5f5", "#808080"]

    seed = _derive_seed(sheet)

    # Coating: normalized, deduplicated inline description.
    coating = " ".join(sheet.split())

    return CharacterLock(
        name=name.strip() or "Character",
        coating=coating,
        seed=seed,
        palette=palette,
        source=sheet,
    )


def lock_from_file(name: str, path: str) -> CharacterLock:
    with open(path, "r", encoding="utf-8") as fh:
        return lock_character(name, fh.read())


def load_lock(path: str) -> CharacterLock:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return CharacterLock(
        name=data["name"],
        coating=data["coating"],
        seed=data["seed"],
        palette=data["palette"],
        source=data["source"],
        version=data.get("version", "1.0"),
    )
