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
import { api, ThesisDetail, Effect, ScoringBreakdown, EvidenceDimension } from "@/lib/api";

export default function EffectDetailPage() {
  const params = useParams();
  const thesisId = params.id as string;
  const effectId = params.effectId as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [effect, setEffect] = useState<Effect | null>(null);
  const [breakdown, setBreakdown] = useState<ScoringBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [scoringOpen, setScoringOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"bets" | "startups">("bets");

  const reloadEffect = async () => {
    const [t, e, b] = await Promise.all([
      api.getThesis(thesisId),
      api.getEffect(effectId),
      api.getScoringBreakdown(thesisId),
    ]);
    setThesis(t);
    setEffect(e);
    setBreakdown(b);
  };

  useEffect(() => {
    if (!thesisId || !effectId) return;
    Promise.all([api.getThesis(thesisId), api.getEffect(effectId), api.getScoringBreakdown(thesisId)])
      .then(([t, e, b]) => {
        setThesis(t);
        setEffect(e);
        setBreakdown(b);
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
        <div className="flex items-center gap-4 mb-6">
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
        </div>

        {scoringOpen && breakdown && (
          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-4">
              <EvidenceColumn breakdown={breakdown} />
              <MomentumColumn breakdown={breakdown} />
              <DataQualityColumn breakdown={breakdown} />
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
            {activeTab === "bets" && effect.equityBets.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                {effect.equityBets.map((bet) => (
                  <EquityBetCard key={bet.id} bet={bet} />
                ))}
              </div>
            )}
            {activeTab === "startups" && effect.startupOpportunities.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                {effect.startupOpportunities.map((opp) => (
                  <StartupCard key={opp.id} opportunity={opp} />
                ))}
              </div>
            )}
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
   SCORING BREAKDOWN COLUMNS (inherited from parent thesis)
   ═══════════════════════════════════════════════════════════════════════════ */

function EvidenceColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const ev = breakdown.evidence;
  const dims = [
    { key: "flow", label: "FLOW", data: ev.flow },
    { key: "structural", label: "STRUCTURAL", data: ev.structural },
    { key: "adoption", label: "ADOPTION", data: ev.adoption },
    { key: "policy", label: "POLICY", data: ev.policy },
  ];

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="uppercase font-bold"
            style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}
          >
            EVIDENCE
          </span>
          <span
            className="uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
          >
            50%
          </span>
        </div>
        <span
          style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "20px", fontWeight: "bold" }}
        >
          {Math.round(ev.score)}
        </span>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={ev.score} size="sm" label="" animated={true} />
      </div>
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
        <span
          className="uppercase"
          style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}
        >
          {label}{" "}
          <span style={{ color: "var(--text-muted)" }}>
            {(dim.weight * 100).toFixed(0)}%
          </span>
        </span>
        <span
          style={{
            color: dim.score != null ? "var(--accent)" : "var(--text-muted)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "13px",
          }}
        >
          {dim.score != null ? Math.round(dim.score) : "—"}
        </span>
      </div>
      <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "4px" }}>
        {dim.description}
      </p>
      {dim.feeds.length > 0 ? (
        <div style={{ fontSize: "11px" }}>
          {dim.feeds.map((f) => (
            <div
              key={f.name}
              className="mb-2 pb-2"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <div className="flex items-center justify-between" style={{ fontFamily: "JetBrains Mono, monospace" }}>
                <span style={{ color: "var(--text-muted)" }}>
                  {f.name}{" "}
                  <span
                    style={{
                      color: f.status === "live" ? "var(--status-live)" : "var(--status-stale)",
                      fontSize: "9px",
                    }}
                  >
                    ●
                  </span>
                </span>
                <span style={{ color: f.normalizedScore != null ? "var(--accent)" : "var(--text-muted)" }}>
                  {f.normalizedScore != null ? f.normalizedScore : "—"}
                </span>
              </div>
              {f.formattedValue && (
                <div style={{ fontFamily: "JetBrains Mono, monospace", color: "var(--text)", fontSize: "12px", marginTop: "2px" }}>
                  {f.formattedValue}
                  {f.seriesId && <span style={{ color: "var(--text-muted)", marginLeft: "6px" }}>{f.seriesId}</span>}
                  {f.keyword && <span style={{ color: "var(--text-muted)", marginLeft: "6px" }}>&quot;{f.keyword}&quot;</span>}
                </div>
              )}
              <div style={{ fontFamily: "JetBrains Mono, monospace", color: "var(--text-muted)", fontSize: "10px", marginTop: "2px" }}>
                {f.pctVs1yr != null && (
                  <span style={{ color: f.pctVs1yr >= 0 ? "#FF4500" : "var(--text-muted)" }}>
                    vs 1yr: {f.pctVs1yr >= 0 ? "+" : ""}{f.pctVs1yr}%
                  </span>
                )}
                {f.pctVs1yr != null && f.pctVs5yrAvg != null && <span> · </span>}
                {f.pctVs5yrAvg != null && (
                  <span style={{ color: f.pctVs5yrAvg >= 0 ? "#FF4500" : "var(--text-muted)" }}>
                    vs 5yr avg: {f.pctVs5yrAvg >= 0 ? "+" : ""}{f.pctVs5yrAvg}%
                  </span>
                )}
              </div>
              {f.context && (
                <div style={{ color: "var(--text-muted)", fontSize: "10px", lineHeight: "1.4", marginTop: "2px" }}>
                  {f.context}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <span style={{ color: "var(--text-muted)", fontSize: "11px", fontStyle: "italic" }}>
          No {label.toLowerCase()} feeds configured
        </span>
      )}
      {dim.lastUpdated && (
        <div style={{ color: "#242424", fontSize: "10px", fontFamily: "JetBrains Mono, monospace", marginTop: "2px" }}>
          Updated {new Date(dim.lastUpdated).toLocaleDateString()}
        </div>
      )}
    </div>
  );
}

function MomentumColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const m = breakdown.momentum;
  const entries = [
    { label: "30D MOMENTUM", weight: "50%", desc: "How much has the evidence score changed in the last 30 days? Positive = thesis accelerating.", data: m.thirtyDay },
    { label: "90D MOMENTUM", weight: "35%", desc: "Medium-term direction — smooths out noise from the 30-day view.", data: m.ninetyDay },
    { label: "1YR MOMENTUM", weight: "15%", desc: "Long-term structural direction — is this thesis gaining or losing ground over a full year?", data: m.oneYear },
  ];

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="uppercase font-bold"
            style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}
          >
            MOMENTUM
          </span>
          <span
            className="uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
          >
            30%
          </span>
        </div>
        <span
          style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "20px", fontWeight: "bold" }}
        >
          {Math.round(m.score)}
        </span>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={m.score} size="sm" label="" animated={true} />
      </div>
      <div className="flex flex-col gap-4">
        {entries.map((e) => (
          <div key={e.label}>
            <div className="flex items-center justify-between mb-1">
              <span
                className="uppercase"
                style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}
              >
                {e.label}{" "}
                <span style={{ color: "var(--text-muted)" }}>{e.weight}</span>
              </span>
              <span
                style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}
              >
                {Math.round(e.data.score)}
              </span>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "4px" }}>
              {e.desc}
            </p>
            <div
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                color: e.data.delta != null && e.data.delta >= 0 ? "#FF4500" : "var(--text-muted)",
              }}
            >
              {e.data.delta != null
                ? `${e.data.delta >= 0 ? "+" : ""}${e.data.delta} points`
                : "— insufficient history"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DataQualityColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const dq = breakdown.dataQuality;

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="uppercase font-bold"
            style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}
          >
            DATA QUALITY
          </span>
          <span
            className="uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
          >
            20%
          </span>
        </div>
        <span
          style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "20px", fontWeight: "bold" }}
        >
          {Math.round(dq.score)}
        </span>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={dq.score} size="sm" label="" animated={true} />
      </div>
      <div className="flex flex-col gap-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}>
              AGREEMENT <span style={{ color: "var(--text-muted)" }}>50%</span>
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.agreement.score)}
            </span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "4px" }}>
            Do the feeds agree with each other? If some say &quot;confirming&quot; but others say &quot;refuting&quot;, confidence is low.
          </p>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
            {dq.agreement.pctConfirming != null
              ? `${dq.agreement.pctConfirming}% of feeds pointing confirming`
              : "— no scored feeds"}
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}>
              FRESHNESS <span style={{ color: "var(--text-muted)" }}>30%</span>
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.freshness.score)}
            </span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "4px" }}>
            How recent is the data? Stale data = less reliable score.
          </p>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
            {dq.freshness.avgAgeDays != null
              ? `Avg age: ${dq.freshness.avgAgeDays}d`
              : "— no data"}{" "}
            · {dq.freshness.live} live / {dq.freshness.stale} stale / {dq.freshness.degraded} degraded
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="uppercase" style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "11px" }}>
              SOURCE QUALITY <span style={{ color: "var(--text-muted)" }}>20%</span>
            </span>
            <span style={{ color: "var(--accent)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {Math.round(dq.sourceQuality.score)}
            </span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "11px", lineHeight: "1.4", marginBottom: "4px" }}>
            Are these feeds from authoritative sources? FRED/BLS = 100. Google Trends = 65. Estimated = 20.
          </p>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px", color: "var(--text-muted)" }}>
            Weighted avg: {dq.sourceQuality.weightedAvg}/100
          </div>
        </div>
      </div>
    </div>
  );
}
