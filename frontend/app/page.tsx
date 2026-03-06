"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import NewThesisPanel from "@/components/NewThesisPanel";
import ErrorBoundary from "@/components/ErrorBoundary";
import { ThesisCardSkeleton } from "@/components/Skeleton";
import { api, Thesis } from "@/lib/api";

type FilterTab = "ALL" | "ACTIVE" | "ARCHIVED";
type SortMode = "order" | "thi-desc" | "conviction" | "updated";

export default function Home() {
  const [theses, setTheses] = useState<Thesis[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterTab>("ALL");
  const [sort, setSort] = useState<SortMode>("order");
  const [tagFilter, setTagFilter] = useState<string | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);

  const loadTheses = useCallback(() => {
    api
      .getTheses()
      .then(setTheses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadTheses();
  }, [loadTheses]);

  const allTags = useMemo(() => {
    const tags = new Set<string>();
    theses.forEach((t) => t.tags.forEach((tag) => tags.add(tag)));
    return Array.from(tags).sort();
  }, [theses]);

  const filtered = useMemo(() => {
    let result = theses;

    if (filter === "ACTIVE") result = result.filter((t) => !t.isArchived);
    else if (filter === "ARCHIVED") result = result.filter((t) => t.isArchived);

    if (tagFilter) result = result.filter((t) => t.tags.includes(tagFilter));

    switch (sort) {
      case "thi-desc":
        result = [...result].sort((a, b) => b.thi.score - a.thi.score);
        break;
      case "conviction":
        result = [...result].sort((a, b) => b.userConviction.score - a.userConviction.score);
        break;
      case "updated":
        result = [...result].sort(
          (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
        );
        break;
      default:
        result = [...result].sort((a, b) => a.displayOrder - b.displayOrder);
    }

    return result;
  }, [theses, filter, sort, tagFilter]);

  return (
    <ErrorBoundary>
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header onNewThesis={() => setPanelOpen(true)} />
      <NewThesisPanel
        isOpen={panelOpen}
        onClose={() => setPanelOpen(false)}
        onCreated={loadTheses}
      />

      <div className="px-12 py-8">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0 mt-8">
            {Array.from({ length: 8 }).map((_, i) => (
              <ThesisCardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div>
            <div className="flex items-start justify-between mb-6">
              <div>
                <div className="flex items-center gap-4 mb-3">
                  {(["ALL", "ACTIVE", "ARCHIVED"] as FilterTab[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setFilter(tab)}
                      className="uppercase pb-1"
                      style={{
                        color: filter === tab ? "var(--text)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        background: "none",
                        border: "none",
                        borderBottom: `1px solid ${filter === tab ? "var(--accent)" : "transparent"}`,
                        cursor: "pointer",
                        fontSize: "13px",
                      }}
                    >
                      {tab}
                    </button>
                  ))}
                  <span style={{ color: "var(--border)" }}>|</span>
                  {allTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setTagFilter(tagFilter === tag ? null : tag)}
                      className="uppercase"
                      style={{
                        color: tagFilter === tag ? "var(--accent)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "12px",
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-3">
                  <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
                    SORT
                  </span>
                  {[
                    { key: "order" as SortMode, label: "DEFAULT" },
                    { key: "thi-desc" as SortMode, label: "THI HIGH-LOW" },
                    { key: "conviction" as SortMode, label: "CONVICTION" },
                    { key: "updated" as SortMode, label: "RECENTLY UPDATED" },
                  ].map((s) => (
                    <button
                      key={s.key}
                      onClick={() => setSort(s.key)}
                      className="uppercase"
                      style={{
                        color: sort === s.key ? "var(--text)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "12px",
                        textDecoration: sort === s.key ? "underline" : "none",
                        textUnderlineOffset: "3px",
                      }}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "14px" }}>
                {filtered.length} theses
              </span>
            </div>

            <div className="mb-6" style={{ borderTop: "1px solid var(--border)" }} />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0">
              {filtered.map((thesis) => (
                <ThesisCard key={thesis.id} thesis={thesis} />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
    </ErrorBoundary>
  );
}

function ThesisCard({ thesis }: { thesis: Thesis }) {
  const [hovered, setHovered] = useState(false);

  return (
    <Link
      href={`/thesis/${thesis.id}`}
      className="block"
      style={{
        background: "#1A1A1A",
        border: `1px solid ${hovered ? "#E8440A" : "#2A2A2A"}`,
        padding: "24px",
        minHeight: "140px",
        textDecoration: "none",
        transition: "border-color 0.15s ease",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="flex items-center gap-4">
        <h2
          className="flex-1 font-bold uppercase"
          style={{
            color: "#F5F3EE",
            fontFamily: "Inter, system-ui, sans-serif",
            fontSize: "18px",
            letterSpacing: "-0.03em",
            lineHeight: "1.3",
          }}
        >
          {thesis.title}
        </h2>
        <div className="flex-shrink-0">
          <Needle score={thesis.thi.score} size="sm" />
        </div>
      </div>
    </Link>
  );
}
