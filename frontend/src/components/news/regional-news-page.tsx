"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { ArticleCard } from "@/components/articles/article-card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageSpinner } from "@/components/ui/spinner";
import type { ArticleList } from "@/types/models";

interface RegionalPageConfig {
  region: "kerala" | "india" | "global" | "breaking";
  title: string;
  subtitle: string;
  accentColor: string;
  badgeColor: string;
  endpoint: string;
  districtFilter?: boolean;
  stateFilter?: boolean;
}

interface RegionalNewsPageProps {
  config: RegionalPageConfig;
}

interface NewsFeedResponse {
  total: number;
  skip: number;
  limit: number;
  articles: ArticleList[];
  applied_filters: Record<string, string>;
}

const KERALA_DISTRICTS = [
  "All Districts",
  "Thiruvananthapuram",
  "Kollam",
  "Pathanamthitta",
  "Alappuzha",
  "Kottayam",
  "Idukki",
  "Ernakulam",
  "Thrissur",
  "Palakkad",
  "Malappuram",
  "Kozhikode",
  "Wayanad",
  "Kannur",
  "Kasaragod",
];

const INDIA_STATES = [
  "All States",
  "Kerala",
  "Maharashtra",
  "Tamil Nadu",
  "Karnataka",
  "Andhra Pradesh",
  "Telangana",
  "Delhi",
  "Uttar Pradesh",
  "West Bengal",
  "Rajasthan",
  "Gujarat",
  "Punjab",
  "Haryana",
  "Bihar",
  "Odisha",
];

export function RegionalNewsPage({ config }: RegionalNewsPageProps) {
  const [articles, setArticles] = useState<ArticleList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bookmarkIds, setBookmarkIds] = useState<Set<string>>(new Set());
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");
  const [topic, setTopic] = useState("");
  const [topicInput, setTopicInput] = useState("");
  const limit = 20;

  // Load bookmarks
  useEffect(() => {
    api
      .get<{ article_id: string }[]>("/bookmarks")
      .then((items) => setBookmarkIds(new Set(items.map((b) => b.article_id))))
      .catch(() => {});
  }, []);

  // Fetch news
  const fetchNews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        skip: String(page * limit),
        limit: String(limit),
      });
      if (district && district !== "All Districts") params.set("district", district);
      if (state && state !== "All States") params.set("state", state);
      if (topic) params.set("topic", topic);

      const url = `${config.endpoint}?${params.toString()}`;
      const data = await api.get<NewsFeedResponse>(url);
      setArticles(data.articles || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError("Failed to load news. Please try again.");
      setArticles([]);
    } finally {
      setLoading(false);
    }
  }, [config.endpoint, page, district, state, topic]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const handleToggleBookmark = async (id: string) => {
    const isBookmarked = bookmarkIds.has(id);
    setBookmarkIds((prev) => {
      const next = new Set(prev);
      isBookmarked ? next.delete(id) : next.add(id);
      return next;
    });
    try {
      if (isBookmarked) {
        await api.delete(`/bookmarks/${id}`);
      } else {
        await api.post("/bookmarks", { article_id: id });
      }
    } catch {
      setBookmarkIds((prev) => {
        const next = new Set(prev);
        isBookmarked ? next.add(id) : next.delete(id);
        return next;
      });
    }
  };

  const handleTopicSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setTopic(topicInput.trim());
    setPage(0);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <h1 className={`text-2xl font-bold ${config.accentColor}`}>
            {config.title}
          </h1>
          {config.region === "breaking" && (
            <span className="flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-0.5 text-xs font-semibold text-red-600">
              <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              LIVE
            </span>
          )}
          <span
            className={`ml-auto rounded-full ${config.badgeColor} px-3 py-0.5 text-xs font-medium`}
          >
            {total} articles
          </span>
        </div>
        <p className="text-sm text-muted-foreground">{config.subtitle}</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Topic search */}
        <form onSubmit={handleTopicSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search topic..."
            value={topicInput}
            onChange={(e) => setTopicInput(e.target.value)}
            className="rounded-md border bg-background px-3 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Search
          </button>
          {topic && (
            <button
              type="button"
              onClick={() => { setTopic(""); setTopicInput(""); setPage(0); }}
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-accent"
            >
              Clear
            </button>
          )}
        </form>

        {/* Kerala district filter */}
        {config.districtFilter && (
          <select
            value={district}
            onChange={(e) => { setDistrict(e.target.value); setPage(0); }}
            className="rounded-md border bg-background px-3 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {KERALA_DISTRICTS.map((d) => (
              <option key={d} value={d === "All Districts" ? "" : d}>
                {d}
              </option>
            ))}
          </select>
        )}

        {/* India state filter */}
        {config.stateFilter && (
          <select
            value={state}
            onChange={(e) => { setState(e.target.value); setPage(0); }}
            className="rounded-md border bg-background px-3 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {INDIA_STATES.map((s) => (
              <option key={s} value={s === "All States" ? "" : s}>
                {s}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <PageSpinner />
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : articles.length === 0 ? (
        <EmptyState
          title="No articles found"
          description={
            topic
              ? `No ${config.title} articles found for "${topic}". Try a different search.`
              : `No ${config.title} articles available right now. Check back soon.`
          }
        />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                {...article}
                isBookmarked={bookmarkIds.has(article.id)}
                onToggleBookmark={handleToggleBookmark}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-accent"
              >
                ← Previous
              </button>
              <span className="text-sm text-muted-foreground">
                Page {page + 1} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-accent"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
