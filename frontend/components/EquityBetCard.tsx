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
}: {
  label: string;
  weightPct: number;
  score: number;
  explanation: string;
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
          {label}
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
      className="border-b border-r flex flex-col"
      style={{ background: "var(--surface)", borderColor: "var(--border)", overflow: "hidden" }}
    >
      {/* Header row: Ticker */}
      <div className="flex items-center gap-3 px-5 pt-5 pb-2">
        <span
          className="font-bold"
          style={{
            color: "var(--accent)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "24px",
            letterSpacing: "-0.02em",
          }}
        >
          {bet.ticker}
        </span>
      </div>

      {/* Sparkline row: full card width */}
      <div className="px-5">
        <StockSparkline ticker={bet.ticker} />
      </div>

      {/* EFS Score Bar */}
      <div className="px-5 pt-3">
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
                      fontSize: "10px",
                      letterSpacing: "0.08em",
                      flexShrink: 0,
                    }}
                  >
                    HIGHEST CONVICTION
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
                />
                <EFSBreakdownRow
                  label="Thesis Beta"
                  weightPct={25}
                  score={efs.thesisBetaScore}
                  explanation={buildExplanation(efs, "beta")}
                />
                <EFSBreakdownRow
                  label="Momentum Alignment"
                  weightPct={20}
                  score={efs.momentumAlignmentScore}
                  explanation={buildExplanation(efs, "momentum")}
                />
                <EFSBreakdownRow
                  label="Valuation Buffer"
                  weightPct={15}
                  score={efs.valuationBufferScore}
                  explanation={buildExplanation(efs, "valuation")}
                />
                <EFSBreakdownRow
                  label="Signal Purity"
                  weightPct={10}
                  score={efs.signalPurityScore}
                  explanation={buildExplanation(efs, "purity")}
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
      <div className="px-5 pt-3 pb-5 flex flex-col flex-1">
        {/* Company name */}
        <div
          className="mb-2"
          style={{
            color: "var(--text)",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          {bet.companyName}
        </div>

        {/* Company description */}
        {bet.companyDescription && (
          <p
            className="mb-3"
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
            {bet.companyDescription}
          </p>
        )}

        {/* Rationale */}
        <p
          style={{
            color: "var(--text-muted)",
            lineHeight: "1.5",
            fontSize: "14px",
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {bet.rationale}
        </p>

        {/* Footer: Role + Feedback + Time horizon */}
        <div className="mt-auto pt-3 flex items-center gap-3">
          <span
            className="uppercase px-2 py-0.5 border"
            style={{
              color: bet.role === "BENEFICIARY" ? "#FF4500" : bet.role === "HEADWIND" ? "#5A5A5A" : "var(--text)",
              borderColor: bet.role === "BENEFICIARY" ? "#FF4500" : bet.role === "HEADWIND" ? "#5A5A5A" : "var(--text)",
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
              color: "var(--text-muted)",
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
