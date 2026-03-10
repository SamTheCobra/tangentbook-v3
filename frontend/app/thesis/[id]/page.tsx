"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  api, ThesisDetail, Effect, EquityBet, StartupOpportunity,
  EquityScoreResult, EFSScore, STSScore,
} from "@/lib/api";
import GradientBar from "@/components/GradientBar";
import CascadeLogo from "@/components/CascadeLogo";

// ─── Types ──────────────────────────────────────────────────────────────────

type CardNode = {
  id: string;
  type: "hero" | "effect";
  depth: number;
  order: number;
  title: string;
  description: string;
  thiScore: number;
  equityBets: EquityBet[];
  startupOpportunities: StartupOpportunity[];
  effectId?: string;
  children: CardNode[];
};

type THIComponent = { label: string; score: number; weight: number };

// ─── Constants ──────────────────────────────────────────────────────────────

const DEPTH_INDENT = 80;
const DEPTH_STYLES: Record<number, { bg: string; textColor: string; mutedColor: string; titleSize: string }> = {
  0: { bg: "#141414", textColor: "#F0EDE8", mutedColor: "#666", titleSize: "2.4rem" },
  1: { bg: "#1a1a1a", textColor: "#ccc", mutedColor: "#555", titleSize: "1.8rem" },
  2: { bg: "#141414", textColor: "#999", mutedColor: "#444", titleSize: "1.4rem" },
  3: { bg: "#0f0f0f", textColor: "#666", mutedColor: "#333", titleSize: "1.1rem" },
};

function getDepthStyle(depth: number) {
  return DEPTH_STYLES[Math.min(depth, 3)];
}

const ORDER_LABELS: Record<number, string> = {
  0: "HERO THESIS",
  1: "2ND ORDER",
  2: "3RD ORDER",
  3: "4TH ORDER",
};

function getOrderLabel(depth: number) {
  return ORDER_LABELS[Math.min(depth, 3)] || `${depth + 1}TH ORDER`;
}

// EFS sub-score weights (standard EFS formula)
const EFS_COMPONENTS = [
  { key: "revenueAlignmentScore" as const, label: "REVENUE ALIGNMENT", weight: 0.30 },
  { key: "thesisBetaScore" as const, label: "THESIS BETA", weight: 0.25 },
  { key: "momentumAlignmentScore" as const, label: "MOMENTUM ALIGNMENT", weight: 0.20 },
  { key: "valuationBufferScore" as const, label: "VALUATION BUFFER", weight: 0.15 },
  { key: "signalPurityScore" as const, label: "SIGNAL PURITY", weight: 0.10 },
];

// ─── Main Page ──────────────────────────────────────────────────────────────

