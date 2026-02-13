"use client";

import { useState } from "react";
import type { TranscriptSegment } from "@/lib/types";

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function TranscriptViewer({
  segments,
  youtubeId,
}: {
  segments: TranscriptSegment[];
  youtubeId: string;
}) {
  const [search, setSearch] = useState("");

  const filtered = search
    ? segments.filter((s) =>
        s.text.toLowerCase().includes(search.toLowerCase())
      )
    : segments;

  return (
    <div>
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search transcript..."
        className="mb-4 w-full rounded-lg border border-zinc-300 px-4 py-2 text-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
      />
      <div className="space-y-1">
        {filtered.map((segment, i) => (
          <div key={i} className="group flex gap-3 rounded px-2 py-1 hover:bg-zinc-50 dark:hover:bg-zinc-900">
            <a
              href={`https://www.youtube.com/watch?v=${youtubeId}&t=${Math.floor(segment.start)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 pt-0.5 font-mono text-xs text-zinc-400 hover:text-zinc-600 dark:text-zinc-500 dark:hover:text-zinc-300"
            >
              {formatTime(segment.start)}
            </a>
            <p className="text-sm text-zinc-700 dark:text-zinc-300">
              {segment.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
