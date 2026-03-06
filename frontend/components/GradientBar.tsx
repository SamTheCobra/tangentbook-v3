"use client";

import { useRef, useEffect } from "react";

interface GradientBarProps {
  value: number;
  height?: number;
}

export default function GradientBar({ value, height = 6 }: GradientBarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Dark track — full width
    ctx.fillStyle = "#1A1A1A";
    ctx.beginPath();
    ctx.roundRect(0, 0, w, h, h / 2);
    ctx.fill();

    // Gradient — static, full width
    const grad = ctx.createLinearGradient(0, 0, w, 0);
    const maxOpacity = 0.85;
    const fullAt = 0.72;
    for (let i = 0; i <= 100; i++) {
      const t = i / 100;
      const eased =
        t < fullAt ? Math.pow(t / fullAt, 3) * maxOpacity : maxOpacity;
      grad.addColorStop(t, `rgba(232, 68, 10, ${eased.toFixed(4)})`);
    }

    // Filled portion — clips the gradient
    const clamped = Math.max(0, Math.min(100, value));
    const fillWidth = (clamped / 100) * w;
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.roundRect(0, 0, fillWidth, h, h / 2);
    ctx.fill();
  }, [value, height]);

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={height}
      style={{ width: "100%", height: `${height}px`, display: "block" }}
    />
  );
}
