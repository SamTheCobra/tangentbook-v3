"use client";

import { EquityBet } from "@/lib/api";
import StockSparkline from "./StockSparkline";

const ALL_ROLES = ["BENEFICIARY", "HEADWIND", "CANARY"] as const;

interface EquityBetCardProps {
  bet: EquityBet;
}

export default function EquityBetCard({ bet }: EquityBetCardProps) {
  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      {/* Row 1: Ticker + Role badges + Sparkline */}
      <div className="flex items-center gap-3 mb-1">
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
        <div className="flex items-center gap-1.5">
          {ALL_ROLES.map((role) => {
            const isActive = bet.role === role;
            return (
              <span
                key={role}
                className="uppercase px-2 py-0.5 border"
                style={{
                  color: isActive ? "#FF4500" : "#242424",
                  borderColor: isActive ? "#FF4500" : "#242424",
                  letterSpacing: "0.08em",
                  fontSize: "11px",
                }}
              >
                {role}
              </span>
            );
          })}
        </div>
        <div className="ml-auto flex-shrink-0">
          <StockSparkline ticker={bet.ticker} role={bet.role} />
        </div>
      </div>

      {/* Row 2: Full company name */}
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

      {/* Row 3: Company description */}
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

      {/* Row 4: Rationale */}
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

      {/* Row 5: Feedback + Time horizon */}
      <div className="mt-3 flex items-center gap-3">
        {bet.isFeedbackIndicator && (
          <span
            className="uppercase"
            style={{
              color: "var(--accent)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
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
  );
}
