#!/usr/bin/env python3
"""
Extracts YouTube video transcript and saves it in JSON + Markdown formats.

Usage:
    python scripts/fetch-transcript.py <youtube_id> <episode_number>

Example:
    python scripts/fetch-transcript.py _ceg7Vi8lqs 66
"""

import json
import os
import subprocess
import sys

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_with_api(video_id: str) -> list[dict] | None:
    """Try youtube-transcript-api first (preferred)."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=["en"])
        segments = []
        for entry in transcript:
            segments.append({
                "start": round(entry.start, 2),
                "duration": round(entry.duration, 2),
                "text": entry.text.strip(),
            })
        return segments
    except Exception as e:
        print(f"  youtube-transcript-api failed: {e}")
        return None


def fetch_with_ytdlp(video_id: str) -> list[dict] | None:
    """Fallback: use yt-dlp to download subtitles."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        tmp_dir = "/tmp/inaudible-subs"
        os.makedirs(tmp_dir, exist_ok=True)

        result = subprocess.run(
            [
                "yt-dlp",
                "--write-auto-sub",
                "--sub-lang", "en",
                "--sub-format", "json3",
                "--skip-download",
                "-o", f"{tmp_dir}/{video_id}",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        sub_file = f"{tmp_dir}/{video_id}.en.json3"
        if not os.path.exists(sub_file):
            print(f"  yt-dlp: subtitle file not found at {sub_file}")
            print(f"  stdout: {result.stdout[-200:]}")
            print(f"  stderr: {result.stderr[-200:]}")
            return None

        with open(sub_file) as f:
            data = json.load(f)

        segments = []
        for event in data.get("events", []):
            if "segs" not in event:
                continue
            text = "".join(s.get("utf8", "") for s in event["segs"]).strip()
            if not text or text == "\n":
                continue
            start_ms = event.get("tStartMs", 0)
            dur_ms = event.get("dDurationMs", 0)
            segments.append({
                "start": round(start_ms / 1000, 2),
                "duration": round(dur_ms / 1000, 2),
                "text": text,
            })

        os.remove(sub_file)
        return segments if segments else None

    except Exception as e:
        print(f"  yt-dlp failed: {e}")
        return None


def merge_into_paragraphs(segments: list[dict], target_duration: float = 30.0, pause_threshold: float = 1.5) -> list[dict]:
    """Merge segments into paragraph-sized chunks for readability.

    Groups segments until either:
    - target_duration seconds of speech have accumulated, OR
    - a natural pause (gap > pause_threshold) is detected after min 10s
    """
    if not segments:
        return segments

    merged = []
    current = dict(segments[0])

    for seg in segments[1:]:
        current_end = current["start"] + current["duration"]
        gap = seg["start"] - current_end
        current_len = current["duration"]

        # Break on long pause after reasonable content, or when target duration reached
        should_break = (
            (gap > pause_threshold and current_len >= 10.0) or
            current_len >= target_duration
        )

        if should_break:
            merged.append(current)
            current = dict(seg)
        else:
            current["text"] += " " + seg["text"]
            current["duration"] = (seg["start"] + seg["duration"]) - current["start"]

    merged.append(current)
    return merged


def save_transcript(segments: list[dict], episode_dir: str):
    """Save as both JSON (for structured viewer) and Markdown (for reading)."""
    # JSON format for TranscriptViewer component
    json_path = os.path.join(episode_dir, "transcript.en.json")
    with open(json_path, "w") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON: {json_path} ({len(segments)} segments)")

    # Markdown format for human reading
    md_path = os.path.join(episode_dir, "transcript.en.md")
    lines = []
    for seg in segments:
        timestamp = format_time(seg["start"])
        lines.append(f"**[{timestamp}]** {seg['text']}\n")
    with open(md_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Saved Markdown: {md_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch-transcript.py <youtube_id> <episode_number>")
        sys.exit(1)

    video_id = sys.argv[1]
    episode_num = sys.argv[2]
    episode_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "content",
        "episodes",
        episode_num,
    )
    os.makedirs(episode_dir, exist_ok=True)

    print(f"Fetching transcript for Episode {episode_num} (YouTube: {video_id})")

    # Try API first
    print("  Trying youtube-transcript-api...")
    segments = fetch_with_api(video_id)

    # Fallback to yt-dlp
    if not segments:
        print("  Trying yt-dlp fallback...")
        segments = fetch_with_ytdlp(video_id)

    if not segments:
        print("  ERROR: Could not fetch transcript from any source.")
        sys.exit(1)

    print(f"  Raw segments: {len(segments)}")

    # Merge into readable paragraphs
    segments = merge_into_paragraphs(segments)
    print(f"  After merging: {len(segments)} segments")

    # Calculate total duration
    if segments:
        last = segments[-1]
        total_secs = last["start"] + last["duration"]
        print(f"  Total duration: {format_time(total_secs)}")

    save_transcript(segments, episode_dir)
    print("Done!")


if __name__ == "__main__":
    main()
