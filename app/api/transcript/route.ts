import { NextRequest, NextResponse } from "next/server";
import { getEditedTranscriptHtml } from "@/lib/episodes";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const episode = Number(searchParams.get("episode"));
  const locale = searchParams.get("locale") ?? "es";

  if (!episode || isNaN(episode)) {
    return NextResponse.json({ error: "Missing episode" }, { status: 400 });
  }

  const html = getEditedTranscriptHtml(episode, locale);
  if (!html) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return new NextResponse(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}
