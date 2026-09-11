import type { Metadata } from "next";
import { RegionalNewsPage } from "@/components/news/regional-news-page";

export const metadata: Metadata = {
  title: "Kerala News | NewsSense AI",
  description:
    "Latest Kerala news from Mathrubhumi, Manorama Online, The Hindu Kerala, NDTV Kerala, and more. Covering all 14 districts of Kerala with verified, AI-analyzed reporting.",
};

export default function KeralaPage() {
  return (
    <RegionalNewsPage
      config={{
        region: "kerala",
        title: "Kerala News",
        subtitle:
          "Real-time news from Kerala — all 14 districts, verified by AI. Sources: Mathrubhumi, Manorama, The Hindu Kerala, NDTV Kerala, and more.",
        accentColor: "text-emerald-700",
        badgeColor: "bg-emerald-100 text-emerald-700",
        endpoint: "/news/kerala",
        districtFilter: true,
      }}
    />
  );
}
