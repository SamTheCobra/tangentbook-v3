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
import { api, ThesisDetail, Effect } from "@/lib/api";

export default function EffectDetailPage() {
  const params = useParams();
  const thesisId = params.id as string;
  const effectId = params.effectId as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [effect, setEffect] = useState<Effect | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"bets" | "startups">("bets");

  const reloadEffect = async () => {
    const [t, e] = await Promise.all([
      api.getThesis(thesisId),
      api.getEffect(effectId),
    ]);
    setThesis(t);
    setEffect(e);
  };

  useEffect(() => {
    if (!thesisId || !effectId) return;
    Promise.all([api.getThesis(thesisId), api.getEffect(effectId)])
      .then(([t, e]) => {
        setThesis(t);
        setEffect(e);
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
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
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
  parentEffectId,
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
