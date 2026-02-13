import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  getAllEpisodes,
  getEpisodeBySlug,
  getEditedTranscriptHtml,
} from "@/lib/episodes";

export function generateStaticParams() {
  const episodes = getAllEpisodes();
  return episodes.map((ep) => ({ slug: ep.slug }));
}

export default async function EditedTranscriptPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const episode = getEpisodeBySlug(slug);
  if (!episode) notFound();

  const html = episode.number
    ? getEditedTranscriptHtml(episode.number, locale)
    : null;
  if (!html) notFound();

  return (
    <div>
      <BackLink locale={locale} slug={slug} />
      <h1 className="mb-6 text-2xl font-bold tracking-tight">
        {episode.title}
      </h1>
      <div
        className="prose prose-zinc max-w-none dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}

function BackLink({ locale, slug }: { locale: string; slug: string }) {
  const t = useTranslations("episode");
  return (
    <Link
      href={`/${locale}/episode/${slug}/`}
      className="mb-6 inline-block text-sm text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
    >
      &larr; {t("backToEpisodes")}
    </Link>
  );
}
