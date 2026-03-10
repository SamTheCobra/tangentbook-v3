"use client";

import { useState } from "react";
import { EquityBet, EFSScore } from "@/lib/api";
import StockSparkline from "./StockSparkline";
import GradientBar from "./GradientBar";

interface EquityBetCardProps {
  bet: EquityBet;
  efs?: EFSScore | null;
  rank?: number;
}

function EFSBreakdownRow({
  label,
  weightPct,
  score,
  explanation,
  sourceUrl,
}: {
  label: string;
  weightPct: number;
  score: number;
  explanation: string;
  sourceUrl?: string;
}) {
  return (
    <div className="mb-3">
      <div className="flex items-center gap-3">
        <span
          className="uppercase"
          style={{
            color: "var(--text-muted)",
            fontSize: "11px",
            letterSpacing: "0.08em",
            minWidth: "160px",
          }}
        >
          {sourceUrl ? (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--text-muted)", textDecoration: "none" }}
              onMouseEnter={(e) => (e.currentTarget.style.textDecoration = "underline")}
              onMouseLeave={(e) => (e.currentTarget.style.textDecoration = "none")}
            >
              {label} ↗
            </a>
          ) : (
            label
          )}
        </span>
        <span
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "11px",
            color: "var(--text-muted)",
            minWidth: "30px",
          }}
        >
          {weightPct}%
        </span>
        <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "11px", color: "var(--text-muted)" }}>
          &rarr;
        </span>
        <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "13px", color: "var(--text)", minWidth: "24px" }}>
          {Math.round(score)}
        </span>
        <span style={{ flex: 1 }}>
          <GradientBar value={score} height={6} />
        </span>
      </div>
      <div
        style={{
          color: "var(--text-muted)",
          fontSize: "12px",
          marginTop: "2px",
          paddingLeft: "0px",
        }}
      >
        {explanation}
      </div>
    </div>
  );
}

function buildExplanation(efs: EFSScore, field: string): string {
  switch (field) {
    case "revenue": {
      if (efs.revenueAlignmentPct != null) {
        return `${efs.revenueAlignmentPct}% of revenue is thesis-aligned (SEC 10-K)`;
      }
      return "Revenue alignment data unavailable";
    }
    case "beta": {
      if (efs.thesisBetaRaw != null) {
        return `${efs.thesisBetaRaw.toFixed(2)} correlation with THI over 12 months`;
      }
      return "Thesis beta data unavailable";
    }
    case "momentum": {
      if (efs.stockReturn90d != null && efs.thiDelta90d != null) {
        const stockDir = efs.stockReturn90d >= 0 ? "+" : "";
        const thiDir = efs.thiDelta90d >= 0 ? "+" : "";
        const bothConfirming =
          (efs.stockReturn90d >= 0 && efs.thiDelta90d >= 0) ||
          (efs.stockReturn90d < 0 && efs.thiDelta90d < 0);
        return `Stock ${stockDir}${efs.stockReturn90d}% and THI ${thiDir}${efs.thiDelta90d}pts over 90d — ${bothConfirming ? "both confirming" : "diverging"}`;
      }
      return "Momentum data unavailable";
    }
    case "valuation": {
      if (efs.forwardPE != null && efs.sectorMedianPE != null) {
        const premium = ((efs.forwardPE / efs.sectorMedianPE - 1) * 100).toFixed(0);
        return `Fwd P/E ${efs.forwardPE}x vs sector ${efs.sectorMedianPE}x (${Number(premium) >= 0 ? premium + "% premium" : Math.abs(Number(premium)) + "% discount"})`;
      }
      return "Valuation data unavailable";
    }
    case "purity": {
      if (efs.segmentCount != null) {
        return `${efs.segmentCount} business segment${efs.segmentCount !== 1 ? "s" : ""}`;
      }
      return "Signal purity data unavailable";
    }
    default:
      return "";
  }
}

