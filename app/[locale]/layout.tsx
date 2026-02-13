import type { ReactNode } from "react";
import { NextIntlClientProvider, useMessages } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { Geist, Geist_Mono } from "next/font/google";
import { routing } from "@/i18n/routing";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import Link from "next/link";
import "../globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages({ locale });
  const site = messages.site as Record<string, string>;
  return {
    title: site.title,
    description: site.description,
  };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-background font-sans text-foreground antialiased`}
      >
        <NextIntlClientProvider messages={messages}>
          <header className="border-b border-zinc-200 dark:border-zinc-800">
            <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
              <Link
                href={`/${locale}`}
                className="text-lg font-semibold tracking-tight"
              >
                (inaudible)
              </Link>
              <LanguageSwitcher />
            </div>
          </header>
          <main className="mx-auto max-w-4xl px-6 py-8">{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
