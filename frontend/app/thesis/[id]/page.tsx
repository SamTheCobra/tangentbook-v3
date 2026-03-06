"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import EquityBetCard from "@/components/EquityBetCard";
import StartupCard from "@/components/StartupCard";
import ErrorBoundary from "@/components/ErrorBoundary";
import ConvictionSlider from "@/components/ConvictionSlider";
import TrashIcon from "@/components/TrashIcon";
import {
  api,
  ThesisDetail,
  Effect,
  ScoringBreakdown,
  EvidenceDimension,
  ScoringBreakdownFeed,
  Portfolio,
  EquityScoreResult,
  EFSScore,
  STSScore,
} from "@/lib/api";

export default function ThesisDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [breakdown, setBreakdown] = useState<ScoringBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [scoringOpen, setScoringOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<"bets" | "startups">("bets");
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [portfolioOpen, setPortfolioOpen] = useState(false);
  const [efsScores, setEfsScores] = useState<EquityScoreResult[]>([]);
  const [stsMap, setStsMap] = useState<Record<string, STSScore>>({});

  const reloadThesis = async () => {
    const [t, b, p, efs] = await Promise.all([
      api.getThesis(id),
      api.getScoringBreakdown(id),
      api.getPortfolio(id).catch(() => null),
      api.getThesisEquityScores(id).catch(() => [] as EquityScoreResult[]),
    ]);
    setThesis(t);
    setBreakdown(b);
    if (p) setPortfolio(p);
    setEfsScores(efs);
    // Fetch STS for startups
    if (t.startupOpportunities.length > 0) {
      const stsResults = await Promise.all(
        t.startupOpportunities.map((opp) =>
          api.getStartupSTS(opp.id).catch(() => null)
        )
      );
      const newStsMap: Record<string, STSScore> = {};
      stsResults.forEach((r) => {
        if (r?.sts) newStsMap[r.oppId] = r.sts;
      });
      setStsMap(newStsMap);
    }
  };

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getThesis(id),
      api.getScoringBreakdown(id).catch(() => null),
      api.getPortfolio(id).catch(() => null),
      api.getThesisEquityScores(id).catch(() => [] as EquityScoreResult[]),
    ])
      .then(async ([t, b, p, efs]) => {
        setThesis(t);
        setBreakdown(b);
        if (p) setPortfolio(p);
        setEfsScores(efs);
        // Fetch STS for startups
        if (t.startupOpportunities.length > 0) {
          const stsResults = await Promise.all(
            t.startupOpportunities.map((opp) =>
              api.getStartupSTS(opp.id).catch(() => null)
            )
          );
          const newStsMap: Record<string, STSScore> = {};
          stsResults.forEach((r) => {
            if (r?.sts) newStsMap[r.oppId] = r.sts;
          });
          setStsMap(newStsMap);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div
          className="px-12 py-8"
          style={{
            color: "var(--text-muted)",
            fontFamily: "JetBrains Mono, monospace",
          }}
        >
          ————————
        </div>
      </main>
    );
  }

  if (!thesis) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div
          className="px-12 py-8"
          style={{ color: "var(--text-muted)", fontSize: "15px" }}
        >
          Thesis not found.
        </div>
      </main>
    );
  }

  const handleConviction = async (score: number, note?: string) => {
    await api.updateConviction(id, score, note);
    await reloadThesis();
  };

  const handleRefreshFeeds = async () => {
    setRefreshing(true);
    try {
      await api.refreshFeeds(id);
      await reloadThesis();
    } catch (e) {
      console.error("Feed refresh failed:", e);
    } finally {
      setRefreshing(false);
    }
  };

  const eScore = Math.round(thesis.thi.evidence.score);
  const mScore = Math.round(thesis.thi.momentum.score);
  const cScore = Math.round(thesis.thi.conviction.score);
  const eContrib = (eScore * 0.50).toFixed(1);
  const mContrib = (mScore * 0.30).toFixed(1);
  const cContrib = (cScore * 0.20).toFixed(1);
  const thiTotal = (eScore * 0.50 + mScore * 0.30 + cScore * 0.20).toFixed(1);

  return (
    <ErrorBoundary>
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div className="px-12 py-8">
          {/* ── BREADCRUMB ── */}
          <div className="flex items-center gap-2 mb-6">
            <Link
              href="/"
              className="uppercase hover:underline"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                textUnderlineOffset: "3px",
                fontSize: "13px",
              }}
            >
              TANGENTBOOK
            </Link>
            <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>
              /
            </span>
            <span
              className="uppercase"
              style={{
                color: "var(--text)",
                letterSpacing: "0.08em",
                fontSize: "13px",
              }}
            >
              {thesis.title}
            </span>
          </div>

          {/* ══════════════════════════════════════════════════
              SECTION 1: HERO
              ══════════════════════════════════════════════════ */}
          <div className="flex gap-12 mb-6">
            <div className="flex-1">
              <h1
                className="font-bold uppercase text-3xl mb-2"
                style={{
                  color: "var(--text)",
                  letterSpacing: "-0.04em",
                  wordWrap: "break-word",
                  overflowWrap: "break-word",
                }}
              >
                {thesis.title}
              </h1>
              <p
                className="mb-4"
                style={{
                  color: "var(--text-muted)",
                  lineHeight: "1.6",
                  fontSize: "16px",
                }}
              >
                {thesis.description}
              </p>
              <div className="flex items-center gap-6 flex-wrap">
                <div className="flex items-center gap-2">
                  <span
                    className="uppercase"
                    style={{
                      color: "var(--text-muted)",
                      letterSpacing: "0.08em",
                      fontSize: "13px",
                    }}
                  >
                    HORIZON
                  </span>
                  <span
                    style={{
                      color: "var(--text)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "15px",
                    }}
                  >
                    {thesis.timeHorizon}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className="uppercase"
                    style={{
                      color: "var(--text-muted)",
                      letterSpacing: "0.08em",
                      fontSize: "13px",
                    }}
                  >
                    DIRECTION
                  </span>
                  <span
                    style={{
                      color: "var(--text)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "15px",
                    }}
                  >
                    {thesis.thi.direction.toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="mt-4">
                <ConvictionSlider
                  score={thesis.userConviction.score}
                  history={
                    thesis.userConviction.history?.map((h) => h.score) || []
                  }
                  onUpdate={handleConviction}
                  divergenceWarning={thesis.userConviction.divergenceWarning}
                />
              </div>
            </div>
            <div className="flex-shrink-0">
              <Needle
                score={thesis.thi.score}
                size="lg"
                label="THESIS HEALTH INDEX"
              />
              <div style={{ fontFamily: "JetBrains Mono, monospace", marginTop: "8px", lineHeight: "1.6" }}>
                <div style={{ fontSize: "12px", color: "#5A5A5A" }}>
                  THI = (Evidence × 0.50) + (Momentum × 0.30) + (Quality × 0.20)
                </div>
                <div style={{ fontSize: "12px", color: "#5A5A5A" }}>
                  THI = ({eScore} × 0.50) + ({mScore} × 0.30) + ({cScore} × 0.20)
                </div>
                <div style={{ fontSize: "12px", color: "#5A5A5A" }}>
                  THI = {eContrib} + {mContrib} + {cContrib}
                </div>
                <div style={{ fontSize: "14px", color: "#FF4500", fontWeight: "bold" }}>
                  THI = {thiTotal} → rounded to {Math.round(Number(thiTotal))}
                </div>
              </div>
            </div>
          </div>

          {/* Collapsible scoring breakdown trigger */}
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setScoringOpen(!scoringOpen)}
              className="uppercase flex items-center gap-2"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "13px",
              }}
            >
              HOW IS THIS SCORED?{" "}
              <span style={{ fontSize: "12px" }}>
                {scoringOpen ? "▲" : "▾"}
              </span>
            </button>
            <button
              onClick={handleRefreshFeeds}
              disabled={refreshing}
              className="uppercase px-3 py-1 border"
              style={{
                color: refreshing ? "var(--text-muted)" : "var(--accent)",
                borderColor: refreshing ? "var(--border)" : "var(--accent)",
                letterSpacing: "0.08em",
                background: "none",
                cursor: refreshing ? "not-allowed" : "pointer",
                fontSize: "11px",
                opacity: refreshing ? 0.5 : 1,
              }}
            >
              {refreshing ? "REFRESHING..." : "REFRESH FEEDS ↺"}
            </button>
          </div>

          {/* ══════════════════════════════════════════════════
              SECTION 2: SCORING BREAKDOWN (collapsible)
              ══════════════════════════════════════════════════ */}
          {scoringOpen && !breakdown && (
            <div className="mb-4 p-3 border" style={{ borderColor: "var(--text-muted)", color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>
              Loading scoring data...
            </div>
          )}
          {scoringOpen && breakdown && (
            <div className="mb-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-4">
                <ErrorBoundary><EvidenceColumn breakdown={breakdown} /></ErrorBoundary>
                <ErrorBoundary><MomentumColumn breakdown={breakdown} /></ErrorBoundary>
                <ErrorBoundary><DataQualityColumn breakdown={breakdown} /></ErrorBoundary>
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════════
              SECTION 2.5: PORTFOLIO TRACKER
              ══════════════════════════════════════════════════ */}
          <PortfolioTracker
            thesisId={thesis.id}
            portfolio={portfolio}
            isOpen={portfolioOpen}
            onToggle={() => setPortfolioOpen(!portfolioOpen)}
            onReload={reloadThesis}
          />

          <div
            className="mb-8"
            style={{ borderTop: "1px solid var(--border)" }}
          />

          {/* ══════════════════════════════════════════════════
              SECTION 3: BETS + OPPORTUNITIES (tabbed)
              ══════════════════════════════════════════════════ */}
          {(thesis.equityBets.length > 0 ||
            thesis.startupOpportunities.length > 0) && (
            <>
              <div className="flex items-center gap-6 mb-4">
                <TabButton
                  label={`EQUITY BETS (${thesis.equityBets.length})`}
                  active={activeTab === "bets"}
                  onClick={() => setActiveTab("bets")}
                />
                <TabButton
                  label={`STARTUP OPPORTUNITIES (${thesis.startupOpportunities.length})`}
                  active={activeTab === "startups"}
                  onClick={() => setActiveTab("startups")}
                />
              </div>
              {activeTab === "bets" && (() => {
                const efsMap: Record<string, EFSScore> = {};
                efsScores.forEach((r) => {
                  if (r.efs) efsMap[r.betId] = r.efs;
                });
                const ROLE_ORDER: Record<string, number> = { BENEFICIARY: 0, HEADWIND: 1, CANARY: 2 };
                const sortedBets = [...thesis.equityBets].sort((a, b) => {
                  const roleA = ROLE_ORDER[a.role] ?? 9;
                  const roleB = ROLE_ORDER[b.role] ?? 9;
                  if (roleA !== roleB) return roleA - roleB;
                  return (efsMap[b.id]?.efsScore ?? -1) - (efsMap[a.id]?.efsScore ?? -1);
                });
                const rankMap: Record<string, number> = {};
                sortedBets.forEach((bet, i) => {
                  if (efsMap[bet.id]) rankMap[bet.id] = i + 1;
                });
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                    {sortedBets.map((bet) => (
                      <EquityBetCard
                        key={bet.id}
                        bet={bet}
                        efs={efsMap[bet.id] ?? null}
                        rank={rankMap[bet.id]}
                      />
                    ))}
                  </div>
                );
              })()}
              {activeTab === "startups" && (() => {
                const sortedOpps = [...thesis.startupOpportunities].sort((a, b) => {
                  const stsA = stsMap[a.id]?.stsScore ?? -1;
                  const stsB = stsMap[b.id]?.stsScore ?? -1;
                  return stsB - stsA;
                });
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                    {sortedOpps.map((opp) => (
                      <StartupCard
                        key={opp.id}
                        opportunity={opp}
                        sts={stsMap[opp.id] ?? null}
                      />
                    ))}
                  </div>
                );
              })()}
            </>
          )}

          {/* ══════════════════════════════════════════════════
              SECTION 5: EFFECT THUMBNAILS
              ══════════════════════════════════════════════════ */}
          {thesis.effects.length > 0 && (
            <>
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="uppercase"
                  style={{
                    color: "var(--text-muted)",
                    letterSpacing: "0.08em",
                    fontSize: "13px",
                  }}
                >
                  2ND ORDER EFFECTS ({thesis.effects.length})
                </h3>
                <AddEffectButton thesisId={thesis.id} onCreated={reloadThesis} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
                {thesis.effects.map((effect) => (
                  <EffectThumbnail
                    key={effect.id}
                    effect={effect}
                    thesisId={thesis.id}
                    onDeleted={reloadThesis}
                  />
                ))}
              </div>
              <div className="mb-8" />
            </>
          )}
        </div>
      </main>
    </ErrorBoundary>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCORING BREAKDOWN COLUMNS
   ═══════════════════════════════════════════════════════════════════════════ */

function EvidenceColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const ev = breakdown.evidence;
  const dims = [
    { key: "flow", label: "Flow signals", data: ev.flow },
    { key: "structural", label: "Structural signals", data: ev.structural },
    { key: "adoption", label: "Adoption signals", data: ev.adoption },
    { key: "policy", label: "Policy signals", data: ev.policy },
  ];

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="mb-3">
        <div className="flex items-center justify-between">
          <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
            EVIDENCE SCORE: {Math.round(ev.score)} / 100
          </span>
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
          Weight in final THI: 50%
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>
          Contribution to THI: {Math.round(ev.score)} × 0.50 = {ev.contribution} points
        </div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={ev.score} size="sm" label="" animated={true} />
      </div>
      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "8px", fontStyle: "italic" }}>
        How it&apos;s calculated:
      </div>
      {dims.map(({ key, label, data }) => {
        const dimScore = data.score != null ? Math.round(data.score) : 0;
        const contrib = ev.dimContributions?.[key] ?? 0;
        return (
          <div key={key} className="mb-1" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px" }}>
            <span style={{ color: "var(--text-muted)" }}>
              {label} ({(data.weight * 100).toFixed(0)}% of Evidence) →{" "}
            </span>
            <span style={{ color: dimScore > 0 ? "var(--accent)" : "var(--text-muted)" }}>
              score {dimScore}
            </span>
            <span style={{ color: "var(--text-muted)" }}>
              {" "}→ contributes {contrib.toFixed(1)} pts
            </span>
          </div>
        );
      })}
      <div style={{ borderTop: "1px solid var(--border)", margin: "8px 0" }} />
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
        Evidence = {ev.formula} = {Math.round(ev.score)}
      </div>
      <div style={{ borderTop: "1px solid var(--border)", margin: "12px 0" }} />
      <div className="flex flex-col gap-4">
        {dims.map(({ key, label, data }) => (
          <DimensionBlock key={key} label={label} dim={data} />
        ))}
      </div>
    </div>
  );
}

