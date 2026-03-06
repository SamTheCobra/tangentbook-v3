"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
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
  const [tagDropdownOpen, setTagDropdownOpen] = useState(false);
  const tagDropdownRef = useRef<HTMLDivElement>(null);

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

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (tagDropdownRef.current && !tagDropdownRef.current.contains(e.target as Node)) {
        setTagDropdownOpen(false);
      }
    };
    if (tagDropdownOpen) {
      document.addEventListener("mousedown", handleClick);
      return () => document.removeEventListener("mousedown", handleClick);
    }
  }, [tagDropdownOpen]);

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

                  {/* Tag filter dropdown */}
                  {allTags.length > 0 && (
                    <div ref={tagDropdownRef} className="relative">
                      <button
                        onClick={() => setTagDropdownOpen(!tagDropdownOpen)}
                        className="uppercase flex items-center gap-1"
                        style={{
                          color: tagFilter ? "var(--accent)" : "var(--text-muted)",
                          letterSpacing: "0.08em",
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          fontSize: "12px",
                        }}
                      >
                        FILTER BY TAG {tagDropdownOpen ? "▴" : "▾"}
                      </button>

                      {tagFilter && (
                        <span
                          className="uppercase ml-2 px-2 py-0.5 border inline-flex items-center gap-1"
                          style={{
                            color: "var(--accent)",
                            borderColor: "var(--accent)",
                            fontSize: "10px",
                            letterSpacing: "0.06em",
                          }}
                        >
                          {tagFilter}
                          <button
                            onClick={(e) => { e.stopPropagation(); setTagFilter(null); }}
                            style={{ color: "var(--accent)", background: "none", border: "none", cursor: "pointer", fontSize: "10px" }}
                          >
                            x
                          </button>
                        </span>
                      )}

                      {tagDropdownOpen && (
                        <div
                          className="absolute top-full left-0 mt-1 border z-50"
                          style={{
                            background: "var(--surface)",
                            borderColor: "var(--border)",
                            minWidth: "180px",
                            maxHeight: "300px",
                            overflowY: "auto",
                          }}
                        >
                          {allTags.map((tag) => (
                            <button
                              key={tag}
                              onClick={() => {
                                setTagFilter(tagFilter === tag ? null : tag);
                                setTagDropdownOpen(false);
                              }}
                              className="w-full text-left px-3 py-2 uppercase flex items-center gap-2"
                              style={{
                                background: tagFilter === tag ? "var(--surface-alt)" : "transparent",
                                border: "none",
                                color: tagFilter === tag ? "var(--accent)" : "var(--text-muted)",
                                fontSize: "11px",
                                letterSpacing: "0.08em",
                                cursor: "pointer",
                              }}
                            >
                              <span
                                style={{
                                  width: "10px",
                                  height: "10px",
                                  border: `1px solid ${tagFilter === tag ? "var(--accent)" : "var(--border)"}`,
                                  background: tagFilter === tag ? "var(--accent)" : "transparent",
                                  display: "inline-block",
                                  flexShrink: 0,
                                }}
                              />
                              {tag}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "14px" }}>
                {filtered.length} theses
              </span>
            </div>

            <div className="mb-6" style={{ borderTop: "1px solid var(--border)" }} />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
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
        background: "#161616",
        border: `1px solid ${hovered ? "var(--accent)" : "var(--border)"}`,
        padding: "28px",
        minHeight: "160px",
        textDecoration: "none",
        transition: "border-color 0.15s ease",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="flex items-center gap-6">
        <div style={{ flex: "0 0 65%" }}>
          <h2
            className="font-bold uppercase"
            style={{
              color: "var(--text)",
              fontFamily: "Inter, system-ui, sans-serif",
              fontSize: "20px",
              letterSpacing: "-0.03em",
              lineHeight: "1.3",
            }}
          >
            {thesis.title}
          </h2>
          <p
            className="mt-2"
            style={{
              color: "var(--text-muted)",
              fontSize: "14px",
              lineHeight: "1.5",
            }}
          >
            {thesis.subtitle}
          </p>
        </div>
        <div className="flex-1 flex justify-center">
          <Needle score={thesis.thi.score} size="sm" />
        </div>
      </div>
    </Link>
  );
}