export default function EquityBetCard({ bet, efs, rank }: EquityBetCardProps) {
  const [expanded, setExpanded] = useState(false);

  const efsScore = efs ? Math.round(efs.efsScore) : null;
  const isHighConviction = rank != null && rank <= 3;

  return (
    <div
      className="flex flex-col"
      style={{ background: "#1C1C1C", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "4px", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.5)" }}
    >
      {/* Header row: Ticker */}
      <div className="flex items-center gap-3 px-3 pt-4 pb-2">
        <a
          href={`https://finance.yahoo.com/quote/${bet.ticker}`}
          target="_blank"
          rel="noopener noreferrer"
          className="font-bold"
          style={{
            color: "var(--accent)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "24px",
            letterSpacing: "-0.02em",
            textDecoration: "none",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.textDecoration = "underline")}
          onMouseLeave={(e) => (e.currentTarget.style.textDecoration = "none")}
        >
          {bet.ticker} ↗
        </a>
      </div>

      {/* Sparkline row: full card width */}
      <div className="px-3">
        <StockSparkline ticker={bet.ticker} />
      </div>

      {/* EFS Score Bar */}
      <div className="px-3 pt-3">
        {efs ? (
          <>
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: 0,
                width: "100%",
                textAlign: "left",
              }}
            >
              <div className="flex items-center gap-3">
                <span
                  className="uppercase"
                  style={{
                    color: "var(--text-muted)",
                    letterSpacing: "0.08em",
                    fontSize: "11px",
                    flexShrink: 0,
                  }}
                >
                  EFS
                </span>
                <span style={{ flex: 1 }}>
                  <GradientBar value={efs.efsScore} height={8} />
                </span>
                <span
                  style={{
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: "13px",
                    color: "var(--text)",
                    flexShrink: 0,
                  }}
                >
                  {efsScore} / 100
                </span>
                {isHighConviction && (
                  <span
                    className="uppercase"
                    style={{
                      color: "#FF4500",
                      fontSize: "9px",
                      letterSpacing: "0.06em",
                      flexShrink: 0,
                      opacity: 0.8,
                    }}
                  >
                    TOP 3
                  </span>
                )}
                <span style={{ color: "var(--text-muted)", fontSize: "10px", marginLeft: "auto" }}>
                  {expanded ? "▲" : "▾"}
                </span>
              </div>
            </button>

            {/* Divergence warning */}
            {efs.momentumDirection === "DIVERGING" && (
              <div
                className="uppercase mt-1"
                style={{
                  color: "#FF4500",
                  fontSize: "12px",
                  letterSpacing: "0.05em",
                }}
              >
                &#9888; DIVERGENCE — Thesis weakening while stock is up. Review position.
              </div>
            )}

            {/* Expanded breakdown */}
            {expanded && (
              <div className="mt-4 pb-2">
                <div className="mb-3">
                  <span
                    className="uppercase font-bold"
                    style={{ color: "var(--text)", letterSpacing: "0.08em", fontSize: "12px" }}
                  >
                    EQUITY FIT SCORE: {efsScore} / 100
                  </span>
                  <div style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "2px" }}>
                    How purely does this stock capture the thesis?
                  </div>
                </div>

                <EFSBreakdownRow
                  label="Revenue Alignment"
                  weightPct={30}
                  score={efs.revenueAlignmentScore}
                  explanation={buildExplanation(efs, "revenue")}
                  sourceUrl={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=${encodeURIComponent(bet.ticker)}&type=10-K&dateb=&owner=include&count=10`}
                />
                <EFSBreakdownRow
                  label="Thesis Beta"
                  weightPct={25}
                  score={efs.thesisBetaScore}
                  explanation={buildExplanation(efs, "beta")}
                  sourceUrl={`https://finance.yahoo.com/quote/${bet.ticker}/history/`}
                />
                <EFSBreakdownRow
                  label="Momentum Alignment"
                  weightPct={20}
                  score={efs.momentumAlignmentScore}
                  explanation={buildExplanation(efs, "momentum")}
                  sourceUrl={`https://finance.yahoo.com/quote/${bet.ticker}/`}
                />
                <EFSBreakdownRow
                  label="Valuation Buffer"
                  weightPct={15}
                  score={efs.valuationBufferScore}
                  explanation={buildExplanation(efs, "valuation")}
                  sourceUrl={`https://finance.yahoo.com/quote/${bet.ticker}/key-statistics/`}
                />
                <EFSBreakdownRow
                  label="Signal Purity"
                  weightPct={10}
                  score={efs.signalPurityScore}
                  explanation={buildExplanation(efs, "purity")}
                  sourceUrl={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=${encodeURIComponent(bet.ticker)}&type=10-K&dateb=&owner=include&count=10`}
                />

                <div
                  style={{
                    borderTop: "1px solid var(--border)",
                    paddingTop: "8px",
                    marginTop: "4px",
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: "11px",
                    color: "var(--text-muted)",
                  }}
                >
                  EFS = ({Math.round(efs.revenueAlignmentScore)}&times;0.30)+({Math.round(efs.thesisBetaScore)}&times;0.25)+({Math.round(efs.momentumAlignmentScore)}&times;0.20)+({Math.round(efs.valuationBufferScore)}&times;0.15)+({Math.round(efs.signalPurityScore)}&times;0.10) ={" "}
                  <span style={{ color: "var(--text)" }}>
                    {(
                      efs.revenueAlignmentScore * 0.3 +
                      efs.thesisBetaScore * 0.25 +
                      efs.momentumAlignmentScore * 0.2 +
                      efs.valuationBufferScore * 0.15 +
                      efs.signalPurityScore * 0.1
                    ).toFixed(1)}
                  </span>
                </div>
              </div>
            )}
          </>
        ) : (
          <span
            style={{
              color: "var(--text-muted)",
              fontSize: "11px",
              fontFamily: "JetBrains Mono, monospace",
            }}
          >
            EFS —
          </span>
        )}
      </div>

      {/* Body */}
      <div className="px-3 pt-3 pb-4 flex flex-col flex-1">
        {/* Company name */}
        <div
          className="mb-1"
          style={{
            color: "var(--text)",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          {bet.companyName}
        </div>

        {/* Description: what they do + why it's a smart play */}
        <p
          style={{
            color: "#999",
            lineHeight: "1.5",
            fontSize: "13px",
          }}
        >
          {bet.companyDescription && `${bet.companyDescription} `}{bet.rationale}
        </p>

        {/* Footer: Role + Feedback + Time horizon */}
        <div className="mt-auto pt-2 flex items-center gap-3">
          <span
            className="uppercase px-2 py-0.5 border"
            style={{
              color: bet.role === "BENEFICIARY" ? "#FF4500" : bet.role === "HEADWIND" ? "#999" : "var(--text)",
              borderColor: bet.role === "BENEFICIARY" ? "#FF4500" : bet.role === "HEADWIND" ? "#999" : "var(--text)",
              letterSpacing: "0.08em",
              fontSize: "10px",
            }}
          >
            {bet.role}
          </span>
          {bet.role === "CANARY" && (
            <span style={{ color: "#FF4500", fontSize: 10, letterSpacing: "0.08em" }}>
              FEEDBACK INDICATOR
            </span>
          )}
          <span
            className="uppercase"
            style={{
              color: "#999",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            {bet.timeHorizon}
          </span>
        </div>
      </div>
    </div>
  );
}
