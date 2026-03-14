"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  api, ThesisDetail, Effect, EquityBet, StartupOpportunity,
  EquityScoreResult, EFSScore, STSScore, FormulasConfig,
  ScoringBreakdown,
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

type THIComponent = { label: string; score: number; weight: number; detail?: string };

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

function buildTHIComponents(
  bd: import("@/lib/api").ScoringBreakdown,
  weights: { evidence: number; momentum: number; conviction: number },
  stored?: { evidenceExplanation?: string | null; momentumExplanation?: string | null; convictionExplanation?: string | null },
): THIComponent[] {
  // Prefer stored Claude-generated explanations; fall back to computed from feed data
  let evidenceDetail = stored?.evidenceExplanation || undefined;
  if (!evidenceDetail) {
    const evidenceFeeds = [bd.evidence.flow, bd.evidence.structural, bd.evidence.adoption, bd.evidence.policy]
      .filter((d) => d.feeds.length > 0);
    const totalFeeds = evidenceFeeds.reduce((n, d) => n + d.feeds.length, 0);
    const confirming = evidenceFeeds.reduce((n, d) => n + d.feeds.filter((f) => f.confirmingDirection === "confirming").length, 0);
    evidenceDetail = totalFeeds > 0
      ? `${confirming} of ${totalFeeds} feeds confirming across ${evidenceFeeds.length} dimensions`
      : undefined;
  }

  let momDetail = stored?.momentumExplanation || undefined;
  if (!momDetail) {
    momDetail = bd.momentum.hasEnoughHistory
      ? `30d Δ${bd.momentum.thirtyDay.delta != null ? (bd.momentum.thirtyDay.delta > 0 ? "+" : "") + bd.momentum.thirtyDay.delta.toFixed(1) : "?"} · 90d Δ${bd.momentum.ninetyDay.delta != null ? (bd.momentum.ninetyDay.delta > 0 ? "+" : "") + bd.momentum.ninetyDay.delta.toFixed(1) : "?"} · 1yr Δ${bd.momentum.oneYear.delta != null ? (bd.momentum.oneYear.delta > 0 ? "+" : "") + bd.momentum.oneYear.delta.toFixed(1) : "?"}`
      : undefined;
  }

  let convDetail = stored?.convictionExplanation || undefined;
  if (!convDetail) {
    const dq = bd.dataQuality;
    const pctConfirm = dq.agreement.pctConfirming != null ? Math.round(dq.agreement.pctConfirming * 100) : null;
    const raw = `${dq.scoredFeeds}/${dq.totalFeeds} feeds scored` +
      (pctConfirm != null ? ` · ${pctConfirm}% agreement` : "") +
      (dq.sourceQuality.activeSources.length > 0 ? ` · ${dq.sourceQuality.activeSources.join(", ")}` : "");
    convDetail = dq.totalFeeds > 0 ? raw : undefined;
  }

  return [
    { label: "EVIDENCE", score: bd.thiFormula.evidenceScore, weight: weights.evidence, detail: evidenceDetail },
    { label: "MOMENTUM", score: bd.thiFormula.momentumScore, weight: weights.momentum, detail: momDetail },
    { label: "CONVICTION", score: bd.thiFormula.qualityScore, weight: weights.conviction, detail: convDetail },
  ];
}

// EFS sub-score weights — defaults, overridden by formulas.json when loaded
const EFS_COMPONENTS_DEFAULT = [
  { key: "revenueAlignmentScore" as const, label: "REVENUE ALIGNMENT", weightKey: "revenue_alignment", weight: 0.30 },
  { key: "thesisBetaScore" as const, label: "THESIS BETA", weightKey: "thesis_beta", weight: 0.25 },
  { key: "momentumAlignmentScore" as const, label: "MOMENTUM ALIGNMENT", weightKey: "momentum_alignment", weight: 0.20 },
  { key: "valuationBufferScore" as const, label: "VALUATION BUFFER", weightKey: "valuation_buffer", weight: 0.15 },
  { key: "signalPurityScore" as const, label: "SIGNAL PURITY", weightKey: "signal_purity", weight: 0.10 },
];

