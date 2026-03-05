export default function Home() {
  return (
    <main className="min-h-screen" style={{ background: "var(--bg)" }}>
      <div className="px-12 py-8">
        <h1
          className="font-bold uppercase text-4xl"
          style={{
            color: "var(--text)",
            letterSpacing: "-0.04em",
            fontFamily: "Inter, system-ui, sans-serif",
          }}
        >
          TANGENTBOOK
        </h1>
        <p
          className="mt-2 text-sm uppercase"
          style={{
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
          }}
        >
          Macro thesis intelligence system
        </p>
        <div
          className="mt-8 p-6 border"
          style={{
            background: "var(--surface)",
            borderColor: "var(--border)",
          }}
        >
          <p
            className="text-lg"
            style={{ color: "var(--text)", fontFamily: "JetBrains Mono, monospace" }}
          >
            Phase 0 complete. Backend and frontend scaffold ready.
          </p>
          <p className="mt-2 text-sm" style={{ color: "var(--text-muted)" }}>
            16 theses seeded. API available at localhost:8000.
          </p>
        </div>
      </div>
    </main>
  );
}
