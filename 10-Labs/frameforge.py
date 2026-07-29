#!/usr/bin/env python3
"""FrameForge — AI Storyboard Service API
FastAPI-based backend for character-consistent storyboard generation.

Pipeline: Character sheet → locked look → shot list → batch frames → compiled video.

Phase 1: Service portal + basic storyboard generation.
"""

import json, os, uuid, io, base64, hashlib, re, time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

# ── Config ──────────────────────────────────────────────────────────────────
DATA_DIR = Path("/var/www/gentechlabs/frameforge/data")
CHARACTERS_DIR = Path("/var/www/gentechlabs/frameforge/characters")
STORYBOARDS_DIR = Path("/var/www/gentechlabs/frameforge/storyboards")
OUTPUT_DIR = Path("/var/www/gentechlabs/frameforge/output")
GALLERY_DIR = Path("/var/www/gentechlabs/frameforge/gallery")

for d in [DATA_DIR, CHARACTERS_DIR, STORYBOARDS_DIR, OUTPUT_DIR, GALLERY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── In-Memory Store ─────────────────────────────────────────────────────────
# Phase 1: Simple JSON file storage. Phase 2: SQLite/Postgres.
def load_store(name):
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}

def save_store(name, data):
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))

def generate_id():
    return uuid.uuid4().hex[:12]

# ── Camera Presets ──────────────────────────────────────────────────────────
CAMERA_PRESETS = {
    "wide": {"angle": "wide establishing shot", "distance": "far", "lens": "16mm"},
    "master": {"angle": "master shot", "distance": "full body", "lens": "35mm"},
    "medium": {"angle": "medium shot", "distance": "waist up", "lens": "50mm"},
    "close": {"angle": "close up", "distance": "face only", "lens": "85mm"},
    "extreme": {"angle": "extreme close up", "distance": "eyes/mouth", "lens": "135mm"},
    "over": {"angle": "over the shoulder", "distance": "medium", "lens": "50mm"},
    "low": {"angle": "low angle", "distance": "full body", "lens": "24mm"},
    "high": {"angle": "high angle", "distance": "full body", "lens": "70mm"},
    "drone": {"angle": "bird's eye", "distance": "extreme wide", "lens": "14mm"},
    "track": {"angle": "tracking side view", "distance": "full body", "lens": "50mm"},
}

MOOD_PRESETS = {
    "bright": "bright, well-lit, golden hour lighting, warm tones",
    "dark": "low key lighting, deep shadows, dramatic contrast",
    "neon": "neon lighting, cyberpunk palette, blue/pink highlights",
    "moody": "overcast, desaturated, soft diffused light",
    "dramatic": "single hard light source, chiaroscuro, deep shadows",
    "warm": "sunset tones, amber and gold, soft glow",
    "cold": "blue hour, cool tones, stark lighting",
    "foggy": "atmospheric fog, volumetric lighting, mist",
    "rain": "rain-slicked surfaces, wet reflections, grey sky",
    "studio": "three-point lighting, clean backdrop, professional",
}

