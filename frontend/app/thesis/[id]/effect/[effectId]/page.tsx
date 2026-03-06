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
import { api, ThesisDetail, Effect, ScoringBreakdown, EvidenceDimension, ScoringBreakdownFeed, EquityScoreResult, EFSScore, STSScore } from "@/lib/api";

export default function EffectDetailPage() {
  const params = useParams();
  const thesisId = params.id as string;
  const effectId = params.effectId as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [effect, setEffect] = useState<Effect | null>(null);
  const [breakdown, setBreakdown] = useState<ScoringBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [scoringOpen, setScoringOpen] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<"bets" | "startups">("bets");
  const [efsScores, setEfsScores] = useState<EquityScoreResult[]>([]);
  const [stsMap, setStsMap] = useState<Record<string, STSScore>>({});

  const reloadEffect = async () => {
    const [t, e, b, efs] = await Promise.all([
      api.getThesis(thesisId),
      api.getEffect(effectId),
      api.getEffectScoringBreakdown(effectId).catch(() => null),
      api.getEffectEquityScores(effectId).catch(() => [] as EquityScoreResult[]),
    ]);
    setThesis(t);
    setEffect(e);
    if (b) setBreakdown(b);
    setEfsScores(efs);
    if (e.startupOpportunities.length > 0) {
      const stsResults = await Promise.all(
        e.startupOpportunities.map((opp) =>
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

  const handleRefreshFeeds = async () => {
    setRefreshing(true);
    try {
      await api.refreshEffectFeeds(effectId);
      await reloadEffect();
    } catch (e) {
      console.error("Feed refresh failed:", e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (!thesisId || !effectId) return;
    Promise.all([
      api.getThesis(thesisId),
      api.getEffect(effectId),
      api.getEffectScoringBreakdown(effectId).catch(() => null),
      api.getEffectEquityScores(effectId).catch(() => [] as EquityScoreResult[]),
    ])
      .then(async ([t, e, b, efs]) => {
        setThesis(t);
        setEffect(e);
        if (b) setBreakdown(b);
        setEfsScores(efs);
        if (e.startupOpportunities.length > 0) {
          const stsResults = await Promise.all(
            e.startupOpportunities.map((opp) =>
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
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [thesisId, effectId]);

  if (loading) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div className="px-12 py-8" style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace" }}>
          ————————
        </div>
      </main>
    );
  }

  if (!thesis || !effect) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div className="px-12 py-8" style={{ color: "var(--text-muted)", fontSize: "15px" }}>Effect not found.</div>
      </main>
    );
  }

  const handleConviction = async (score: number, note?: string) => {
    await api.updateEffectConviction(effectId, score, note);
    await reloadEffect();
  };

  const orderLabel = effect.order === 2 ? "2ND ORDER" : "3RD ORDER";

  return (
    <ErrorBoundary>
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header />
      <div className="px-12 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6 flex-wrap">
          <Link
            href="/"
            className="uppercase hover:underline"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", textUnderlineOffset: "3px", fontSize: "13px" }}
          >
            TANGENTBOOK
          </Link>
          <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>/</span>
          <Link
            href={`/thesis/${thesisId}`}
            className="uppercase hover:underline"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", textUnderlineOffset: "3px", fontSize: "13px" }}
          >
            {thesis.title}
          </Link>
          <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>/</span>
          <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
            {effect.title}
          </span>
        </div>

        {/* ══════════════════════════════════════════════════
            SECTION 1: HERO
            ══════════════════════════════════════════════════ */}
        <div className="flex gap-12 mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span
                className="uppercase px-2 py-0.5 border"
                style={{ color: "var(--text-muted)", borderColor: "var(--border)", letterSpacing: "0.08em", fontSize: "12px" }}
              >
                {orderLabel} EFFECT
              </span>
            </div>
            <h1
              className="font-bold uppercase text-2xl mb-2"
              style={{ color: "var(--text)", letterSpacing: "-0.04em", wordWrap: "break-word", overflowWrap: "break-word" }}
            >
              {effect.title}
            </h1>
            <p className="mb-4" style={{ color: "var(--text-muted)", lineHeight: "1.6", fontSize: "16px", wordWrap: "break-word", overflowWrap: "break-word" }}>
              {effect.description}
            </p>
            <div className="flex items-center gap-6 flex-wrap">
              <div className="flex items-center gap-2">
                <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}>
                  PARENT THI
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {Math.round(thesis.thi.score)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}>
                  INHERITANCE
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {(effect.inheritanceWeight * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}>
                  DIRECTION
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {effect.thi.direction.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="mt-4">
              <ConvictionSlider
                score={effect.userConviction.score}
                history={effect.userConviction.history?.map((h) => h.score) || []}
                onUpdate={handleConviction}
                divergenceWarning={effect.userConviction.divergenceWarning}
              />
            </div>
          </div>
          <div className="flex-shrink-0">
            <Needle score={effect.thi.score} size="lg" label="EFFECT HEALTH" />
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

        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* ══════════════════════════════════════════════════
            SECTION 2: BETS + OPPORTUNITIES (tabbed)
            ══════════════════════════════════════════════════ */}
        {(effect.equityBets.length > 0 || effect.startupOpportunities.length > 0) && (
          <>
            <div className="flex items-center gap-6 mb-4">
              <TabButton
                label={`EQUITY BETS (${effect.equityBets.length})`}
                active={activeTab === "bets"}
                onClick={() => setActiveTab("bets")}
              />
              <TabButton
                label={`STARTUP OPPORTUNITIES (${effect.startupOpportunities.length})`}
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
              const sortedBets = [...effect.equityBets].sort((a, b) => {
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
              const sortedOpps = [...effect.startupOpportunities].sort((a, b) => {
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
            SECTION 3: CHILD EFFECTS (thumbnail grid)
            ══════════════════════════════════════════════════ */}
        {effect.childEffects && effect.childEffects.length > 0 && (
          <>
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              3RD ORDER EFFECTS ({effect.childEffects.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 mb-8">
              {effect.childEffects.map((child) => (
                <ChildEffectThumbnail
                  key={child.id}
                  child={child}
                  thesisId={thesisId}
                  parentEffectId={effect.id}
                  onDeleted={reloadEffect}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
    </ErrorBoundary>
  );
}

function TabButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
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

function ChildEffectThumbnail({
  child,
  thesisId,
  onDeleted,
}: {
  child: Effect;
  thesisId: string;
  parentEffectId: string;
  onDeleted: () => void;
}) {
  const tickers = child.equityBets.map((b) => b.ticker);

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm(`Delete "${child.title}"? This cannot be undone.`)) return;
    await api.deleteEffect(child.id);
    onDeleted();
  };

  return (
    <Link
      href={`/thesis/${thesisId}/effect/${child.id}`}
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
              {child.title}
            </h4>
            <button
              onClick={handleDelete}
              className="flex-shrink-0 mt-0.5"
              style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
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
            {child.description}
          </p>
        </div>
        <div className="flex-shrink-0 flex flex-col items-center">
          <Needle score={child.thi.score} size="sm" />
          <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "2px" }}>
            THI
          </span>
        </div>
      </div>
      {tickers.length > 0 && (
        <div className="mt-3" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
          {tickers.map((t, i) => (
            <span key={t}>
              <span style={{ color: "#FF4500" }}>{t}</span>
              {i < tickers.length - 1 && <span style={{ color: "#5A5A5A" }}> · </span>}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCORING BREAKDOWN COLUMNS (effect's own feeds)
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
    <div className="border p-5" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
      <div className="mb-3">
        <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
          EVIDENCE SCORE: {Math.round(ev.score)} / 100
        </span>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
          Weight in final THI: 50%
        </div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>
          Contribution: {Math.round(ev.score)} × 0.50 = {ev.contribution} pts
        </div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={ev.score} size="sm" label="" animated={true} />
      </div>
      {dims.map(({ key, label, data }) => {
        const s = data.score != null ? Math.round(data.score) : 0;
        const c = ev.dimContributions?.[key] ?? 0;
        return (
          <div key={key} className="mb-1" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px" }}>
            <span style={{ color: "var(--text-muted)" }}>{label} ({(data.weight * 100).toFixed(0)}%) → </span>
            <span style={{ color: s > 0 ? "var(--accent)" : "var(--text-muted)" }}>score {s}</span>
            <span style={{ color: "var(--text-muted)" }}> → {c.toFixed(1)} pts</span>
          </div>
        );
      })}
      <div style={{ borderTop: "1px solid var(--border)", margin: "8px 0" }} />
      <div className="flex flex-col gap-4">
        {dims.map(({ key, label, data }) => (
          <DimensionBlock key={key} label={label} dim={data} />
        ))}
      </div>
    </div>
  );
}

function DimensionBlock({ label, dim }: { label: string; dim: EvidenceDimension }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}>{label}</span>
        <span style={{ color: dim.score != null ? "var(--accent)" : "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
          {dim.score != null ? `${Math.round(dim.score)} / 100` : "—"}
        </span>
      </div>
      <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "6px" }}>{dim.description}</p>
      {dim.feeds.length > 0 ? (
        <div style={{ fontSize: "11px" }}>
          {dim.feeds.map((f) => <FeedRow key={f.name} feed={f} />)}
        </div>
      ) : (
        <span style={{ color: "var(--text-muted)", fontSize: "11px", fontStyle: "italic" }}>No {label.toLowerCase()} feeds configured</span>
      )}
    </div>
  );
}

function FeedRow({ feed: f }: { feed: ScoringBreakdownFeed }) {
  const statusLabel = f.status === "live" ? "LIVE" : f.status === "stale" ? "STALE" : f.status === "degraded" ? "DEGRADED" : "OFFLINE";
  const statusColor = f.status === "live" ? "var(--status-live)" : f.status === "stale" ? "#F59E0B" : "#EF4444";
  const sourceLabel = f.source === "FRED" ? `FRED: ${f.seriesId}` : f.source === "GTRENDS" ? `GTrends: "${f.keyword}"` : f.source || "";
  if (f.status === "live" && f.normalizedScore != null) {
    return (
      <div className="mb-3 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text)", fontWeight: "bold" }}>{f.name} ({sourceLabel})</div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "3px" }}>
          <span style={{ color: "var(--text)" }}>Current: {f.formattedValue || "—"}</span>
          <span style={{ color: "var(--text-muted)" }}> | </span>
          <span style={{ color: "var(--accent)" }}>Score: {f.normalizedScore} / 100</span>
        </div>
        {f.context && <div style={{ color: "var(--text-muted)", fontSize: "10px", lineHeight: "1.4", marginTop: "2px" }}>{f.context}</div>}
        {f.lastUpdated && (
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "10px", marginTop: "2px", color: "var(--text-muted)" }}>
            Updated: {new Date(f.lastUpdated).toLocaleString()} | <span style={{ color: statusColor }}>{statusLabel}</span>
          </div>
        )}
      </div>
    );
  }
  return (
    <div className="mb-3 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>{f.name} ({sourceLabel})</div>
      <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", marginTop: "3px", color: statusColor }}>
        {f.formattedValue ? `Last known: ${f.formattedValue} — DATA ${statusLabel}` : "No data fetched yet. Click REFRESH FEEDS to pull latest."}
      </div>
    </div>
  );
}

function MomentumColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const m = breakdown.momentum;
  return (
    <div className="border p-5" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
      <div className="mb-3">
        <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
          MOMENTUM SCORE: {Math.round(m.score)} / 100
        </span>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>Weight in final THI: 30%</div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>Contribution: {Math.round(m.score)} × 0.30 = {m.contribution} pts</div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={m.score} size="sm" label="" animated={true} />
      </div>
      {!m.hasEnoughHistory ? (
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", lineHeight: "1.6" }}>
          Not enough historical snapshots yet. Score defaults to 50 (neutral).
        </div>
      ) : (
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
          Momentum computed from evidence deltas over 30d/90d/1yr windows.
        </div>
      )}
    </div>
  );
}

function DataQualityColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const dq = breakdown.dataQuality;
  return (
    <div className="border p-5" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
      <div className="mb-3">
        <span className="uppercase font-bold" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}>
          DATA QUALITY SCORE: {Math.round(dq.score)} / 100
        </span>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>Weight in final THI: 20%</div>
        <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--accent)", marginTop: "2px" }}>Contribution: {Math.round(dq.score)} × 0.20 = {dq.contribution} pts</div>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={dq.score} size="sm" label="" animated={true} />
      </div>
      <div className="flex flex-col gap-3" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
        <div>Agreement (50%): {dq.agreement.scoredCount}/{dq.agreement.totalCount} feeds scored → score {Math.round(dq.agreement.score)}</div>
        <div>Freshness (30%): {dq.freshness.live} live / {dq.freshness.degraded} degraded → score {Math.round(dq.freshness.score)}</div>
        <div>Source Quality (20%): avg {dq.sourceQuality.weightedAvg}/100 → score {Math.round(dq.sourceQuality.score)}</div>
      </div>
    </div>
  );
}
