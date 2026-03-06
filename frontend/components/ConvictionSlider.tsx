"use client";

import { useState, useRef } from "react";
import Sparkline from "./Sparkline";

interface ConvictionSliderProps {
  score: number;
  history?: number[];
  onUpdate: (score: number, note?: string) => void;
  divergenceWarning?: string | null;
}

export default function ConvictionSlider({
  score,
  history = [],
  onUpdate,
  divergenceWarning,
}: ConvictionSliderProps) {
  const [value, setValue] = useState(score);
  const [showNote, setShowNote] = useState(false);
  const [note, setNote] = useState("");
  const noteRef = useRef<HTMLInputElement>(null);

  const handleChange = (newVal: number) => {
    setValue(newVal);
  };

  const handleCommit = () => {
    if (value !== score) {
      const diff = Math.abs(value - score);
      if (diff >= 2) {
        setShowNote(true);
        setTimeout(() => noteRef.current?.focus(), 50);
      } else {
        onUpdate(value);
      }
    }
  };

  const submitNote = () => {
    onUpdate(value, note || undefined);
    setShowNote(false);
    setNote("");
  };

  const handleReset = () => {
    setValue(7);
    onUpdate(7, "Reset to default");
  };

  return (
    <div>
      <div className="flex items-center gap-3">
        <span
          className="text-xs uppercase"
          style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
        >
          CONVICTION
        </span>
        <input
          type="range"
          min={1}
          max={10}
          value={value}
          onChange={(e) => handleChange(parseInt(e.target.value))}
          onMouseUp={handleCommit}
          onTouchEnd={handleCommit}
          className="flex-1"
          style={{
            accentColor: "var(--accent)",
            height: "2px",
            maxWidth: "120px",
          }}
        />
        <span
          style={{
            color: "var(--text)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "16px",
            minWidth: "32px",
          }}
        >
          {value}/10
        </span>
        {history.length > 1 && (
          <div className="flex flex-col items-center">
            <Sparkline data={history} width={48} height={16} />
            <span
              style={{
                color: "var(--text-muted)",
                fontSize: "8px",
                letterSpacing: "0.04em",
                marginTop: "1px",
              }}
            >
              YOUR CONVICTION HISTORY
            </span>
          </div>
        )}
        <button
          onClick={handleReset}
          className="uppercase"
          style={{
            color: "var(--text-muted)",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "11px",
            letterSpacing: "0.06em",
          }}
        >
          RESET TO DEFAULT
        </button>
      </div>

      {showNote && (
        <div className="mt-2 flex items-center gap-2">
          <input
            ref={noteRef}
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") submitNote();
              if (e.key === "Escape") { setShowNote(false); setNote(""); }
            }}
            onBlur={submitNote}
            placeholder="Note why you changed this (optional)"
            className="text-xs px-2 py-1 border flex-1"
            style={{
              background: "var(--surface)",
              borderColor: "var(--border)",
              color: "var(--text)",
              fontFamily: "JetBrains Mono, monospace",
              outline: "none",
            }}
          />
        </div>
      )}

      {divergenceWarning && (
        <div
          className="mt-2 px-3 py-1 border text-xs"
          style={{
            borderColor: "var(--accent)",
            color: "var(--accent)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "13px",
          }}
        >
          {divergenceWarning}
        </div>
      )}
    </div>
  );
}
