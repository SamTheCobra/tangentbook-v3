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
  Feed,
  Effect,
  ScoringBreakdown,
  EvidenceDimension,
} from "@/lib/api";

export default function ThesisDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [breakdown, setBreakdown] = useState<ScoringBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [feedsOpen, setFeedsOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [scoringOpen, setScoringOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"bets" | "startups">("bets");

  const reloadThesis = async () => {
    const [t, b] = await Promise.all([
      api.getThesis(id),
      api.getScoringBreakdown(id),
    ]);
    setThesis(t);
    setBreakdown(b);
  };

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getThesis(id),
      api.getFeeds(id),
      api.getScoringBreakdown(id),
    ])
      .then(([t, f, b]) => {
        setThesis(t);
        setFeeds(f);
        setBreakdown(b);
      })
      .catch(() => {})
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
      const [t, f, b] = await Promise.all([
        api.getThesis(id),
        api.getFeeds(id),
        api.getScoringBreakdown(id),
      ]);
      setThesis(t);
      setFeeds(f);
      setBreakdown(b);
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
                formulaText={thiFormula}
              />
            </div>
          </div>

          {/* Collapsible scoring breakdown trigger */}
          <button
            onClick={() => setScoringOpen(!scoringOpen)}
            className="uppercase flex items-center gap-2 mb-6"
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

          {/* ══════════════════════════════════════════════════
              SECTION 2: SCORING BREAKDOWN (collapsible)
              ══════════════════════════════════════════════════ */}
          {scoringOpen && breakdown && (
            <div className="mb-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-4">
                <EvidenceColumn breakdown={breakdown} />
                <MomentumColumn breakdown={breakdown} />
                <DataQualityColumn breakdown={breakdown} />
              </div>
            </div>
          )}

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
              {activeTab === "bets" && thesis.equityBets.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                  {thesis.equityBets.map((bet) => (
                    <EquityBetCard key={bet.id} bet={bet} />
                  ))}
                </div>
              )}
              {activeTab === "startups" &&
                thesis.startupOpportunities.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
                    {thesis.startupOpportunities.map((opp) => (
                      <StartupCard key={opp.id} opportunity={opp} />
                    ))}
                  </div>
                )}
              <div
                className="mb-8"
                style={{ borderTop: "1px solid var(--border)" }}
              />
            </>
          )}

          {/* ══════════════════════════════════════════════════
              SECTION 4: FEEDS
              ══════════════════════════════════════════════════ */}
          <FeedPanel
            feeds={feeds}
            feedsOpen={feedsOpen}
            setFeedsOpen={setFeedsOpen}
            refreshing={refreshing}
            onRefresh={handleRefreshFeeds}
          />

          {/* ══════════════════════════════════════════════════
              SECTION 5: EFFECT THUMBNAILS
              ══════════════════════════════════════════════════ */}
          {thesis.effects.length > 0 && (
            <>
              <div
                className="mb-8"
                style={{ borderTop: "1px solid var(--border)" }}
              />
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
            style={{
              color: "var(--text)",
              letterSpacing: "0.08em",
              fontSize: "13px",
            }}
          >
            EVIDENCE
          </span>
          <span
            className="uppercase"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            50%
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
        <span
          className="uppercase"
          style={{
            color: "var(--text)",
            letterSpacing: "0.08em",
            fontSize: "11px",
          }}
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
      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "11px",
          lineHeight: "1.4",
          marginBottom: "4px",
        }}
      >
        {dim.description}
      </p>
      {dim.feeds.length > 0 ? (
        <div
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "11px",
          }}
        >
          {dim.feeds.map((f) => (
            <div
              key={f.name}
              className="flex items-center justify-between"
              style={{ color: "var(--text-muted)", lineHeight: "1.6" }}
            >
              <span>
                {f.name}{" "}
                <span
                  style={{
                    color:
                      f.status === "live"
                        ? "var(--status-live)"
                        : "var(--status-stale)",
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
          ))}
        </div>
      ) : (
        <span
          style={{
            color: "var(--text-muted)",
            fontSize: "11px",
            fontStyle: "italic",
          }}
        >
          No {label.toLowerCase()} feeds configured
        </span>
      )}
      {dim.lastUpdated && (
        <div
          style={{
            color: "#242424",
            fontSize: "10px",
            fontFamily: "JetBrains Mono, monospace",
            marginTop: "2px",
          }}
        >
          Updated {new Date(dim.lastUpdated).toLocaleDateString()}
        </div>
      )}
    </div>
  );
}

