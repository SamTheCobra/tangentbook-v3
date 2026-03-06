"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Effect } from "@/lib/api";

interface EffectChainProps {
  thesisId: string;
  thesisTitle: string;
  thesisScore: number;
  effects: Effect[];
}

export default function EffectChain({ thesisId, effects }: EffectChainProps) {
  if (effects.length === 0) return null;

  return (
    <div className="flex flex-col gap-0">
      {effects.map((effect) => (
        <EffectRow key={effect.id} effect={effect} thesisId={thesisId} />
      ))}
    </div>
  );
}

function EffectRow({ effect, thesisId }: { effect: Effect; thesisId: string }) {
  const [expanded, setExpanded] = useState(false);
  const router = useRouter();
  const hasChildren = effect.childEffects && effect.childEffects.length > 0;
  const hasDescription = !!effect.description;
  const tickers = effect.equityBets.map((b) => b.ticker);
  const canExpand = hasDescription || hasChildren || tickers.length > 0;

  let clickTimer: ReturnType<typeof setTimeout> | null = null;

  const handleClick = () => {
    if (clickTimer) {
      clearTimeout(clickTimer);
      clickTimer = null;
      router.push(`/thesis/${thesisId}/effect/${effect.id}`);
      return;
    }
    clickTimer = setTimeout(() => {
      clickTimer = null;
      if (canExpand) setExpanded(!expanded);
    }, 250);
  };

  return (
    <div>
      {/* 2nd order row */}
      <button
        onClick={handleClick}
        className="w-full text-left flex items-center gap-3 py-3 px-4"
        style={{
          background: "none",
          border: "none",
          borderLeft: "2px solid #242424",
          cursor: "pointer",
        }}
      >
        <span style={{ color: "var(--text-muted)", fontSize: "12px", width: "14px", flexShrink: 0 }}>
          {canExpand ? (expanded ? "▼" : "▶") : " "}
        </span>
        <span
          className="flex-1 uppercase font-bold"
          style={{
            color: "var(--text)",
            letterSpacing: "-0.02em",
            fontSize: "14px",
            lineHeight: "1.3",
          }}
        >
          {effect.title}
        </span>
        <span
          style={{
            color: "#FF4500",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "14px",
            flexShrink: 0,
          }}
        >
          THI {Math.round(effect.thi.score)}
        </span>
      </button>

      {/* Expanded: description + tickers + 3rd order */}
      {expanded && (
        <div
          className="pb-3 px-4"
          style={{ borderLeft: "2px solid #242424", marginLeft: 0 }}
        >
          {/* Description */}
          {hasDescription && (
            <div className="pl-7 mb-3">
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "14px",
                  lineHeight: "1.5",
                }}
              >
                {effect.description}
              </p>
            </div>
          )}

          {/* Tickers row */}
          {tickers.length > 0 && (
            <div className="pl-7 mb-3" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
              {tickers.map((t, i) => (
                <span key={t}>
                  <span style={{ color: "#FF4500" }}>{t}</span>
                  {i < tickers.length - 1 && <span style={{ color: "#5A5A5A" }}> · </span>}
                </span>
              ))}
            </div>
          )}

          {/* 3rd order effects */}
          {hasChildren && (
            <div className="pl-7 flex flex-col gap-0">
              {effect.childEffects.map((child) => (
                <ThirdOrderRow key={child.id} effect={child} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ThirdOrderRow({ effect }: { effect: Effect }) {
  const [expanded, setExpanded] = useState(false);
  const hasDescription = !!effect.description;
  const tickers = effect.equityBets?.map((b) => b.ticker) || [];
  const canExpand = hasDescription || tickers.length > 0;

  return (
    <div>
      <button
        onClick={() => canExpand && setExpanded(!expanded)}
        className="w-full text-left flex items-center gap-3 py-2 px-3"
        style={{
          background: "none",
          border: "none",
          borderLeft: "2px solid #FF4500",
          cursor: canExpand ? "pointer" : "default",
        }}
      >
        <span style={{ color: "var(--text-muted)", fontSize: "11px", width: "12px", flexShrink: 0 }}>
          {canExpand ? (expanded ? "▼" : "▶") : " "}
        </span>
        <span
          className="flex-1 uppercase font-bold"
          style={{
            color: "var(--text)",
            letterSpacing: "-0.02em",
            fontSize: "12px",
            lineHeight: "1.3",
          }}
        >
          {effect.title}
        </span>
        <span
          style={{
            color: "#FF4500",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "12px",
            flexShrink: 0,
          }}
        >
          THI {Math.round(effect.thi.score)}
        </span>
      </button>

      {expanded && (
        <div className="pb-2 px-3" style={{ borderLeft: "2px solid #FF4500" }}>
          {hasDescription && (
            <div className="pl-6 mb-2">
              <p style={{ color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.5" }}>
                {effect.description}
              </p>
            </div>
          )}
          {tickers.length > 0 && (
            <div className="pl-6" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "12px" }}>
              {tickers.map((t, i) => (
                <span key={t}>
                  <span style={{ color: "#FF4500" }}>{t}</span>
                  {i < tickers.length - 1 && <span style={{ color: "#5A5A5A" }}> · </span>}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