# ── Character Locker ────────────────────────────────────────────────────────
class CharacterLocker:
    """Store character reference data for consistent generation."""

    @staticmethod
    def lock(character_data: dict) -> dict:
        """Store a character's reference config and return a locked character ID."""
        chars = load_store("characters")
        char_id = generate_id()
        
        # Generate a seedable config from the character data
        config = {
            "id": char_id,
            "name": character_data.get("name", "Unnamed Character"),
            "description": character_data.get("description", ""),
            "physical_traits": character_data.get("physical_traits", ""),
            "clothing": character_data.get("clothing", ""),
            "palette": character_data.get("palette", ""),
            "seed_notes": character_data.get("seed_notes", ""),
            "coating": character_data.get("coating", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": 1,
        }
        
        chars[char_id] = config
        save_store("characters", chars)
        return config

    @staticmethod
    def get(char_id: str) -> dict:
        """Retrieve a locked character config."""
        chars = load_store("characters")
        return chars.get(char_id)

    @staticmethod
    def update(char_id: str, updates: dict) -> dict:
        """Update a character's config (new coating, etc)."""
        chars = load_store("characters")
        if char_id not in chars:
            return None
        chars[char_id].update(updates)
        chars[char_id]["version"] += 1
        chars[char_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_store("characters", chars)
        return chars[char_id]

    @staticmethod
    def list_all() -> dict:
        return load_store("characters")

# ── Prompt Engine ───────────────────────────────────────────────────────────
class PromptEngine:
    """Build time-coded generation prompts from character config + shot data."""

    @staticmethod
    def build_frame_prompt(char_config: dict, shot: dict, frame_index: int = 0) -> str:
        """Build a full generation prompt for one storyboard frame."""
        camera = CAMERA_PRESETS.get(shot.get("camera", "medium"), CAMERA_PRESETS["medium"])
        mood = MOOD_PRESETS.get(shot.get("mood", "dramatic"), MOOD_PRESETS["dramatic"])
        
        parts = [
            f"Character: {char_config.get('name', 'character')}",
            f"Description: {char_config.get('physical_traits', '')}",
            f"Wearing: {char_config.get('clothing', '')}",
            f"Color palette: {char_config.get('palette', '')}",
            f"Action: {shot.get('action', 'standing')}",
            f"Camera: {camera['angle']} ({camera['distance']}, {camera['lens']})",
            f"Lighting: {mood}",
            f"Background: {shot.get('background', 'simple background')}",
            f"Composition notes: {shot.get('composition', '')}",
        ]
        
        if char_config.get("coating"):
            parts.append(f"Style coating: {char_config['coating']}")
        
        if shot.get("emotion"):
            parts.append(f"Expression: {shot['emotion']}")
        
        if shot.get("props"):
            parts.append(f"Props: {shot['props']}")
        
        return ". ".join(parts)

    @staticmethod
    def build_timecoded_prompts(char_config: dict, scene_shots: list, fps: int = 24, seconds_per_shot: int = 4) -> str:
        """Build full time-coded prompt string for video generation."""
        timecodes = []
        current_time = 0
        
        for i, shot in enumerate(scene_shots):
            start = current_time
            end = current_time + seconds_per_shot
            prompt = PromptEngine.build_frame_prompt(char_config, shot, i)
            timecodes.append(f"[{start}s-{end}s] {prompt}")
            current_time = end
        
        return "\n".join(timecodes)

# ── Storyboard Engine ───────────────────────────────────────────────────────
class StoryboardEngine:
    """Generate storyboards from character config + shot list."""

    @staticmethod
    def create_storyboard(char_id: str, scenes: list, title: str = "Untitled") -> dict:
        """Create a storyboard from a character and shot list."""
        char_config = CharacterLocker.get(char_id)
        if not char_config:
            return {"error": "Character not found"}
        
        storyboards = load_store("storyboards")
        sb_id = generate_id()
        
        # Process each scene
        processed_scenes = []
        total_frames = 0
        
        for scene_idx, scene in enumerate(scenes):
            shots = scene.get("shots", [])
            scene_frames = []
            
            for shot_idx, shot in enumerate(shots):
                prompt = PromptEngine.build_frame_prompt(char_config, shot, shot_idx)
                scene_frames.append({
                    "shot_number": shot_idx + 1,
                    "prompt": prompt,
                    "camera": shot.get("camera", "medium"),
                    "mood": shot.get("mood", "dramatic"),
                    "action": shot.get("action", "standing"),
                    "background": shot.get("background", ""),
                    "composition": shot.get("composition", ""),
                    "emotion": shot.get("emotion", ""),
                    "props": shot.get("props", ""),
                    "dialogue": shot.get("dialogue", ""),
                    "status": "pending",
                    "generated_url": None,
                })
            
            total_frames += len(scene_frames)
            processed_scenes.append({
                "scene_number": scene_idx + 1,
                "title": scene.get("title", f"Scene {scene_idx + 1}"),
                "description": scene.get("description", ""),
                "location": scene.get("location", ""),
                "time_of_day": scene.get("time_of_day", ""),
                "shots": scene_frames,
            })
        
        # Generate time-coded prompt string for video
        flat_shots = []
        for scene in processed_scenes:
            for shot in scene["shots"]:
                flat_shots.append({
                    "action": shot["action"],
                    "camera": shot["camera"],
                    "mood": shot["mood"],
                    "background": shot.get("background", ""),
                    "emotion": shot.get("emotion", ""),
                })
        
        timecoded_prompts = PromptEngine.build_timecoded_prompts(char_config, flat_shots)
        
        storyboard = {
            "id": sb_id,
            "title": title,
            "character_id": char_id,
            "character_name": char_config["name"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "draft",
            "total_scenes": len(scenes),
            "total_frames": total_frames,
            "scenes": processed_scenes,
            "timecoded_prompts": timecoded_prompts,
            "share_url": f"https://frameforge.gentechlabs.net/storyboard/{sb_id}",
            "generated_video_url": None,
        }
        
        storyboards[sb_id] = storyboard
        save_store("storyboards", storyboards)
        return storyboard

    @staticmethod
    def get_storyboard(sb_id: str) -> dict:
        storyboards = load_store("storyboards")
        return storyboards.get(sb_id)

    @staticmethod
    def list_storyboards() -> dict:
        return load_store("storyboards")

    @staticmethod
    def generate_preview(sb_id: str) -> dict:
        """Generate HTML preview of the storyboard."""
        sb = StoryboardEngine.get_storyboard(sb_id)
        if not sb:
            return {"error": "Storyboard not found"}
        
        # Build HTML preview
        char = CharacterLocker.get(sb["character_id"])
        
        html_parts = [
            '<!DOCTYPE html><html lang="en"><head>',
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<title>FrameForge — {sb["title"]}</title>',
            '<style>',
            '* { margin: 0; padding: 0; box-sizing: border-box; }',
            'body { font-family: "Inter", system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; }',
            '.header { padding: 40px 20px; border-bottom: 1px solid #1e1e2e; }',
            '.header h1 { font-size: 2em; background: linear-gradient(135deg, #6c5ce7, #a29bfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }',
            '.header .meta { color: #64748b; margin-top: 8px; font-size: 0.9em; }',
            '.scene { margin: 20px; border: 1px solid #1e1e2e; border-radius: 12px; overflow: hidden; }',
            '.scene-header { padding: 16px 20px; background: #12121a; border-bottom: 1px solid #1e1e2e; font-weight: 600; }',
            '.shot { padding: 16px 20px; border-bottom: 1px solid #1e1e2e; display: grid; grid-template-columns: 80px 1fr; gap: 16px; }',
            '.shot:last-child { border-bottom: none; }',
            '.shot-number { width: 48px; height: 48px; background: #6c5ce7; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2em; }',
            '.shot-details { }',
            '.shot-camera { color: #6c5ce7; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.05em; }',
            '.shot-prompt { color: #94a3b8; font-size: 0.9em; margin-top: 4px; line-height: 1.5; }',
            '.shot-extra { color: #64748b; font-size: 0.85em; margin-top: 4px; }',
            '.prompt-section { margin: 20px; padding: 20px; background: #12121a; border-radius: 12px; border: 1px solid #1e1e2e; }',
            '.prompt-section h3 { color: #6c5ce7; margin-bottom: 12px; }',
            '.prompt-section pre { background: #0a0a0f; padding: 16px; border-radius: 8px; font-family: "JetBrains Mono", monospace; font-size: 0.85em; line-height: 1.6; overflow-x: auto; white-space: pre-wrap; color: #94a3b8; }',
            '</style></head><body>',
            f'<div class="header"><h1>🎬 {sb["title"]}</h1>',
            f'<div class="meta">Character: {sb["character_name"]} · {sb["total_scenes"]} scenes · {sb["total_frames"]} frames · {sb["created_at"][:10]}</div></div>',
        ]
        
        for scene in sb.get("scenes", []):
            html_parts.append(f'<div class="scene">')
            html_parts.append(f'<div class="scene-header">Scene {scene["scene_number"]}: {scene["title"]}')
            if scene.get("location"):
                html_parts.append(f' · 📍 {scene["location"]}')
            if scene.get("time_of_day"):
                html_parts.append(f' · 🕐 {scene["time_of_day"]}')
            html_parts.append('</div>')
            
            for shot in scene.get("shots", []):
                html_parts.append(f'<div class="shot">')
                html_parts.append(f'<div class="shot-number">{shot["shot_number"]}</div>')
                html_parts.append(f'<div class="shot-details">')
                html_parts.append(f'<div class="shot-camera">🎥 {shot["camera"].upper()} · {shot["mood"].upper()}</div>')
                html_parts.append(f'<div class="shot-prompt">{shot["prompt"]}</div>')
                extras = []
                if shot.get("dialogue"): extras.append(f'💬 {shot["dialogue"]}')
                if shot.get("props"): extras.append(f'📦 {shot["props"]}')
                if extras:
                    html_parts.append(f'<div class="shot-extra">{" · ".join(extras)}</div>')
                html_parts.append('</div></div>')
            
            html_parts.append('</div>')
        
        # Timecoded prompts
        html_parts.append(f'<div class="prompt-section">')
        html_parts.append(f'<h3>🎯 Time-Coded Generation Prompts</h3>')
        html_parts.append(f'<pre>{sb.get("timecoded_prompts", "No prompts generated")}</pre>')
        html_parts.append('</div>')
        
        html_parts.append('</body></html>')
        
        preview_html = "\n".join(html_parts)
        
        # Save preview
        preview_path = GALLERY_DIR / f"{sb_id}.html"
        preview_path.write_text(preview_html)
        
        sb["preview_url"] = f"https://frameforge.gentechlabs.net/gallery/{sb_id}.html"
        
        # Update storyboard
        storyboards = load_store("storyboards")
        storyboards[sb_id] = sb
        save_store("storyboards", storyboards)
        
        return {
            "storyboard_id": sb_id,
            "preview_url": sb["preview_url"], 
            "total_frames": sb["total_frames"],
            "total_scenes": sb["total_scenes"],
            "share_url": sb["share_url"],
        }

# ── API Handler (FastAPI-compatible) ────────────────────────────────────────
def handle_request(method: str, path: str, body: dict = None) -> dict:
    """Route requests to the right handler."""
    
    # Health check
    if path == "/health" and method == "GET":
        return {"status": "ok", "service": "frameforge", "version": "0.1.0"}
    
    # Character endpoints
    if path == "/v1/characters" and method == "GET":
        return {"characters": CharacterLocker.list_all()}
    
    if path == "/v1/characters" and method == "POST" and body:
        result = CharacterLocker.lock(body)
        return {"character": result, "id": result["id"]}
    
    if path.startswith("/v1/characters/") and method == "GET":
        char_id = path.split("/")[-1]
        char = CharacterLocker.get(char_id)
        if not char:
            return {"error": "Character not found"}
        return {"character": char}
    
    # Storyboard endpoints
    if path == "/v1/storyboards" and method == "GET":
        return {"storyboards": StoryboardEngine.list_storyboards()}
    
    if path == "/v1/storyboards" and method == "POST" and body:
        char_id = body.get("character_id")
        scenes = body.get("scenes", [])
        title = body.get("title", "Untitled Storyboard")
        if not char_id or not scenes:
            return {"error": "character_id and scenes required"}
        result = StoryboardEngine.create_storyboard(char_id, scenes, title)
        return {"storyboard": result, "id": result.get("id")}
    
    if path.startswith("/v1/storyboards/") and path.endswith("/preview") and method == "GET":
        sb_id = path.split("/")[-2]
        result = StoryboardEngine.generate_preview(sb_id)
        return result
    
    if path.startswith("/v1/storyboards/") and method == "GET":
        sb_id = path.split("/")[-1]
        sb = StoryboardEngine.get_storyboard(sb_id)
        if not sb:
            return {"error": "Storyboard not found"}
        return {"storyboard": sb}
    
    # Camera presets
    if path == "/v1/presets/cameras" and method == "GET":
        return {"presets": CAMERA_PRESETS}
    
    if path == "/v1/presets/moods" and method == "GET":
        return {"presets": MOOD_PRESETS}
    
    return {"error": "Not found"}

# ── CLI Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 FrameForge — Pipeline Test\n")
        
        # 1. Lock a character
        hikari = {
            "name": "HIKARI Sakura",
            "description": "Japanese-Filipina teenage girl, 17 years old",
            "physical_traits": "Slim build, long black hair tied in a high ponytail with red ribbon, fair skin, expressive dark brown eyes",
            "clothing": "Black t-shirt with pink cherry blossom print, dark ripped jeans, black nail polish, silver ring",
            "palette": "Black, pink, silver, dark denim blue, fair skin tones",
            "seed_notes": "Anime-inspired semi-realism, vibrant but grounded colors",
            "coating": "Seedance 2.0 anime-realism hybrid, warm skin tones, soft rim lighting, cinematic depth of field",
        }
        
        char = CharacterLocker.lock(hikari)
        print(f"✅ Character locked: {char['name']} (ID: {char['id']})")
        
        # 2. Create a storyboard
        scenes = [
            {
                "title": "Morning Rooftop",
                "description": "HIKARI watches the sunrise from a rooftop in Cebu City",
                "location": "Rooftop, Cebu City skyline",
                "time_of_day": "Dawn",
                "shots": [
                    {
                        "camera": "wide",
                        "mood": "warm",
                        "action": "Standing at edge of rooftop, looking at the horizon, wind gently moving her hair and shirt",
                        "background": "Cebu City skyline at dawn, mountains in the distance, pastel orange and pink sky",
                        "emotion": "Peaceful, contemplative",
                        "composition": "Rule of thirds, HIKARI on the left third, cityscape stretching to the right",
                    },
                    {
                        "camera": "close",
                        "mood": "bright",
                        "action": "She smiles softly, eyes reflecting the sunrise",
                        "background": "Soft bokeh of the sunrise behind her",
                        "emotion": "Hopeful, content",
                        "composition": "Shallow depth of field, focus on eyes and subtle smile",
                    },
                    {
                        "camera": "high",
                        "mood": "dramatic",
                        "action": "She turns and walks toward the rooftop door, silhouette against the bright sky",
                        "background": "Bright sunrise sky, city below",
                        "emotion": "Determined",
                        "composition": "HIKARI as a dark silhouette against the bright sky, leading lines from the rooftop edge",
                    },
                ]
            },
            {
                "title": "The Message",
                "description": "HIKARI receives an unexpected message on her phone",
                "location": "Her bedroom",
                "time_of_day": "Late morning",
                "shots": [
                    {
                        "camera": "medium",
                        "mood": "moody",
                        "action": "Sitting on the edge of her bed, phone in hand, staring at the screen",
                        "background": "Modest bedroom, posters on wall, guitar in corner",
                        "emotion": "Surprised, uncertain",
                        "props": "Smartphone with glowing screen",
                        "composition": "Phone screen catching the light, her face half-lit by the glow",
                    },
                    {
                        "camera": "extreme",
                        "mood": "dramatic",
                        "action": "Her eyes widen, mouth slightly open",
                        "background": "Dark, close on face",
                        "emotion": "Shock, realization",
                        "composition": "Extreme close up on eyes — the reflection of the phone screen visible in her pupils",
                    },
                ]
            },
        ]
        
        sb = StoryboardEngine.create_storyboard(char["id"], scenes, "HIKARI Sakura no Chikai — Scene 1-2")
        print(f"✅ Storyboard created: {sb['title']}")
        print(f"   {sb['total_scenes']} scenes, {sb['total_frames']} frames")
        
        # 3. Generate preview
        preview = StoryboardEngine.generate_preview(sb["id"])
        print(f"✅ Preview generated: {preview['preview_url']}")
        
        # Print the timecoded prompts
        print(f"\n📋 Time-Coded Prompts:\n{sb['timecoded_prompts']}\n")
        
        print(f"✅ FrameForge pipeline test PASSED")
