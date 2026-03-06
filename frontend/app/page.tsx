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

  const handleCollapse = async (id: string) => {
    await api.toggleCollapse(id);
    setTheses((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isCollapsed: !t.isCollapsed } : t))
    );
  };

  const handleArchive = async (id: string) => {
    await api.toggleArchive(id);
    setTheses((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isArchived: !t.isArchived } : t))
    );
  };

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    await api.deleteThesis(id);
    setTheses((prev) => prev.filter((t) => t.id !== id));
  };

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
            {/* Controls bar */}
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
                <ThesisCard
                  key={thesis.id}
                  thesis={thesis}
                  onCollapse={() => handleCollapse(thesis.id)}
                  onArchive={() => handleArchive(thesis.id)}
                  onDelete={() => handleDelete(thesis.id, thesis.title)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
    </ErrorBoundary>
  );
}

function ThesisCard({
  thesis,
  onCollapse,
  onArchive,
  onDelete,
}: {
  thesis: Thesis;
  onCollapse: () => void;
  onArchive: () => void;
  onDelete: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  if (thesis.isCollapsed) {
    return (
      <div
        className="border px-5 py-3 flex items-center justify-between"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <Link
            href={`/thesis/${thesis.id}`}
            className="font-bold uppercase hover:underline"
            style={{ color: "var(--text)", letterSpacing: "-0.03em", textUnderlineOffset: "3px", fontSize: "14px" }}
          >
            {thesis.title}
          </Link>
        </div>
        <div className="flex items-center gap-4 ml-4">
          <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
            {Math.round(thesis.thi.score)}
          </span>
          <button
            onClick={onCollapse}
            style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "14px" }}
          >
            +
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="border p-5 relative"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-4">
          <div className="flex items-start justify-between">
            <Link
              href={`/thesis/${thesis.id}`}
              className="font-bold uppercase hover:underline"
              style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3", textUnderlineOffset: "3px", fontSize: "15px" }}
            >
              {thesis.title}
            </Link>
            <div className="flex items-center gap-1 ml-2 flex-shrink-0">
              <button
                onClick={onCollapse}
                className="px-1"
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "14px" }}
              >
                —
              </button>
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="px-1"
                  style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "14px" }}
                >
                  ...
                </button>
                {menuOpen && (
                  <div
                    className="absolute right-0 top-5 z-10 border py-1"
                    style={{ background: "var(--surface-alt)", borderColor: "var(--border)", minWidth: "140px" }}
                  >
                    <button
                      onClick={() => { onArchive(); setMenuOpen(false); }}
                      className="block w-full text-left px-3 py-1.5 uppercase"
                      style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", letterSpacing: "0.08em", fontSize: "12px" }}
                    >
                      {thesis.isArchived ? "Unarchive" : "Archive thesis"}
                    </button>
                    <button
                      onClick={() => { onDelete(); setMenuOpen(false); }}
                      className="block w-full text-left px-3 py-1.5 uppercase"
                      style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", letterSpacing: "0.08em", fontSize: "12px" }}
                    >
                      Delete thesis
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
          <p className="mt-2" style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}>
            {thesis.subtitle}
          </p>
        </div>
        <Needle score={thesis.thi.score} size="sm" />
      </div>

      <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
              CONVICTION
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
              {thesis.userConviction.score}/10
            </span>
          </div>
          <div className="flex items-center gap-3">
            {thesis.equityBets.slice(0, 3).map((bet) => (
              <span
                key={bet.id}
                style={{
                  color: bet.role === "BENEFICIARY" ? "var(--positive)" : bet.role === "HEADWIND" ? "var(--text-muted)" : "var(--accent)",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "13px",
                }}
              >
                {bet.ticker}
              </span>
            ))}
            <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
              {thesis.timeHorizon}
            </span>
          </div>
        </div>

        {thesis.userConviction.divergenceWarning && (
          <div
            className="mt-2 px-2 py-1 border"
            style={{ borderColor: "var(--accent)", color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}
          >
            {thesis.userConviction.divergenceWarning}
          </div>
        )}
      </div>

      {thesis.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {thesis.tags.map((tag) => (
            <span
              key={tag}
              className="uppercase px-2 py-0.5 border"
              style={{ color: "var(--text-muted)", borderColor: "var(--border)", letterSpacing: "0.08em", fontSize: "11px" }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
