"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import { api, ThesisDetail, Feed, Effect } from "@/lib/api";

export default function ThesisDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedsOpen, setFeedsOpen] = useState(false);

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
          ————
        </div>
      </main>
    );
  }

  if (!thesis) {
    return (
      <main className="min-h-screen" style={{ background: "var(--bg)" }}>
        <Header />
        <div className="px-12 py-8" style={{ color: "var(--text-muted)" }}>Thesis not found.</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header />
      <div className="px-12 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6">
          <Link
            href="/"
            className="text-xs uppercase hover:underline"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em", textUnderlineOffset: "3px" }}
          >
            TANGENTBOOK
          </Link>
          <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>/</span>
          <span
            className="text-xs uppercase"
            style={{ color: "var(--text)", letterSpacing: "0.08em" }}
          >
            {thesis.title}
          </span>
        </div>

        {/* Hero section */}
        <div className="flex gap-12 mb-8">
          <div className="flex-1">
            <h1
              className="font-bold uppercase text-3xl mb-2"
              style={{ color: "var(--text)", letterSpacing: "-0.04em" }}
            >
              {thesis.title}
            </h1>
            <p className="text-base mb-4" style={{ color: "var(--text-muted)", lineHeight: "1.6" }}>
              {thesis.description}
            </p>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}>
                  HORIZON
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
                  {thesis.timeHorizon}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}>
                  CONVICTION
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
                  {thesis.userConviction.score}/10
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "11px" }}>
                  DIRECTION
                </span>
                <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
                  {thesis.thi.direction.toUpperCase()}
                </span>
              </div>
            </div>
            {thesis.userConviction.divergenceWarning && (
              <div
                className="mt-3 px-3 py-2 border text-xs"
                style={{
                  borderColor: "var(--accent)",
                  color: "var(--accent)",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              >
                {thesis.userConviction.divergenceWarning}
              </div>
            )}
          </div>
          <div className="flex-shrink-0">
            <Needle score={thesis.thi.score} size="lg" label="THESIS HEALTH INDEX" />
          </div>
        </div>

        {/* 1px separator */}
        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* Sub-needles row */}
        <div className="flex gap-12 mb-8">
          <div className="text-center">
            <Needle score={thesis.thi.evidence.score} size="md" label="EVIDENCE" />
            <span
              className="text-xs uppercase mt-1 block"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
            >
              WEIGHT {(thesis.thi.evidence.weight * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-center">
            <Needle score={thesis.thi.momentum.score} size="md" label="MOMENTUM" />
            <span
              className="text-xs uppercase mt-1 block"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
            >
              WEIGHT {(thesis.thi.momentum.weight * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-center">
            <Needle score={thesis.thi.conviction.score} size="md" label="DATA QUALITY" />
            <span
              className="text-xs uppercase mt-1 block"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
            >
              WEIGHT {(thesis.thi.conviction.weight * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* 1px separator */}
        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* Feed Health Panel */}
        <div className="mb-8">
          <button
            onClick={() => setFeedsOpen(!feedsOpen)}
            className="text-xs uppercase mb-4 flex items-center gap-2"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              background: "none",
              border: "none",
              cursor: "pointer",
              fontFamily: "Inter, system-ui, sans-serif",
            }}
          >
            FEEDS ({feeds.length})
            <span style={{ fontSize: "10px" }}>{feedsOpen ? "−" : "+"}</span>
          </button>

          {feedsOpen && (
            <div className="border" style={{ borderColor: "var(--border)" }}>
              {feeds.map((feed, i) => (
                <div
                  key={feed.id}
                  className="px-4 py-2 flex items-center gap-4"
                  style={{
                    borderTop: i > 0 ? "1px solid var(--border)" : "none",
                    background: "var(--surface)",
                  }}
                >
                  <span
                    className="text-xs uppercase px-2 py-0.5 border flex-shrink-0"
                    style={{
                      color: "var(--text-muted)",
                      borderColor: "var(--border)",
                      letterSpacing: "0.08em",
                      fontSize: "9px",
                      minWidth: "60px",
                      textAlign: "center",
                    }}
                  >
                    {feed.source}
                  </span>
                  <span className="text-xs flex-1" style={{ color: "var(--text)" }}>
                    {feed.name}
                  </span>
                  <span
                    className="text-xs"
                    style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace" }}
                  >
                    {feed.lastFetched ? new Date(feed.lastFetched).toLocaleDateString() : "——"}
                  </span>
                  <span
                    className="text-xs"
                    style={{
                      color: "var(--text)",
                      fontFamily: "JetBrains Mono, monospace",
                      minWidth: "32px",
                      textAlign: "right",
                    }}
                  >
                    {feed.normalizedScore != null ? Math.round(feed.normalizedScore) : "——"}
                  </span>
                  <StatusDot status={feed.status} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Equity Bets */}
        {thesis.equityBets.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="text-xs uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
            >
              EQUITY BETS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {thesis.equityBets.map((bet) => (
                <div
                  key={bet.id}
                  className="border p-4"
                  style={{ background: "var(--surface)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className="font-bold"
                      style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "16px" }}
                    >
                      {bet.ticker}
                    </span>
                    <span
                      className="text-xs uppercase px-2 py-0.5 border"
                      style={{
                        color:
                          bet.role === "BENEFICIARY"
                            ? "var(--positive)"
                            : bet.role === "HEADWIND"
                            ? "var(--text-muted)"
                            : "var(--accent)",
                        borderColor:
                          bet.role === "BENEFICIARY"
                            ? "var(--positive)"
                            : bet.role === "HEADWIND"
                            ? "var(--text-muted)"
                            : "var(--accent)",
                        letterSpacing: "0.08em",
                        fontSize: "9px",
                      }}
                    >
                      {bet.role}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
                    {bet.rationale}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Startup Opportunities */}
        {thesis.startupOpportunities.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="text-xs uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
            >
              STARTUP OPPORTUNITIES
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {thesis.startupOpportunities.map((opp) => (
                <div
                  key={opp.id}
                  className="border p-4"
                  style={{ background: "var(--surface)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm" style={{ color: "var(--text)" }}>
                      {opp.name}
                    </span>
                    <span
                      className="text-xs uppercase px-2 py-0.5 border"
                      style={{
                        color:
                          opp.timing === "RIGHT_TIMING"
                            ? "var(--positive)"
                            : opp.timing === "TOO_EARLY"
                            ? "var(--text-muted)"
                            : "var(--accent)",
                        borderColor:
                          opp.timing === "RIGHT_TIMING"
                            ? "var(--positive)"
                            : opp.timing === "TOO_EARLY"
                            ? "var(--text-muted)"
                            : "var(--accent)",
                        letterSpacing: "0.08em",
                        fontSize: "9px",
                      }}
                    >
                      {opp.timing.replace("_", " ")}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
                    {opp.oneLiner}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Effects */}
        {thesis.effects.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="text-xs uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
            >
              2ND ORDER EFFECTS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
              {thesis.effects.map((effect) => (
                <EffectCard key={effect.id} effect={effect} />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}

function EffectCard({ effect }: { effect: Effect }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border p-5" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-left"
            style={{ background: "none", border: "none", cursor: "pointer" }}
          >
            <h4
              className="font-bold uppercase text-xs"
              style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3" }}
            >
              {effect.title}
            </h4>
          </button>
          <p className="mt-1 text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
            {effect.description}
          </p>
        </div>
        <Needle score={effect.thi.score} size="sm" />
      </div>

      {expanded && (
        <div className="mt-3 pt-3" style={{ borderTop: "1px solid var(--border)" }}>
          {effect.equityBets.length > 0 && (
            <div className="mb-3">
              <span
                className="text-xs uppercase block mb-2"
                style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
              >
                EQUITY BETS
              </span>
              {effect.equityBets.map((bet) => (
                <div key={bet.id} className="flex items-center gap-3 mb-1">
                  <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>
                    {bet.ticker}
                  </span>
                  <span
                    className="text-xs uppercase"
                    style={{
                      color:
                        bet.role === "BENEFICIARY" ? "var(--positive)" : bet.role === "HEADWIND" ? "var(--text-muted)" : "var(--accent)",
                      fontSize: "9px",
                      letterSpacing: "0.08em",
                    }}
                  >
                    {bet.role}
                  </span>
                </div>
              ))}
            </div>
          )}

          {effect.startupOpportunities.length > 0 && (
            <div>
              <span
                className="text-xs uppercase block mb-2"
                style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}
              >
                OPPORTUNITIES
              </span>
              {effect.startupOpportunities.map((opp) => (
                <div key={opp.id} className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>
                  <span style={{ color: "var(--text)" }}>{opp.name}</span> — {opp.oneLiner}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === "live"
      ? "var(--positive)"
      : status === "stale"
      ? "var(--accent)"
      : status === "degraded"
      ? "var(--text-muted)"
      : "var(--text-muted)";

  return (
    <div className="flex items-center gap-2">
      <div
        className="w-2 h-2"
        style={{ background: color, borderRadius: "1px" }}
      />
      {status !== "live" && (
        <span
          className="text-xs uppercase"
          style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "9px" }}
        >
          {status.toUpperCase()}
        </span>
      )}
    </div>
  );
}
