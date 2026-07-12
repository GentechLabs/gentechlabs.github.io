#!/usr/bin/env python3
"""
X Feed Monitor — searches for keywords, flags relevant posts.
Designed for cron runs every 2h. Tracks seen post IDs to avoid duplicates.
"""
import subprocess
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SEEN_FILE = os.path.expanduser("~/.hermes/data/x-seen-posts.json")
KEYWORDS = [
    "x402",
    "GenLayer",
    "ARC hackathon",
    "AI agents",
    "multi-agent",
    "Hermes agent",
    "Solana hackathon",
    "Base chain",
    "HTTP 402",
]

def load_seen() -> set:
    """Load previously seen post IDs."""
    try:
        with open(SEEN_FILE, "r") as f:
            data = json.load(f)
            # Only keep last 500 IDs to prevent unbounded growth
            return set(data.get("seen_ids", [])[-500:])
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_seen(seen: set):
    """Save seen post IDs."""
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump({"seen_ids": list(seen)[-500:], "updated": datetime.now(timezone.utc).isoformat()}, f)

def xurl_search(query: str, count: int = 5) -> list:
    """Search X for a query, return posts."""
    safe_query = query.replace('"', '\\"')
    cmd = f'xurl search "{safe_query}" -n {count}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("data", [])
    except json.JSONDecodeError:
        return []

def run_monitor():
    """Main monitoring pipeline."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    seen = load_seen()
    new_posts = []

    for keyword in KEYWORDS:
        posts = xurl_search(keyword, count=5)
        for post in posts:
            post_id = post.get("id", "")
            if post_id and post_id not in seen:
                seen.add(post_id)
                new_posts.append({
                    "keyword": keyword,
                    "id": post_id,
                    "text": post.get("text", "")[:200],
                    "author_id": post.get("author_id", "unknown"),
                    "created": post.get("created_at", ""),
                    "url": f"https://x.com/i/status/{post_id}",
                })

    save_seen(seen)

    # Build output
    output = [f"🔍 X Feed Monitor — {now}\n"]

    if not new_posts:
        output.append("✅ No new keyword matches.")
    else:
        output.append(f"📢 {len(new_posts)} new posts found:\n")
        for post in new_posts:
            output.append(f"🏷️ **{post['keyword']}**")
            output.append(f"   {post['text'][:150]}...")
            output.append(f"   🔗 {post['url']}\n")

    return "\n".join(output)

if __name__ == "__main__":
    print(run_monitor())
