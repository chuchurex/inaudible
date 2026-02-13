import Link from "next/link";
import type { Episode } from "@/lib/types";

export default function EpisodeCard({
  episode,
  locale,
}: {
  episode: Episode;
  locale: string;
}) {
  const label =
    episode.type === "episode"
      ? `Episode ${episode.number}`
      : episode.type === "bonus"
        ? "Bonus"
        : "Meta";

  return (
    <Link
      href={`/${locale}/episode/${episode.slug}`}
      className="block rounded-lg border border-zinc-200 p-5 transition-colors hover:border-zinc-400 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-600 dark:hover:bg-zinc-900"
    >
      <div className="mb-1 text-sm text-zinc-500 dark:text-zinc-400">
        {label} &middot; {episode.duration}
      </div>
      <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        {episode.title}
      </h2>
      {episode.description && (
        <p className="mt-2 line-clamp-2 text-sm text-zinc-600 dark:text-zinc-400">
          {episode.description}
        </p>
      )}
      {episode.categories && episode.categories.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {episode.categories.slice(0, 5).map((cat) => (
            <span
              key={cat}
              className="rounded-full bg-zinc-100 px-2.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
            >
              {cat}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}
