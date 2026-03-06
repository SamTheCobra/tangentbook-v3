"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import EquityBetCard from "@/components/EquityBetCard";
import StartupCard from "@/components/StartupCard";
import ErrorBoundary from "@/components/ErrorBoundary";
import { api, ThesisDetail, Effect } from "@/lib/api";

export default function EffectDetailPage() {
  const params = useParams();
  const thesisId = params.id as string;
  const effectId = params.effectId as string;
  const [thesis, setThesis] = useState<ThesisDetail | null>(null);
  const [effect, setEffect] = useState<Effect | null>(null);
  const [loading, setLoading] = useState(true);

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

        {/* Hero */}
        <div className="flex gap-12 mb-8">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span
                className="uppercase px-2 py-0.5 border"
                style={{ color: "var(--text-muted)", borderColor: "var(--border)", letterSpacing: "0.08em", fontSize: "12px" }}
              >
                {effect.order === 2 ? "2ND ORDER" : "3RD ORDER"} EFFECT
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
                  CONVICTION
                </span>
                <span style={{ color: "#E8440A", fontFamily: "JetBrains Mono, monospace", fontSize: "15px" }}>
                  {effect.userConviction.score}/10
                </span>
              </div>
            </div>
          </div>
          <div className="flex-shrink-0">
            <Needle score={effect.thi.score} size="lg" label="EFFECT HEALTH" />
          </div>
        </div>

        <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />

        {/* Equity Bets */}
        {effect.equityBets.length > 0 && (
          <>
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              EQUITY BETS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {effect.equityBets.map((bet) => (
                <EquityBetCard key={bet.id} bet={bet} />
              ))}
            </div>
          </>
        )}

        {/* Startup Opportunities */}
        {effect.startupOpportunities.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              STARTUP OPPORTUNITIES
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-0 mb-8">
              {effect.startupOpportunities.map((opp) => (
                <StartupCard key={opp.id} opportunity={opp} />
              ))}
            </div>
          </>
        )}

        {/* Child Effects */}
        {effect.childEffects && effect.childEffects.length > 0 && (
          <>
            <div className="mb-8" style={{ borderTop: "1px solid var(--border)" }} />
            <h3
              className="uppercase mb-4"
              style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
            >
              3RD ORDER EFFECTS
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-0 mb-8">
              {effect.childEffects.map((child) => (
                <div
                  key={child.id}
                  className="border p-5"
                  style={{ background: "var(--surface)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 mr-3">
                      <h4
                        className="font-bold uppercase"
                        style={{ color: "var(--text)", letterSpacing: "-0.03em", lineHeight: "1.3", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}
                      >
                        {child.title}
                      </h4>
                      <p className="mt-1" style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}>
                        {child.description}
                      </p>
                    </div>
                    <Needle score={child.thi.score} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </main>
    </ErrorBoundary>
  );
}
