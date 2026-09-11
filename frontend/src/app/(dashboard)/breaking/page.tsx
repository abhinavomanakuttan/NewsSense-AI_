import type { Metadata } from "next";
import { RegionalNewsPage } from "@/components/news/regional-news-page";

export const metadata: Metadata = {
  title: "Breaking News | NewsSense AI",
  description:
    "Breaking news from Kerala, India, and around the world — updated every 2 minutes from high-priority verified sources.",
};

export default function BreakingPage() {
  return (
    <RegionalNewsPage
      config={{
        region: "breaking",
        title: "Breaking News",
        subtitle:
          "Live breaking news from high-priority sources — updated every 2 minutes. Kerala, India, and global. Only articles from the last 2 hours.",
        accentColor: "text-red-700",
        badgeColor: "bg-red-100 text-red-700",
        endpoint: "/news/breaking",
      }}
    />
  );
}