export default function ThesisTreePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [activePanels, setActivePanels] = useState<Record<string, string | null>>({});
  const [playsTabs, setPlaysTabs] = useState<Record<string, "stocks" | "startups">>({});
  const [efsMap, setEfsMap] = useState<Record<string, EFSScore>>({});
  const [stsMap, setStsMap] = useState<Record<string, STSScore>>({});
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState("");
  const [generatingFor, setGeneratingFor] = useState<string | null>(null);
  const [hoveredCardId, setHoveredCardId] = useState<string | null>(null);
  const [expandedBetIds, setExpandedBetIds] = useState<Record<string, string | null>>({});
  const [breakdownMap, setBreakdownMap] = useState<Record<string, THIComponent[]>>({});
  const fetchedBreakdowns = useRef<Set<string>>(new Set());

  const reloadThesis = async () => {
    const [t, efs] = await Promise.all([
      api.getThesis(id),
      api.getThesisEquityScores(id).catch(() => [] as EquityScoreResult[]),
    ]);
    setThesis(t);
    const newEfs: Record<string, EFSScore> = {};
    efs.forEach((r) => { if (r.efs) newEfs[r.betId] = r.efs; });
    setEfsMap(newEfs);
    const allOpps = [
      ...t.startupOpportunities,
      ...t.effects.flatMap((e) => [
        ...e.startupOpportunities,
        ...e.childEffects.flatMap((c) => c.startupOpportunities),
      ]),
    ];
    if (allOpps.length > 0) {
      const stsResults = await Promise.all(
        allOpps.map((o) => api.getStartupSTS(o.id).catch(() => null))
      );
      const newSts: Record<string, STSScore> = {};
      stsResults.forEach((r) => { if (r?.sts) newSts[r.oppId] = r.sts; });
      setStsMap(newSts);
    }
  };

  useEffect(() => {
    if (!id) return;
    api.getThesis(id)
      .then(async (t) => {
        setThesis(t);
        setExpandedIds(new Set(["hero"]));
        // Populate hero breakdown immediately
        setBreakdownMap((prev) => ({
          ...prev,
          hero: [
            { label: "EVIDENCE", score: t.thi.evidence.score, weight: t.thi.evidence.weight },
            { label: "MOMENTUM", score: t.thi.momentum.score, weight: t.thi.momentum.weight },
            { label: "CONVICTION", score: t.thi.conviction.score, weight: t.thi.conviction.weight },
          ],
        }));
        const efs = await api.getThesisEquityScores(id).catch(() => [] as EquityScoreResult[]);
        const newEfs: Record<string, EFSScore> = {};
        efs.forEach((r) => { if (r.efs) newEfs[r.betId] = r.efs; });
        setEfsMap(newEfs);
        const allOpps = [
          ...t.startupOpportunities,
          ...t.effects.flatMap((e) => [
            ...e.startupOpportunities,
            ...e.childEffects.flatMap((c) => c.startupOpportunities),
          ]),
        ];
        if (allOpps.length > 0) {
          const stsResults = await Promise.all(
            allOpps.map((o) => api.getStartupSTS(o.id).catch(() => null))
          );
          const newSts: Record<string, STSScore> = {};
          stsResults.forEach((r) => { if (r?.sts) newSts[r.oppId] = r.sts; });
          setStsMap(newSts);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  // Fetch scoring breakdown for effect cards when they become expanded
  useEffect(() => {
    if (!thesis) return;
    expandedIds.forEach((cardId) => {
      if (cardId === "hero") return;
      if (fetchedBreakdowns.current.has(cardId)) return;
      fetchedBreakdowns.current.add(cardId);
      const effectId = cardId.replace("effect-", "");
      api.getEffectScoringBreakdown(effectId)
        .then((bd) => {
          setBreakdownMap((prev) => ({
            ...prev,
            [cardId]: [
              { label: "EVIDENCE", score: bd.thiFormula.evidenceScore, weight: thesis.thi.evidence.weight },
              { label: "MOMENTUM", score: bd.thiFormula.momentumScore, weight: thesis.thi.momentum.weight },
              { label: "CONVICTION", score: bd.thiFormula.qualityScore, weight: thesis.thi.conviction.weight },
            ],
          }));
        })
        .catch(() => {});
    });
  }, [expandedIds, thesis]);

  if (loading || !thesis) {
    return (
      <div style={{
        minHeight: "100vh", background: "var(--bg)",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <span style={{
          fontFamily: "var(--font-mono), monospace", fontSize: "13px", color: "#333",
        }}>
          {loading ? "————————" : "Thesis not found."}
        </span>
      </div>
    );
  }

  const tree = buildTree(thesis);

  const toggleCard = (cardId: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(cardId)) {
        next.delete(cardId);
      } else {
        next.add(cardId);
      }
      return next;
    });
  };

  const handleSaveTitle = async (node: CardNode) => {
    if (!editDraft.trim()) { setEditingId(null); return; }
    if (node.type === "hero") {
      await api.updateThesis(id, { title: editDraft.trim() });
    } else if (node.effectId) {
      await api.updateEffect(node.effectId, { title: editDraft.trim() });
    }
    setEditingId(null);
    await reloadThesis();
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${thesis.title}"? This cannot be undone.`)) return;
    await api.deleteThesis(id);
    router.push("/");
  };

  const handleGenerateEffects = async (order: number) => {
    setGeneratingFor(`gen-${order}`);
    try {
      await api.generateEffects(id, order, 3);
      await reloadThesis();
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingFor(null);
    }
  };

  const togglePill = (cardId: string, panel: string) => {
    setActivePanels((prev) => ({
      ...prev,
      [cardId]: prev[cardId] === panel ? null : panel,
    }));
    setExpandedBetIds((prev) => ({ ...prev, [cardId]: null }));
  };

  const flatNodes = flattenTree(tree);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      {/* Top bar */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "20px 32px", borderBottom: "1px solid #141414",
      }}>
        <a
          href="/"
          style={{
            display: "flex", alignItems: "center", gap: "8px",
            textDecoration: "none", lineHeight: 0,
          }}
        >
          <span style={{
            fontFamily: "var(--font-mono), monospace",
            fontSize: "14px", color: "#333",
          }}>
            &larr;
          </span>
          <span style={{ opacity: 0.3 }}>
            <CascadeLogo height={28} />
          </span>
        </a>
        <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
          <span style={{
            fontFamily: "var(--font-mono), monospace", fontSize: "11px",
            color: "#333", letterSpacing: "0.04em",
            maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
          }}>
            {thesis.title}
          </span>
          <button
            onClick={handleDelete}
            style={{
              background: "none", border: "none", cursor: "pointer",
              fontFamily: "var(--font-mono), monospace", fontSize: "11px",
              color: "#333", letterSpacing: "0.06em", textTransform: "uppercase",
            }}
          >
            Delete
          </button>
        </div>
      </div>

      {/* Tree */}
      <div style={{ padding: "40px 32px 80px", maxWidth: "1200px", margin: "0 auto" }}>
        {flatNodes.map((node) => {
          const isExpanded = expandedIds.has(node.id);
          const isHovered = hoveredCardId === node.id;
          const ds = getDepthStyle(node.depth);
          const totalPlays = node.equityBets.length + node.startupOpportunities.length;
          const nodeBreakdown = breakdownMap[node.id];
          const cardPanel = activePanels[node.id] || null;
          const cardPlaysTab = playsTabs[node.id] || "stocks";
          const cardExpandedBet = expandedBetIds[node.id] || null;

          const borderStyle = isExpanded
            ? "3px solid #FF4500"
            : isHovered ? "2px solid #FF4500" : "1px solid #222";
          const basePad = isExpanded ? 25 : isHovered ? 26 : 27;

          return (
            <div
              key={node.id}
              style={{
                marginLeft: `${node.depth * DEPTH_INDENT}px`,
                marginBottom: "4px",
              }}
            >
              {/* ── COLLAPSED ROW ── */}
              {!isExpanded ? (
                <div
                  onClick={() => toggleCard(node.id)}
                  onMouseEnter={() => setHoveredCardId(node.id)}
                  onMouseLeave={() => setHoveredCardId(null)}
                  style={{
                    display: "flex", alignItems: "center", gap: "12px",
                    background: ds.bg,
                    border: borderStyle,
                    padding: `0 ${basePad}px`,
                    height: "48px", cursor: "pointer",
                  }}
                >
                  <span style={{
                    fontFamily: "var(--font-mono), monospace",
                    fontSize: "10px", letterSpacing: "0.12em",
                    color: ds.mutedColor, textTransform: "uppercase",
                    flexShrink: 0, minWidth: "80px",
                  }}>
                    {getOrderLabel(node.depth)}
                  </span>
                  <span style={{
                    fontFamily: "'Bricolage Grotesque', sans-serif",
                    fontSize: "1rem", fontWeight: 800,
                    color: ds.textColor, flex: 1, minWidth: 0,
                    whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                  }}>
                    {node.title}
                  </span>
                  <span style={{
                    fontFamily: "var(--font-mono), monospace",
                    fontSize: "13px", fontWeight: 700,
                    color: "#FF4500", flexShrink: 0,
                  }}>
                    {Math.round(node.thiScore)}
                  </span>
                </div>
              ) : (
                /* ── EXPANDED CARD ── */
                <div
                  onMouseEnter={() => setHoveredCardId(node.id)}
                  onMouseLeave={() => setHoveredCardId(null)}
                  style={{
                    background: ds.bg,
                    border: "3px solid #FF4500",
                    padding: "25px 29px",
                  }}
                >
                  {/* Collapse button row */}
                  <div
                    onClick={() => toggleCard(node.id)}
                    style={{
                      cursor: "pointer",
                      display: "flex", alignItems: "center", justifyContent: "flex-end",
                      marginBottom: "8px",
                    }}
                  >
                    <span style={{
                      fontFamily: "var(--font-mono), monospace",
                      fontSize: "10px", color: "#444", letterSpacing: "0.04em",
                    }}>
                      ▴ Collapse
                    </span>
                  </div>

                  {/* ── TWO-COLUMN HEADER ── */}
                  <div style={{ display: "flex", gap: "24px" }}>
                    {/* LEFT COLUMN ~60% — order, title, description */}
                    <div style={{ flex: "0 0 58%", minWidth: 0 }}>
                      <div style={{
                        fontFamily: "var(--font-mono), monospace",
                        fontSize: "10px", letterSpacing: "0.12em",
                        color: ds.mutedColor, marginBottom: "8px",
                        textTransform: "uppercase",
                      }}>
                        {getOrderLabel(node.depth)}
                      </div>

                      {editingId === node.id ? (
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <input
                            autoFocus
                            value={editDraft}
                            onChange={(e) => setEditDraft(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleSaveTitle(node);
                              if (e.key === "Escape") setEditingId(null);
                            }}
                            style={{
                              flex: 1, background: "transparent",
                              border: "none", borderBottom: "1px solid var(--accent)",
                              outline: "none", color: ds.textColor,
                              fontFamily: "'Bricolage Grotesque', sans-serif",
                              fontSize: ds.titleSize, fontWeight: 800,
                              padding: "0 0 2px",
                            }}
                          />
                          <button onClick={() => handleSaveTitle(node)} style={{
                            background: "none", border: "none", cursor: "pointer",
                            fontFamily: "var(--font-mono), monospace", fontSize: "11px",
                            color: "var(--accent)",
                          }}>Save</button>
                          <button onClick={() => setEditingId(null)} style={{
                            background: "none", border: "none", cursor: "pointer",
                            fontFamily: "var(--font-mono), monospace", fontSize: "11px",
                            color: "#666",
                          }}>Cancel</button>
                        </div>
                      ) : (
                        <h2
                          onDoubleClick={(e) => {
                            e.stopPropagation();
                            setEditDraft(node.title);
                            setEditingId(node.id);
                          }}
                          style={{
                            fontFamily: "'Bricolage Grotesque', sans-serif",
                            fontSize: ds.titleSize, fontWeight: 800,
                            color: ds.textColor,
                            lineHeight: "1.15", letterSpacing: "-0.02em",
                            margin: 0,
                          }}
                        >
                          {node.title}
                        </h2>
                      )}

                      <ExpandableText text={node.description} color={ds.mutedColor} />
                    </div>

                    {/* RIGHT COLUMN ~40% — THI gauge + score breakdown */}
                    <div style={{ flex: "0 0 40%", minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "center" }}>
                        <THIGauge score={Math.round(node.thiScore)} size={160} />
                      </div>

                      {/* Score breakdown — always visible for all cards */}
                      {nodeBreakdown && nodeBreakdown.length > 0 && (
                        <div style={{ marginTop: "16px" }}>
                          {nodeBreakdown.map((c) => (
                            <BreakdownRow
                              key={c.label}
                              label={c.label}
                              score={c.score}
                              weight={c.weight}
                            />
                          ))}
                          {/* THI formula */}
                          <div style={{
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: "9px", color: "#444",
                            marginTop: "10px", lineHeight: "1.5",
                          }}>
                            THI = {nodeBreakdown.map((c) =>
                              `(${Math.round(c.score)}×${c.weight.toFixed(2)})`
                            ).join(" + ")} = {Math.round(node.thiScore)}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* ── PILL ACTION ROW (below two-column header) ── */}
                  <div style={{
                    display: "flex", gap: "8px", marginTop: "20px", flexWrap: "wrap",
                    borderTop: "1px solid #222", paddingTop: "16px",
                  }}>
                    {totalPlays > 0 && (
                      <PillButton
                        label={`Stocks & Startups (${totalPlays})`}
                        isOpen={cardPanel === "plays"}
                        onClick={() => togglePill(node.id, "plays")}
                      />
                    )}
                    {node.depth < 2 && (
                      <PillButton
                        label="+ More Effects"
                        isOpen={cardPanel === "effects"}
                        onClick={() => togglePill(node.id, "effects")}
                      />
                    )}
                  </div>

                  {/* ── PANEL: Stocks & Startups ── */}
                  {cardPanel === "plays" && totalPlays > 0 && (
                    <div style={{
                      marginTop: "16px", padding: "16px",
                      background: "rgba(255,255,255,0.02)",
                    }}>
                      <div style={{
                        display: "flex", gap: "16px", marginBottom: "14px",
                        borderBottom: "1px solid #1a1a1a", paddingBottom: "8px",
                      }}>
                        {(["stocks", "startups"] as const).map((t) => (
                          <button
                            key={t}
                            onClick={() => setPlaysTabs((prev) => ({ ...prev, [node.id]: t }))}
                            style={{
                              background: "none", border: "none", cursor: "pointer",
                              fontFamily: "var(--font-mono), monospace",
                              fontSize: "10px", letterSpacing: "0.1em",
                              textTransform: "uppercase",
                              color: cardPlaysTab === t ? "var(--text)" : "#333",
                              borderBottom: cardPlaysTab === t ? "1px solid var(--accent)" : "1px solid transparent",
                              paddingBottom: "4px",
                            }}
                          >
                            {t === "stocks" ? `Stocks (${node.equityBets.length})` : `Startups (${node.startupOpportunities.length})`}
                          </button>
                        ))}
                      </div>

                      {/* Stocks */}
                      {cardPlaysTab === "stocks" && (
                        <div style={{ maxHeight: "500px", overflowY: "auto" }}>
                          {node.equityBets.map((bet) => {
                            const efs = efsMap[bet.id];
                            const isBetExpanded = cardExpandedBet === bet.id;
                            return (
                              <div key={bet.id} style={{
                                marginBottom: "12px", paddingBottom: "12px",
                                borderBottom: "1px solid #1a1a1a",
                              }}>
                                {/* Stock header row */}
                                <div
                                  onClick={() => setExpandedBetIds((prev) => ({
                                    ...prev,
                                    [node.id]: isBetExpanded ? null : bet.id,
                                  }))}
                                  style={{ cursor: "pointer" }}
                                >
                                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                                    <a
                                      href={`https://finance.yahoo.com/quote/${bet.ticker}`}
                                      target="_blank" rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                      style={{
                                        fontFamily: "var(--font-mono), monospace",
                                        fontSize: "14px", fontWeight: 700,
                                        color: "var(--accent)", textDecoration: "none",
                                      }}
                                    >
                                      {bet.ticker}
                                    </a>
                                    <span style={{
                                      fontFamily: "var(--font-inter), sans-serif",
                                      fontSize: "12px", color: "#888",
                                    }}>
                                      {bet.companyName}
                                    </span>
                                    <span style={{
                                      fontFamily: "var(--font-mono), monospace",
                                      fontSize: "9px", letterSpacing: "0.06em",
                                      padding: "2px 6px",
                                      border: "1px solid",
                                      borderColor: bet.role === "BENEFICIARY" ? "var(--accent)" : bet.role === "HEADWIND" ? "#666" : "#F59E0B",
                                      color: bet.role === "BENEFICIARY" ? "var(--accent)" : bet.role === "HEADWIND" ? "#666" : "#F59E0B",
                                      textTransform: "uppercase",
                                    }}>
                                      {bet.role}
                                    </span>
                                    {efs && (
                                      <span style={{
                                        fontFamily: "var(--font-mono), monospace",
                                        fontSize: "13px", fontWeight: 700,
                                        color: "#FF4500", marginLeft: "auto",
                                      }}>
                                        {Math.round(efs.efsScore)} / 100
                                      </span>
                                    )}
                                  </div>
                                  <div style={{ fontSize: "11px", color: "#555", lineHeight: "1.4", marginBottom: "6px" }}>
                                    {bet.rationale}
                                  </div>
                                  {efs && (
                                    <GradientBar value={efs.efsScore} height={4} />
                                  )}
                                </div>

                                {/* Expanded EFS sub-score breakdown */}
                                {isBetExpanded && efs && (
                                  <div style={{
                                    marginTop: "12px", padding: "12px",
                                    background: "rgba(0,0,0,0.3)",
                                  }}>
                                    {EFS_COMPONENTS.map((comp) => {
                                      const val = efs[comp.key];
                                      return (
                                        <BreakdownRow
                                          key={comp.key}
                                          label={comp.label}
                                          score={val}
                                          weight={comp.weight}
                                          detail={getEfsDetail(comp.key, efs)}
                                        />
                                      );
                                    })}
                                    {/* EFS formula */}
                                    <div style={{
                                      fontFamily: "var(--font-mono), monospace",
                                      fontSize: "9px", color: "#444",
                                      marginTop: "10px", lineHeight: "1.5",
                                    }}>
                                      EFS = {EFS_COMPONENTS.map((c) =>
                                        `(${Math.round(efs[c.key])}×${c.weight.toFixed(2)})`
                                      ).join(" + ")} = {Math.round(efs.efsScore)}
                                    </div>
                                    {/* Role tag */}
                                    <div style={{
                                      marginTop: "8px",
                                      display: "inline-block",
                                      padding: "3px 8px",
                                      border: "1px solid var(--accent)",
                                      fontFamily: "var(--font-mono), monospace",
                                      fontSize: "9px", letterSpacing: "0.06em",
                                      color: "var(--accent)", textTransform: "uppercase",
                                    }}>
                                      {bet.role}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Startups */}
                      {cardPlaysTab === "startups" && (
                        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
                          {node.startupOpportunities.map((opp) => {
                            const sts = stsMap[opp.id];
                            return (
                              <div key={opp.id} style={{
                                marginBottom: "10px", paddingBottom: "10px",
                                borderBottom: "1px solid #1a1a1a",
                              }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                                  <span style={{
                                    fontFamily: "var(--font-inter), sans-serif",
                                    fontSize: "13px", fontWeight: 600, color: "var(--text)",
                                  }}>
                                    {opp.name}
                                  </span>
                                  <span style={{
                                    fontFamily: "var(--font-mono), monospace",
                                    fontSize: "10px", letterSpacing: "0.06em",
                                    color: opp.timing === "RIGHT_TIMING" ? "var(--accent)" : "#666",
                                    textTransform: "uppercase",
                                  }}>
                                    {opp.timing.replace(/_/g, " ")}
                                  </span>
                                  {sts && (
                                    <span style={{
                                      fontFamily: "var(--font-mono), monospace",
                                      fontSize: "11px", fontWeight: 700,
                                      color: "var(--text)", marginLeft: "auto",
                                    }}>
                                      STS {Math.round(sts.stsScore)} / 100
                                    </span>
                                  )}
                                </div>
                                {sts && (
                                  <div style={{ marginBottom: "4px" }}>
                                    <GradientBar value={sts.stsScore} height={3} />
                                  </div>
                                )}
                                <div style={{ fontSize: "11px", color: "#555", lineHeight: "1.4" }}>
                                  {opp.oneLiner}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── PANEL: More Effects ── */}
                  {cardPanel === "effects" && node.depth < 2 && (
                    <div style={{
                      marginTop: "16px", padding: "16px",
                      background: "rgba(255,255,255,0.02)",
                    }}>
                      {node.children.length === 0 ? (
                        <button
                          onClick={() => handleGenerateEffects(node.depth + 2)}
                          disabled={generatingFor !== null}
                          style={{
                            background: "none", border: "1px solid #333",
                            padding: "8px 16px", cursor: generatingFor ? "wait" : "pointer",
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: "11px", color: ds.textColor,
                            letterSpacing: "0.04em",
                          }}
                        >
                          {generatingFor === `gen-${node.depth + 2}` ? "Generating..." : "+ Expand this thesis"}
                        </button>
                      ) : (
                        <button
                          onClick={() => handleGenerateEffects(node.depth === 0 ? 2 : 3)}
                          disabled={generatingFor !== null}
                          style={{
                            background: "none", border: "1px solid #333",
                            padding: "8px 16px", cursor: generatingFor ? "wait" : "pointer",
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: "11px", color: ds.textColor,
                            letterSpacing: "0.04em",
                          }}
                        >
                          {generatingFor ? "Generating..." : `+ Generate more ${node.depth === 0 ? "2nd" : "3rd"} order effects`}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Helper: EFS detail text ─────────────────────────────────────────────────

function getEfsDetail(key: string, efs: EFSScore): string {
  switch (key) {
    case "revenueAlignmentScore":
      return efs.revenueAlignmentPct != null
        ? `${Math.round(efs.revenueAlignmentPct)}% revenue from ${efs.segmentCount ?? "?"} aligned segments`
        : "Revenue alignment data unavailable";
    case "thesisBetaScore":
      return efs.thesisBetaRaw != null
        ? `Raw beta: ${efs.thesisBetaRaw.toFixed(2)} vs thesis`
        : "Thesis beta data unavailable";
    case "momentumAlignmentScore":
      return efs.momentumDirection
        ? `${efs.momentumDirection} momentum — stock ${efs.stockReturn90d != null ? (efs.stockReturn90d > 0 ? "+" : "") + efs.stockReturn90d.toFixed(1) + "%" : "?"} / THI ${efs.thiDelta90d != null ? (efs.thiDelta90d > 0 ? "+" : "") + efs.thiDelta90d.toFixed(1) : "?"} (90d)`
        : "Momentum data unavailable";
    case "valuationBufferScore":
      return efs.forwardPE != null && efs.sectorMedianPE != null
        ? `Fwd P/E ${efs.forwardPE.toFixed(1)}× vs sector median ${efs.sectorMedianPE.toFixed(1)}×`
        : "Valuation data unavailable";
    case "signalPurityScore":
      return efs.dataSourcesUsed.length > 0
        ? `Sources: ${efs.dataSourcesUsed.join(", ")}`
        : "Signal purity data unavailable";
    default:
      return "";
  }
}

// ─── Helper: Build Tree ─────────────────────────────────────────────────────

function buildTree(thesis: ThesisDetail): CardNode {
  const heroChildren: CardNode[] = [];
  thesis.effects.forEach((effect) => {
    heroChildren.push(buildEffectNode(effect, 1));
  });
  return {
    id: "hero",
    type: "hero",
    depth: 0,
    order: 0,
    title: thesis.title,
    description: thesis.description,
    thiScore: thesis.thi.score,
    equityBets: thesis.equityBets,
    startupOpportunities: thesis.startupOpportunities,
    children: heroChildren,
  };
}

function buildEffectNode(effect: Effect, depth: number): CardNode {
  const children: CardNode[] = (effect.childEffects || []).map((child) =>
    buildEffectNode(child, depth + 1)
  );
  return {
    id: `effect-${effect.id}`,
    type: "effect",
    depth,
    order: effect.order,
    title: effect.title,
    description: effect.description,
    thiScore: effect.thi.score,
    equityBets: effect.equityBets,
    startupOpportunities: effect.startupOpportunities,
    effectId: effect.id,
    children,
  };
}

// ─── Helper: Flatten Tree ───────────────────────────────────────────────────

function flattenTree(root: CardNode): CardNode[] {
  const result: CardNode[] = [root];
  for (const child of root.children) flattenRec(child, result);
  return result;
}

function flattenRec(node: CardNode, result: CardNode[]) {
  result.push(node);
  for (const child of node.children) flattenRec(child, result);
}

// ─── THI Gauge — Canvas, matching original Needle gradient ───────────────────

function THIGauge({ score, size = 160 }: { score: number; size?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const height = Math.round(size * 0.65);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, size, height);

    const cx = size / 2;
    const cy = height - 4;
    const radius = size / 2 - 8;
    const s = Math.max(0, Math.min(100, score));
    const needleAngle = Math.PI + (s / 100) * Math.PI;
    const nx = cx + radius * Math.cos(needleAngle);
    const ny = cy + radius * Math.sin(needleAngle);

    // WEDGE — cubic ease-in orange gradient (exact values from Needle.tsx)
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

    // ARC OUTLINE
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI, false);
    ctx.strokeStyle = "rgba(255,255,255,0.13)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // TICK MARKS at 0, 50, 100
    [0, 50, 100].forEach(v => {
      const a = Math.PI + (v / 100) * Math.PI;
      ctx.beginPath();
      ctx.moveTo(cx + (radius - 8) * Math.cos(a), cy + (radius - 8) * Math.sin(a));
      ctx.lineTo(cx + (radius + 3) * Math.cos(a), cy + (radius + 3) * Math.sin(a));
      ctx.strokeStyle = "rgba(255,255,255,0.22)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // NEEDLE LINE
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(nx, ny);
    ctx.strokeStyle = "#FF4500";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.stroke();

    // PIVOT DOT
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#FF4500";
    ctx.fill();

    // TIP DOT
    ctx.beginPath();
    ctx.arc(nx, ny, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#FF4500";
    ctx.fill();
  }, [score, size, height]);

  return (
    <div style={{ textAlign: "center" }}>
      <canvas
        ref={canvasRef}
        style={{ width: size, height, display: "block" }}
      />
      <div style={{
        fontFamily: "var(--font-mono), monospace",
        fontSize: "20px",
        fontWeight: 700,
        color: "#FF4500",
        marginTop: "2px",
      }}>
        {score}
      </div>
    </div>
  );
}

// ─── Breakdown Row (THI sub-scores + EFS sub-scores) ─────────────────────────

function BreakdownRow({ label, score, weight, detail }: {
  label: string; score: number; weight: number; detail?: string;
}) {
  const pctLabel = `${Math.round(weight * 100)}%`;
  return (
    <div style={{ marginBottom: "10px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "3px" }}>
        <span style={{
          fontFamily: "var(--font-mono), monospace",
          fontSize: "9px", letterSpacing: "0.08em",
          color: "#555", textTransform: "uppercase",
          flex: 1,
        }}>
          {label}
        </span>
        <span style={{
          fontFamily: "var(--font-mono), monospace",
          fontSize: "9px", color: "#444",
        }}>
          {pctLabel}
        </span>
        <span style={{
          fontFamily: "var(--font-mono), monospace",
          fontSize: "12px", fontWeight: 700,
          color: "#FF4500",
        }}>
          &rarr; {Math.round(score)}
        </span>
      </div>
      <GradientBar value={score} height={4} />
      {detail && (
        <div style={{
          fontFamily: "var(--font-inter), sans-serif",
          fontSize: "10px", color: "#444",
          fontStyle: "italic", marginTop: "3px",
          lineHeight: "1.4",
        }}>
          {detail}
        </div>
      )}
    </div>
  );
}

// ─── Pill Button ─────────────────────────────────────────────────────────────

function PillButton({ label, isOpen, onClick }: { label: string; isOpen: boolean; onClick: () => void }) {
  return (
    <button
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      style={{
        display: "inline-flex", alignItems: "center", gap: "4px",
        padding: "6px 14px",
        background: isOpen ? "rgba(255,69,0,0.12)" : "transparent",
        border: isOpen ? "1px solid #FF4500" : "1px solid #333",
        cursor: "pointer",
        fontFamily: "var(--font-mono), monospace",
        fontSize: "10px", fontWeight: 700,
        letterSpacing: "0.06em",
        color: isOpen ? "#FF4500" : "#888",
        textTransform: "uppercase",
      }}
    >
      {isOpen ? "▾" : "▸"} {label}
    </button>
  );
}

// ─── Expandable Text ────────────────────────────────────────────────────────

function ExpandableText({ text, color }: { text: string; color: string }) {
  const [expanded, setExpanded] = useState(false);
  if (!text) return null;
  const isLong = text.length > 200;

  return (
    <div style={{ marginTop: "12px" }}>
      <p style={{
        fontSize: "14px", lineHeight: "1.6", color,
        display: expanded ? "block" : "-webkit-box",
        WebkitLineClamp: expanded ? undefined : 2,
        WebkitBoxOrient: "vertical" as const,
        overflow: expanded ? "visible" : "hidden",
        margin: 0,
      }}>
        {text}
      </p>
      {isLong && (
        <button
          onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
          style={{
            background: "none", border: "none", cursor: "pointer",
            fontFamily: "var(--font-mono), monospace",
            fontSize: "10px", color, letterSpacing: "0.04em",
            marginTop: "4px", padding: 0, opacity: 0.7,
          }}
        >
          {expanded ? "Show less" : "Read more"}
        </button>
      )}
    </div>
  );
}
