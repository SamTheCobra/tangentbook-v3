"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, Thesis, MacroHeader } from "@/lib/api";
import CascadeLogo from "@/components/CascadeLogo";

type FilterTab = "ALL" | "ACTIVE" | "ARCHIVED";
type SortMode = "order" | "thi-desc" | "conviction" | "updated";

const STATUS_MESSAGES = [
  "Analyzing thesis...",
  "Finding non-obvious plays...",
  "Mapping downstream effects...",
  "Building your tree...",
];

export default function Home() {
  const router = useRouter();
  const [theses, setTheses] = useState<Thesis[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterTab>("ALL");
  const [sort, setSort] = useState<SortMode>("order");
  const [tagFilter, setTagFilter] = useState<string | null>(null);
  const [macro, setMacro] = useState<MacroHeader | null>(null);

  // New thesis input state
  const [showInput, setShowInput] = useState(false);
  const [rawThesis, setRawThesis] = useState("");
  const [conviction, setConviction] = useState(7);
  const [generating, setGenerating] = useState(false);
  const [statusIdx, setStatusIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadTheses = useCallback(() => {
    api.getTheses().then(setTheses).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadTheses();
    api.getMacroHeader().then(setMacro).catch(() => {});
  }, [loadTheses]);

  useEffect(() => {
    if (generating) {
      setStatusIdx(0);
      intervalRef.current = setInterval(() => {
        setStatusIdx((p) => (p + 1) % STATUS_MESSAGES.length);
      }, 2500);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [generating]);

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

  const handleGenerate = async () => {
    if (!rawThesis.trim()) return;
    setGenerating(true);
    setError(null);
    try {
      const result = await api.generateThesis(rawThesis.trim(), conviction);
      router.push(`/thesis/${result.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Generation failed");
      setGenerating(false);
    }
  };

  const handleRefreshAll = async () => {
    for (const t of theses) {
      await api.refreshFeeds(t.id).catch(() => {});
    }
    loadTheses();
  };


  // Full-screen loading overlay
  if (generating) {
    return (
      <div style={{
        position: "fixed", inset: 0, background: "#0A0A0A",
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        zIndex: 9999,
      }}>
        <div style={{ marginBottom: "48px", opacity: 0.25 }}>
          <CascadeLogo height={28} />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
          <div style={{
            width: "8px", height: "8px", background: "var(--accent)",
            animation: "cascadePulse 1.5s ease-in-out infinite",
          }} />
          <span style={{
            fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
            fontSize: "14px", letterSpacing: "0.04em", color: "var(--text)",
          }}>
            {STATUS_MESSAGES[statusIdx]}
          </span>
        </div>
        <div style={{ color: "#333", fontSize: "12px" }}>
          This takes 15-30 seconds
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>

      {/* ─── TOP NAV BAR ─── */}
      <header style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 48px", height: "56px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg)",
      }}>
        {/* Left: Wordmark */}
        <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
          <a href="/" style={{ display: "block", lineHeight: 0 }}>
            <CascadeLogo height={28} />
          </a>

          {/* Macro data pills */}
          {macro && (
            <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
              <MacroPill label="REGIME" value={macro.regime || "——"} />
              <MacroPill label="FFR" value={macro.ffr != null ? `${macro.ffr.toFixed(2)}%` : "——"} />
              <MacroPill label="10Y-2Y" value={macro.tenYearTwoYearSpread != null ? `${macro.tenYearTwoYearSpread.toFixed(2)}` : "——"} />
              <MacroPill label="VIX" value={macro.vix != null ? macro.vix.toFixed(1) : "——"} />
            </div>
          )}
        </div>

        {/* Right: actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <button
            onClick={handleRefreshAll}
            style={{
              background: "none", border: "1px solid #333",
              padding: "6px 14px", cursor: "pointer",
              fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
              fontSize: "10px", fontWeight: 700, letterSpacing: "0.08em",
              color: "#888", textTransform: "uppercase",
            }}
          >
            Refresh All Feeds
          </button>
          <button
            onClick={() => setShowInput(!showInput)}
            style={{
              background: "var(--text)", border: "none",
              padding: "6px 14px", cursor: "pointer",
              fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
              fontSize: "10px", fontWeight: 700, letterSpacing: "0.08em",
              color: "#0A0A0A", textTransform: "uppercase",
            }}
          >
            + New Thesis
          </button>
        </div>
      </header>

      {/* ─── NEW THESIS INPUT (slides open below nav) ─── */}
      {showInput && (
        <div style={{
          borderBottom: "1px solid var(--border)",
          padding: "20px 48px",
          background: "#111",
          animation: "cascadeFadeIn 0.2s ease",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "16px", maxWidth: "800px" }}>
            <input
              autoFocus
              value={rawThesis}
              onChange={(e) => setRawThesis(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleGenerate(); if (e.key === "Escape") setShowInput(false); }}
              placeholder="Enter a macro thesis..."
              style={{
                flex: 1, background: "transparent", border: "none",
                borderBottom: "1px solid #333", color: "var(--text)",
                fontFamily: "'Bricolage Grotesque', sans-serif",
                fontSize: "16px", fontWeight: 700,
                outline: "none", padding: "8px 0",
              }}
            />
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{
                fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                fontSize: "10px", letterSpacing: "0.06em", color: "#444",
                textTransform: "uppercase",
              }}>
                Conviction
              </span>
              <input
                type="range" min={1} max={10} value={conviction}
                onChange={(e) => setConviction(parseInt(e.target.value))}
                style={{ accentColor: "var(--accent)", width: "60px" }}
              />
              <span style={{
                fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                fontSize: "12px", color: "var(--text)", minWidth: "28px",
              }}>
                {conviction}/10
              </span>
            </div>
            <button
              onClick={handleGenerate}
              disabled={!rawThesis.trim()}
              style={{
                background: rawThesis.trim() ? "var(--text)" : "transparent",
                color: rawThesis.trim() ? "#0A0A0A" : "#333",
                border: rawThesis.trim() ? "none" : "1px solid #333",
                padding: "8px 20px", cursor: rawThesis.trim() ? "pointer" : "not-allowed",
                fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                fontSize: "10px", fontWeight: 700, letterSpacing: "0.06em",
                textTransform: "uppercase", whiteSpace: "nowrap",
              }}
            >
              Generate &rarr;
            </button>
            <button
              onClick={() => setShowInput(false)}
              style={{
                background: "none", border: "none", cursor: "pointer",
                color: "#444", fontSize: "14px", padding: "4px",
              }}
            >
              ✕
            </button>
          </div>
          {error && (
            <div style={{
              marginTop: "8px", color: "var(--accent)",
              fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
              fontSize: "11px",
            }}>
              {error}
            </div>
          )}
        </div>
      )}

      {/* ─── HERO HEADER ─── */}
      <HeroHeader onNewThesis={() => setShowInput(true)} />

      {/* ─── MAIN CONTENT ─── */}
      <div style={{ padding: "32px 48px", maxWidth: "1200px", margin: "0 auto" }}>
        {loading ? (
          <div style={{
            color: "var(--text-muted)",
            fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
            fontSize: "13px",
          }}>
            ————————
          </div>
        ) : (
          <>
            {/* ─── FILTER / SORT BAR ─── */}
            <div style={{
              display: "flex", alignItems: "flex-start", justifyContent: "space-between",
              marginBottom: "24px",
            }}>
              <div>
                {/* Filter tabs + tag dropdown */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "10px" }}>
                  {(["ALL", "ACTIVE", "ARCHIVED"] as FilterTab[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setFilter(tab)}
                      style={{
                        background: "none", border: "none", cursor: "pointer",
                        fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                        fontSize: "11px", letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        color: filter === tab ? "var(--text)" : "var(--text-muted)",
                        borderBottom: filter === tab ? "1px solid var(--text)" : "1px solid transparent",
                        paddingBottom: "4px",
                      }}
                    >
                      {tab}
                    </button>
                  ))}
                  {allTags.length > 0 && (
                    <>
                      <span style={{ color: "var(--border)" }}>|</span>
                      <select
                        value={tagFilter || ""}
                        onChange={(e) => setTagFilter(e.target.value || null)}
                        style={{
                          backgroundColor: "#111",
                          color: "#fff",
                          border: "1px solid #333",
                          padding: "4px 8px",
                          fontSize: "0.7rem",
                          letterSpacing: "0.05em",
                          fontFamily: "inherit",
                          cursor: "pointer",
                        }}
                      >
                        <option value="">ALL TAGS</option>
                        {allTags.map((tag) => (
                          <option key={tag} value={tag}>{tag.toUpperCase()}</option>
                        ))}
                      </select>
                    </>
                  )}
                </div>

                {/* Sort controls */}
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <span style={{
                    fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                    fontSize: "10px", letterSpacing: "0.08em",
                    color: "var(--text-muted)", textTransform: "uppercase",
                  }}>
                    Sort
                  </span>
                  {([
                    { key: "order" as SortMode, label: "DEFAULT" },
                    { key: "thi-desc" as SortMode, label: "THI HIGH-LOW" },
                    { key: "conviction" as SortMode, label: "CONVICTION" },
                    { key: "updated" as SortMode, label: "RECENTLY UPDATED" },
                  ]).map((s) => (
                    <button
                      key={s.key}
                      onClick={() => setSort(s.key)}
                      style={{
                        background: "none", border: "none", cursor: "pointer",
                        fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                        fontSize: "10px", letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        color: sort === s.key ? "var(--text)" : "var(--text-muted)",
                        textDecoration: sort === s.key ? "underline" : "none",
                        textUnderlineOffset: "3px",
                      }}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Thesis count */}
              <span style={{
                fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
                fontSize: "12px", color: "var(--text-muted)",
              }}>
                {filtered.length} theses
              </span>
            </div>

            {/* Divider */}
            <div style={{ borderTop: "1px solid var(--border)", marginBottom: "24px" }} />

            {/* ─── THESIS CARD GRID ─── */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "16px",
              alignItems: "stretch",
            }}>
              {filtered.map((thesis) => (
                <ThesisCard
                  key={thesis.id}
                  thesis={thesis}
                  onClick={() => router.push(`/thesis/${thesis.id}`)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Hero Header ─────────────────────────────────────────────────────────────

function HeroHeader({ onNewThesis }: { onNewThesis: () => void }) {
  const [btnHovered, setBtnHovered] = useState(false);
  return (
    <div style={{
      padding: "80px 0 60px",
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center",
      width: "100%",
      borderBottom: "1px solid #222",
    }}>
      <div style={{
        display: "flex", justifyContent: "center", alignItems: "center",
        width: "100%",
      }}>
        <CascadeLogo height={80} />
      </div>
      <div style={{
        fontSize: "1.1rem",
        color: "#666",
        letterSpacing: "0.08em",
        marginTop: "12px",
      }}>
        Unintended, but not unpredicted.
      </div>
      <button
        onClick={onNewThesis}
        onMouseEnter={() => setBtnHovered(true)}
        onMouseLeave={() => setBtnHovered(false)}
        style={{
          marginTop: "32px",
          padding: "14px 48px",
          fontSize: "0.85rem",
          letterSpacing: "0.12em",
          border: "1px solid #FF4500",
          color: btnHovered ? "#000" : "#FF4500",
          background: btnHovered ? "#FF4500" : "transparent",
          cursor: "pointer",
          fontFamily: "inherit",
          textTransform: "uppercase",
          fontWeight: 700,
        }}
      >
        + New Thesis
      </button>
    </div>
  );
}

// ─── Thesis Card ─────────────────────────────────────────────────────────────

function ThesisCard({ thesis, onClick }: { thesis: Thesis; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  const thiScore = Math.round(thesis.thi.score);

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: hovered ? "#1a1a1a" : "#111",
        textAlign: "left",
        border: hovered ? "2px solid #FF4500" : "2px solid #333",
        padding: "16px",
        height: "220px",
        overflow: "hidden",
        cursor: "pointer",
        display: "flex", flexDirection: "row", alignItems: "stretch",
        transform: hovered ? "translateY(-3px)" : "translateY(0)",
        transition: "border-color 0.2s ease, background 0.2s ease, transform 0.2s ease",
      }}
    >
      {/* LEFT — title + description + metadata */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        minWidth: 0, paddingRight: "12px",
      }}>
        <h3 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: "1.1rem", fontWeight: 800,
          color: "var(--text)",
          letterSpacing: "-0.02em",
          lineHeight: "1.3",
          margin: 0,
          textTransform: "uppercase",
        }}>
          {thesis.title}
        </h3>
        {(thesis.description || thesis.subtitle) && (
          <p style={{
            fontFamily: "var(--font-inter), 'Inter', sans-serif",
            fontSize: "0.85rem", lineHeight: "1.5", color: "#555",
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical" as const,
            overflow: "hidden",
            marginTop: "8px",
            flex: 1,
          }}>
            {thesis.description || thesis.subtitle}
          </p>
        )}
        <div style={{
          fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
          fontSize: "10px", color: "#333", letterSpacing: "0.04em",
          display: "flex", gap: "8px", alignItems: "center",
          marginTop: "auto", paddingTop: "10px",
        }}>
          <span>{thesis.effects.length} effects</span>
          <span>&middot;</span>
          <span>{new Date(thesis.createdAt).toLocaleDateString()}</span>
        </div>
      </div>

      {/* RIGHT — THI gauge */}
      <div style={{
        width: "120px", padding: "12px",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        flexShrink: 0,
      }}>
        <div style={{ width: "120px", height: "80px", overflow: "hidden", flexShrink: 0 }}>
          <CardNeedle score={thiScore} />
        </div>
        <div style={{
          fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
          fontSize: "14px", fontWeight: 700,
          color: "#FF4500", marginTop: "4px",
        }}>
          {thiScore}
        </div>
      </div>
    </div>
  );
}

// ─── Card Needle (canvas, exact gradient from Needle.tsx) ────────────────────

function CardNeedle({ score }: { score: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const size = 120;
  const canvasH = 78;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = canvasH * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, size, canvasH);

    const cx = size / 2;
    const cy = canvasH - 3;
    const radius = size / 2 - 6;
    const s = Math.max(0, Math.min(100, score));
    const needleAngle = Math.PI + (s / 100) * Math.PI;
    const nx = cx + radius * Math.cos(needleAngle);
    const ny = cy + radius * Math.sin(needleAngle);

    // Wedge — cubic ease-in orange gradient (exact values from Needle.tsx)
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius - 4, Math.PI, needleAngle, false);
    ctx.closePath();
    const grad = ctx.createLinearGradient(cx - radius, 0, cx + radius, 0);
    const maxOpacity = 0.65;
    const fullAt = 0.72;
    for (let i = 0; i <= 100; i++) {
      const t = i / 100;
      const eased = t < fullAt ? Math.pow(t / fullAt, 3) * maxOpacity : maxOpacity;
      grad.addColorStop(t, `rgba(255,69,0,${eased.toFixed(4)})`);
    }
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();

    // Arc outline
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI, false);
    ctx.strokeStyle = "rgba(255,255,255,0.13)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Tick marks at 0, 50, 100
    [0, 50, 100].forEach(v => {
      const a = Math.PI + (v / 100) * Math.PI;
      ctx.beginPath();
      ctx.moveTo(cx + (radius - 8) * Math.cos(a), cy + (radius - 8) * Math.sin(a));
      ctx.lineTo(cx + (radius + 3) * Math.cos(a), cy + (radius + 3) * Math.sin(a));
      ctx.strokeStyle = "rgba(255,255,255,0.22)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Needle line
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(nx, ny);
    ctx.strokeStyle = "#FF4500";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.stroke();

    // Pivot dot
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#FF4500";
    ctx.fill();

    // Tip dot
    ctx.beginPath();
    ctx.arc(nx, ny, 2, 0, Math.PI * 2);
    ctx.fillStyle = "#FF4500";
    ctx.fill();
  }, [score]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "100%", display: "block" }}
    />
  );
}

// ─── Macro Pill ──────────────────────────────────────────────────────────────

function MacroPill({ label, value }: { label: string; value: string }) {
  const isPlaceholder = value === "——";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
      <span style={{
        fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
        fontSize: "10px", letterSpacing: "0.08em",
        color: "var(--text-muted)", textTransform: "uppercase",
      }}>
        {label}
      </span>
      <span style={{
        fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
        fontSize: "12px",
        color: isPlaceholder ? "var(--text-muted)" : "var(--text)",
      }}>
        {value}
      </span>
    </div>
  );
}
