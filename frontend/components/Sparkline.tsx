"use client";

import { LineChart, Line, ResponsiveContainer } from "recharts";

interface SparklineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}

export default function Sparkline({
  data,
  color,
  width = 80,
  height = 24,
}: SparklineProps) {
  if (!data || data.length < 2) {
    return (
      <span
        style={{
          color: "var(--text-muted)",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "10px",
        }}
      >
        ——
      </span>
    );
  }

  const chartData = data.map((v, i) => ({ v, i }));
  const lineColor = color || "var(--text-muted)";

  return (
    <div style={{ width, height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="v"
            stroke={lineColor}
            strokeWidth={1}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
