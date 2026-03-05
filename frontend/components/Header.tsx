"use client";

import { useEffect, useState } from "react";
import ThemeToggle from "./ThemeToggle";
import { api, MacroHeader } from "@/lib/api";

export default function Header() {
  const [macro, setMacro] = useState<MacroHeader | null>(null);

  useEffect(() => {
    api.getMacroHeader().then(setMacro).catch(() => {});
  }, []);

  return (
    <header
      className="w-full border-b px-12 py-3 flex items-center justify-between"
      style={{
        background: "var(--bg)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-center gap-8">
        <span
          className="font-bold text-lg uppercase"
          style={{
            color: "var(--text)",
            letterSpacing: "-0.04em",
            fontFamily: "Inter, system-ui, sans-serif",
          }}
        >
          TANGENTBOOK
        </span>

        {macro && (
          <div className="flex items-center gap-6">
            <MacroItem label="REGIME" value={macro.regime || "——"} />
            <MacroItem
              label="FFR"
              value={macro.ffr != null ? `${macro.ffr.toFixed(2)}%` : "——"}
            />
            <MacroItem
              label="10Y–2Y"
              value={
                macro.tenYearTwoYearSpread != null
                  ? `${macro.tenYearTwoYearSpread.toFixed(2)}`
                  : "——"
              }
            />
            <MacroItem
              label="VIX"
              value={macro.vix != null ? macro.vix.toFixed(1) : "——"}
            />
          </div>
        )}
      </div>

      <div className="flex items-center gap-6">
        <ThemeToggle />
      </div>
    </header>
  );
}

function MacroItem({ label, value }: { label: string; value: string }) {
  const isPlaceholder = value === "——";
  return (
    <div className="flex items-center gap-2">
      <span
        className="text-xs uppercase"
        style={{
          color: "var(--text-muted)",
          letterSpacing: "0.08em",
          fontSize: "11px",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        {label}
      </span>
      <span
        style={{
          color: isPlaceholder ? "var(--text-muted)" : "var(--text)",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "13px",
        }}
      >
        {value}
      </span>
    </div>
  );
}
