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

function getComputedCSSVar(name: string): string {
  if (typeof window === "undefined") return "";
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Map score to wedge opacity
function scoreToOpacity(score: number): number {
  const s = Math.max(0, Math.min(100, score));
  if (s <= 30) return 0.05 + (s / 30) * 0.10;        // 0.05–0.15
  if (s <= 60) return 0.15 + ((s - 30) / 30) * 0.15;  // 0.15–0.30
  if (s <= 80) return 0.30 + ((s - 60) / 20) * 0.20;  // 0.30–0.50
  return 0.50 + ((s - 80) / 20) * 0.20;                // 0.50–0.70
}

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

    const muted = getComputedCSSVar("--text-muted") || "#8A8580";

    ctx.clearRect(0, 0, cfg.width, cfg.height);

    const cx = cfg.width / 2;
    const cy = cfg.height * 0.72;
    const radius = cfg.needleLen + 8;

    const clampedScore = Math.max(0, Math.min(100, displayScore));
    const needleAngle = Math.PI + (clampedScore / 100) * Math.PI;

    // ── 1. Swept wedge fill (drawn first, behind everything) ──
    if (clampedScore > 0.5) {
      const wedgeOpacity = scoreToOpacity(clampedScore);

      // Create radial gradient from pivot to arc edge
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, `rgba(232, 68, 10, ${wedgeOpacity})`);
      grad.addColorStop(1, `rgba(232, 68, 10, ${wedgeOpacity * 0.4})`);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius, Math.PI, needleAngle);
      ctx.closePath();
      ctx.fillStyle = grad;
      ctx.fill();
    }

    // ── 2. Dark arc background ──
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, Math.PI * 2);
    ctx.strokeStyle = "#1E1B18";
    ctx.lineWidth = cfg.strokeWidth + 4;
    ctx.stroke();

    // ── 3. Arc outline ──
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, Math.PI * 2);
    ctx.strokeStyle = "#2A2723";
    ctx.lineWidth = cfg.strokeWidth;
    ctx.stroke();

    // ── 4. Tick marks ──
    for (let i = 0; i <= 10; i++) {
      const angle = Math.PI + (i / 10) * Math.PI;
      const tickInner = radius - (i % 5 === 0 ? 8 : 4);
      const tickOuter = radius + 2;
      ctx.beginPath();
      ctx.moveTo(cx + tickInner * Math.cos(angle), cy + tickInner * Math.sin(angle));
      ctx.lineTo(cx + tickOuter * Math.cos(angle), cy + tickOuter * Math.sin(angle));
      ctx.strokeStyle = i % 5 === 0 ? muted : "#2A2723";
      ctx.lineWidth = i % 5 === 0 ? 1.5 : 0.75;
      ctx.stroke();
    }

    // ── 5. Needle line ──
    const needleX = cx + cfg.needleLen * Math.cos(needleAngle);
    const needleY = cy + cfg.needleLen * Math.sin(needleAngle);

    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(needleX, needleY);
    ctx.strokeStyle = "#E8440A";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.stroke();

    // ── 6. Needle tip dot ──
    ctx.beginPath();
    ctx.arc(needleX, needleY, size === "lg" ? 4 : 3, 0, Math.PI * 2);
    ctx.fillStyle = "#E8440A";
    ctx.fill();

    // ── 7. Pivot dot ──
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#E8440A";
    ctx.fill();

    // ── 8. REFUTED / CONFIRMED labels ──
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

    // ── 9. Score text ──
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
