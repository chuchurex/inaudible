#!/usr/bin/env python3
"""
Translates an English transcript to Spanish using Claude API.
Processes in chunks to handle long episodes.

Usage:
    python scripts/translate.py <episode_number> [--target es]

Example:
    python scripts/translate.py 66
    python scripts/translate.py 66 --target es

Requires ANTHROPIC_API_KEY in .env.local or environment.
"""

import json
import os
import sys

import anthropic


def load_env():
    """Load .env.local if ANTHROPIC_API_KEY not in environment."""
    if "ANTHROPIC_API_KEY" in os.environ:
        return
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".env.local",
    )
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def chunk_segments(segments: list[dict], max_segments: int = 50) -> list[list[dict]]:
    """Split transcript into chunks for translation."""
    chunks = []
    for i in range(0, len(segments), max_segments):
        chunks.append(segments[i : i + max_segments])
    return chunks


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def translate_chunk(
    client: anthropic.Anthropic,
    segments: list[dict],
    target_lang: str,
    episode_context: str,
) -> list[dict]:
    """Translate a chunk of transcript segments."""
    text_block = ""
    for seg in segments:
        text_block += f"[{format_time(seg['start'])}] {seg['text']}\n"

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        system=(
            f"You are a professional translator specializing in spiritual and philosophical content. "
            f"You are translating a podcast transcript about the Law of One and Confederation philosophy. "
            f"Context: {episode_context}\n\n"
            f"Rules:\n"
            f"- Translate from English to {target_lang}\n"
            f"- Preserve the conversational tone\n"
            f"- Keep proper nouns (Ra, Confederation, Law of One) as-is\n"
            f"- Keep technical spiritual terms with their common Spanish equivalents\n"
            f"- Preserve the timestamp markers exactly as [HH:MM:SS] or [M:SS]\n"
            f"- Return ONLY the translated text with timestamps, no explanations\n"
            f"- Each line must start with the timestamp in brackets"
        ),
        messages=[
            {
                "role": "user",
                "content": f"Translate this transcript segment:\n\n{text_block}",
            }
        ],
    )

    translated_text = response.content[0].text
    translated_segments = []

    for seg, line in zip(segments, translated_text.strip().split("\n")):
        # Extract text after timestamp
        text = line
        if "]" in line:
            text = line.split("]", 1)[1].strip()
        translated_segments.append(
            {"start": seg["start"], "duration": seg["duration"], "text": text}
        )

    return translated_segments


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate.py <episode_number> [--target es]")
        sys.exit(1)

    episode_num = sys.argv[1]
    target_lang = "es"

    # Parse --target flag
    if "--target" in sys.argv:
        idx = sys.argv.index("--target")
        if idx + 1 < len(sys.argv):
            target_lang = sys.argv[idx + 1]

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    episode_dir = os.path.join(project_root, "content", "episodes", episode_num)

    # Load source transcript
    source_path = os.path.join(episode_dir, "transcript.en.json")
    if not os.path.exists(source_path):
        print(f"Error: No English transcript found at {source_path}")
        print("Run fetch-transcript.py first.")
        sys.exit(1)

    with open(source_path) as f:
        segments = json.load(f)

    # Load episode metadata for context
    meta_path = os.path.join(episode_dir, "meta.json")
    episode_context = f"Episode {episode_num}"
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        episode_context = f"Episode {meta.get('number', episode_num)}: {meta.get('title', '')}"
        if meta.get("description"):
            episode_context += f" - {meta['description']}"

    load_env()

    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY not found.")
        print("Set it in .env.local or as an environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic()

    print(f"Translating Episode {episode_num} to {target_lang}")
    print(f"  Source: {len(segments)} segments")

    chunks = chunk_segments(segments, max_segments=50)
    print(f"  Processing {len(chunks)} chunks...")

    all_translated = []
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i + 1}/{len(chunks)} ({len(chunk)} segments)...", end=" ", flush=True)
        translated = translate_chunk(client, chunk, target_lang, episode_context)
        all_translated.extend(translated)
        print("done")

    # Save JSON
    json_path = os.path.join(episode_dir, f"transcript.{target_lang}.json")
    with open(json_path, "w") as f:
        json.dump(all_translated, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON: {json_path}")

    # Save Markdown
    md_path = os.path.join(episode_dir, f"transcript.{target_lang}.md")
    lines = []
    for seg in all_translated:
        timestamp = format_time(seg["start"])
        lines.append(f"**[{timestamp}]** {seg['text']}\n")
    with open(md_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Saved Markdown: {md_path}")

    print("Done!")


if __name__ == "__main__":
    main()