function getEfsComponents(f: FormulasConfig | null) {
  if (!f) return EFS_COMPONENTS_DEFAULT;
  return EFS_COMPONENTS_DEFAULT.map((c) => ({
    ...c,
    weight: f.efs.weights[c.weightKey] ?? c.weight,
  }));
}

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
  const [stocksSubTabs, setStocksSubTabs] = useState<Record<string, "ai" | "screened">>({});
  const [efsMap, setEfsMap] = useState<Record<string, EFSScore>>({});
  const [stsMap, setStsMap] = useState<Record<string, STSScore>>({});
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState("");
  const [generatingFor, setGeneratingFor] = useState<string | null>(null);
  const [hoveredCardId, setHoveredCardId] = useState<string | null>(null);
  const [expandedBetIds, setExpandedBetIds] = useState<Record<string, string | null>>({});
  const [breakdownMap, setBreakdownMap] = useState<Record<string, THIComponent[]>>({});
  const [fullBreakdownMap, setFullBreakdownMap] = useState<Record<string, ScoringBreakdown>>({});
  const [formulas, setFormulas] = useState<FormulasConfig | null>(null);
  const [revealedPanels, setRevealedPanels] = useState<Set<string>>(new Set());
  const [refreshingFeeds, setRefreshingFeeds] = useState<string | null>(null); // "global" or card id
  const fetchedBreakdowns = useRef<Set<string>>(new Set());

  const fetchAllEfsAndSts = async (t: ThesisDetail) => {
    // Collect all effect IDs (including nested)
    const allEffectIds: string[] = [];
    const collectIds = (effects: Effect[]) => {
      for (const e of effects) {
        allEffectIds.push(e.id);
        if (e.childEffects) collectIds(e.childEffects);
      }
    };
    collectIds(t.effects);

    // Fetch EFS for thesis + all effects in parallel
    const efsPromises = [
      api.getThesisEquityScores(id).catch(() => [] as EquityScoreResult[]),
      ...allEffectIds.map((eid) =>
        api.getEffectEquityScores(eid).catch(() => [] as EquityScoreResult[])
      ),
    ];
    const efsResults = await Promise.all(efsPromises);
    const newEfs: Record<string, EFSScore> = {};
    efsResults.flat().forEach((r) => { if (r.efs) newEfs[r.betId] = r.efs; });
    setEfsMap(newEfs);

    // Fetch STS for all startups
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

  const reloadThesis = async () => {
    const t = await api.getThesis(id);
    setThesis(t);
    await fetchAllEfsAndSts(t);
  };

  useEffect(() => {
    api.getFormulas().then(setFormulas).catch(() => {});
  }, []);

  useEffect(() => {
    if (!id) return;
    api.getThesis(id)
      .then(async (t) => {
        setThesis(t);
        setExpandedIds(new Set(["hero"]));
        // Populate hero breakdown from full scoring API
        const storedExplanations = {
          evidenceExplanation: t.thi.evidence.explanation,
          momentumExplanation: t.thi.momentum.explanation,
          convictionExplanation: t.thi.conviction.explanation,
        };
        api.getScoringBreakdown(id)
          .then((bd) => {
            setFullBreakdownMap((prev) => ({ ...prev, hero: bd }));
            setBreakdownMap((prev) => ({
              ...prev,
              hero: buildTHIComponents(bd, {
                evidence: t.thi.evidence.weight,
                momentum: t.thi.momentum.weight,
                conviction: t.thi.conviction.weight,
              }, storedExplanations),
            }));
          })
          .catch(() => {
            // Fallback with stored explanations only
            setBreakdownMap((prev) => ({
              ...prev,
              hero: [
                { label: "EVIDENCE", score: t.thi.evidence.score, weight: t.thi.evidence.weight, detail: storedExplanations.evidenceExplanation || undefined },
                { label: "MOMENTUM", score: t.thi.momentum.score, weight: t.thi.momentum.weight, detail: storedExplanations.momentumExplanation || undefined },
                { label: "CONVICTION", score: t.thi.conviction.score, weight: t.thi.conviction.weight, detail: storedExplanations.convictionExplanation || undefined },
              ],
            }));
          });
        await fetchAllEfsAndSts(t);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  // Fetch scoring breakdown for effect cards when they become expanded
  useEffect(() => {
    if (!thesis) return;
    // Build a flat map of effectId -> effect thi data for stored explanations
    const effectMap: Record<string, { evidenceExplanation?: string | null; momentumExplanation?: string | null; convictionExplanation?: string | null }> = {};
    const collectEffects = (effects: typeof thesis.effects) => {
      for (const e of effects) {
        effectMap[e.id] = {
          evidenceExplanation: e.thi.evidenceExplanation,
          momentumExplanation: e.thi.momentumExplanation,
          convictionExplanation: e.thi.convictionExplanation,
        };
        if (e.childEffects) collectEffects(e.childEffects);
      }
    };
    collectEffects(thesis.effects);

    expandedIds.forEach((cardId) => {
      if (cardId === "hero") return;
      if (fetchedBreakdowns.current.has(cardId)) return;
      fetchedBreakdowns.current.add(cardId);
      const effectId = cardId.replace("effect-", "");
      const stored = effectMap[effectId];
      api.getEffectScoringBreakdown(effectId)
        .then((bd) => {
          setFullBreakdownMap((prev) => ({ ...prev, [cardId]: bd }));
          setBreakdownMap((prev) => ({
            ...prev,
            [cardId]: buildTHIComponents(bd, {
              evidence: thesis.thi.evidence.weight,
              momentum: thesis.thi.momentum.weight,
              conviction: thesis.thi.conviction.weight,
            }, stored),
          }));
        })
        .catch(() => {
          // Fallback: show stored explanations without computed feed data
          setBreakdownMap((prev) => ({
            ...prev,
            [cardId]: [
              { label: "EVIDENCE", score: 50, weight: thesis.thi.evidence.weight, detail: stored?.evidenceExplanation || undefined },
              { label: "MOMENTUM", score: 50, weight: thesis.thi.momentum.weight, detail: stored?.momentumExplanation || undefined },
              { label: "CONVICTION", score: 50, weight: thesis.thi.conviction.weight, detail: stored?.convictionExplanation || undefined },
            ],
          }));
        });
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

  const handleRefreshFeeds = async (sourceId: string) => {
    setRefreshingFeeds(sourceId);
    try {
      await api.refreshFeeds(id);
      fetchedBreakdowns.current.clear();
      await reloadThesis();
      // Re-fetch breakdowns for expanded cards
      setFullBreakdownMap({});
      setBreakdownMap({});
    } catch {
      setRefreshingFeeds("failed");
      setTimeout(() => setRefreshingFeeds(null), 3000);
      return;
    }
    setRefreshingFeeds(null);
  };

  const togglePill = (cardId: string, panel: string) => {
    const isOpening = activePanels[cardId] !== panel;
    setActivePanels((prev) => ({
      ...prev,
      [cardId]: prev[cardId] === panel ? null : panel,
    }));
    setExpandedBetIds((prev) => ({ ...prev, [cardId]: null }));
    // Trigger EFS bar stagger animation when opening plays panel
    if (isOpening && panel === "plays") {
      setRevealedPanels((prev) => { const n = new Set(prev); n.delete(cardId); return n; });
      requestAnimationFrame(() => {
        setRevealedPanels((prev) => { const n = new Set(prev); n.add(cardId); return n; });
      });
    }
  };

  const flatNodes = flattenTree(tree);
  const EFS_COMPONENTS = getEfsComponents(formulas);

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
          <a
            href="/methodology"
            style={{
              fontFamily: "var(--font-mono), monospace",
              fontSize: "0.75rem", fontWeight: 700,
              letterSpacing: "0.1em", textTransform: "uppercase",
              color: "#888", textDecoration: "none",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#888")}
          >
            METHODOLOGY
          </a>
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

      {/* Refresh feeds bar */}
      <div style={{ padding: "16px 32px 0", maxWidth: "1200px", margin: "0 auto", display: "flex", justifyContent: "flex-end" }}>
        <button
          onClick={() => handleRefreshFeeds("global")}
          disabled={refreshingFeeds !== null}
          onMouseEnter={(e) => { if (!refreshingFeeds) { e.currentTarget.style.color = "#fff"; e.currentTarget.style.borderColor = "#fff"; } }}
          onMouseLeave={(e) => { if (!refreshingFeeds) { e.currentTarget.style.color = refreshingFeeds === "failed" ? "#FF4500" : "#888"; e.currentTarget.style.borderColor = "#444"; } }}
          style={{
            padding: "6px 14px",
            fontFamily: "var(--font-mono), monospace",
            fontSize: "0.7rem", fontWeight: 700,
            letterSpacing: "0.1em", textTransform: "uppercase",
            border: "1px solid #444",
            color: refreshingFeeds === "failed" ? "#FF4500" : "#888",
            background: "transparent",
            cursor: refreshingFeeds ? "wait" : "pointer",
            opacity: refreshingFeeds && refreshingFeeds !== "failed" ? 0.5 : 1,
          }}
        >
          {refreshingFeeds === "global" ? "REFRESHING..." : refreshingFeeds === "failed" ? "REFRESH FAILED" : "\u21BB REFRESH FEEDS"}
        </button>
      </div>

      {/* Tree */}
      <div style={{ padding: "24px 32px 80px", maxWidth: "1200px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "12px" }}>
        {flatNodes.map((node) => {
          const isExpanded = expandedIds.has(node.id);
          const isHovered = hoveredCardId === node.id;
          const ds = getDepthStyle(node.depth);
          const totalPlays = node.equityBets.length + node.startupOpportunities.length;
          const nodeBreakdown = breakdownMap[node.id];
          const cardPanel = activePanels[node.id] || null;
          const cardPlaysTab = playsTabs[node.id] || "stocks";
          const cardExpandedBet = expandedBetIds[node.id] || null;

          return (
            <div
              key={node.id}
              style={{
                marginLeft: `${node.depth * DEPTH_INDENT}px`,
                marginBottom: "0",
              }}
            >
              <div
                onMouseEnter={() => setHoveredCardId(node.id)}
                onMouseLeave={() => setHoveredCardId(null)}
                style={{
                  background: isExpanded ? "#161616" : isHovered ? "#1a1a1a" : ds.bg,
                  border: isExpanded ? "2px solid #FF4500" : isHovered ? "2px solid #FF4500" : "1px solid #222",
                  maxHeight: isExpanded ? "2000px" : "52px",
                  overflow: isExpanded ? "visible" : "hidden",
                  transition: isExpanded
                    ? "max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, background 0.2s ease"
                    : "max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, background 0.2s ease",
                }}
              >
                {/* ── HEADER ROW ── */}
                <div
                  onClick={() => toggleCard(node.id)}
                  style={{
                    position: "relative",
                    padding: "12px 20px",
                    height: "48px", cursor: "pointer",
                  }}
                >
                  {/* Collapsed content: order + title + score */}
                  <div style={{
                    display: "flex", alignItems: "center", gap: "12px",
                    position: "absolute", inset: 0,
                    padding: "12px 20px",
                    opacity: isExpanded ? 0 : 1,
                    transition: isExpanded
                      ? "opacity 0.15s ease 0.1s"
                      : "opacity 0.2s ease 0.15s",
                  }}>
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
                  {/* Expanded content: collapse button */}
                  <div style={{
                    display: "flex", alignItems: "center", justifyContent: "flex-end",
                    position: "absolute", inset: 0,
                    padding: "12px 20px",
                    opacity: isExpanded ? 1 : 0,
                    transition: isExpanded
                      ? "opacity 0.15s ease"
                      : "opacity 0.15s ease",
                    pointerEvents: isExpanded ? "auto" as const : "none" as const,
                  }}>
                    <span style={{
                      fontFamily: "var(--font-mono), monospace",
                      fontSize: "10px", color: "#444", letterSpacing: "0.04em",
                    }}>
                      ▴ Collapse
                    </span>
                  </div>
                </div>

                {/* ── EXPANDED CONTENT (revealed by max-height) ── */}
                <div style={{
                  padding: "0 29px 25px",
                  opacity: isExpanded ? 1 : 0,
                  pointerEvents: isExpanded ? "auto" as const : "none" as const,
                  transition: "opacity 0.15s ease",
                }}>

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

                    {/* RIGHT COLUMN ~40% — THI gauge + breakdown */}
                    <div style={{ flex: "0 0 40%", minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "center", marginBottom: "16px" }}>
                        <THIGauge score={Math.round(node.thiScore)} size={160} animate />
                      </div>
                      <THIBreakdownPanel
                        bd={fullBreakdownMap[node.id] || null}
                        thiScore={Math.round(node.thiScore)}
                        nodeBreakdown={nodeBreakdown}
                      />
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
                    <button
                      onClick={(e) => { e.stopPropagation(); handleRefreshFeeds(node.id); }}
                      disabled={refreshingFeeds !== null}
                      onMouseEnter={(e) => { if (!refreshingFeeds) { e.currentTarget.style.color = "#fff"; e.currentTarget.style.borderColor = "#fff"; } }}
                      onMouseLeave={(e) => { if (!refreshingFeeds) { e.currentTarget.style.color = refreshingFeeds === "failed" ? "#FF4500" : "#888"; e.currentTarget.style.borderColor = "#444"; } }}
                      style={{
                        display: "inline-flex", alignItems: "center", gap: "4px",
                        padding: "6px 14px",
                        fontFamily: "var(--font-mono), monospace",
                        fontSize: "0.7rem", fontWeight: 700,
                        letterSpacing: "0.1em", textTransform: "uppercase",
                        border: "1px solid #444",
                        color: refreshingFeeds === "failed" ? "#FF4500" : "#888",
                        background: "transparent",
                        cursor: refreshingFeeds ? "wait" : "pointer",
                        opacity: refreshingFeeds && refreshingFeeds !== "failed" ? 0.5 : 1,
                      }}
                    >
                      {refreshingFeeds === node.id ? "REFRESHING..." : refreshingFeeds === "failed" ? "REFRESH FAILED" : "\u21BB REFRESH FEEDS"}
                    </button>
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
                      {cardPlaysTab === "stocks" && (() => {
                        const activeStocksSubTab = stocksSubTabs[node.id] || "ai";
                        const aiBets = node.equityBets.filter((b) => !b.source || b.source === "ai");
                        const screenedBets = node.equityBets.filter((b) => b.source === "screened");

                        const sortByEfs = (bets: EquityBet[]) =>
                          [...bets].sort((a, b) => (efsMap[b.id]?.efsScore ?? 0) - (efsMap[a.id]?.efsScore ?? 0));

                        const activeBets = sortByEfs(activeStocksSubTab === "ai" ? aiBets : screenedBets);
                        const top3Ids = new Set(activeBets.slice(0, 3).map((b) => b.id));

                        return (
                          <div>
                            <div style={{
                              display: "flex", gap: "0", marginBottom: "12px",
                              borderBottom: "1px solid #1a1a1a",
                            }}>
                              {(["ai", "screened"] as const).map((sub) => {
                                const count = sub === "ai" ? aiBets.length : screenedBets.length;
                                const isActive = activeStocksSubTab === sub;
                                return (
                                  <button
                                    key={sub}
                                    onClick={() => setStocksSubTabs((prev) => ({ ...prev, [node.id]: sub }))}
                                    style={{
                                      background: "none", border: "none", cursor: "pointer",
                                      fontFamily: "var(--font-mono), monospace",
                                      fontSize: "9px", letterSpacing: "0.1em",
                                      textTransform: "uppercase",
                                      color: isActive ? "var(--accent)" : "#444",
                                      borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                                      padding: "6px 12px 6px 0",
                                      marginRight: "12px",
                                    }}
                                  >
                                    {sub === "ai" ? `AI Suggested (${count})` : `Screened (${count})`}
                                  </button>
                                );
                              })}
                            </div>

                            {activeBets.length === 0 ? (
                              <div style={{
                                fontFamily: "var(--font-mono), monospace",
                                fontSize: "11px", color: "#444",
                                padding: "12px 0",
                              }}>
                                {activeStocksSubTab === "ai" ? "No AI suggested stocks yet." : "No screened stocks yet."}
                              </div>
                            ) : (
                              <div style={{ maxHeight: "500px", overflowY: "auto" }}>
                                {activeBets.map((bet, betIdx) => {
                                  const efs = efsMap[bet.id];
                                  const isBetExpanded = cardExpandedBet === bet.id;
                                  const barsRevealed = revealedPanels.has(node.id);
                                  const isTop3 = top3Ids.has(bet.id);
                                  return (
                                    <div key={bet.id} style={{
                                      marginBottom: "12px", paddingBottom: "12px",
                                      borderBottom: "1px solid #1a1a1a",
                                    }}>
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
                                          {isTop3 && (
                                            <span style={{
                                              fontFamily: "var(--font-mono), monospace",
                                              fontSize: "8px", letterSpacing: "0.08em",
                                              padding: "1px 5px",
                                              border: "1px solid var(--accent)",
                                              color: "var(--accent)",
                                              textTransform: "uppercase",
                                            }}>
                                              TOP 3
                                            </span>
                                          )}
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
                                          <GradientBar value={efs.efsScore} height={4} animate={barsRevealed} delay={betIdx * 80} />
                                        )}
                                      </div>

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
                                          <div style={{
                                            fontFamily: "var(--font-mono), monospace",
                                            fontSize: "9px", color: "#444",
                                            marginTop: "10px", lineHeight: "1.5",
                                          }}>
                                            EFS = {EFS_COMPONENTS.map((c) =>
                                              `(${Math.round(efs[c.key])}×${c.weight.toFixed(2)})`
                                            ).join(" + ")} = {Math.round(efs.efsScore)}
                                          </div>
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
                          </div>
                        );
                      })()}

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
              </div>
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

function THIGauge({ score, size = 160, animate }: { score: number; size?: number; animate?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const displayScore = useRef(0);
  const height = Math.round(size * 0.65);
  const [displayNum, setDisplayNum] = useState(animate ? 0 : score);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = height * dpr;

    const cx = size / 2;
    const cy = height - 4;
    const radius = size / 2 - 8;

    const drawGauge = (s: number) => {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, size, height);
      const clamped = Math.max(0, Math.min(100, s));
      const needleAngle = Math.PI + (clamped / 100) * Math.PI;
      const nx = cx + radius * Math.cos(needleAngle);
      const ny = cy + radius * Math.sin(needleAngle);

      // WEDGE
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

      // TICK MARKS
      [0, 50, 100].forEach(v => {
        const a = Math.PI + (v / 100) * Math.PI;
        ctx.beginPath();
        ctx.moveTo(cx + (radius - 8) * Math.cos(a), cy + (radius - 8) * Math.sin(a));
        ctx.lineTo(cx + (radius + 3) * Math.cos(a), cy + (radius + 3) * Math.sin(a));
        ctx.strokeStyle = "rgba(255,255,255,0.22)";
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      // NEEDLE
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
    };

    if (!animate) {
      drawGauge(score);
      setDisplayNum(score);
      return;
    }

    // Animate from current displayScore to target over 1.2s ease-out
    const from = displayScore.current;
    const to = score;
    const duration = 1200;
    let startTime: number | null = null;
    let rafId: number;

    const step = (ts: number) => {
      if (!startTime) startTime = ts;
      const elapsed = ts - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      const current = from + (to - from) * eased;
      drawGauge(current);
      displayScore.current = current;
      setDisplayNum(Math.round(current));
      if (progress < 1) rafId = requestAnimationFrame(step);
    };
    rafId = requestAnimationFrame(step);

    return () => cancelAnimationFrame(rafId);
  }, [score, size, height, animate]);

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
        {displayNum}
      </div>
    </div>
  );
}

// ─── THI Breakdown Panel — Three-Column Layout ──────────────────────────────

function THIBreakdownPanel({ bd, thiScore, nodeBreakdown }: {
  bd: ScoringBreakdown | null;
  thiScore: number;
  nodeBreakdown?: THIComponent[];
}) {
  // Use full breakdown if available, fall back to nodeBreakdown
  const rows = bd
    ? [
        { label: "EVIDENCE", weight: 0.50, score: bd.thiFormula.evidenceScore, detail: nodeBreakdown?.find((r) => r.label === "EVIDENCE")?.detail },
        { label: "MOMENTUM", weight: 0.30, score: bd.thiFormula.momentumScore, detail: nodeBreakdown?.find((r) => r.label === "MOMENTUM")?.detail },
        { label: "DATA QUALITY", weight: 0.20, score: bd.thiFormula.qualityScore, detail: nodeBreakdown?.find((r) => r.label === "CONVICTION")?.detail },
      ]
    : nodeBreakdown
      ? nodeBreakdown.map((r) => ({
          label: r.label === "CONVICTION" ? "DATA QUALITY" : r.label,
          weight: r.weight,
          score: r.score,
          detail: r.detail,
        }))
      : null;

  if (!rows) return null;

  // Detect momentum no-history state
  const momRow = rows.find((r) => r.label === "MOMENTUM");
  const momNoHistory = bd
    ? (!bd.momentum.hasEnoughHistory ||
       bd.thiFormula.momentumScore === 0 ||
       (bd.momentum.thirtyDay.delta === bd.momentum.ninetyDay.delta &&
        bd.momentum.ninetyDay.delta === bd.momentum.oneYear.delta))
    : (momRow?.score === 0);

  // Evidence sub-dimensions (only if bd available and feeds exist)
  const evidenceDims = bd ? [
    { key: "flow" as const, label: "FLOW", weight: 0.35 },
    { key: "structural" as const, label: "STRUCTURAL", weight: 0.30 },
    { key: "adoption" as const, label: "ADOPTION", weight: 0.20 },
    { key: "policy" as const, label: "POLICY", weight: 0.15 },
  ].filter((d) => bd.evidence[d.key].feeds.length > 0) : [];

  return (
    <div>
      {rows.map((row) => (
        <div key={row.label} style={{ marginBottom: "12px" }}>
          <div style={{
            display: "flex", justifyContent: "space-between", alignItems: "center",
            marginBottom: "4px",
          }}>
            <span style={{
              fontFamily: "var(--font-mono), monospace",
              fontSize: "0.7rem", letterSpacing: "0.08em",
              textTransform: "uppercase" as const,
              color: "#888",
            }}>
              {row.label} <span style={{ color: "#555" }}>{Math.round(row.weight * 100)}%</span>
            </span>
            <span style={{
              fontFamily: "var(--font-mono), monospace",
              fontSize: "1rem", fontWeight: 700,
              color: "#FF4500",
            }}>
              {Math.round(row.score)}
            </span>
          </div>
          <GradientBar value={row.score} height={3} />
          {row.label === "MOMENTUM" && momNoHistory ? (
            <div style={{
              fontFamily: "var(--font-inter), sans-serif",
              fontSize: "0.7rem", color: "#555", fontStyle: "italic",
              marginTop: "4px", lineHeight: 1.5,
            }}>
              Builds after first feed refresh
            </div>
          ) : row.detail ? (
            <div style={{
              fontFamily: "var(--font-inter), sans-serif",
              fontSize: "0.7rem", color: "#666",
              fontStyle: "italic", marginTop: "4px", lineHeight: 1.4,
            }}>
              {row.detail}
            </div>
          ) : null}

          {/* Evidence sub-dimensions inline */}
          {row.label === "EVIDENCE" && evidenceDims.length > 0 && (
            <div style={{ marginTop: "8px", paddingLeft: "8px", borderLeft: "1px solid #1a1a1a" }}>
              {evidenceDims.map((d) => {
                const dim = bd!.evidence[d.key];
                return (
                  <div key={d.key} style={{ marginBottom: "6px" }}>
                    <div style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      marginBottom: "2px",
                    }}>
                      <span style={{
                        fontFamily: "var(--font-mono), monospace",
                        fontSize: "8px", letterSpacing: "0.06em",
                        textTransform: "uppercase" as const, color: "#444",
                      }}>
                        {d.label} ({Math.round(d.weight * 100)}%)
                      </span>
                      <span style={{
                        fontFamily: "var(--font-mono), monospace",
                        fontSize: "10px", fontWeight: 700, color: "#FF4500",
                      }}>
                        {dim.score != null ? Math.round(dim.score) : "—"}
                      </span>
                    </div>
                    <GradientBar value={dim.score ?? 0} height={2} />
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ))}

      {/* Formula row */}
      {bd && (
        <div style={{
          borderTop: "1px solid #1a1a1a",
          paddingTop: "8px", marginTop: "4px",
          fontFamily: "var(--font-mono), monospace",
          fontSize: "8px", color: "#444", lineHeight: 1.5,
        }}>
          THI = ({Math.round(bd.thiFormula.evidenceScore)}&times;.50) + ({Math.round(bd.thiFormula.momentumScore)}&times;.30) + ({Math.round(bd.thiFormula.qualityScore)}&times;.20) = <span style={{ color: "#FF4500", fontWeight: 700 }}>{thiScore}</span>
        </div>
      )}
    </div>
  );
}

// ─── Breakdown Row (THI sub-scores + EFS sub-scores) ─────────────────────────

function BreakdownRow({ label, score, weight, detail }: {
  label: string; score: number; weight: number; detail?: string;
}) {
  const pctLabel = `${Math.round(weight * 100)}%`;
  return (
    <div style={{ marginBottom: "12px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
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
      <GradientBar value={score} height={3} />
      {detail && (
        <div style={{
          fontFamily: "var(--font-inter), sans-serif",
          fontSize: "0.7rem", color: "#666",
          fontStyle: "italic", marginTop: "4px",
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
        fontSize: "0.95rem", lineHeight: "1.6", color: "#ccc",
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
