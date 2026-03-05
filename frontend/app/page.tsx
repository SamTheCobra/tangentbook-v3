"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import Needle from "@/components/Needle";
import { api, Thesis } from "@/lib/api";

export default function Home() {
  const [theses, setTheses] = useState<Thesis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getTheses()
      .then(setTheses)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Header />
      <div className="px-12 py-8">
        {loading ? (
          <p
            className="font-mono"
            style={{ color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace" }}
          >
            ————
          </p>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-8">
              <h2
                className="font-bold uppercase text-2xl"
                style={{
                  color: "var(--text)",
                  letterSpacing: "-0.03em",
                  fontFamily: "Inter, system-ui, sans-serif",
                }}
              >
                THESES
              </h2>
              <span
                className="text-xs uppercase"
                style={{
                  color: "var(--text-muted)",
                  letterSpacing: "0.08em",
                  fontFamily: "JetBrains Mono, monospace",
                }}
              >
                {theses.length} active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0">
              {theses.map((thesis) => (
                <ThesisCard key={thesis.id} thesis={thesis} />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function ThesisCard({ thesis }: { thesis: Thesis }) {
  return (
    <div
      className="border p-5"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 mr-4">
          <h3
            className="font-bold uppercase text-sm"
            style={{
              color: "var(--text)",
              letterSpacing: "-0.03em",
              fontFamily: "Inter, system-ui, sans-serif",
              lineHeight: "1.3",
            }}
          >
            {thesis.title}
          </h3>
          <p
            className="mt-1 text-xs"
            style={{
              color: "var(--text-muted)",
              lineHeight: "1.4",
            }}
          >
            {thesis.subtitle}
          </p>
        </div>
        <Needle score={thesis.thi.score} size="sm" />
      </div>

      <div
        className="mt-3 pt-3 flex items-center justify-between border-t"
        style={{ borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-4">
          <span
            className="text-xs uppercase"
            style={{
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              fontSize: "11px",
            }}
          >
            CONVICTION
          </span>
          <span
            style={{
              color: "var(--text)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "13px",
            }}
          >
            {thesis.userConviction.score}/10
          </span>
        </div>
        <span
          className="text-xs uppercase"
          style={{
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            fontSize: "10px",
          }}
        >
          {thesis.timeHorizon}
        </span>
      </div>

      {thesis.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {thesis.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs uppercase px-2 py-0.5 border"
              style={{
                color: "var(--text-muted)",
                borderColor: "var(--border)",
                letterSpacing: "0.08em",
                fontSize: "9px",
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
