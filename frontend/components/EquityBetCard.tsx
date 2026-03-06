"use client";

import { EquityBet } from "@/lib/api";
import Sparkline from "./Sparkline";

const ALL_ROLES = ["BENEFICIARY", "HEADWIND", "CANARY"] as const;

interface EquityBetCardProps {
  bet: EquityBet;
}

export default function EquityBetCard({ bet }: EquityBetCardProps) {
  const priceHistory = bet.priceHistory?.map((p) => p.close) || [];
  const hasPrice = bet.currentPrice != null;
  const hasPriceChange = bet.priceChange12mPct != null;

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      {/* Ticker + Price */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <span
            className="font-bold block"
            style={{
              color: "var(--accent)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "20px",
              letterSpacing: "-0.02em",
            }}
          >
            {bet.ticker}
          </span>
          <span
            className="block mt-0.5"
            style={{
              color: "var(--text)",
              fontSize: "14px",
              lineHeight: "1.3",
            }}
          >
            {bet.companyName}
          </span>
        </div>
        <div className="text-right flex-shrink-0 ml-3">
          {hasPrice && (
            <span
              className="block"
              style={{
                color: "var(--text)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "15px",
              }}
            >
              ${bet.currentPrice!.toFixed(2)}
            </span>
          )}
          {hasPriceChange && (
            <span
              className="block"
              style={{
                color: bet.priceChange12mPct! >= 0 ? "var(--positive)" : "var(--text-muted)",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
              }}
            >
              {bet.priceChange12mPct! >= 0 ? "+" : ""}
              {bet.priceChange12mPct!.toFixed(1)}%
            </span>
          )}
        </div>
      </div>

      {/* Sparkline */}
      {priceHistory.length > 1 && (
        <div className="mb-3">
          <Sparkline
            data={priceHistory}
            color="var(--accent)"
            width={200}
            height={32}
          />
        </div>
      )}

      {/* Rationale */}
      <p style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}>
        {bet.rationale}
      </p>

      {/* Role badges — all shown, active highlighted */}
      <div className="mt-3 flex items-center gap-2">
        {ALL_ROLES.map((role) => {
          const isActive = bet.role === role;
          const activeColor =
            role === "BENEFICIARY"
              ? "var(--positive)"
              : role === "HEADWIND"
              ? "var(--accent)"
              : "var(--accent-soft)";
          return (
            <span
              key={role}
              className="uppercase px-2 py-0.5 border"
              style={{
                color: isActive ? activeColor : "var(--border)",
                borderColor: isActive ? activeColor : "var(--border)",
                letterSpacing: "0.08em",
                fontSize: "11px",
                opacity: isActive ? 1 : 0.4,
              }}
            >
              {role}
            </span>
          );
        })}
      </div>

      {/* Feedback + Time */}
      <div className="mt-2 flex items-center gap-3">
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
