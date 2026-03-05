"use client";

import { EquityBet } from "@/lib/api";
import Sparkline from "./Sparkline";

interface EquityBetCardProps {
  bet: EquityBet;
}

export default function EquityBetCard({ bet }: EquityBetCardProps) {
  const roleColor =
    bet.role === "BENEFICIARY"
      ? "var(--positive)"
      : bet.role === "HEADWIND"
      ? "var(--text-muted)"
      : "var(--accent)";

  const priceHistory = bet.priceHistory?.map((p) => p.close) || [];
  const hasPrice = bet.currentPrice != null;
  const hasPriceChange = bet.priceChange12mPct != null;

  return (
    <div
      className="border p-4"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <span
            className="font-bold"
            style={{
              color: "var(--text)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "16px",
            }}
          >
            {bet.ticker}
          </span>
          {hasPrice && (
            <span
              style={{
                color: "var(--text-muted)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
              }}
            >
              ${bet.currentPrice!.toFixed(2)}
            </span>
          )}
          {hasPriceChange && (
            <span
              style={{
                color: bet.priceChange12mPct! >= 0 ? "var(--positive)" : "var(--text-muted)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
              }}
            >
              {bet.priceChange12mPct! >= 0 ? "+" : ""}
              {bet.priceChange12mPct!.toFixed(1)}%
            </span>
          )}
        </div>
        <span
          className="text-xs uppercase px-2 py-0.5 border"
          style={{
            color: roleColor,
            borderColor: roleColor,
            letterSpacing: "0.08em",
            fontSize: "9px",
          }}
        >
          {bet.role}
        </span>
      </div>

      {priceHistory.length > 1 && (
        <div className="mb-2">
          <Sparkline
            data={priceHistory}
            color={roleColor}
            width={200}
            height={32}
          />
        </div>
      )}

      <p className="text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
        {bet.rationale}
      </p>

      <div className="mt-2 flex items-center gap-3">
        {bet.isFeedbackIndicator && (
          <span
            className="text-xs uppercase"
            style={{
              color: "var(--accent)",
              letterSpacing: "0.08em",
              fontSize: "9px",
            }}
          >
            FEEDBACK INDICATOR
          </span>
        )}
        <span
          className="text-xs uppercase"
          style={{
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            fontSize: "9px",
          }}
        >
          {bet.timeHorizon}
        </span>
      </div>
    </div>
  );
}
