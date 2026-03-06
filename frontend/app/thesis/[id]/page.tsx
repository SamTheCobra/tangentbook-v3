"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import EquityBetCard from "@/components/EquityBetCard";
import StartupCard from "@/components/StartupCard";
import ErrorBoundary from "@/components/ErrorBoundary";
import EffectChain from "@/components/EffectChain";
import ConvictionSlider from "@/components/ConvictionSlider";
import TrashIcon from "@/components/TrashIcon";
import { api, ThesisDetail, Feed, Effect } from "@/lib/api";

export default function ThesisDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedsOpen, setFeedsOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const reloadThesis = async () => {
    const t = await api.getThesis(id);
    setThesis(t);
  };

  useEffect(() => {
    if (!id) return;
    Promise.all([api.getThesis(id), api.getFeeds(id)])
      .then(([t, f]) => {
        setThesis(t);
        setFeeds(f);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

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

  if (!thesis) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div className="px-12 py-8" style={{ color: "var(--text-muted)", fontSize: "15px" }}>Thesis not found.</div>
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
      const [t, f] = await Promise.all([api.getThesis(id), api.getFeeds(id)]);
      setThesis(t);
      setFeeds(f);
    } catch (e) {
      console.error("Feed refresh failed:", e);
    } finally {
      setRefreshing(false);
    }
  };

  const eScore = Math.round(thesis.thi.evidence.score);
  const mScore = Math.round(thesis.thi.momentum.score);
  const cScore = Math.round(thesis.thi.conviction.score);
  const thiFormula = `THI = Evidence(${eScore}) × 0.50 + Momentum(${mScore}) × 0.30 + Quality(${cScore}) × 0.20`;

  return (
    <ErrorBoundary>
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header />
      <div className="px-12 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6">
          <Link
            href="/"
            className="uppercase hover:underline"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", textUnderlineOffset: "3px", fontSize: "13px" }}
          >
            TANGENTBOOK
          </Link>
          <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>/</span>
          <span
            className="uppercase"
            style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "13px" }}
          >
            {thesis.title}
          </span>
        </div>

        {/* Hero section */}
        <div className="flex gap-12 mb-8">
          <div className="flex-1">
            <h1
              className="font-bold uppercase text-3xl mb-2"
              style={{ color: "var(--text)", letterSpacing: "-0.04em", wordWrap: "break-word", overflowWrap: "break-word" }}
            >
              {thesis.title}
            </h1>
            <p className="mb-4" style={{ color: "var(--text-muted)", lineHeight: "1.6", fontSize: "16px", wordWrap: "break-word", overflowWrap: "break-word" }}>
              {thesis.description}
            </p>
            <div className="flex items-center gap-6 flex-wrap">
              <div className="flex items-center gap-2">
                <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}>
                  HORIZON
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {thesis.timeHorizon}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}>
                  DIRECTION
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {thesis.thi.direction.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="mt-4">
              <ConvictionSlider
                score={thesis.userConviction.score}
                history={thesis.userConviction.history?.map((h) => h.score) || []}
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
              formulaText={thiFormula}
            />
          </div>
        </div>

        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* Scoring Breakdown Panel */}
        <h3
          className="uppercase mb-4"
          style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
        >
          SCORING BREAKDOWN
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-4">
          <ScoreColumn
            label="EVIDENCE"
            score={thesis.thi.evidence.score}
            weight={thesis.thi.evidence.weight}
            description="Measures whether real-world data confirms the thesis is happening. Higher means more data points are moving in the predicted direction."
            breakdowns={[
              { label: "FLOW", pct: 35 },
              { label: "STRUCTURAL", pct: 30 },
              { label: "ADOPTION", pct: 20 },
              { label: "POLICY", pct: 15 },
            ]}
          />
          <ScoreColumn
            label="MOMENTUM"
            score={thesis.thi.momentum.score}
            weight={thesis.thi.momentum.weight}
            description="Measures whether the thesis is accelerating or decelerating. Compares recent data changes across multiple time windows."
            breakdowns={[
              { label: "30D", pct: 50 },
              { label: "90D", pct: 35 },
              { label: "1YR", pct: 15 },
            ]}
          />
          <ScoreColumn
            label="DATA QUALITY"
            score={thesis.thi.conviction.score}
            weight={thesis.thi.conviction.weight}
            description="Measures how trustworthy the score is. Low quality means feeds disagree, data is stale, or sources are unreliable."
            breakdowns={[
              { label: "AGREEMENT", pct: 50 },
              { label: "FRESHNESS", pct: 30 },
              { label: "SRC QUAL", pct: 20 },
            ]}
          />
        </div>

        <div
          className="text-center mb-8"
          style={{
            color: "var(--text-muted)",
            fontSize: "12px",
            letterSpacing: "0.04em",
            fontFamily: "JetBrains Mono, monospace",
          }}
        >
          ↑ These scores are computed from the FEEDS section below
        </div>

        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* Feed Health Panel */}
        <FeedPanel
          feeds={feeds}
          feedsOpen={feedsOpen}
          setFeedsOpen={setFeedsOpen}
          refreshing={refreshing}
          onRefresh={handleRefreshFeeds}
        />

        {/* Equity Bets */}
        {thesis.equityBets.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              EQUITY BETS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {thesis.equityBets.map((bet) => (
                <EquityBetCard key={bet.id} bet={bet} />
              ))}
            </div>
          </>
        )}

        {/* Startup Opportunities */}
        {thesis.startupOpportunities.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              STARTUP OPPORTUNITIES
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {thesis.startupOpportunities.map((opp) => (
                <StartupCard key={opp.id} opportunity={opp} />
              ))}
            </div>
          </>
        )}

        {/* Effect Chain Diagram */}
        {thesis.effects.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              EFFECT CHAIN
            </h3>
            <div className="mb-8">
              <EffectChain
                thesisId={thesis.id}
                thesisTitle={thesis.title}
                thesisScore={thesis.thi.score}
                effects={thesis.effects}
              />
            </div>
          </>
        )}

        {/* Effects Grid with 3rd order toggle */}
        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
        <div className="flex items-center justify-between mb-4">
          <h3
            className="uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
          >
            2ND ORDER EFFECTS ({thesis.effects.length})
          </h3>
          <AddEffectButton thesisId={thesis.id} onCreated={reloadThesis} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
          {thesis.effects.map((effect) => (
            <EffectCard key={effect.id} effect={effect} thesisId={thesis.id} onUpdated={reloadThesis} />
          ))}
        </div>

        <div className="mb-8" />
      </div>
    </main>
    </ErrorBoundary>
  );
}

