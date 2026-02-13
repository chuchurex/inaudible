export interface Episode {
  number: number | null;
  type: "episode" | "bonus" | "meta";
  title: string;
  slug: string;
  youtubeId: string;
  duration: string;
  description?: string;
  categories?: string[];
}

export interface TranscriptSegment {
  start: number;
  text: string;
}
