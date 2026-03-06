"use client";

import { EquityBet } from "@/lib/api";
import StockSparkline from "./StockSparkline";

interface EquityBetCardProps {
  bet: EquityBet;
}

export default function EquityBetCard({ bet }: EquityBetCardProps) {
  return (
    <div
      className="border-b"
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

      {/* Body */}
      <div className="px-5 pt-3 pb-5">
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
              wordWrap: "break-word",
              overflowWrap: "break-word",
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
            wordWrap: "break-word",
            overflowWrap: "break-word",
          }}
        >
          {bet.rationale}
        </p>

        {/* Footer: Feedback + Time horizon */}
        <div className="mt-3 flex items-center gap-3">
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
