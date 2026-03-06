"use client";

import { useMemo, useState } from "react";

interface StockSparklineProps {
  ticker: string;
  role: string;
}

function seedRandom(str: string): () => number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0;
  }
  return () => {
    hash = (hash * 16807 + 0) % 2147483647;
    return (hash & 0x7fffffff) / 0x7fffffff;
  };
}

function generatePriceData(ticker: string, role: string): number[] {
  const rng = seedRandom(ticker);
  const points = 30;
  const data: number[] = [100];
  const drift = role === "BENEFICIARY" ? 0.002 : role === "HEADWIND" ? -0.002 : 0;
  const volatility = role === "CANARY" ? 0.04 : 0.025;

  for (let i = 1; i < points; i++) {
    const change = drift + (rng() - 0.5) * volatility;
    data.push(data[i - 1] * (1 + change));
  }
  return data;
}

export default function StockSparkline({ ticker, role }: StockSparklineProps) {
  const [hovered, setHovered] = useState(false);

  const data = useMemo(() => generatePriceData(ticker, role), [ticker, role]);

  const last5Changes = useMemo(() => {
    const changes: string[] = [];
    for (let i = data.length - 5; i < data.length; i++) {
      const pct = ((data[i] - data[i - 1]) / data[i - 1]) * 100;
      changes.push(`${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`);
    }
    return changes;
  }, [data]);

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 80;
  const h = 32;

  const isUp = data[data.length - 1] > data[0];
  const color = isUp ? "#FF4500" : "#5A5A5A";

  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h - ((v - min) / range) * (h - 4) - 2;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div
      className="relative"
      style={{ width: w, maxWidth: w, overflow: "hidden" }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <svg width={w} height={h} style={{ display: "block" }}>
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeLinejoin="round"
        />
      </svg>

      {hovered && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            right: 0,
            background: "#161616",
            border: "1px solid #242424",
            padding: "4px 8px",
            whiteSpace: "nowrap",
            zIndex: 10,
            marginBottom: "4px",
          }}
        >
          <span
            style={{
              color: "#F0EDE8",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "10px",
            }}
          >
            {last5Changes.join(" · ")}
          </span>
        </div>
      )}
    </div>
  );
}
