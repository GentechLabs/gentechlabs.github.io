#!/usr/bin/env python3
"""
X Morning Briefing — pulls timeline + bookmarks, summarizes for delivery.
Used by Hermes cron to generate daily social digest.
"""
import subprocess
import json
import sys
from datetime import datetime, timezone

def xurl(cmd: str) -> dict:
    """Run xurl command and return parsed JSON."""
    result = subprocess.run(
        f"xurl {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def extract_posts(data: list, source: str) -> list:
    """Normalize posts from xurl response."""
    posts = []
    for item in data:
        post = {
            "source": source,
            "id": item.get("id", ""),
            "author": item.get("author_id", item.get("user", {}).get("username", "unknown")),
            "text": item.get("text", "")[:280],
            "created": item.get("created_at", ""),
            "likes": item.get("public_metrics", {}).get("like_count", 0),
            "reposts": item.get("public_metrics", {}).get("retweet_count", 0),
        }
        posts.append(post)
    return posts

def run_briefing():
    """Main briefing pipeline."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    output = [f"📰 X Morning Briefing — {now}\n"]

    # 1. Home timeline (last 20 posts)
    timeline = xurl("timeline -n 20")
    timeline_posts = []
    if "data" in timeline:
        timeline_posts = extract_posts(timeline["data"], "timeline")
        output.append(f"🕐 Timeline: {len(timeline_posts)} recent posts")
    elif "error" in timeline:
        output.append(f"⚠️ Timeline error: {timeline['error']}")

    # 2. Bookmarks (last 10)
    bookmarks = xurl("bookmarks -n 10")
    bookmark_posts = []
    if "data" in bookmarks:
        bookmark_posts = extract_posts(bookmarks["data"], "bookmark")
        output.append(f"🔖 Bookmarks: {len(bookmark_posts)} saved")
    elif "error" in bookmarks:
        output.append(f"⚠️ Bookmarks error: {bookmarks['error']}")

    # 3. Mentions (last 10)
    mentions = xurl("mentions -n 10")
    mention_posts = []
    if "data" in mentions:
        mention_posts = extract_posts(mentions["data"], "mention")
        output.append(f"💬 Mentions: {len(mention_posts)} new")
    elif "error" in mentions:
        output.append(f"⚠️ Mentions error: {mentions['error']}")

    # Build summary
    all_posts = timeline_posts + bookmark_posts + mention_posts

    if not all_posts:
        output.append("\n✅ No new activity to report.")
    else:
        output.append(f"\n📊 Total: {len(all_posts)} posts across sources")
        output.append("\n--- Raw data below for agent processing ---")
        output.append(json.dumps(all_posts, indent=2))

    return "\n".join(output)

if __name__ == "__main__":
    print(run_briefing())
