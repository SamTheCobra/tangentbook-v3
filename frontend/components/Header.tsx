"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ThemeToggle from "./ThemeToggle";
import { api, MacroHeader } from "@/lib/api";

interface HeaderProps {
  onNewThesis?: () => void;
}

export default function Header({ onNewThesis }: HeaderProps) {
  const [macro, setMacro] = useState<MacroHeader | null>(null);

  useEffect(() => {
    api.getMacroHeader().then(setMacro).catch((e) => console.error("Macro header fetch failed:", e));
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
        <Link
          href="/"
          className="font-bold text-xl uppercase"
          style={{
            color: "var(--text)",
            letterSpacing: "-0.04em",
            fontFamily: "Inter, system-ui, sans-serif",
            textDecoration: "none",
          }}
        >
          TANGENTBOOK
        </Link>

        {macro && (
          <div className="flex items-center gap-6">
            <MacroItem label="REGIME" value={macro.regime || "N/A"} />
            <MacroItem
              label="FFR"
              value={macro.ffr != null ? `${macro.ffr.toFixed(2)}%` : "N/A"}
            />
            <MacroItem
              label="10Y-2Y"
              value={
                macro.tenYearTwoYearSpread != null
                  ? `${macro.tenYearTwoYearSpread.toFixed(2)}`
                  : "N/A"
              }
            />
            <MacroItem
              label="VIX"
              value={macro.vix != null ? macro.vix.toFixed(1) : "N/A"}
            />
          </div>
        )}
      </div>

      <div className="flex items-center gap-6">
        <ThemeToggle />
        {onNewThesis && (
          <button
            onClick={onNewThesis}
            className="uppercase px-3 py-1.5 border"
            style={{
              color: "var(--text)",
              borderColor: "var(--text)",
              letterSpacing: "0.08em",
              background: "none",
              cursor: "pointer",
              fontFamily: "Inter, system-ui, sans-serif",
              fontSize: "13px",
            }}
          >
            + NEW THESIS
          </button>
        )}
      </div>
    </header>
  );
}

function MacroItem({ label, value }: { label: string; value: string }) {
  const isPlaceholder = value === "N/A" || value === "——";
  return (
    <div className="flex items-center gap-2">
      <span
        className="uppercase"
        style={{
          color: "var(--text-muted)",
          letterSpacing: "0.08em",
          fontSize: "13px",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        {label}
      </span>
      <span
        style={{
          color: isPlaceholder ? "var(--text-muted)" : "var(--accent)",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: "15px",
        }}
      >
        {value}
      </span>
    </div>
  );
}