function MomentumColumn({ breakdown }: { breakdown: ScoringBreakdown }) {
  const m = breakdown.momentum;
  const entries = [
    {
      label: "30D MOMENTUM",
      weight: "50%",
      desc: "How much has the evidence score changed in the last 30 days? Positive = thesis accelerating.",
      data: m.thirtyDay,
    },
    {
      label: "90D MOMENTUM",
      weight: "35%",
      desc: "Medium-term direction — smooths out noise from the 30-day view.",
      data: m.ninetyDay,
    },
    {
      label: "1YR MOMENTUM",
      weight: "15%",
      desc: "Long-term structural direction — is this thesis gaining or losing ground over a full year?",
      data: m.oneYear,
    },
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
            style={{
              color: "var(--text)",
              letterSpacing: "0.08em",
              fontSize: "13px",
            }}
          >
            MOMENTUM
          </span>
          <span
            className="uppercase"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            30%
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
                style={{
                  color: "var(--text)",
                  letterSpacing: "0.08em",
                  fontSize: "11px",
                }}
              >
                {e.label}{" "}
                <span style={{ color: "var(--text-muted)" }}>{e.weight}</span>
              </span>
              <span
                style={{
                  color: "var(--accent)",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "13px",
                }}
              >
                {Math.round(e.data.score)}
              </span>
            </div>
            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "11px",
                lineHeight: "1.4",
                marginBottom: "4px",
              }}
            >
              {e.desc}
            </p>
            <div
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                color:
                  e.data.delta != null && e.data.delta >= 0
                    ? "#FF4500"
                    : "var(--text-muted)",
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
            style={{
              color: "var(--text)",
              letterSpacing: "0.08em",
              fontSize: "13px",
            }}
          >
            DATA QUALITY
          </span>
          <span
            className="uppercase"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            20%
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
          {Math.round(dq.score)}
        </span>
      </div>
      <div className="flex justify-center mb-4">
        <Needle score={dq.score} size="sm" label="" animated={true} />
      </div>
      <div className="flex flex-col gap-4">
        {/* Agreement */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span
              className="uppercase"
              style={{
                color: "var(--text)",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              AGREEMENT{" "}
              <span style={{ color: "var(--text-muted)" }}>50%</span>
            </span>
            <span
              style={{
                color: "var(--accent)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
              }}
            >
              {Math.round(dq.agreement.score)}
            </span>
          </div>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "11px",
              lineHeight: "1.4",
              marginBottom: "4px",
            }}
          >
            Do the feeds agree with each other? If some say &quot;confirming&quot; but
            others say &quot;refuting&quot;, confidence is low.
          </p>
          <div
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "12px",
              color: "var(--text-muted)",
            }}
          >
            {dq.agreement.pctConfirming != null
              ? `${dq.agreement.pctConfirming}% of feeds pointing confirming`
              : "— no scored feeds"}
          </div>
        </div>

        {/* Freshness */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span
              className="uppercase"
              style={{
                color: "var(--text)",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              FRESHNESS{" "}
              <span style={{ color: "var(--text-muted)" }}>30%</span>
            </span>
            <span
              style={{
                color: "var(--accent)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
              }}
            >
              {Math.round(dq.freshness.score)}
            </span>
          </div>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "11px",
              lineHeight: "1.4",
              marginBottom: "4px",
            }}
          >
            How recent is the data? Stale data = less reliable score.
          </p>
          <div
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "12px",
              color: "var(--text-muted)",
            }}
          >
            {dq.freshness.avgAgeDays != null
              ? `Avg age: ${dq.freshness.avgAgeDays}d`
              : "— no data"}{" "}
            · {dq.freshness.live} live / {dq.freshness.stale} stale /{" "}
            {dq.freshness.degraded} degraded
          </div>
        </div>

        {/* Source Quality */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span
              className="uppercase"
              style={{
                color: "var(--text)",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              SOURCE QUALITY{" "}
              <span style={{ color: "var(--text-muted)" }}>20%</span>
            </span>
            <span
              style={{
                color: "var(--accent)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
              }}
            >
              {Math.round(dq.sourceQuality.score)}
            </span>
          </div>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "11px",
              lineHeight: "1.4",
              marginBottom: "4px",
            }}
          >
            Are these feeds from authoritative sources? FRED/BLS = 100. Google
            Trends = 65. Estimated = 20.
          </p>
          <div
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "12px",
              color: "var(--text-muted)",
            }}
          >
            Weighted avg: {dq.sourceQuality.weightedAvg}/100
          </div>
        </div>
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
   FEED PANEL
   ═══════════════════════════════════════════════════════════════════════════ */

