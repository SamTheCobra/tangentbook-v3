"use client";

import { StartupOpportunity } from "@/lib/api";

const ALL_TIMINGS = ["TOO_EARLY", "RIGHT_TIMING", "CROWDING"] as const;

interface StartupCardProps {
  opportunity: StartupOpportunity;
}

export default function StartupCard({ opportunity }: StartupCardProps) {
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

      {/* Timing badges — all shown, active highlighted, inactive very dark */}
      <div className="mt-3 flex items-center gap-2">
        {ALL_TIMINGS.map((timing) => {
          const isActive = opportunity.timing === timing;
          return (
            <span
              key={timing}
              className="uppercase px-2 py-0.5 border"
              style={{
                color: isActive ? "#E8440A" : "#3A3A3A",
                borderColor: isActive ? "#E8440A" : "#2A2A2A",
                letterSpacing: "0.08em",
                fontSize: "11px",
              }}
            >
              {timing.replace(/_/g, " ")}
            </span>
          );
        })}
      </div>

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
