#!/usr/bin/env python3
"""Bundle Meta Ray-Ban game into single self-contained HTML file."""
import re
import os

BASE = '/root/vaults/gentech/github/ProtoJay4789.github.io/Games/Meta-Rayban-Fighter'
SRC = os.path.join(BASE, 'src')

# Order matters: files with no deps first, then dependents
JS_FILES = [
    'classes.js',           # CLASSES, CLASS_COLORS, CLASS_ICONS
    'game-constants.js',    # ENEMIES, LEVELS, ACTIONS
    'characters.js',        # CHARACTERS (SVG data)
    'game-state.js',        # PartyMember, GameState (depends on classes, constants)
    'gesture-controller.js',# GestureController
    'touch-controller.js',  # TouchController
    'app.js',               # MetaFighterApp (depends on everything)
]

def strip_import_export(js_content):
    """Remove import and export statements."""
    lines = js_content.split('\n')
    cleaned = []
    for line in lines:
        # Remove export statements
        line = re.sub(r'^export\s+(const|class|let|var|function)\s+', r'\1 ', line)
        line = re.sub(r'^export\s+\{\s*[^}]+\s*\};?', '', line)
        line = re.sub(r'^export\s+default\s+', '', line)
        line = re.sub(r'\s*//# sourceMappingURL=.*', '', line)
        # Skip import lines entirely
        if re.match(r'^\s*import\s+', line):
            continue
        if line.strip():
            cleaned.append(line)
    return '\n'.join(cleaned)

def read_file_content(path):
    with open(path, 'r') as f:
        return f.read()

# Read CSS
css_content = read_file_content(os.path.join(BASE, 'styles.css'))

# Read and bundle JS
js_parts = []
for js_file in JS_FILES:
    filepath = os.path.join(SRC, js_file)
    content = read_file_content(filepath)
    stripped = strip_import_export(content)
    js_parts.append(f'/* === {js_file} === */\n{stripped}')

combined_js = '\n\n'.join(js_parts)

# Read original HTML
html_content = read_file_content(os.path.join(BASE, 'index.html'))

# Build the self-contained HTML
bundled_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Darkest Raybands</title>
  <style>
""" + css_content + """
  </style>
</head>
<body>
  <div id="hud" class="hud-container">
    <div id="effect-container" class="effect-container"></div>
    <div class="game-main">
      <div class="header">
        <div class="level-indicator">Level: <span id="level">1</span></div>
        <div id="turn-indicator" class="turn-indicator player-turn">Your turn</div>
      </div>
      <div class="combat-area-2d">
        <div class="hero-side">
          <div id="hero-slot-1" class="combat-slot hero-slot" data-index="0">
            <div class="slot-character" id="hero-1"></div>
            <div class="slot-hp-bar">
              <div class="slot-hp-fill hero-hp-fill" id="hero-1-hp" style="width: 100%"></div>
            </div>
          </div>
          <div id="hero-slot-2" class="combat-slot hero-slot" data-index="1">
            <div class="slot-character" id="hero-2"></div>
            <div class="slot-hp-bar">
              <div class="slot-hp-fill hero-hp-fill" id="hero-2-hp" style="width: 100%"></div>
            </div>
          </div>
          <div id="hero-slot-3" class="combat-slot hero-slot" data-index="2">
            <div class="slot-character" id="hero-3"></div>
            <div class="slot-hp-bar">
              <div class="slot-hp-fill hero-hp-fill" id="hero-3-hp" style="width: 100%"></div>
            </div>
          </div>
        </div>
        <div class="attack-zone">
          <div id="attacking-character" class="attacking-character hidden"></div>
        </div>
        <div class="enemy-side">
          <div id="enemy-slot" class="combat-slot enemy-slot">
            <div class="slot-character" id="enemy-1"></div>
            <div class="slot-hp-bar">
              <div class="slot-hp-fill enemy-hp-fill" id="enemy-1-hp" style="width: 100%"></div>
            </div>
            <div class="slot-name" id="enemy-name">Skeleton</div>
          </div>
        </div>
      </div>
      <div class="party-panel">
        <div id="party-container" class="party-container"></div>
      </div>
    </div>
    <div class="game-sidebar">
      <div class="sidebar-tabs">
        <button class="tab-btn active" id="abilities-tab">⚔️</button>
        <button class="tab-btn" id="items-tab">🎒</button>
      </div>
      <div class="sidebar-panel active" id="abilities-panel">
        <div class="panel-title">Abilities</div>
        <div id="abilities-container" class="abilities-container"></div>
      </div>
      <div class="sidebar-panel" id="items-panel" style="display: none;">
        <div class="panel-title">Items</div>
        <div id="items-container" class="items-container"></div>
      </div>
      <div class="combat-log" id="combat-log">
        <div class="log-entry">Combat log initialized...</div>
      </div>
    </div>
  </div>
  <div id="game-over" class="overlay hidden" style="display: none;">
    <div class="overlay-content">
      <h1>💀 YOUR PARTY FELL</h1>
      <p>The dungeon claims another soul.</p>
      <button id="restart-btn-over" class="restart-btn">Start Over</button>
    </div>
  </div>
  <div id="game-won" class="overlay hidden" style="display: none;">
    <div class="overlay-content">
      <h1>⚔️ VICTORY!</h1>
      <p>Your party conquers the dungeon!</p>
      <button id="restart-btn-won" class="restart-btn">New Run</button>
    </div>
  </div>
  <script>
""" + combined_js + """
  </script>
</body>
</html>
"""

outpath = os.path.join(BASE, 'index-bundled.html')
with open(outpath, 'w') as f:
    f.write(bundled_html)

js_size = len(combined_js)
css_size = len(css_content)
html_size = len(bundled_html)
print(f"✅ Bundle complete!")
print(f"   CSS: {css_size} chars")
print(f"   JS:  {js_size} chars")
print(f"   Total: {html_size} chars (~{html_size // 1024}KB)")
print(f"   Output: {outpath}")