function formatFeedName(feed: Feed): string {
  return feed.name.replace(/^(Fred|Gtrends|Alpha Vantage)\s+/i, "");
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
            fontSize: "13px",
          }}
        >
          FEEDS ({feeds.length})
          <span style={{ fontSize: "12px" }}>{feedsOpen ? "▲" : "▾"}</span>
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
          <span
            style={{
              color: "var(--text-muted)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "12px",
            }}
          >
            {live} live / {stale} stale / {degraded} degraded / {offline}{" "}
            offline
          </span>
        )}
      </div>

      {feedsOpen && (
        <div className="border" style={{ borderColor: "var(--border)" }}>
          <div
            className="px-4 py-2 flex items-center gap-4"
            style={{
              background: "var(--bg)",
              borderBottom: "1px solid var(--border)",
            }}
          >
            <span style={{ width: "12px", flexShrink: 0 }} />
            <span
              className="flex-1 min-w-0 uppercase"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              SOURCE / FEED NAME
            </span>
            <span
              className="flex-shrink-0 uppercase"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
                minWidth: "60px",
                textAlign: "right",
              }}
            >
              RAW
            </span>
            <span
              className="flex-shrink-0 uppercase"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
                minWidth: "50px",
                textAlign: "right",
              }}
            >
              SCORE
            </span>
            <span
              className="flex-shrink-0 uppercase"
              style={{
                color: "var(--text-muted)",
                letterSpacing: "0.08em",
                fontSize: "11px",
                minWidth: "60px",
                textAlign: "right",
              }}
            >
              STATUS
            </span>
          </div>
          {feeds.map((feed, i) => {
            const isExpanded = expandedFeed === feed.id;
            const score =
              feed.normalizedScore != null
                ? Math.round(feed.normalizedScore)
                : null;

            return (
              <div
                key={feed.id}
                style={{
                  borderTop:
                    i > 0 ? "1px solid var(--border)" : "none",
                  background: "var(--surface)",
                }}
              >
                <button
                  onClick={() =>
                    setExpandedFeed(isExpanded ? null : feed.id)
                  }
                  className="w-full px-4 py-3 flex items-center gap-4 text-left"
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  <span
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "11px",
                      width: "12px",
                      flexShrink: 0,
                    }}
                  >
                    {isExpanded ? "−" : "+"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <span
                      style={{
                        color: "var(--text)",
                        fontSize: "14px",
                        display: "block",
                      }}
                    >
                      {formatFeedName(feed)}
                    </span>
                    <span
                      style={{
                        color: "#242424",
                        fontSize: "11px",
                        fontFamily: "JetBrains Mono, monospace",
                      }}
                    >
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
                  <span
                    className="flex-shrink-0"
                    style={{
                      color:
                        score != null
                          ? "var(--accent)"
                          : "var(--text-muted)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "13px",
                      minWidth: "50px",
                      textAlign: "right",
                    }}
                  >
                    {score != null ? score : "——"}
                  </span>
                  <FeedStatusBadge status={feed.status} />
                </button>
                {isExpanded && (
                  <div
                    className="px-4 pb-3 pl-10"
                    style={{ background: "var(--surface)" }}
                  >
                    <div
                      className="grid grid-cols-2 gap-x-6 gap-y-2"
                      style={{ maxWidth: "600px" }}
                    >
                      <div>
                        <span
                          className="uppercase block"
                          style={{
                            color: "#242424",
                            letterSpacing: "0.08em",
                            fontSize: "11px",
                            marginBottom: "2px",
                          }}
                        >
                          SOURCE
                        </span>
                        <span
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "13px",
                          }}
                        >
                          {feed.source} — {feed.sourceType}
                        </span>
                      </div>
                      <div>
                        <span
                          className="uppercase block"
                          style={{
                            color: "#242424",
                            letterSpacing: "0.08em",
                            fontSize: "11px",
                            marginBottom: "2px",
                          }}
                        >
                          DIRECTION
                        </span>
                        <span
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "13px",
                          }}
                        >
                          {feed.confirmingDirection === "higher"
                            ? "↑ Higher confirms"
                            : "↓ Lower confirms"}
                        </span>
                      </div>
                      <div>
                        <span
                          className="uppercase block"
                          style={{
                            color: "#242424",
                            letterSpacing: "0.08em",
                            fontSize: "11px",
                            marginBottom: "2px",
                          }}
                        >
                          WEIGHT
                        </span>
                        <span
                          style={{
                            color: "var(--text-muted)",
                            fontFamily: "JetBrains Mono, monospace",
                            fontSize: "13px",
                          }}
                        >
                          {feed.weight.toFixed(2)}
                        </span>
                      </div>
                      <div>
                        <span
                          className="uppercase block"
                          style={{
                            color: "#242424",
                            letterSpacing: "0.08em",
                            fontSize: "11px",
                            marginBottom: "2px",
                          }}
                        >
                          LAST FETCHED
                        </span>
                        <span
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "13px",
                          }}
                        >
                          {feed.lastFetched
                            ? new Date(feed.lastFetched).toLocaleString()
                            : "——"}
                        </span>
                      </div>
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
