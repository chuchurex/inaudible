import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { getAllEpisodes } from "@/lib/episodes";
import EpisodeCard from "@/components/EpisodeCard";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const episodes = getAllEpisodes();

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">
          <HomeHeading />
        </h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">
          <HomeSubtitle />
        </p>
      </div>
      <div className="space-y-4">
        {episodes.map((episode) => (
          <EpisodeCard
            key={episode.slug}
            episode={episode}
            locale={locale}
          />
        ))}
      </div>
    </div>
  );
}

function HomeHeading() {
  const t = useTranslations("home");
  return <>{t("heading")}</>;
}

function HomeSubtitle() {
  const t = useTranslations("home");
  return <>{t("subtitle")}</>;
}
