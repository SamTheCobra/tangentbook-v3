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
          ————————
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
    <ErrorBoundary>
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
            <div className="mb-3 flex items-center gap-4">
              <button
                onClick={async () => {
                  await api.refreshFeeds(id);
                  const [t, f] = await Promise.all([api.getThesis(id), api.getFeeds(id)]);
                  setThesis(t);
                  setFeeds(f);
                }}
                className="text-xs uppercase hover:underline"
                style={{
                  color: "var(--text-muted)",
                  letterSpacing: "0.08em",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  textUnderlineOffset: "3px",
                }}
              >
                REFRESH
              </button>
              {(() => {
                const live = feeds.filter((f) => f.status === "live").length;
                const offline = feeds.filter((f) => f.status === "offline").length;
                const degraded = feeds.filter((f) => f.status === "degraded").length;
                return (
                  <span style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "11px" }}>
                    {live} live / {feeds.length - live - offline - degraded} stale / {degraded} degraded / {offline} offline
                  </span>
                );
              })()}
            </div>
          )}

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
              className="text-xs uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
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

        {/* Effects */}
        {/* Effect Chain Diagram */}
        {thesis.effects.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="text-xs uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
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

        {/* Effects Grid */}
        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
        <div className="flex items-center justify-between mb-4">
          <h3
            className="text-xs uppercase"
            style={{ color: "var(--text-muted)", letterSpacing: "0.08em" }}
          >
            2ND ORDER EFFECTS ({thesis.effects.length})
          </h3>
          <AddEffectButton thesisId={thesis.id} onCreated={async () => {
            const t = await api.getThesis(id);
            setThesis(t);
          }} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
          {thesis.effects.map((effect) => (
            <EffectCard key={effect.id} effect={effect} thesisId={thesis.id} onUpdated={async () => {
              const t = await api.getThesis(id);
              setThesis(t);
            }} />
          ))}
        </div>
      </div>
    </main>
    </ErrorBoundary>
  );
}

function EffectCard({ effect, thesisId, onUpdated }: { effect: Effect; thesisId: string; onUpdated: () => void }) {
  const [expanded, setExpanded] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Delete "${effect.title}"? This cannot be undone.`)) return;
    await api.deleteEffect(effect.id);
    onUpdated();
  };

  return (
    <div className="border p-5" style={{ background: "var(--surface)", borderColor: "var(--border)" }}>
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-3">
          <div className="flex items-start justify-between">
            <Link
              href={`/thesis/${thesisId}/effect/${effect.id}`}
              className="font-bold uppercase text-xs hover:underline"
              style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3", textUnderlineOffset: "3px" }}
            >
              {effect.title}
            </Link>
            <div className="flex items-center gap-1 ml-1">
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-xs"
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
              >
                {expanded ? "−" : "+"}
              </button>
              <button
                onClick={handleDelete}
                className="text-xs"
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
                title="Delete effect"
              >
                x
              </button>
            </div>
          </div>
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
              <span className="text-xs uppercase block mb-2" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}>
                EQUITY BETS
              </span>
              {effect.equityBets.map((bet) => (
                <div key={bet.id} className="flex items-center gap-3 mb-1">
                  <span style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>{bet.ticker}</span>
                  <span className="text-xs uppercase" style={{
                    color: bet.role === "BENEFICIARY" ? "var(--positive)" : bet.role === "HEADWIND" ? "var(--text-muted)" : "var(--accent)",
                    fontSize: "9px", letterSpacing: "0.08em",
                  }}>{bet.role}</span>
                </div>
              ))}
            </div>
          )}
          {effect.startupOpportunities.length > 0 && (
            <div>
              <span className="text-xs uppercase block mb-2" style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "10px" }}>
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
        className="text-xs uppercase"
        style={{
          color: "var(--text-muted)",
          letterSpacing: "0.08em",
          background: "none",
          border: "none",
          cursor: "pointer",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
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
        className="text-xs px-2 py-1 border"
        style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)", outline: "none" }}
      />
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
        className="text-xs px-2 py-1 border flex-1"
        style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)", outline: "none" }}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <button
        onClick={handleSubmit}
        className="text-xs uppercase px-2 py-1 border"
        style={{ color: "var(--text)", borderColor: "var(--text)", background: "none", cursor: "pointer", letterSpacing: "0.08em" }}
      >
        ADD
      </button>
      <button
        onClick={() => setOpen(false)}
        className="text-xs"
        style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer" }}
      >
        x
      </button>
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
