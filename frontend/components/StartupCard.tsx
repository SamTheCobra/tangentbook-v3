"use client";

import { StartupOpportunity, STSScore } from "@/lib/api";
import GradientBar from "./GradientBar";

const ALL_TIMINGS = ["TOO_EARLY", "RIGHT_TIMING", "CROWDING"] as const;

interface StartupCardProps {
  opportunity: StartupOpportunity;
  sts?: STSScore | null;
}

export default function StartupCard({ opportunity, sts }: StartupCardProps) {
  const activeTiming = sts ? sts.timingLabel : opportunity.timing;

  return (
    <div
      className="p-3"
      style={{ background: "#1C1C1C", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "4px", boxShadow: "0 1px 4px rgba(0,0,0,0.5)" }}
    >
      <div className="mb-1">
        <span className="font-bold" style={{ color: "var(--text)", fontSize: "16px" }}>
          {opportunity.name}
        </span>
      </div>
      <p style={{ color: "#999", lineHeight: "1.5", fontSize: "13px", wordWrap: "break-word", overflowWrap: "break-word" }}>
        {opportunity.oneLiner}
      </p>

      {/* STS score + timing */}
      {sts ? (
        <div className="mt-3">
          <div className="flex items-center gap-3 mb-2">
            <span
              className="uppercase"
              style={{
                color: "#999",
                letterSpacing: "0.08em",
                fontSize: "11px",
                flexShrink: 0,
              }}
            >
              STS
            </span>
            <span style={{ flex: 1 }}>
              <GradientBar value={sts.stsScore} height={6} />
            </span>
            <span
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
                color: "var(--text)",
                flexShrink: 0,
              }}
            >
              {Math.round(sts.stsScore)}/100
            </span>
          </div>
          <span
            className="uppercase px-2 py-0.5 border"
            style={{
              color: "#FF4500",
              borderColor: "#FF4500",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            {activeTiming.replace(/_/g, " ")}
          </span>
        </div>
      ) : (
        /* Timing badges — all shown, active highlighted, inactive very dark */
        <div className="mt-3 flex items-center gap-2">
          {ALL_TIMINGS.map((timing) => {
            const isActive = activeTiming === timing;
            return (
              <span
                key={timing}
                className="uppercase px-2 py-0.5 border"
                style={{
                  color: isActive ? "#FF4500" : "#242424",
                  borderColor: isActive ? "#FF4500" : "#242424",
                  letterSpacing: "0.08em",
                  fontSize: "11px",
                }}
              >
                {timing.replace(/_/g, " ")}
              </span>
            );
          })}
        </div>
      )}

      <div className="mt-2">
        <span
          className="uppercase"
          style={{
            color: "#999",
            letterSpacing: "0.08em",
            fontSize: "11px",
          }}
        >
          {opportunity.timeHorizon}
        </span>
      </div>
    </div>
  );
}
