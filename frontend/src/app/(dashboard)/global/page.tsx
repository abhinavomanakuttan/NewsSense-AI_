import type { Metadata } from "next";
import { RegionalNewsPage } from "@/components/news/regional-news-page";

export const metadata: Metadata = {
  title: "Global News | NewsSense AI",
  description:
    "International news from around the world — AI-curated and fact-checked. Sources: Reuters, AP, BBC, Al Jazeera, Guardian, DW, and more.",
};

export default function GlobalPage() {
  return (
    <RegionalNewsPage
      config={{
        region: "global",
        title: "Global News",
        subtitle:
          "World news — AI-verified international reporting. Sources: Reuters, AP, BBC, Al Jazeera, Guardian, Deutsche Welle, and more.",
        accentColor: "text-blue-700",
        badgeColor: "bg-blue-100 text-blue-700",
        endpoint: "/news/global",
      }}
    />
  );
}
