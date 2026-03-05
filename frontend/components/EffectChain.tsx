"use client";

import Link from "next/link";
import { Effect } from "@/lib/api";

interface EffectChainProps {
  thesisId: string;
  thesisTitle: string;
  thesisScore: number;
  effects: Effect[];
}

export default function EffectChain({ thesisId, thesisTitle, thesisScore, effects }: EffectChainProps) {
  if (effects.length === 0) return null;

  return (
    <div className="overflow-x-auto">
      <div className="flex items-start gap-0 min-w-max">
        {/* Root thesis node */}
        <ChainNode
          label={thesisTitle}
          score={thesisScore}
          href={`/thesis/${thesisId}`}
          isRoot
        />

        {/* Connector */}
        <div className="flex items-center self-center">
          <div style={{ width: "32px", height: "1px", background: "var(--border)" }} />
          <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>&rarr;</span>
          <div style={{ width: "8px", height: "1px", background: "var(--border)" }} />
        </div>

        {/* 2nd order effects column */}
        <div className="flex flex-col gap-2">
          {effects.map((effect) => (
            <div key={effect.id} className="flex items-start gap-0">
              <ChainNode
                label={effect.title}
                score={effect.thi.score}
                href={`/thesis/${thesisId}/effect/${effect.id}`}
                isConfirmed={effect.thi.direction === "confirming"}
              />

              {/* 3rd order children */}
              {effect.childEffects && effect.childEffects.length > 0 && (
                <>
                  <div className="flex items-center self-center">
                    <div style={{ width: "24px", height: "1px", background: "var(--border)" }} />
                    <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>&rarr;</span>
                    <div style={{ width: "8px", height: "1px", background: "var(--border)" }} />
                  </div>
                  <div className="flex flex-col gap-2">
                    {effect.childEffects.map((child) => (
                      <ChainNode
                        key={child.id}
                        label={child.title}
                        score={child.thi.score}
                        isConfirmed={child.thi.direction === "confirming"}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ChainNode({
  label,
  score,
  href,
  isRoot = false,
  isConfirmed = false,
}: {
  label: string;
  score: number;
  href?: string;
  isRoot?: boolean;
  isConfirmed?: boolean;
}) {
  const borderColor = isConfirmed ? "var(--positive)" : "var(--border)";

  const content = (
    <div
      className="border px-3 py-2"
      style={{
        background: "var(--surface)",
        borderColor,
        maxWidth: "180px",
      }}
    >
      <div
        className="text-xs uppercase"
        style={{
          color: "var(--text)",
          letterSpacing: "-0.02em",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "10px",
          lineHeight: "1.3",
        }}
      >
        {label}
      </div>
      <div
        className="mt-1"
        style={{
          color: isRoot ? "var(--accent)" : "var(--text-muted)",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "11px",
        }}
      >
        {Math.round(score)}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="hover:opacity-80" style={{ textDecoration: "none" }}>
        {content}
      </Link>
    );
  }

  return content;
}
