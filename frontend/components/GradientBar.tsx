"use client";

import { useRef, useEffect } from "react";

interface GradientBarProps {
  value: number;
  height?: number;
  animate?: boolean;
  delay?: number;
}

export default function GradientBar({ value, height = 6, animate, delay = 0 }: GradientBarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.width;
    const h = canvas.height;

    const grad = ctx.createLinearGradient(0, 0, w, 0);
    const maxOpacity = 0.85;
    const fullAt = 0.72;
    for (let i = 0; i <= 100; i++) {
      const t = i / 100;
      const eased = t < fullAt ? Math.pow(t / fullAt, 3) * maxOpacity : maxOpacity;
      grad.addColorStop(t, `rgba(232, 68, 10, ${eased.toFixed(4)})`);
    }

    const clamped = Math.max(0, Math.min(100, value));

    const drawBar = (pct: number) => {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#1A1A1A";
      ctx.beginPath();
      ctx.roundRect(0, 0, w, h, h / 2);
      ctx.fill();
      const fillWidth = (pct / 100) * w;
      if (fillWidth > 0) {
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(0, 0, fillWidth, h, h / 2);
        ctx.fill();
      }
    };

    if (!animate) {
      drawBar(clamped);
      return;
    }

    // Animated: ease-out from 0 to target over 600ms after delay
    drawBar(0);
    const duration = 600;
    let startTime: number | null = null;
    let rafId: number;
    const timeoutId = setTimeout(() => {
      const step = (ts: number) => {
        if (!startTime) startTime = ts;
        const elapsed = ts - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        drawBar(clamped * eased);
        if (progress < 1) rafId = requestAnimationFrame(step);
      };
      rafId = requestAnimationFrame(step);
    }, delay);

    return () => { clearTimeout(timeoutId); cancelAnimationFrame(rafId); };
  }, [value, height, animate, delay]);

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={height}
      style={{ width: "100%", height: `${height}px`, display: "block" }}
    />
  );
}
