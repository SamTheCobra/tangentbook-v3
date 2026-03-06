"use client";

import { StartupOpportunity, STSScore } from "@/lib/api";

const ALL_TIMINGS = ["TOO_EARLY", "RIGHT_TIMING", "CROWDING"] as const;

interface StartupCardProps {
  opportunity: StartupOpportunity;
  sts?: STSScore | null;
}

export default function StartupCard({ opportunity, sts }: StartupCardProps) {
  const activeTiming = sts ? sts.timingLabel : opportunity.timing;

  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="mb-2">
        <span className="font-bold" style={{ color: "var(--text)", fontSize: "16px" }}>
          {opportunity.name}
        </span>
      </div>
      <p style={{ color: "var(--text-muted)", lineHeight: "1.5", fontSize: "14px", wordWrap: "break-word", overflowWrap: "break-word" }}>
        {opportunity.oneLiner}
      </p>

      {/* STS score + timing */}
      {sts ? (
        <div className="mt-3 flex items-center gap-3">
          <span
            className="uppercase"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            STS
          </span>
          <span
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "13px",
              color: "var(--text)",
            }}
          >
            {Math.round(sts.stsScore)}/100
          </span>
          <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>&rarr;</span>
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
            color: "var(--text-muted)",
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