function DimensionBlock({
  label,
  dim,
}: {
  label: string;
  dim: EvidenceDimension;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}>
          {label}
        </span>
        <span
          style={{
            color: dim.score != null ? "var(--accent)" : "var(--text-muted)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "13px",
          }}
        >
          {dim.score != null ? `${Math.round(dim.score)} / 100` : "—"}
        </span>
      </div>
      <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "6px" }}>
        {dim.description}
      </p>
      {dim.feeds.length > 0 ? (
        <div style={{ fontSize: "11px" }}>
          {dim.feeds.map((f) => (
            <FeedRow key={f.name} feed={f} />
          ))}
        </div>
      ) : (
        <span style={{ color: "var(--text-muted)", fontSize: "11px", fontStyle: "italic" }}>
          No {label.toLowerCase()} feeds configured
        </span>
      )}
    </div>
  );
}

function FeedRow({ feed: f }: { feed: ScoringBreakdownFeed }) {
  const statusLabel = f.status === "live" ? "LIVE" : f.status === "stale" ? "STALE" : f.status === "degraded" ? "DEGRADED" : "OFFLINE";
  const statusColor = f.status === "live" ? "var(--status-live)" : f.status === "stale" ? "#F59E0B" : "#EF4444";
  const sourceLabel = f.source === "FRED" ? `FRED: ${f.seriesId}` : f.source === "GTRENDS" ? `GTrends: "${f.keyword}"` : f.source || "";

  // Live feed with data
  if (f.status === "live" && f.normalizedScore != null) {
    return (
      <div className="mb-3 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text)", fontWeight: "bold" }}>
          {f.name} ({sourceLabel})
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "3px" }}>
          <span style={{ color: "var(--text)" }}>Current: {f.formattedValue || "—"}</span>
          <span style={{ color: "var(--text-muted)" }}>{" "}|{" "}</span>
          <span style={{ color: "var(--accent)" }}>Score: {f.normalizedScore} / 100</span>
        </div>
        {(f.pctVs1yr != null || f.pctVs5yrAvg != null) && (
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "10px", marginTop: "2px", color: "var(--text-muted)" }}>
            {f.pctVs1yr != null && (
              <span>
                1yr ago → <span style={{ color: f.pctVs1yr >= 0 ? "#FF4500" : "var(--text-muted)" }}>
                  {f.pctVs1yr >= 0 ? "UP" : "DOWN"} {Math.abs(f.pctVs1yr)}%
                </span>
                {f.confirmingDirection && (
                  <span> — {f.pctVs1yr >= 0 === (f.confirmingDirection === "higher") ? "CONFIRMING" : "REFUTING"}{" "}
                    ({f.confirmingDirection} = confirming)
                  </span>
                )}
              </span>
            )}
          </div>
        )}
        {f.lastUpdated && (
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "10px", marginTop: "2px", color: "var(--text-muted)" }}>
            Last updated: {new Date(f.lastUpdated).toLocaleString()}{" "}|{" "}Status: <span style={{ color: statusColor }}>{statusLabel}</span>
          </div>
        )}
      </div>
    );
  }

  // Degraded feed
  if (f.status === "degraded" || f.status === "stale") {
    return (
      <div className="mb-3 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
          {f.name} ({sourceLabel})
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "3px", color: statusColor }}>
          {f.formattedValue ? (
            <>Last known: {f.formattedValue} — DATA {statusLabel}</>
          ) : (
            <>No data fetched yet. Click REFRESH FEEDS to pull latest.</>
          )}
        </div>
        {f.normalizedScore != null && (
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "10px", marginTop: "2px", color: "var(--text-muted)" }}>
            Score held at last known value: {f.normalizedScore}. Marked {statusLabel}.
          </div>
        )}
      </div>
    );
  }

  // No data yet
  return (
    <div className="mb-3 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
        {f.name} ({sourceLabel})
      </div>
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "3px", color: "var(--text-muted)" }}>
        No data fetched yet. Click REFRESH FEEDS to pull latest.
      </div>
    </div>
  );
}

function MomentumColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const m = breakdown.momentum;
  const entries = [
    { label: "30-day change", weight: "50%", weightNum: 0.50, data: m.thirtyDay },
    { label: "90-day change", weight: "35%", weightNum: 0.35, data: m.ninetyDay },
    { label: "1-year change", weight: "15%", weightNum: 0.15, data: m.oneYear },
  ];

  const mFormula = `(${Math.round(m.thirtyDay.score)}×0.50) + (${Math.round(m.ninetyDay.score)}×0.35) + (${Math.round(m.oneYear.score)}×0.15)`;

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="mb-3">
        <div className="flex items-center justify-between">
          <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
            MOMENTUM SCORE: {Math.round(m.score)} / 100
          </span>
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
          Weight in final THI: 30%
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>
          Contribution to THI: {Math.round(m.score)} × 0.30 = {m.contribution} points
        </div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={m.score} size="sm" label="" animated={true} />
      </div>

      {!m.hasEnoughHistory ? (
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.6" }}>
          Not enough historical snapshots yet to compute momentum.
          Score defaults to 50 (neutral) until 30 days of data exists.
          {m.firstSnapshotDate && (
            <> First snapshot: {new Date(m.firstSnapshotDate).toLocaleDateString()}.</>
          )}
        </div>
      ) : (
        <>
          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "8px", fontStyle: "italic" }}>
            How it&apos;s calculated:
          </div>
          <div className="flex flex-col gap-4">
            {entries.map((e) => (
              <div key={e.label}>
                <div className="flex items-center justify-between mb-1">
                  <span style={{ color: "var(--text)", fontSize: "11px" }}>
                    {e.label} ({e.weight} of Momentum)
                  </span>
                  <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
                    {Math.round(e.data.score)}
                  </span>
                </div>
                <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.5" }}>
                  {e.data.delta != null && e.data.prevEvidence != null ? (
                    <>
                      Evidence was {e.data.prevEvidence} on{" "}
                      {e.data.prevDate ? new Date(e.data.prevDate).toLocaleDateString() : "?"} → {m.currentEvidence} today
                      <br />
                      <span style={{ color: e.data.delta >= 0 ? "#FF4500" : "var(--text-muted)" }}>
                        Delta: {e.data.delta >= 0 ? "+" : ""}{e.data.delta} pts → score {Math.round(e.data.score)}
                        {e.data.delta === 0 ? " (neutral)" : e.data.delta > 0 ? " (strengthening)" : " (weakening)"}
                      </span>
                    </>
                  ) : (
                    <span>— insufficient history for this window</span>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div style={{ borderTop: "1px solid var(--border)", margin: "8px 0" }} />
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
            Momentum = {mFormula} = {Math.round(m.score)}
          </div>
        </>
      )}
    </div>
  );
}

function DataQualityColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const dq = breakdown.dataQuality;
  const dqFormula = `(${Math.round(dq.agreement.score)}×0.50) + (${Math.round(dq.freshness.score)}×0.30) + (${Math.round(dq.sourceQuality.score)}×0.20)`;

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="mb-3">
        <div className="flex items-center justify-between">
          <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
            DATA QUALITY SCORE: {Math.round(dq.score)} / 100
          </span>
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
          Weight in final THI: 20%
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>
          Contribution to THI: {Math.round(dq.score)} × 0.20 = {dq.contribution} points
        </div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={dq.score} size="sm" label="" animated={true} />
      </div>
      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "8px", fontStyle: "italic" }}>
        How it&apos;s calculated:
      </div>
      <div className="flex flex-col gap-4">
        {/* Agreement */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span style={{ color: "var(--text)", fontSize: "11px" }}>
              Feed Agreement (50% of Quality)
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.agreement.score)}
            </span>
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.5" }}>
            {dq.agreement.scoredCount > 0 ? (
              <>
                {dq.agreement.scoredCount} of {dq.agreement.totalCount} feeds returning scores.
                <br />
                {dq.agreement.pctConfirming != null && `${dq.agreement.pctConfirming}% of scored feeds pointing confirming.`}
              </>
            ) : (
              "— no scored feeds yet"
            )}
          </div>
        </div>

        {/* Freshness */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span style={{ color: "var(--text)", fontSize: "11px" }}>
              Data Freshness (30% of Quality)
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.freshness.score)}
            </span>
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.5" }}>
            {dq.freshness.degraded > 0 && `${dq.freshness.degraded} feeds degraded (no recent data). `}
            {dq.freshness.avgAgeDays != null ? `Avg data age: ${dq.freshness.avgAgeDays}d. ` : ""}
            {dq.freshness.live} live / {dq.freshness.stale} stale / {dq.freshness.degraded} degraded.
            {dq.freshness.score === 0 && <><br />Score: 0 — fix feeds to improve this.</>}
          </div>
        </div>

        {/* Source Quality */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span style={{ color: "var(--text)", fontSize: "11px" }}>
              Source Quality (20% of Quality)
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.sourceQuality.score)}
            </span>
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.5" }}>
            Active sources: {dq.sourceQuality.activeSources.length > 0
              ? dq.sourceQuality.activeSources.map(s => `${s} (${s === "FRED" ? "100" : s === "GTRENDS" ? "65" : "50"})`).join(", ")
              : "none yet"}
            <br />
            Weighted avg: {dq.sourceQuality.weightedAvg}/100 → score {Math.round(dq.sourceQuality.score)}
          </div>
        </div>
      </div>
      <div style={{ borderTop: "1px solid var(--border)", margin: "8px 0" }} />
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
        Quality = {dqFormula} = {Math.round(dq.score)}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════════════════════ */

