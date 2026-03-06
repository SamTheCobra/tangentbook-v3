"use client";

import { useEffect, useRef, useState } from "react";

interface NeedleProps {
  score: number; // 0-100
  size?: "sm" | "md" | "lg";
  label?: string;
  animated?: boolean;
  formulaText?: string;
}

const SIZES = {
  sm: { width: 120, height: 72, needleLen: 42, fontSize: 14, strokeWidth: 1.5 },
  md: { width: 200, height: 120, needleLen: 72, fontSize: 20, strokeWidth: 2 },
  lg: { width: 400, height: 240, needleLen: 150, fontSize: 36, strokeWidth: 2.5 },
};

export default function Needle({ score, size = "md", label = "THI", animated = true, formulaText }: NeedleProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const prevScoreRef = useRef(0);

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
      const duration = 1200;
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

    ctx.clearRect(0, 0, cfg.width, cfg.height);

    const cx = cfg.width / 2;
    const cy = cfg.height * 0.72;
    const radius = cfg.needleLen + 8;

    const s = Math.max(0, Math.min(100, displayScore));
    const needleAngle = Math.PI + (s / 100) * Math.PI;
    const nx = cx + radius * Math.cos(needleAngle);
    const ny = cy + radius * Math.sin(needleAngle);

    // Scale factors per size
    const lineW = size === "lg" ? 2.5 : size === "md" ? 2 : 1.5;
    const pivotR = size === "lg" ? 5 : size === "md" ? 4 : 3;
    const tipR = size === "lg" ? 4 : size === "md" ? 3 : 2.5;

    const opacity =
      s < 30 ? 0.10 + (s / 30) * 0.15 :
      s < 60 ? 0.25 + ((s - 30) / 30) * 0.20 :
      s < 80 ? 0.45 + ((s - 60) / 20) * 0.15 :
               0.60 + ((s - 80) / 20) * 0.10;

    // WEDGE
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius - 4, Math.PI, needleAngle, false);
    ctx.closePath();
    const gx0 = cx - radius;
    const gx1 = cx + radius;
    const grad = ctx.createLinearGradient(gx0, 0, gx1, 0);
    grad.addColorStop(0,    "rgba(232,68,10,0)");
    grad.addColorStop(0.50, `rgba(232,68,10,${opacity})`);
    grad.addColorStop(1,    `rgba(232,68,10,${opacity})`);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();

    // ARC OUTLINE
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI, false);
    ctx.strokeStyle = "rgba(255,255,255,0.13)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // TICK MARKS at 0, 50, 100
    [0, 50, 100].forEach(v => {
      const a = Math.PI + (v / 100) * Math.PI;
      ctx.beginPath();
      ctx.moveTo(cx + (radius - 8) * Math.cos(a), cy + (radius - 8) * Math.sin(a));
      ctx.lineTo(cx + (radius + 3) * Math.cos(a), cy + (radius + 3) * Math.sin(a));
      ctx.strokeStyle = "rgba(255,255,255,0.22)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // NEEDLE LINE
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(nx, ny);
    ctx.strokeStyle = "#E8440A";
    ctx.lineWidth = lineW;
    ctx.lineCap = "round";
    ctx.stroke();

    // PIVOT DOT
    ctx.beginPath();
    ctx.arc(cx, cy, pivotR, 0, Math.PI * 2);
    ctx.fillStyle = "#E8440A";
    ctx.fill();

    // TIP DOT
    ctx.beginPath();
    ctx.arc(nx, ny, tipR, 0, Math.PI * 2);
    ctx.fillStyle = "#E8440A";
    ctx.fill();

    // SCORE TEXT
    ctx.font = `bold ${cfg.fontSize}px "JetBrains Mono", monospace`;
    ctx.fillStyle = "#E8440A";
    ctx.textAlign = "center";
    ctx.fillText(Math.round(displayScore).toString(), cx, cy + cfg.fontSize + (size === "lg" ? 12 : 6));
  }, [displayScore, size]);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setDisplayScore((s) => s);
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => observer.disconnect();
  }, []);

  const cfg = SIZES[size];

  return (
    <div
      className="flex flex-col items-center"
      style={{ overflow: "visible", paddingBottom: size === "lg" ? "24px" : size === "md" ? "20px" : "8px" }}
    >
      <canvas
        ref={canvasRef}
        style={{ width: cfg.width, height: cfg.height }}
        className="block"
      />

      {/* Label */}
      <div
        className="text-center uppercase"
        style={{
          color: "#6B6B6B",
          letterSpacing: "0.08em",
          fontSize: size === "lg" ? "12px" : size === "md" ? "11px" : "9px",
          fontFamily: "Inter, system-ui, sans-serif",
          marginTop: size === "lg" ? "8px" : "4px",
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>

      {/* Formula text */}
      {formulaText && (
        <div
          className="text-center"
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "11px",
            color: "#6B6B6B",
            letterSpacing: "-0.02em",
            maxWidth: cfg.width + 60,
            lineHeight: "1.4",
            marginTop: "4px",
          }}
        >
          {formulaText}
        </div>
      )}
    </div>
  );
}
