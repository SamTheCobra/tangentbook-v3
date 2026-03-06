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

interface TooltipState {
  index: number;
  x: number;
  y: number;
}

export default function StockSparkline({ ticker }: StockSparklineProps) {
  const [data, setData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

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

  if (loading) {
    return (
      <div style={{ width: "100%", height: 36, background: "var(--surface-alt)" }} />
    );
  }

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

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const index = Math.round((x / rect.width) * (prices.length - 1));
    const clamped = Math.max(0, Math.min(prices.length - 1, index));
    setTooltip({ index: clamped, x: e.clientX, y: e.clientY });
  };

  const handleMouseLeave = () => {
    setTooltip(null);
  };

  // pctChanges is offset by 1 (index 0 of pctChanges = change from price[0] to price[1])
  const tooltipPctIdx = tooltip ? tooltip.index - 1 : -1;
  const tooltipPct = tooltipPctIdx >= 0 ? parseFloat(pctChanges[tooltipPctIdx]) : null;

  return (
    <div style={{ width: "100%", height: 36, overflow: "hidden" }}>
      <svg
        viewBox="0 0 200 36"
        preserveAspectRatio="none"
        style={{ width: "100%", height: 36, display: "block", cursor: "crosshair" }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
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
            position: "fixed",
            left: tooltip.x + 12,
            top: tooltip.y - 40,
            background: "#161616",
            border: "1px solid #242424",
            padding: "6px 10px",
            fontSize: 10,
            color: "#F0EDE8",
            fontFamily: "JetBrains Mono, monospace",
            whiteSpace: "nowrap",
            zIndex: 9999,
            pointerEvents: "none",
          }}
        >
          <div>{dates[tooltip.index]}</div>
          {tooltipPct !== null && (
            <div style={{ color: tooltipPct >= 0 ? "#FF4500" : "#5A5A5A" }}>
              {tooltipPct >= 0 ? "+" : ""}{pctChanges[tooltipPctIdx]}%
            </div>
          )}
          <div style={{ color: "#5A5A5A" }}>
            ${prices[tooltip.index].toFixed(2)}
          </div>
        </div>
      )}
    </div>
  );
}
