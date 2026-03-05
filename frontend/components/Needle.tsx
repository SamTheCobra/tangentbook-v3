"use client";

import { useEffect, useRef, useState } from "react";

interface NeedleProps {
  score: number; // 0-100
  size?: "sm" | "md" | "lg";
  label?: string;
  animated?: boolean;
}

const SIZES = {
  sm: { width: 120, height: 72, needleLen: 42, fontSize: 14, labelSize: 9, strokeWidth: 1.5 },
  md: { width: 200, height: 120, needleLen: 72, fontSize: 20, labelSize: 10, strokeWidth: 2 },
  lg: { width: 400, height: 240, needleLen: 150, fontSize: 36, labelSize: 12, strokeWidth: 2.5 },
};

function getComputedCSSVar(name: string): string {
  if (typeof window === "undefined") return "";
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export default function Needle({ score, size = "md", label = "THI", animated = true }: NeedleProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const prevScoreRef = useRef(0);

  // Animate score on mount and when score changes
  useEffect(() => {
    if (!animated) {
      setDisplayScore(score);
      return;
    }

    const from = prevScoreRef.current;
    const to = score;
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const duration = 1200; // 1.2s linear
      const progress = Math.min(elapsed / duration, 1);

      const current = from + (to - from) * progress;
      setDisplayScore(current);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        prevScoreRef.current = to;
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [score, animated]);

  // Draw canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const cfg = SIZES[size];
    const dpr = window.devicePixelRatio || 1;
    canvas.width = cfg.width * dpr;
    canvas.height = cfg.height * dpr;
    ctx.scale(dpr, dpr);

    // Read CSS vars
    const muted = getComputedCSSVar("--text-muted") || "#6B6B6B";
    const accent = getComputedCSSVar("--accent") || "#C4A882";
    const surfaceAlt = getComputedCSSVar("--surface-alt") || "#2A2A2A";

    // Clear
    ctx.clearRect(0, 0, cfg.width, cfg.height);

    const cx = cfg.width / 2;
    const cy = cfg.height * 0.72;
    const radius = cfg.needleLen + 8;

    // Zone colors (very low opacity)
    const zones = [
      { start: Math.PI, end: Math.PI * 1.2, color: "rgba(200, 80, 80, 0.06)" },
      { start: Math.PI * 1.2, end: Math.PI * 1.4, color: "rgba(200, 140, 80, 0.06)" },
      { start: Math.PI * 1.4, end: Math.PI * 1.6, color: "rgba(200, 200, 100, 0.06)" },
      { start: Math.PI * 1.6, end: Math.PI * 1.8, color: "rgba(140, 200, 120, 0.06)" },
      { start: Math.PI * 1.8, end: Math.PI * 2, color: "rgba(100, 180, 100, 0.06)" },
    ];

    // Draw arc zones
    for (const zone of zones) {
      ctx.beginPath();
      ctx.arc(cx, cy, radius, zone.start, zone.end);
      ctx.lineTo(cx, cy);
      ctx.closePath();
      ctx.fillStyle = zone.color;
      ctx.fill();
    }

    // Draw arc outline
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, Math.PI * 2);
    ctx.strokeStyle = surfaceAlt;
    ctx.lineWidth = cfg.strokeWidth;
    ctx.stroke();

    // Tick marks
    for (let i = 0; i <= 10; i++) {
      const angle = Math.PI + (i / 10) * Math.PI;
      const tickInner = radius - (i % 5 === 0 ? 8 : 4);
      const tickOuter = radius + 2;
      ctx.beginPath();
      ctx.moveTo(cx + tickInner * Math.cos(angle), cy + tickInner * Math.sin(angle));
      ctx.lineTo(cx + tickOuter * Math.cos(angle), cy + tickOuter * Math.sin(angle));
      ctx.strokeStyle = i % 5 === 0 ? muted : surfaceAlt;
      ctx.lineWidth = i % 5 === 0 ? 1.5 : 0.75;
      ctx.stroke();
    }

    // Needle
    const clampedScore = Math.max(0, Math.min(100, displayScore));
    const needleAngle = Math.PI + (clampedScore / 100) * Math.PI;
    const needleX = cx + cfg.needleLen * Math.cos(needleAngle);
    const needleY = cy + cfg.needleLen * Math.sin(needleAngle);

    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(needleX, needleY);
    ctx.strokeStyle = accent;
    ctx.lineWidth = cfg.strokeWidth;
    ctx.lineCap = "round";
    ctx.stroke();

    // Center dot
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fillStyle = accent;
    ctx.fill();

    // Labels: REFUTED / CONFIRMED
    if (size !== "sm") {
      const labelFontSize = size === "lg" ? 11 : 9;
      ctx.font = `${labelFontSize}px Inter, system-ui, sans-serif`;
      ctx.fillStyle = muted;
      ctx.textAlign = "left";
      ctx.letterSpacing = "0.08em";
      ctx.fillText("REFUTED", cx - radius - 4, cy + (size === "lg" ? 18 : 14));
      ctx.textAlign = "right";
      ctx.fillText("CONFIRMED", cx + radius + 4, cy + (size === "lg" ? 18 : 14));
    }

    // Score text
    ctx.font = `bold ${cfg.fontSize}px "JetBrains Mono", monospace`;
    ctx.fillStyle = accent;
    ctx.textAlign = "center";
    ctx.fillText(Math.round(displayScore).toString(), cx, cy + cfg.fontSize + (size === "lg" ? 12 : 6));

    // Label
    const labelY = cy + cfg.fontSize + (size === "lg" ? 28 : size === "md" ? 18 : 14);
    ctx.font = `${cfg.labelSize}px Inter, system-ui, sans-serif`;
    ctx.fillStyle = muted;
    ctx.textAlign = "center";
    ctx.fillText(label, cx, labelY);
  }, [displayScore, size, label]);

  // Re-render on theme change
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setDisplayScore((s) => s); // Force re-render
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => observer.disconnect();
  }, []);

  const cfg = SIZES[size];
  return (
    <canvas
      ref={canvasRef}
      style={{ width: cfg.width, height: cfg.height }}
      className="block"
    />
  );
}
