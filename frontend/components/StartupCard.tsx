"use client";

import { StartupOpportunity } from "@/lib/api";

interface StartupCardProps {
  opportunity: StartupOpportunity;
}

export default function StartupCard({ opportunity }: StartupCardProps) {
  const timingColor =
    opportunity.timing === "RIGHT_TIMING"
      ? "var(--positive)"
      : opportunity.timing === "TOO_EARLY"
      ? "var(--text-muted)"
      : "var(--accent)";

  return (
    <div
      className="border p-4"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-bold text-sm" style={{ color: "var(--text)" }}>
          {opportunity.name}
        </span>
        <span
          className="text-xs uppercase px-2 py-0.5 border"
          style={{
            color: timingColor,
            borderColor: timingColor,
            letterSpacing: "0.08em",
            fontSize: "9px",
          }}
        >
          {opportunity.timing.replace(/_/g, " ")}
        </span>
      </div>
      <p className="text-xs" style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
        {opportunity.oneLiner}
      </p>
      <div className="mt-2">
        <span
          className="text-xs uppercase"
          style={{
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            fontSize: "9px",
          }}
        >
          {opportunity.timeHorizon}
        </span>
      </div>
    </div>
  );
}