function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="uppercase pb-1"
      style={{
        color: active ? "var(--accent)" : "var(--text-muted)",
        letterSpacing: "0.08em",
        fontSize: "13px",
        background: "none",
        border: "none",
        borderBottom: active ? "2px solid var(--accent)" : "2px solid transparent",
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   EFFECT THUMBNAILS
   ═══════════════════════════════════════════════════════════════════════════ */

function EffectThumbnail({
  effect,
  thesisId,
  onDeleted,
}: {
  effect: Effect;
  thesisId: string;
  onDeleted: () => void;
}) {
  const tickers = effect.equityBets.map((b) => b.ticker);

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm(`Delete "${effect.title}"? This cannot be undone.`)) return;
    await api.deleteEffect(effect.id);
    onDeleted();
  };

  return (
    <Link
      href={`/thesis/${thesisId}/effect/${effect.id}`}
      className="border p-5 block hover:opacity-80"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
        textDecoration: "none",
        cursor: "pointer",
      }}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2">
            <h4
              className="font-bold uppercase"
              style={{
                color: "var(--text)",
                letterSpacing: "-0.03em",
                lineHeight: "1.3",
                fontSize: "14px",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              {effect.title}
            </h4>
            <button
              onClick={handleDelete}
              className="flex-shrink-0 mt-0.5"
              style={{
                color: "var(--text-muted)",
                background: "none",
                border: "none",
                cursor: "pointer",
              }}
              title="Delete effect"
            >
              <TrashIcon size={14} />
            </button>
          </div>
          <p
            className="mt-1"
            style={{
              color: "var(--text-muted)",
              lineHeight: "1.5",
              fontSize: "13px",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {effect.description}
          </p>
        </div>
        <div className="flex-shrink-0 flex flex-col items-center">
          <Needle score={effect.thi.score} size="sm" />
          <span
            style={{
              color: "var(--text-muted)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "11px",
              marginTop: "2px",
            }}
          >
            THI
          </span>
        </div>
      </div>
      {tickers.length > 0 && (
        <div
          className="mt-3"
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "13px",
          }}
        >
          {tickers.map((t, i) => (
            <span key={t}>
              <span style={{ color: "#FF4500" }}>{t}</span>
              {i < tickers.length - 1 && (
                <span style={{ color: "#5A5A5A" }}> · </span>
              )}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ADD EFFECT BUTTON
   ═══════════════════════════════════════════════════════════════════════════ */

function AddEffectButton({
  thesisId,
  onCreated,
}: {
  thesisId: string;
  onCreated: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = async () => {
    if (!title || !description) return;
    await api.createEffect(thesisId, { title, description, order: 2 });
    setTitle("");
    setDescription("");
    setOpen(false);
    onCreated();
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="uppercase"
        style={{
          color: "var(--text-muted)",
          letterSpacing: "0.08em",
          background: "none",
          border: "none",
          cursor: "pointer",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
          fontSize: "13px",
        }}
      >
        + ADD 2ND ORDER EFFECT
      </button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Effect title"
        className="px-2 py-1 border"
        style={{
          background: "var(--bg)",
          borderColor: "var(--border)",
          color: "var(--text)",
          outline: "none",
          fontSize: "14px",
        }}
      />
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
        className="px-2 py-1 border flex-1"
        style={{
          background: "var(--bg)",
          borderColor: "var(--border)",
          color: "var(--text)",
          outline: "none",
          fontSize: "14px",
        }}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <button
        onClick={handleSubmit}
        className="uppercase px-2 py-1 border"
        style={{
          color: "var(--text)",
          borderColor: "var(--text)",
          background: "none",
          cursor: "pointer",
          letterSpacing: "0.08em",
          fontSize: "13px",
        }}
      >
        ADD
      </button>
      <button
        onClick={() => setOpen(false)}
        style={{
          color: "var(--text-muted)",
          background: "none",
          border: "none",
          cursor: "pointer",
        }}
      >
        <TrashIcon size={14} />
      </button>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   PORTFOLIO TRACKER
   ═══════════════════════════════════════════════════════════════════════════ */

const INTERPRETATION_LABELS: Record<string, { label: string; color: string; desc: string }> = {
  ALIGNED_WINNING: { label: "ALIGNED & WINNING", color: "#22C55E", desc: "THI is strong and your portfolio is performing — thesis is validated by both data and market." },
  THESIS_STRONG_PORTFOLIO_WEAK: { label: "THESIS STRONG, PORTFOLIO WEAK", color: "#FF4500", desc: "Data supports this thesis but your positions haven't moved yet — potential buying opportunity or wrong picks." },
  THESIS_WEAK_PORTFOLIO_STRONG: { label: "THESIS WEAK, PORTFOLIO STRONG", color: "#F59E0B", desc: "Your positions are up but the underlying thesis is weakening — consider taking profits." },
  ALIGNED_LOSING: { label: "ALIGNED & LOSING", color: "#EF4444", desc: "Both THI and portfolio are down — thesis may be wrong or too early." },
  NEUTRAL: { label: "NEUTRAL", color: "var(--text-muted)", desc: "No strong signal in either direction." },
};

function PortfolioTracker({
  thesisId,
  portfolio,
  isOpen,
  onToggle,
  onReload,
}: {
  thesisId: string;
  portfolio: Portfolio | null;
  isOpen: boolean;
  onToggle: () => void;
  onReload: () => void;
}) {
  const [addingPosition, setAddingPosition] = useState(false);
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("");
  const [entryPrice, setEntryPrice] = useState("");
  const [isShort, setIsShort] = useState(false);

  const hasPositions = portfolio && portfolio.positions.length > 0;

  const handleAddPosition = async () => {
    if (!ticker || !shares || !entryPrice) return;
    await api.addPosition(thesisId, {
      ticker: ticker.toUpperCase(),
      shares: parseFloat(shares),
      entry_price: parseFloat(entryPrice),
      is_short: isShort,
    });
    setTicker("");
    setShares("");
    setEntryPrice("");
    setIsShort(false);
    setAddingPosition(false);
    onReload();
  };

  const handleDeletePosition = async (positionId: string) => {
    if (!confirm("Remove this position?")) return;
    await api.deletePosition(positionId);
    onReload();
  };

  const interp = portfolio ? INTERPRETATION_LABELS[portfolio.interpretation] || INTERPRETATION_LABELS.NEUTRAL : INTERPRETATION_LABELS.NEUTRAL;

  return (
    <div className="mb-6">
      <div className="flex items-center gap-4 mb-4">
        <button
          onClick={onToggle}
          className="uppercase flex items-center gap-2"
          style={{
            color: hasPositions ? "var(--accent)" : "var(--text-muted)",
            letterSpacing: "0.08em",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "13px",
          }}
        >
          {hasPositions ? "PORTFOLIO TRACKER" : "TRACK THIS THESIS"}{" "}
          <span style={{ fontSize: "12px" }}>{isOpen ? "▲" : "▾"}</span>
        </button>
        {hasPositions && portfolio && (
          <span
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "13px",
              color: portfolio.totalPnl >= 0 ? "#22C55E" : "#EF4444",
            }}
          >
            {portfolio.totalPnl >= 0 ? "+" : ""}{portfolio.totalPnlPct.toFixed(1)}% (${portfolio.totalPnl.toFixed(0)})
          </span>
        )}
      </div>

      {isOpen && (
        <div
          className="border p-5 mb-4"
          style={{ background: "var(--surface)", borderColor: "var(--border)" }}
        >
          {/* Interpretation banner */}
          {hasPositions && (
            <div className="mb-4 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
              <div className="flex items-center gap-3 mb-1">
                <span
                  className="uppercase font-bold"
                  style={{ color: interp.color, letterSpacing: "0.08em", fontSize: "12px" }}
                >
                  {interp.label}
                </span>
                <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
                  THI {Math.round(portfolio!.thiScore)} · P&L {portfolio!.totalPnlPct >= 0 ? "+" : ""}{portfolio!.totalPnlPct.toFixed(1)}%
                </span>
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4" }}>
                {interp.desc}
              </p>
            </div>
          )}

          {/* Position list */}
          {hasPositions && (
            <div className="mb-4">
              <div
                className="grid mb-2 uppercase"
                style={{
                  gridTemplateColumns: "80px 1fr 80px 80px 80px 30px",
                  gap: "8px",
                  color: "var(--text-muted)",
                  letterSpacing: "0.08em",
                  fontSize: "10px",
                }}
              >
                <span>TICKER</span>
                <span>SHARES × ENTRY</span>
                <span>CURRENT</span>
                <span>P&L</span>
                <span>P&L %</span>
                <span />
              </div>
              {portfolio!.positions.map((p) => (
                <div
                  key={p.id}
                  className="grid items-center"
                  style={{
                    gridTemplateColumns: "80px 1fr 80px 80px 80px 30px",
                    gap: "8px",
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: "12px",
                    lineHeight: "2",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  <span style={{ color: p.isShort ? "#EF4444" : "var(--accent)" }}>
                    {p.isShort ? "▼" : ""}{p.ticker}
                  </span>
                  <span style={{ color: "var(--text-muted)" }}>
                    {p.shares} × ${p.entryPrice.toFixed(2)}
                  </span>
                  <span style={{ color: "var(--text)" }}>
                    ${(p.currentPrice || p.entryPrice).toFixed(2)}
                  </span>
                  <span style={{ color: (p.pnl || 0) >= 0 ? "#22C55E" : "#EF4444" }}>
                    {(p.pnl || 0) >= 0 ? "+" : ""}${(p.pnl || 0).toFixed(0)}
                  </span>
                  <span style={{ color: (p.pnlPct || 0) >= 0 ? "#22C55E" : "#EF4444" }}>
                    {(p.pnlPct || 0) >= 0 ? "+" : ""}{(p.pnlPct || 0).toFixed(1)}%
                  </span>
                  <button
                    onClick={() => handleDeletePosition(p.id)}
                    style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
                  >
                    <TrashIcon size={12} />
                  </button>
                </div>
              ))}
              <div
                className="grid mt-2 font-bold"
                style={{
                  gridTemplateColumns: "80px 1fr 80px 80px 80px 30px",
                  gap: "8px",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "12px",
                }}
              >
                <span style={{ color: "var(--text)" }}>TOTAL</span>
                <span style={{ color: "var(--text-muted)" }}>
                  Cost: ${portfolio!.totalCost.toFixed(0)}
                </span>
                <span style={{ color: "var(--text)" }}>
                  ${portfolio!.totalValue.toFixed(0)}
                </span>
                <span style={{ color: portfolio!.totalPnl >= 0 ? "#22C55E" : "#EF4444" }}>
                  {portfolio!.totalPnl >= 0 ? "+" : ""}${portfolio!.totalPnl.toFixed(0)}
                </span>
                <span style={{ color: portfolio!.totalPnlPct >= 0 ? "#22C55E" : "#EF4444" }}>
                  {portfolio!.totalPnlPct >= 0 ? "+" : ""}{portfolio!.totalPnlPct.toFixed(1)}%
                </span>
                <span />
              </div>
            </div>
          )}

          {/* Add position form */}
          {addingPosition ? (
            <div className="flex items-center gap-2 flex-wrap">
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="TICKER"
                className="px-2 py-1 border"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  fontSize: "13px",
                  width: "80px",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              />
              <input
                type="number"
                value={shares}
                onChange={(e) => setShares(e.target.value)}
                placeholder="Shares"
                className="px-2 py-1 border"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  fontSize: "13px",
                  width: "80px",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              />
              <input
                type="number"
                value={entryPrice}
                onChange={(e) => setEntryPrice(e.target.value)}
                placeholder="Entry $"
                className="px-2 py-1 border"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  fontSize: "13px",
                  width: "90px",
                  fontFamily: "JetBrains Mono, monospace",
                }}
                onKeyDown={(e) => e.key === "Enter" && handleAddPosition()}
              />
              <label
                className="flex items-center gap-1 uppercase"
                style={{ color: "var(--text-muted)", fontSize: "11px", letterSpacing: "0.08em", cursor: "pointer" }}
              >
                <input
                  type="checkbox"
                  checked={isShort}
                  onChange={(e) => setIsShort(e.target.checked)}
                  style={{ accentColor: "var(--accent)" }}
                />
                SHORT
              </label>
              <button
                onClick={handleAddPosition}
                className="uppercase px-2 py-1 border"
                style={{
                  color: "var(--text)",
                  borderColor: "var(--text)",
                  background: "none",
                  cursor: "pointer",
                  letterSpacing: "0.08em",
                  fontSize: "12px",
                }}
              >
                ADD
              </button>
              <button
                onClick={() => setAddingPosition(false)}
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
              >
                <TrashIcon size={14} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setAddingPosition(true)}
              className="uppercase"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                background: "none",
                border: "none",
                cursor: "pointer",
                textDecoration: "underline",
                textUnderlineOffset: "3px",
                fontSize: "12px",
              }}
            >
              + ADD POSITION
            </button>
          )}
        </div>
      )}
    </div>
  );
}
