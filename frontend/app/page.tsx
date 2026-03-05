"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import { api, Thesis } from "@/lib/api";

type FilterTab = "ALL" | "ACTIVE" | "ARCHIVED";
type SortMode = "order" | "thi-desc" | "conviction" | "updated";

export default function Home() {
  const [theses, setTheses] = useState<Thesis[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterTab>("ALL");
  const [sort, setSort] = useState<SortMode>("order");
  const [tagFilter, setTagFilter] = useState<string | null>(null);

  useEffect(() => {
    api
      .getTheses()
      .then(setTheses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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

  const handleCollapse = async (id: string) => {
    await api.toggleCollapse(id);
    setTheses((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isCollapsed: !t.isCollapsed } : t))
    );
  };

  return (
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header />
      <div className="px-12 py-8">
        {loading ? (
          <div style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace" }}>
            ————
          </div>
        ) : (
          <div>
            {/* Controls bar */}
            <div className="flex items-start justify-between mb-6">
              <div>
                {/* Filter tabs */}
                <div className="flex items-center gap-4 mb-3">
                  {(["ALL", "ACTIVE", "ARCHIVED"] as FilterTab[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setFilter(tab)}
                      className="text-xs uppercase pb-1"
                      style={{
                        color: filter === tab ? "var(--text)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        borderBottom: filter === tab ? "1px solid var(--text)" : "1px solid transparent",
                        background: "none",
                        border: "none",
                        borderBottomWidth: "1px",
                        borderBottomStyle: "solid",
                        borderBottomColor: filter === tab ? "var(--text)" : "transparent",
                        cursor: "pointer",
                        fontFamily: "Inter, system-ui, sans-serif",
                      }}
                    >
                      {tab}
                    </button>
                  ))}
                  <span style={{ color: "var(--border)" }}>|</span>
                  {/* Tag filters */}
                  {allTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setTagFilter(tagFilter === tag ? null : tag)}
                      className="text-xs uppercase"
                      style={{
                        color: tagFilter === tag ? "var(--accent)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "10px",
                        fontFamily: "Inter, system-ui, sans-serif",
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>

                {/* Sort controls */}
                <div className="flex items-center gap-3">
                  <span
                    className="text-xs uppercase"
                    style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
                  >
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
                      className="text-xs uppercase"
                      style={{
                        color: sort === s.key ? "var(--text)" : "var(--text-muted)",
                        letterSpacing: "0.08em",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "10px",
                        textDecoration: sort === s.key ? "underline" : "none",
                        textUnderlineOffset: "3px",
                        fontFamily: "Inter, system-ui, sans-serif",
                      }}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              <span
                style={{
                  color: "var(--text-muted)",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "12px",
                }}
              >
                {filtered.length} theses
              </span>
            </div>

            {/* 1px separator */}
            <div className="mb-6" style={{ borderTop: "1px solid var(--border)" }} />

            {/* Thesis grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0">
              {filtered.map((thesis) => (
                <ThesisCard
                  key={thesis.id}
                  thesis={thesis}
                  onCollapse={() => handleCollapse(thesis.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function ThesisCard({
  thesis,
  onCollapse,
}: {
  thesis: Thesis;
  onCollapse: () => void;
}) {
  // Collapsed view: single-line compact row
  if (thesis.isCollapsed) {
    return (
      <div
        className="border px-5 py-3 flex items-center justify-between"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <Link
            href={`/thesis/${thesis.id}`}
            className="font-bold uppercase text-xs truncate hover:underline"
            style={{
              color: "var(--text)",
              letterSpacing: "-0.03em",
              textDecorationColor: "var(--text-muted)",
              textUnderlineOffset: "3px",
            }}
          >
            {thesis.title}
          </Link>
        </div>
        <div className="flex items-center gap-4 ml-4">
          <span
            style={{
              color: "var(--accent)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "13px",
            }}
          >
            {Math.round(thesis.thi.score)}
          </span>
          <button
            onClick={onCollapse}
            className="text-xs"
            style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
          >
            +
          </button>
        </div>
      </div>
    );
  }

  // Expanded view
  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-4">
          <div className="flex items-start justify-between">
            <Link
              href={`/thesis/${thesis.id}`}
              className="font-bold uppercase text-sm hover:underline"
              style={{
                color: "var(--text)",
                letterSpacing: "-0.03em",
                lineHeight: "1.3",
                textDecorationColor: "var(--text-muted)",
                textUnderlineOffset: "3px",
              }}
            >
              {thesis.title}
            </Link>
            <button
              onClick={onCollapse}
              className="text-xs ml-2 flex-shrink-0"
              style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
            >
              —
            </button>
          </div>
          <p className="mt-1 text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
            {thesis.subtitle}
          </p>
        </div>
        <Needle score={thesis.thi.score} size="sm" />
      </div>

      <div
        className="mt-3 pt-3 flex items-center justify-between border-t"
        style={{ borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-4">
          <span
            className="text-xs uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
          >
            CONVICTION
          </span>
          <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
            {thesis.userConviction.score}/10
          </span>
        </div>
        <div className="flex items-center gap-3">
          {thesis.equityBets.slice(0, 3).map((bet) => (
            <span
              key={bet.id}
              className="text-xs"
              style={{
                color:
                  bet.role === "BENEFICIARY"
                    ? "var(--positive)"
                    : bet.role === "HEADWIND"
                    ? "var(--text-muted)"
                    : "var(--accent)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "11px",
              }}
            >
              {bet.ticker}
            </span>
          ))}
          <span
            className="text-xs uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
          >
            {thesis.timeHorizon}
          </span>
        </div>
      </div>

      {thesis.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {thesis.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs uppercase px-2 py-0.5 border"
              style={{
                color: "var(--text-muted)",
                borderColor: "var(--border)",
                letterSpacing: "0.08em",
                fontSize: "9px",
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
