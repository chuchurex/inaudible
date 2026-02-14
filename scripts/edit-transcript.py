#!/usr/bin/env python3
"""
Generates an edited HTML transcript from a raw transcript JSON.
Cleans up speech repetitions, filler words, and structures the
conversation into themed sections with speaker identification.

Uses the Claude API to process the transcript in chunks.

Usage:
    python scripts/edit-transcript.py <episode_number> [--lang es] [--reference 66]

Example:
    python scripts/edit-transcript.py 65
    python scripts/edit-transcript.py 65 --lang es
    python scripts/edit-transcript.py 65 --lang es --reference 66

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


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def chunk_segments(segments: list[dict], max_segments: int = 40) -> list[list[dict]]:
    """Split transcript into chunks for processing."""
    chunks = []
    for i in range(0, len(segments), max_segments):
        chunks.append(segments[i : i + max_segments])
    return chunks


def load_reference_html(episode_num: str, lang: str, project_root: str) -> str | None:
    """Load a reference edited HTML to use as style guide."""
    ref_path = os.path.join(
        project_root, "content", "episodes", episode_num, f"transcript.{lang}.html"
    )
    if os.path.exists(ref_path):
        with open(ref_path) as f:
            return f.read()
    return None


def edit_transcript(
    client: anthropic.Anthropic,
    segments: list[dict],
    meta: dict,
    lang: str,
    reference_html: str | None,
    chunk_index: int,
    total_chunks: int,
    previous_sections: str,
) -> str:
    """Process a chunk of transcript into edited HTML sections."""
    text_block = ""
    for seg in segments:
        text_block += f"[{format_time(seg['start'])}] {seg['text']}\n"

    lang_names = {"es": "Spanish", "en": "English"}
    lang_name = lang_names.get(lang, lang)

    reference_instruction = ""
    if reference_html:
        # Only include CSS/structure reference on first chunk
        if chunk_index == 0:
            reference_instruction = (
                f"\n\nHere is a COMPLETE reference HTML from another episode. "
                f"Match this EXACT style, CSS, and HTML structure:\n\n"
                f"```html\n{reference_html}\n```\n"
            )
        else:
            reference_instruction = (
                f"\n\nContinue using the same HTML structure (sections, dialogue divs, "
                f"speaker classes, blockquotes) as the previous chunks."
            )

    context_instruction = ""
    if previous_sections:
        context_instruction = (
            f"\n\nHere are the section titles already generated in previous chunks "
            f"(do NOT repeat these, create new section titles):\n{previous_sections}"
        )

    if chunk_index == 0:
        structure_instruction = (
            "Generate a COMPLETE HTML document starting with <!DOCTYPE html>, "
            "including all CSS styles, the <header> section, and the first content sections. "
            "Do NOT close the </body> or </html> tags — more content will follow."
        )
    elif chunk_index == total_chunks - 1:
        structure_instruction = (
            "Generate ONLY the <section> HTML elements for this chunk's content. "
            "Do NOT include <!DOCTYPE>, <head>, <style>, or <header>. "
            "After the last section, add the closing <footer>, </body>, and </html> tags."
        )
    else:
        structure_instruction = (
            "Generate ONLY the <section> HTML elements for this chunk's content. "
            "Do NOT include <!DOCTYPE>, <head>, <style>, or <header>."
        )

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=16000,
        system=(
            f"You are an expert transcript editor for a podcast about the Law of One "
            f"and Confederation philosophy. Your task is to create a clean, readable "
            f"edited HTML transcript in {lang_name}.\n\n"
            f"Episode: {meta.get('title', '')} (Episode {meta.get('number', '')})\n"
            f"Description: {meta.get('description', '')}\n"
            f"Duration: {meta.get('duration', '')}\n\n"
            f"EDITING RULES:\n"
            f"- Remove speech repetitions, filler words, false starts, and verbal tics\n"
            f"- Clean up grammar while preserving the speaker's voice and meaning\n"
            f"- Identify speakers by name (look for self-introductions or context clues)\n"
            f"- Group related dialogue into thematic sections with descriptive <h2> titles\n"
            f"- Use <blockquote> for channeled/quoted material with <span class='source'> attribution\n"
            f"- Use CSS classes: 'speaker jeremy', 'speaker jamie', 'speaker nithin', 'speaker ryan' etc.\n"
            f"- Keep the conversational tone natural but readable\n"
            f"- Preserve important spiritual/philosophical concepts accurately\n"
            f"- Keep proper nouns as-is (Ra, Confederation, Law of One, etc.)\n"
            f"- Return ONLY valid HTML, no markdown or explanations\n\n"
            f"{structure_instruction}"
            f"{reference_instruction}"
            f"{context_instruction}"
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Edit and structure this transcript chunk "
                    f"({chunk_index + 1}/{total_chunks}):\n\n{text_block}"
                ),
            }
        ],
    )

    return response.content[0].text


def extract_section_titles(html: str) -> str:
    """Extract h2 section titles from HTML for context."""
    titles = []
    for line in html.split("\n"):
        if "<h2>" in line and "</h2>" in line:
            start = line.index("<h2>") + 4
            end = line.index("</h2>")
            titles.append(f"- {line[start:end]}")
    return "\n".join(titles)


def main():
    if len(sys.argv) < 2:
        print("Usage: python edit-transcript.py <episode_number> [--lang es] [--reference 66]")
        sys.exit(1)

    episode_num = sys.argv[1]
    lang = "es"
    reference_ep = "66"

    # Parse flags
    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            lang = sys.argv[idx + 1]

    if "--reference" in sys.argv:
        idx = sys.argv.index("--reference")
        if idx + 1 < len(sys.argv):
            reference_ep = sys.argv[idx + 1]

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    episode_dir = os.path.join(project_root, "content", "episodes", episode_num)

    # Load source transcript
    source_path = os.path.join(episode_dir, f"transcript.{lang}.json")
    if not os.path.exists(source_path):
        print(f"Error: No {lang} transcript found at {source_path}")
        sys.exit(1)

    with open(source_path) as f:
        segments = json.load(f)

    # Load episode metadata
    meta_path = os.path.join(episode_dir, "meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)

    # Load reference HTML
    reference_html = load_reference_html(reference_ep, lang, project_root)
    if reference_html:
        print(f"  Using episode {reference_ep} as style reference")
    else:
        print(f"  No reference HTML found for episode {reference_ep}, using defaults")

    load_env()

    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY not found.")
        print("Set it in .env.local or as an environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic()

    print(f"Editing Episode {episode_num} transcript ({lang})")
    print(f"  Source: {len(segments)} segments")

    chunks = chunk_segments(segments, max_segments=40)
    print(f"  Processing {len(chunks)} chunks...")

    all_html_parts = []
    previous_sections = ""

    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i + 1}/{len(chunks)} ({len(chunk)} segments)...", end=" ", flush=True)
        html_part = edit_transcript(
            client,
            chunk,
            meta,
            lang,
            reference_html,
            chunk_index=i,
            total_chunks=len(chunks),
            previous_sections=previous_sections,
        )
        all_html_parts.append(html_part)
        previous_sections += extract_section_titles(html_part) + "\n"
        print("done")

    # Combine all parts
    full_html = "\n\n".join(all_html_parts)

    # Save
    output_path = os.path.join(episode_dir, f"transcript.{lang}.html")
    with open(output_path, "w") as f:
        f.write(full_html)
    print(f"  Saved: {output_path}")
    print("Done!")


if __name__ == "__main__":
    main()
