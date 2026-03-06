"use client";

import { useState, useEffect } from "react";

interface StockSparklineProps {
  ticker: string;
}

interface StockData {
  prices: number[];
  dates: string[];
  pctChanges: string[];
}

export default function StockSparkline({ ticker }: StockSparklineProps) {
  const [data, setData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [tooltip, setTooltip] = useState(false);

  useEffect(() => {
    fetch(`/api/stock/${ticker}`)
      .then((r) => r.json())
      .then((d: StockData) => {
        if (d.prices.length >= 2) {
          setData(d);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [ticker]);

  // Loading skeleton
  if (loading) {
    return (
      <div style={{ width: "100%", height: 36, background: "var(--surface-alt)" }} />
    );
  }

  // Fallback: flat grey line if no data
  if (!data || data.prices.length < 2) {
    return (
      <div style={{ width: "100%", height: 36, overflow: "hidden" }}>
        <svg viewBox="0 0 200 36" preserveAspectRatio="none" style={{ width: "100%", height: 36, display: "block" }}>
          <line x1="0" y1="18" x2="200" y2="18" stroke="#5A5A5A" strokeWidth={1} />
        </svg>
      </div>
    );
  }

  const { prices, dates, pctChanges } = data;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;
  const normalize = (v: number) => ((v - min) / range) * 30 + 3;

  const pathD = prices
    .map((p, i) => {
      const x = (i / (prices.length - 1)) * 200;
      const y = 36 - normalize(p);
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  const isUp = prices[prices.length - 1] > prices[0];
  const color = isUp ? "#FF4500" : "#5A5A5A";

  // Last 5 months for tooltip
  const tooltipEntries = pctChanges.slice(-5).map((pct, i) => {
    const dateIdx = dates.length - 5 + i;
    return {
      date: dates[dateIdx] || "",
      pct,
    };
  });

  return (
    <div
      style={{ width: "100%", height: 36, overflow: "hidden", position: "relative" }}
      onMouseEnter={() => setTooltip(true)}
      onMouseLeave={() => setTooltip(false)}
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
      {tooltip && tooltipEntries.length > 0 && (
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
          {tooltipEntries.map((entry, i) => (
            <div
              key={i}
              className="flex justify-between gap-4"
              style={{ color: parseFloat(entry.pct) >= 0 ? "#FF4500" : "#5A5A5A" }}
            >
              <span>{entry.date}</span>
              <span>
                {parseFloat(entry.pct) >= 0 ? "+" : ""}
                {entry.pct}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
