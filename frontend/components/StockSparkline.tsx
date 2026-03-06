"use client";

import { useState } from "react";

interface StockSparklineProps {
  ticker: string;
  role: string;
}

export default function StockSparkline({ ticker, role }: StockSparklineProps) {
  const [tooltip, setTooltip] = useState<string[] | null>(null);

  const seed = ticker.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = (i: number) => ((seed * (i + 1) * 2654435761) >>> 0) / 4294967295;

  const points = Array.from({ length: 12 }, (_, i) => {
    const noise = (rand(i) - 0.5) * 20;
    const trend =
      role === "BENEFICIARY" ? i * 2 :
      role === "HEADWIND" ? i * -2 :
      Math.sin(i) * 4;
    return 40 + trend + noise;
  });

  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const normalize = (v: number) => ((v - min) / range) * 30 + 3;

  const pathD = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * 200;
      const y = 36 - normalize(p);
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  const pctChanges = points
    .slice(-5)
    .map((p, i, arr) =>
      i === 0 ? null : ((p - arr[i - 1]) / arr[i - 1] * 100).toFixed(1)
    )
    .filter((v): v is string => v !== null);

  const isUp = points[points.length - 1] > points[0];
  const color = isUp ? "#FF4500" : "#5A5A5A";

  return (
    <div
      style={{ width: "100%", height: 36, overflow: "hidden", position: "relative" }}
      onMouseEnter={() => setTooltip(pctChanges)}
      onMouseLeave={() => setTooltip(null)}
    >
      <svg
        viewBox="0 0 200 36"
        preserveAspectRatio="none"
        style={{ width: "100%", height: 36, display: "block" }}
      >
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth={1}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {tooltip && (
        <div
          style={{
            position: "absolute",
            bottom: 40,
            right: 0,
            background: "#161616",
            border: "1px solid #242424",
            padding: "6px 10px",
            fontSize: 10,
            color: "#F0EDE8",
            fontFamily: "JetBrains Mono, monospace",
            whiteSpace: "nowrap",
            zIndex: 50,
            pointerEvents: "none",
          }}
        >
          {tooltip.map((v, i) => (
            <div
              key={i}
              style={{ color: parseFloat(v) >= 0 ? "#FF4500" : "#5A5A5A" }}
            >
              {parseFloat(v) >= 0 ? "+" : ""}
              {v}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
