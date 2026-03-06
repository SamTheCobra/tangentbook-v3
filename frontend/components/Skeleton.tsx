"use client";

interface SkeletonProps {
  width?: string;
  lines?: number;
}

export default function Skeleton({ width = "100%", lines = 1 }: SkeletonProps) {
  return (
    <div style={{ width }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="mb-1"
          style={{
            color: "var(--text-muted)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "16px",
          }}
        >
          ————
        </div>
      ))}
    </div>
  );
}

export function ThesisCardSkeleton() {
  return (
    <div
      className="border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-4">
          <div style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "14px" }}>
            ————————
          </div>
          <div className="mt-2" style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
            ——————————————
          </div>
        </div>
        <div style={{ width: 120, height: 72, background: "var(--surface-alt)" }} />
      </div>
      <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
        <div style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: "13px" }}>
          ————
        </div>
      </div>
    </div>
  );
}
