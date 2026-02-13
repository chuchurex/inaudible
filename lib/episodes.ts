import fs from "fs";
import path from "path";
import type { Episode, TranscriptSegment } from "./types";

const CONTENT_DIR = path.join(process.cwd(), "content", "episodes");

export function getAllEpisodes(): Episode[] {
  const dirs = fs.readdirSync(CONTENT_DIR).filter((d) => {
    return fs.statSync(path.join(CONTENT_DIR, d)).isDirectory();
  });

  const episodes: Episode[] = [];
  for (const dir of dirs) {
    const metaPath = path.join(CONTENT_DIR, dir, "meta.json");
    if (fs.existsSync(metaPath)) {
      const meta = JSON.parse(fs.readFileSync(metaPath, "utf-8"));
      episodes.push(meta);
    }
  }

  return episodes.sort((a, b) => (b.number ?? 0) - (a.number ?? 0));
}

export function getEpisodeBySlug(slug: string): Episode | null {
  const episodes = getAllEpisodes();
  return episodes.find((e) => e.slug === slug) ?? null;
}

export function getTranscript(
  episodeNumber: number,
  locale: string
): TranscriptSegment[] | null {
  const transcriptPath = path.join(
    CONTENT_DIR,
    String(episodeNumber),
    `transcript.${locale}.json`
  );

  if (!fs.existsSync(transcriptPath)) return null;

  return JSON.parse(fs.readFileSync(transcriptPath, "utf-8"));
}

export function getTranscriptMarkdown(
  episodeNumber: number,
  locale: string
): string | null {
  const mdPath = path.join(
    CONTENT_DIR,
    String(episodeNumber),
    `transcript.${locale}.md`
  );

  if (!fs.existsSync(mdPath)) return null;

  return fs.readFileSync(mdPath, "utf-8");
}

export function hasEditedTranscript(
  episodeNumber: number,
  locale: string
): boolean {
  const htmlPath = path.join(
    CONTENT_DIR,
    String(episodeNumber),
    `transcript.${locale}.html`
  );
  return fs.existsSync(htmlPath);
}

export function getEditedTranscriptHtml(
  episodeNumber: number,
  locale: string
): string | null {
  const htmlPath = path.join(
    CONTENT_DIR,
    String(episodeNumber),
    `transcript.${locale}.html`
  );
  if (!fs.existsSync(htmlPath)) return null;
  return fs.readFileSync(htmlPath, "utf-8");
}
