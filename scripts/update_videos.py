#!/usr/bin/env python3
"""
update_videos.py
────────────────
Reads the YouTube RSS feed for the Boreal Times channel,
extracts the latest 10 videos, and rewrites the videoData
block inside index.html automatically.

HOW TO GET YOUR CHANNEL ID:
  1. Go to https://www.youtube.com/@borealtimesPT
  2. Right-click → View Page Source
  3. Ctrl+F → search for "channel/"
  4. Copy the ID that starts with UC (e.g. UCxxxxxxxxxxxxxxxxxxxxxxxxx)
  5. Paste it in CHANNEL_ID below.
"""

import renimport os
import sys
import xml.etree.ElementTree as ET
import renimport osquests
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURE THIS — replace with your real Channel ID (starts with UC...)
# Get it at: youtube.com/@borealtimes → View Page Source → search "channel/"
# ─────────────────────────────────────────────────────────────────────────────
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UCiXYKVWDEwjULv6QpPj2dZA")

RSS_URL    = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
INDEX_FILE = "index.html"
MAX_VIDEOS = 10

# Category mapping — edit to match your content
CATEGORY_MAP = {
    "quantum":      "Technology",
    "polylaminin":  "Science",
    "spacex":       "Space Tech",
    "moon":         "Space Tech",
    "glacier":      "Environment",
    "ice":          "Environment",
    "starlink":     "Telecom",
    "laser":        "Defense",
    "railgun":      "Defense",
    "navy":         "Defense",
    "tesla":        "EV Tech",
    "huawei":       "Technology",
    "harmonyos":    "Technology",
    "agi":          "AI Research",
    "intelligence": "AI Research",
    "battery":      "EV Tech",
    "autonomy":     "Autonomy",
    "economy":      "Economy",
    "regulation":   "Regulation",
}

def guess_category(title: str) -> str:
    """Guess category from video title keywords."""
    t = title.lower()
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in t:
            return cat
    return "Technology"

def format_date(iso_date: str) -> str:
    """Convert ISO 8601 date to 'April 14, 2026' format."""
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%B %-d, %Y")
    except Exception:
        return iso_date[:10]

def fetch_videos() -> list[dict]:
    """Fetch and parse the YouTube RSS feed."""
    print(f"Fetching RSS: {RSS_URL}")
    resp = requests.get(RSS_URL, timeout=15)
    resp.raise_for_status()

    ns = {
        "atom":  "http://www.w3.org/2005/Atom",
        "media": "http://search.yahoo.com/mrss/",
        "yt":    "http://www.youtube.com/xml/schemas/2015",
    }

    root = ET.fromstring(resp.text)
    videos = []

    for entry in root.findall("atom:entry", ns)[:MAX_VIDEOS]:
        video_id_el = entry.find("yt:videoId", ns)
        title_el    = entry.find("atom:title", ns)
        published_el= entry.find("atom:published", ns)
        desc_el     = entry.find(".//media:description", ns)

        if video_id_el is None or title_el is None:
            continue

        title    = title_el.text or "Untitled"
        video_id = video_id_el.text
        date     = format_date(published_el.text) if published_el is not None else ""
        desc     = (desc_el.text or "")[:200].replace("\n", " ").strip()
        category = guess_category(title)

        videos.append({
            "title":    title,
            "category": category,
            "date":     date,
            "desc":     desc,
            "videoId":  video_id,
        })

    print(f"Found {len(videos)} videos.")
    return videos

def escape_js(s: str) -> str:
    """Escape a string for use inside a JS template literal or quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

def build_video_data_js(videos: list[dict]) -> str:
    """Build the full videoData JS block as a formatted string."""
    keys = ["featured", "side1", "side2", "side3",
            "v1", "v2", "v3", "v4", "v5", "v6"]

    lines = ["        // ==================== VIDEO DATA ===================="]
    lines.append("        // ── Auto-updated by GitHub Actions from YouTube RSS ──────────────────")
    lines.append(f"        // ── Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ──")
    lines.append("        const videoData = {")

    for i, video in enumerate(videos):
        key = keys[i] if i < len(keys) else f"v{i}"
        comma = "," if i < len(videos) - 1 else ""
        lines.append(f'            {key}: {{')
        lines.append(f'                title:    "{escape_js(video["title"])}",')
        lines.append(f'                category: "{escape_js(video["category"])}",')
        lines.append(f'                date:     "{escape_js(video["date"])}",')
        lines.append(f'                desc:     "{escape_js(video["desc"])}",')
        lines.append(f'                videoId:  "{escape_js(video["videoId"])}"')
        lines.append(f'            }}{comma}')

    lines.append("        };")
    return "\n".join(lines)

def patch_index(new_video_data_js: str) -> bool:
    """Replace the videoData block in index.html with the new one."""
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Match from the VIDEO DATA comment to the closing "};" of videoData
    pattern = re.compile(
        r"        // ={10,} VIDEO DATA ={10,}.*?        \};",
        re.DOTALL
    )

    if not pattern.search(content):
        print("ERROR: Could not find videoData block in index.html.")
        print("Make sure index.html contains a line like:")
        print("  // ==================== VIDEO DATA ====================")
        return False

    new_content = pattern.sub(new_video_data_js, content)

    if new_content == content:
        print("No changes needed — videoData is already up to date.")
        return False

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("index.html updated successfully.")
    return True

def main():
    if CHANNEL_ID == "UCiXYKVWDEwjULv6QpPj2dZA":
        print("ERROR: Please set your YouTube CHANNEL_ID in scripts/update_videos.py")
        print("Get it at: youtube.com/@borealtimesPT → View Page Source → search 'channel/'")
        sys.exit(1)

    videos = fetch_videos()
    if not videos:
        print("No videos found — aborting.")
        sys.exit(1)

    new_js = build_video_data_js(videos)
    patch_index(new_js)

if __name__ == "__main__":
    main()
