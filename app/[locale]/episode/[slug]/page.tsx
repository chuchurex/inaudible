import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  getEpisodeBySlug,
  getTranscript,
  getTranscriptMarkdown,
  hasEditedTranscript,
} from "@/lib/episodes";
import TranscriptViewer from "@/components/TranscriptViewer";

export default async function EpisodePage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const episode = getEpisodeBySlug(slug);
  if (!episode) notFound();

  const segments = episode.number
    ? getTranscript(episode.number, locale)
    : null;
  const markdown =
    !segments && episode.number
      ? getTranscriptMarkdown(episode.number, locale)
      : null;

  const editedTranscriptAvailable =
    episode.number ? hasEditedTranscript(episode.number, locale) : false;

  const label =
    episode.type === "episode"
      ? `Episode ${episode.number}`
      : episode.type === "bonus"
        ? "Bonus"
        : "Meta";

  return (
    <div>
      <EpisodeNav locale={locale} />

      <div className="mb-6">
        <div className="mb-1 text-sm text-zinc-500">{label}</div>
        <h1 className="text-3xl font-bold tracking-tight">{episode.title}</h1>
        {episode.description && (
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            {episode.description}
          </p>
        )}
        {episode.categories && episode.categories.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {episode.categories.map((cat) => (
              <span
                key={cat}
                className="rounded-full bg-zinc-100 px-2.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
              >
                {cat}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mb-8 aspect-video w-full overflow-hidden rounded-lg">
        <iframe
          src={`https://www.youtube.com/embed/${episode.youtubeId}`}
          title={episode.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="h-full w-full"
        />
      </div>

      <div className="mb-4 flex items-center justify-between">
        <TranscriptHeading />
        <div className="flex items-center gap-4">
          {editedTranscriptAvailable && (
            <a
              href={`/api/transcript?episode=${episode.number}&locale=${locale}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-amber-600 hover:text-amber-500 dark:text-amber-400 dark:hover:text-amber-300"
            >
              <EditedTranscriptLink />
            </a>
          )}
          <a
            href={`https://www.youtube.com/watch?v=${episode.youtubeId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
          >
            <WatchOnYoutube />
          </a>
        </div>
      </div>

      {segments ? (
        <TranscriptViewer
          segments={segments}
          youtubeId={episode.youtubeId}
        />
      ) : markdown ? (
        <div className="prose prose-zinc max-w-none dark:prose-invert">
          <pre className="whitespace-pre-wrap text-sm leading-relaxed">
            {markdown}
          </pre>
        </div>
      ) : (
        <NoTranscript />
      )}
    </div>
  );
}

function EpisodeNav({ locale }: { locale: string }) {
  const t = useTranslations("episode");
  return (
    <Link
      href={`/${locale}`}
      className="mb-6 inline-block text-sm text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
    >
      &larr; {t("backToEpisodes")}
    </Link>
  );
}

function TranscriptHeading() {
  const t = useTranslations("episode");
  return <h2 className="text-xl font-semibold">{t("transcript")}</h2>;
}

function WatchOnYoutube() {
  const t = useTranslations("episode");
  return <>{t("watchOnYoutube")}</>;
}

function EditedTranscriptLink() {
  const t = useTranslations("episode");
  return <>{t("readEditedTranscript")}</>;
}

function NoTranscript() {
  const t = useTranslations("episode");
  return (
    <p className="text-zinc-500 dark:text-zinc-400">{t("noTranscript")}</p>
  );
}
