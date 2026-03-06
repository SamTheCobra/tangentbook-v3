"use client";

import { useState } from "react";
import { api, ThesisCreateInput } from "@/lib/api";

interface NewThesisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export default function NewThesisPanel({ isOpen, onClose, onCreated }: NewThesisPanelProps) {
  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [description, setDescription] = useState("");
  const [timeHorizon, setTimeHorizon] = useState("1-3yr");
  const [tags, setTags] = useState("");
  const [conviction, setConviction] = useState(5);
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!title || !subtitle || !description) return;

    setSaving(true);
    try {
      const data: ThesisCreateInput = {
        title,
        subtitle,
        description,
        time_horizon: timeHorizon,
        tags: tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        user_conviction_score: conviction,
      };
      await api.createThesis(data);
      onCreated();
      onClose();
      // Reset
      setTitle("");
      setSubtitle("");
      setDescription("");
      setTimeHorizon("1-3yr");
      setTags("");
      setConviction(5);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40"
        style={{ background: "rgba(0,0,0,0.5)" }}
        onClick={onClose}
      />
      {/* Panel */}
      <div
        className="fixed top-0 right-0 bottom-0 z-50 border-l overflow-y-auto"
        style={{
          width: "480px",
          background: "var(--surface)",
          borderColor: "var(--border)",
          opacity: 1,
          transition: "opacity 200ms linear",
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
            <button
              onClick={onClose}
              style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "18px" }}
            >
              x
            </button>
          </div>

          <div className="space-y-5">
            <Field label="TITLE">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border text-base"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                }}
              />
            </Field>

            <Field label="SUBTITLE">
              <input
                type="text"
                value={subtitle}
                onChange={(e) => setSubtitle(e.target.value)}
                placeholder="The core claim in one sentence"
                className="w-full px-3 py-2 border text-base"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                }}
              />
            </Field>

            <Field label="DESCRIPTION">
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={5}
                className="w-full px-3 py-2 border text-base resize-none"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                }}
              />
            </Field>

            <Field label="TIME HORIZON">
              <select
                value={timeHorizon}
                onChange={(e) => setTimeHorizon(e.target.value)}
                className="w-full px-3 py-2 border text-base"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                }}
              >
                <option value="0-6mo">0-6mo</option>
                <option value="6-18mo">6-18mo</option>
                <option value="1-3yr">1-3yr</option>
                <option value="3-7yr">3-7yr</option>
                <option value="7yr+">7yr+</option>
              </select>
            </Field>

            <Field label="TAGS">
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="macro, AI, consumer (comma-separated)"
                className="w-full px-3 py-2 border text-base"
                style={{
                  background: "var(--bg)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              />
            </Field>

            <Field label="YOUR CONVICTION">
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={conviction}
                  onChange={(e) => setConviction(parseInt(e.target.value))}
                  style={{ accentColor: "var(--accent)", flex: 1 }}
                />
                <span
                  style={{
                    color: "var(--text)",
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: "14px",
                  }}
                >
                  {conviction}/10
                </span>
              </div>
            </Field>

            <button
              onClick={handleSubmit}
              disabled={saving || !title || !subtitle || !description}
              className="w-full py-2 text-base uppercase border"
              style={{
                background: !title || !subtitle || !description ? "transparent" : "var(--text)",
                color: !title || !subtitle || !description ? "var(--text-muted)" : "var(--bg)",
                borderColor: "var(--text)",
                letterSpacing: "0.08em",
                cursor: !title || !subtitle || !description ? "not-allowed" : "pointer",
                opacity: saving ? 0.5 : 1,
              }}
            >
              {saving ? "SAVING..." : "CREATE THESIS"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label
        className="uppercase block mb-1"
        style={{ color: "var(--text-muted)", letterSpacing: "0.08em", fontSize: "13px" }}
      >
        {label}
      </label>
      {children}
    </div>
  );
}
