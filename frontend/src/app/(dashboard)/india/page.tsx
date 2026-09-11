import type { Metadata } from "next";
import { RegionalNewsPage } from "@/components/news/regional-news-page";

export const metadata: Metadata = {
  title: "India News | NewsSense AI",
  description:
    "Latest national news from India — politics, economy, judiciary, defence, elections, and more. Powered by The Hindu, NDTV, Times of India, Indian Express, PIB, and 15+ verified sources.",
};

export default function IndiaPage() {
  return (
    <RegionalNewsPage
      config={{
        region: "india",
        title: "India News",
        subtitle:
          "National and state news from across India — AI-verified, multi-source. Sources: The Hindu, NDTV, TOI, Indian Express, PIB, Hindustan Times, and more.",
        accentColor: "text-orange-700",
        badgeColor: "bg-orange-100 text-orange-700",
        endpoint: "/news/india",
        stateFilter: true,
      }}
    />
  );
}
