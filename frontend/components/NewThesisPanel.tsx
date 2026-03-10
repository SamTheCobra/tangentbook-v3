"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface NewThesisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

const STATUS_MESSAGES = [
  "Analyzing macro thesis...",
  "Scoring equity bets...",
  "Finding startup opportunities...",
  "Mapping causal effects...",
];

export default function NewThesisPanel({ isOpen, onClose, onCreated }: NewThesisPanelProps) {
  const router = useRouter();
  const [rawThesis, setRawThesis] = useState("");
  const [conviction, setConviction] = useState(7);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusIdx, setStatusIdx] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (generating) {
      setStatusIdx(0);
      intervalRef.current = setInterval(() => {
        setStatusIdx((prev) => (prev + 1) % STATUS_MESSAGES.length);
      }, 3000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [generating]);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!rawThesis.trim()) return;

    setGenerating(true);
    setError(null);

    try {
      const result = await api.generateThesis(rawThesis.trim(), conviction);
      onCreated();
      onClose();
      setRawThesis("");
      setConviction(7);
      router.push(`/thesis/${result.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Generation failed. Try again.");
    } finally {
      setGenerating(false);
    }
  };

  const canSubmit = rawThesis.trim().length > 0 && !generating;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40"
        style={{ background: "rgba(0,0,0,0.5)" }}
        onClick={generating ? undefined : onClose}
      />
      {/* Panel */}
      <div
        className="fixed top-0 right-0 bottom-0 z-50 border-l overflow-y-auto"
        style={{
          width: "480px",
          background: "var(--surface)",
          borderColor: "var(--border)",
        }}
      >
        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <h2
              className="font-bold uppercase text-lg"
              style={{ color: "var(--text)", letterSpacing: "-0.03em" }}
            >
              NEW THESIS
            </h2>
            {!generating && (
              <button
                onClick={onClose}
                style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "18px" }}
              >
                ✕
              </button>
            )}
          </div>

          <div className="space-y-6">
            {/* Thesis input */}
            <div>
              <label
                className="uppercase block mb-2"
                style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
              >
                YOUR THESIS
              </label>
              <textarea
                value={rawThesis}
                onChange={(e) => setRawThesis(e.target.value)}
                placeholder="Describe your macro thesis in one sentence..."
                rows={4}
                disabled={generating}
                className="w-full px-3 py-3 border text-base resize-none"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  fontSize: "16px",
                  lineHeight: "1.6",
                  opacity: generating ? 0.5 : 1,
                }}
              />
              <div
                style={{
                  color: "var(--text-muted)",
                  fontSize: "12px",
                  marginTop: "6px",
                }}
              >
                e.g. &ldquo;AI Content Explosion will cause a Verification Crisis&rdquo;
              </div>
            </div>

            {/* Conviction slider */}
            <div>
              <label
                className="uppercase block mb-2"
                style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
              >
                YOUR CONVICTION
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={conviction}
                  onChange={(e) => setConviction(parseInt(e.target.value))}
                  disabled={generating}
                  style={{ accentColor: "var(--accent)", flex: 1, opacity: generating ? 0.5 : 1 }}
                />
                <span
                  style={{
                    color: "var(--text)",
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: "14px",
                    minWidth: "40px",
                  }}
                >
                  {conviction}/10
                </span>
              </div>
            </div>

            {/* Loading status */}
            {generating && (
              <div
                style={{
                  padding: "16px",
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                }}
              >
                <div className="flex items-center gap-3">
                  <div
                    style={{
                      width: "8px",
                      height: "8px",
                      background: "var(--accent)",
                      animation: "pulse 1.5s ease-in-out infinite",
                    }}
                  />
                  <span
                    className="uppercase"
                    style={{
                      color: "var(--text)",
                      fontSize: "13px",
                      letterSpacing: "0.06em",
                      fontFamily: "JetBrains Mono, monospace",
                    }}
                  >
                    {STATUS_MESSAGES[statusIdx]}
                  </span>
                </div>
                <div
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "11px",
                    marginTop: "8px",
                  }}
                >
                  This takes 10-15 seconds. Claude is generating equity bets, startup opportunities, and causal effects.
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div
                style={{
                  padding: "12px",
                  border: "1px solid #FF4500",
                  color: "#FF4500",
                  fontSize: "13px",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              >
                {error}
              </div>
            )}

            {/* Generate button */}
            <button
              onClick={handleGenerate}
              disabled={!canSubmit}
              className="w-full py-3 text-base uppercase border"
              style={{
                background: canSubmit ? "var(--text)" : "transparent",
                color: canSubmit ? "var(--bg)" : "var(--text-muted)",
                borderColor: "var(--text)",
                letterSpacing: "0.08em",
                cursor: canSubmit ? "pointer" : "not-allowed",
                opacity: generating ? 0.5 : 1,
                fontSize: "14px",
              }}
            >
              {generating ? "GENERATING..." : "GENERATE THESIS"}
            </button>
          </div>
        </div>

        {/* Pulse animation */}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
          }
        `}</style>
      </div>
    </>
  );
}