function formatFeedName(feed: Feed): string {
  let name = feed.name;
  name = name.replace(/^(Fred|Gtrends|Alpha Vantage)\s+/i, "");
  return name;
}

function formatRawValue(feed: Feed): string {
  if (feed.rawValue == null) return "——";
  const v = feed.rawValue;
  if (v >= 1_000_000_000_000) return `${(v / 1_000_000_000_000).toFixed(1)}T`;
  if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  if (Number.isInteger(v)) return v.toString();
  return v.toFixed(2);
}

function ScoreColumn({
  label,
  score,
  weight,
  description,
  breakdowns,
}: {
  label: string;
  score: number;
  weight: number;
  description: string;
  breakdowns: { label: string; pct: number }[];
}) {
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
            {label}
          </span>
          <span
            className="uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
          >
            {(weight * 100).toFixed(0)}%
          </span>
        </div>
        <span
          style={{
            color: "var(--accent)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "20px",
            fontWeight: "bold",
          }}
        >
          {Math.round(score)}
        </span>
      </div>

      <div className="flex justify-center mb-3">
        <Needle score={score} size="sm" label="" animated={true} />
      </div>

      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "13px",
          lineHeight: "1.5",
          marginBottom: "16px",
        }}
      >
        {description}
      </p>

      <div className="flex flex-col gap-2">
        {breakdowns.map((b) => (
          <div key={b.label} className="flex items-center gap-3">
            <span
              className="uppercase flex-shrink-0"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
                width: "80px",
              }}
            >
              {b.label}
            </span>
            <div
              style={{
                width: "40px",
                height: "4px",
                background: "var(--border)",
                position: "relative",
                flexShrink: 0,
              }}
            >
              <div
                style={{
                  width: `${b.pct}%`,
                  height: "100%",
                  background: "var(--accent)",
                }}
              />
            </div>
            <span
              style={{
                color: "var(--text-muted)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "11px",
              }}
            >
              {b.pct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeedPanel({
  feeds,
  feedsOpen,
  setFeedsOpen,
  refreshing,
  onRefresh,
}: {
  feeds: Feed[];
  feedsOpen: boolean;
  setFeedsOpen: (v: boolean) => void;
  refreshing: boolean;
  onRefresh: () => void;
}) {
  const [expandedFeed, setExpandedFeed] = useState<string | null>(null);

  const live = feeds.filter((f) => f.status === "live").length;
  const offline = feeds.filter((f) => f.status === "offline").length;
  const degraded = feeds.filter((f) => f.status === "degraded").length;
  const stale = feeds.length - live - offline - degraded;

  return (
    <div className="mb-8">
      <div className="flex items-center gap-4 mb-4">
        <button
          onClick={() => setFeedsOpen(!feedsOpen)}
          className="uppercase flex items-center gap-2"
          style={{
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontFamily: "Inter, system-ui, sans-serif",
            fontSize: "13px",
          }}
        >
          FEEDS ({feeds.length})
          <span style={{ fontSize: "12px" }}>{feedsOpen ? "−" : "+"}</span>
        </button>

        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="uppercase px-3 py-1 border"
          style={{
            color: refreshing ? "var(--text-muted)" : "var(--accent)",
            borderColor: refreshing ? "var(--border)" : "var(--accent)",
            letterSpacing: "0.08em",
            background: "none",
            cursor: refreshing ? "wait" : "pointer",
            fontSize: "12px",
            opacity: refreshing ? 0.6 : 1,
          }}
        >
          {refreshing ? "FETCHING..." : "REFRESH ALL"}
        </button>

        {feedsOpen && (
          <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>
            {live} live / {stale} stale / {degraded} degraded / {offline} offline
          </span>
        )}
      </div>

      {feedsOpen && (
        <div className="border" style={{ borderColor: "var(--border)" }}>
          {/* Column headers */}
          <div
            className="px-4 py-2 flex items-center gap-4"
            style={{ background: "var(--bg)", borderBottom: "1px solid var(--border)" }}
          >
            <span style={{ width: "12px", flexShrink: 0 }} />
            <span
              className="flex-1 min-w-0 uppercase"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
            >
              SOURCE / FEED NAME &amp; KEYWORD
            </span>
            <span
              className="flex-shrink-0 uppercase"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px", minWidth: "60px", textAlign: "right" }}
            >
              RAW VALUE
            </span>
            <div className="flex items-center gap-1 flex-shrink-0" style={{ width: "100px" }}>
              <span
                className="uppercase"
                style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}
              >
                NORMALIZED
              </span>
              <span
                title="Score from 0-100 based on where this value sits in its 5-year historical range"
                style={{
                  color: "var(--text-muted)",
                  fontSize: "11px",
                  cursor: "help",
                  border: "1px solid var(--border)",
                  width: "14px",
                  height: "14px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  lineHeight: "1",
                }}
              >
                ?
              </span>
            </div>
            <span
              className="flex-shrink-0 uppercase"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px", minWidth: "80px", textAlign: "right" }}
            >
              LAST UPDATED
            </span>
            <span
              className="flex-shrink-0 uppercase"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px", minWidth: "60px", textAlign: "right" }}
            >
              STATUS
            </span>
          </div>
          {feeds.map((feed, i) => {
            const isExpanded = expandedFeed === feed.id;
            const score = feed.normalizedScore != null ? Math.round(feed.normalizedScore) : null;

            return (
              <div
                key={feed.id}
                style={{
                  borderTop: i > 0 ? "1px solid var(--border)" : "none",
                  background: "var(--surface)",
                }}
              >
                <button
                  onClick={() => setExpandedFeed(isExpanded ? null : feed.id)}
                  className="w-full px-4 py-3 flex items-center gap-4 text-left"
                  style={{ background: "none", border: "none", cursor: "pointer" }}
                >
                  <span style={{ color: "var(--text-muted)", fontSize: "11px", width: "12px", flexShrink: 0 }}>
                    {isExpanded ? "−" : "+"}
                  </span>

                  <div className="flex-1 min-w-0">
                    <span style={{ color: "var(--text)", fontSize: "14px", display: "block" }}>
                      {formatFeedName(feed)}
                    </span>
                    <span style={{ color: "#242424", fontSize: "11px", fontFamily: "JetBrains Mono, monospace" }}>
                      {feed.seriesId || feed.keyword || feed.source}
                    </span>
                  </div>

                  <span
                    className="flex-shrink-0"
                    style={{
                      color: "var(--text)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "13px",
                      minWidth: "60px",
                      textAlign: "right",
                    }}
                  >
                    {formatRawValue(feed)}
                  </span>

                  <div className="flex items-center gap-2 flex-shrink-0" style={{ width: "100px" }}>
                    <div
                      style={{
                        width: "60px",
                        height: "6px",
                        background: "var(--surface-alt)",
                        position: "relative",
                      }}
                    >
                      {score != null && (
                        <div
                          style={{
                            width: `${Math.min(score, 100)}%`,
                            height: "100%",
                            background: "var(--accent)",
                          }}
                        />
                      )}
                    </div>
                    <span
                      style={{
                        color: score != null ? "var(--accent)" : "var(--text-muted)",
                        fontFamily: "JetBrains Mono, monospace",
                        fontSize: "13px",
                        minWidth: "24px",
                        textAlign: "right",
                      }}
                    >
                      {score != null ? score : "——"}
                    </span>
                  </div>

                  <span
                    className="flex-shrink-0"
                    style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "11px", minWidth: "80px", textAlign: "right" }}
                  >
                    {feed.lastFetched ? new Date(feed.lastFetched).toLocaleDateString() : "——"}
                  </span>

                  <FeedStatusBadge status={feed.status} />
                </button>

                {isExpanded && (
                  <div
                    className="px-4 pb-3 pl-10"
                    style={{ background: "var(--surface)" }}
                  >
                    <div className="grid grid-cols-2 gap-x-6 gap-y-2" style={{ maxWidth: "600px" }}>
                      <div>
                        <span className="uppercase block" style={{ color: "#242424", letterSpacing: "0.08em", fontSize: "11px", marginBottom: "2px" }}>
                          SOURCE
                        </span>
                        <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                          {feed.source} — {feed.sourceType}
                        </span>
                      </div>
                      <div>
                        <span className="uppercase block" style={{ color: "#242424", letterSpacing: "0.08em", fontSize: "11px", marginBottom: "2px" }}>
                          CONFIRMING DIRECTION
                        </span>
                        <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                          {feed.confirmingDirection === "higher" ? "↑ Higher confirms" : "↓ Lower confirms"}
                        </span>
                      </div>
                      <div>
                        <span className="uppercase block" style={{ color: "#242424", letterSpacing: "0.08em", fontSize: "11px", marginBottom: "2px" }}>
                          WEIGHT
                        </span>
                        <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
                          {feed.weight.toFixed(2)}
                        </span>
                      </div>
                      <div>
                        <span className="uppercase block" style={{ color: "#242424", letterSpacing: "0.08em", fontSize: "11px", marginBottom: "2px" }}>
                          UPDATE FREQ
                        </span>
                        <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                          {feed.updateFrequency}
                        </span>
                      </div>
                    </div>
                    {feed.description && (
                      <p className="mt-2" style={{ color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.5" }}>
                        {feed.description}
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function FeedStatusBadge({ status }: { status: string }) {
  const config: Record<string, string> = {
    live: "var(--status-live)",
    stale: "var(--status-stale)",
    degraded: "var(--status-degraded)",
    offline: "var(--status-offline)",
  };
  const color = config[status] || config.stale;

  return (
    <span
      className="uppercase flex-shrink-0"
      style={{
        color,
        letterSpacing: "0.08em",
        fontSize: "11px",
        minWidth: "60px",
        textAlign: "right",
      }}
    >
      {status.toUpperCase()}
    </span>
  );
}

function EffectCard({ effect, thesisId, onUpdated }: { effect: Effect; thesisId: string; onUpdated: () => void }) {
  const [expanded, setExpanded] = useState(false);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete "${effect.title}"? This cannot be undone.`)) return;
    await api.deleteEffect(effect.id);
    onUpdated();
  };

  const tickers = effect.equityBets.map((b) => b.ticker);
  const hasContent = effect.equityBets.length > 0 || effect.startupOpportunities.length > 0 || (effect.childEffects && effect.childEffects.length > 0);

  return (
    <div
      className="border"
      style={{ background: "var(--surface)", borderColor: "var(--border)", cursor: hasContent ? "pointer" : "default" }}
      onClick={() => hasContent && setExpanded(!expanded)}
    >
      {/* Collapsed: clean headline card */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2">
              <Link
                href={`/thesis/${thesisId}/effect/${effect.id}`}
                className="font-bold uppercase hover:underline"
                style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3", textUnderlineOffset: "3px", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}
                onClick={(e) => e.stopPropagation()}
              >
                {effect.title}
              </Link>
              <button
                onClick={handleDelete}
                className="flex-shrink-0 mt-0.5"
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
                title="Delete effect"
              >
                <TrashIcon size={14} />
              </button>
            </div>
            <p className="mt-2" style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}>
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

        {/* Footer: tickers + expand toggle */}
        {hasContent && (
          <div className="flex items-center justify-between mt-4">
            <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {tickers.map((t, i) => (
                <span key={t}>
                  <span style={{ color: "#FF4500" }}>{t}</span>
                  {i < tickers.length - 1 && <span style={{ color: "#5A5A5A" }}> · </span>}
                </span>
              ))}
            </div>
            <span
              className="uppercase flex-shrink-0"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              {expanded ? "— COLLAPSE ▲" : "+ EXPAND ▾"}
            </span>
          </div>
        )}
      </div>

      {/* Expanded: full detail */}
      {expanded && (
        <div className="px-5 pb-5" onClick={(e) => e.stopPropagation()}>
          {/* Equity Bets — full cards */}
          {effect.equityBets.length > 0 && (
            <div className="pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              <span className="uppercase block mb-3" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
                EQUITY BETS
              </span>
              <div className="grid grid-cols-1 gap-0">
                {effect.equityBets.map((bet) => (
                  <EquityBetCard key={bet.id} bet={bet} />
                ))}
              </div>
            </div>
          )}

          {/* Startup Opportunities */}
          {effect.startupOpportunities.length > 0 && (
            <div className="mt-4 pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              <span className="uppercase block mb-3" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
                STARTUP OPPORTUNITIES
              </span>
              <div className="grid grid-cols-1 gap-0">
                {effect.startupOpportunities.map((opp) => (
                  <StartupCard key={opp.id} opportunity={opp} />
                ))}
              </div>
            </div>
          )}

          {/* 3rd order effects */}
          {effect.childEffects && effect.childEffects.length > 0 && (
            <div className="mt-4 pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              <span className="uppercase block mb-3" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "12px" }}>
                3RD ORDER EFFECTS ({effect.childEffects.length})
              </span>
              <div className="pl-4" style={{ borderLeft: "1px solid var(--border)" }}>
                {effect.childEffects.map((child) => (
                  <div key={child.id} className="mb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 mr-3">
                        <h4
                          className="font-bold uppercase"
                          style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3", fontSize: "13px" }}
                        >
                          {child.title}
                        </h4>
                        <p className="mt-1" style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "13px" }}>
                          {child.description}
                        </p>
                        {child.equityBets && child.equityBets.length > 0 && (
                          <div className="mt-1" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>
                            {child.equityBets.map((bet, i) => (
                              <span key={bet.id}>
                                <span style={{ color: "#FF4500" }}>{bet.ticker}</span>
                                {i < child.equityBets.length - 1 && <span style={{ color: "#5A5A5A" }}> · </span>}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <Needle score={child.thi.score} size="sm" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AddEffectButton({ thesisId, onCreated }: { thesisId: string; onCreated: () => void }) {
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
        style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)", outline: "none", fontSize: "14px" }}
      />
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
        className="px-2 py-1 border flex-1"
        style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)", outline: "none", fontSize: "14px" }}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <button
        onClick={handleSubmit}
        className="uppercase px-2 py-1 border"
        style={{ color: "var(--text)", borderColor: "var(--text)", background: "none", cursor: "pointer", letterSpacing: "0.08em", fontSize: "13px" }}
      >
        ADD
      </button>
      <button
        onClick={() => setOpen(false)}
        style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
      >
        <TrashIcon size={14} />
      </button>
    </div>
  );
}
