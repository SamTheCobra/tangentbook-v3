import CascadeLogo from "@/components/CascadeLogo";

export default function MethodologyPage() {
  const headingFont = "'Bricolage Grotesque', sans-serif";
  const monoFont = "var(--font-mono), 'JetBrains Mono', monospace";
  const bodyFont = "var(--font-inter), sans-serif";

  const h2Style: React.CSSProperties = {
    fontFamily: headingFont,
    fontSize: "2rem", fontWeight: 800,
    color: "#fff", letterSpacing: "-0.02em",
    margin: "0 0 8px",
  };

  const h3Style: React.CSSProperties = {
    fontFamily: monoFont,
    fontSize: "11px", fontWeight: 700,
    letterSpacing: "0.1em", textTransform: "uppercase",
    color: "#FF4500", margin: "32px 0 8px",
  };

  const bodyStyle: React.CSSProperties = {
    fontFamily: bodyFont,
    fontSize: "1rem", lineHeight: 1.7,
    color: "#ccc", margin: "0 0 16px",
  };

  const formulaBoxStyle: React.CSSProperties = {
    fontFamily: monoFont,
    fontSize: "14px", fontWeight: 700,
    color: "#FF4500", lineHeight: 1.8,
    background: "rgba(255,69,0,0.06)",
    border: "1px solid #222",
    padding: "16px 20px",
    margin: "16px 0 20px",
    whiteSpace: "pre-wrap" as const,
  };

  const pillStyle = (color: string): React.CSSProperties => ({
    display: "inline-block",
    fontFamily: monoFont,
    fontSize: "10px", fontWeight: 700,
    letterSpacing: "0.06em",
    padding: "4px 12px",
    border: `1px solid ${color}`,
    color,
    marginRight: "8px",
    marginBottom: "8px",
  });

  const sectionDivider: React.CSSProperties = {
    borderTop: "1px solid #1a1a1a",
    margin: "48px 0",
  };

  const sourceCardStyle: React.CSSProperties = {
    padding: "16px",
    background: "rgba(255,255,255,0.02)",
    border: "1px solid #1a1a1a",
    marginBottom: "12px",
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      {/* ── NAV ── */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 48px", height: "56px",
        borderBottom: "1px solid var(--border)",
      }}>
        <a href="/" style={{ display: "block", lineHeight: 0 }}>
          <CascadeLogo height={28} />
        </a>
        <a
          href="/methodology"
          style={{
            fontFamily: monoFont,
            fontSize: "0.75rem", fontWeight: 700,
            letterSpacing: "0.1em", textTransform: "uppercase",
            color: "#fff", textDecoration: "none",
          }}
        >
          METHODOLOGY
        </a>
      </div>

      {/* ── CONTENT ── */}
      <div style={{ maxWidth: "860px", margin: "0 auto", padding: "60px 40px 120px" }}>

        {/* ─── SECTION 1: HERO ─── */}
        <h1 style={{
          fontFamily: headingFont,
          fontSize: "3.2rem", fontWeight: 800,
          color: "#fff", letterSpacing: "-0.03em",
          lineHeight: 1.1, margin: "0 0 20px",
        }}>
          How CASCADE Thinks
        </h1>
        <p style={{ ...bodyStyle, color: "#666", fontSize: "1.1rem" }}>
          Every score in CASCADE is derived from public, verifiable data sources &mdash;
          not editorial opinion, not black-box AI. When you enter a thesis, the
          system asks a simple question: what does the data actually say?
        </p>

        <div style={sectionDivider} />

        {/* ─── SECTION 2: THI ─── */}
        <h2 style={h2Style}>Thesis Health Index</h2>
        <p style={{
          fontFamily: monoFont,
          fontSize: "10px", letterSpacing: "0.1em",
          color: "#555", textTransform: "uppercase",
          margin: "0 0 16px",
        }}>
          The core signal. 0&ndash;100.
        </p>
        <p style={bodyStyle}>
          The THI measures how strongly the available public data confirms or
          refutes your thesis at this moment in time. It is not a prediction.
          It is a reading &mdash; like a thermometer for macro conviction.
        </p>

        <div style={formulaBoxStyle}>
          THI = (Evidence &times; 0.50) + (Momentum &times; 0.30) + (Data Quality &times; 0.20)
        </div>

        <div style={{ margin: "20px 0 28px" }}>
          <span style={pillStyle("#FF4500")}>CONFIRMING &ge; 60</span>
          <span style={pillStyle("#888")}>NEUTRAL 40&ndash;60</span>
          <span style={pillStyle("#444")}>REFUTING &le; 40</span>
        </div>

        {/* Evidence */}
        <h3 style={h3Style}>Evidence &mdash; 50% weight</h3>
        <p style={bodyStyle}>
          The weight of current data pointing in the thesis direction.
        </p>
        <p style={bodyStyle}>
          Each thesis is assigned data feeds from FRED and Google Trends.
          Every feed is normalized using percentile rank against its own
          5-year history &mdash; so a reading of 74 means the current value is
          in the 74th percentile of the last five years of observations.
          This removes absolute-value bias and makes cross-series comparison
          meaningful.
        </p>
        <p style={bodyStyle}>Feeds are grouped by type:</p>
        <div style={{ marginLeft: "8px", marginBottom: "16px" }}>
          {[
            { label: "FLOW", pct: "35%", desc: "money supply, capital movement, currency signals" },
            { label: "STRUCTURAL", pct: "30%", desc: "lasting systemic changes: rates, employment, policy" },
            { label: "ADOPTION", pct: "20%", desc: "behavioral signals: Google Trends, consumer data" },
            { label: "POLICY", pct: "15%", desc: "regulatory and government signals" },
          ].map((g) => (
            <div key={g.label} style={{ display: "flex", gap: "8px", marginBottom: "6px" }}>
              <span style={{ fontFamily: monoFont, fontSize: "10px", fontWeight: 700, color: "#FF4500", minWidth: "110px" }}>
                {g.label} ({g.pct})
              </span>
              <span style={{ fontFamily: bodyFont, fontSize: "0.9rem", color: "#888" }}>
                {g.desc}
              </span>
            </div>
          ))}
        </div>

        {/* Momentum */}
        <h3 style={h3Style}>Momentum &mdash; 30% weight</h3>
        <p style={bodyStyle}>
          Is the thesis gaining or losing ground?
        </p>
        <p style={bodyStyle}>
          Momentum measures the rate of change of the Evidence score over
          three time horizons, weighted toward recent movement:
        </p>
        <div style={formulaBoxStyle}>
          Momentum = (30-day &Delta; &times; 0.50) + (90-day &Delta; &times; 0.30) + (1-year &Delta; &times; 0.20)
        </div>
        <p style={bodyStyle}>
          A delta of +30 evidence points maps to a momentum score of 100.
          A delta of &minus;30 maps to 0. This means a thesis can have a moderate
          THI but high momentum &mdash; it&rsquo;s moving in the right direction fast.
        </p>

        {/* Data Quality */}
        <h3 style={h3Style}>Data Quality &mdash; 20% weight</h3>
        <p style={bodyStyle}>
          How reliable is the signal?
        </p>
        <div style={formulaBoxStyle}>
          Data Quality = (Signal Agreement &times; 0.40) + (Freshness &times; 0.35) + (Source Quality &times; 0.25)
        </div>
        <p style={bodyStyle}>
          Signal Agreement measures variance across feeds &mdash; if all feeds point
          the same direction, confidence is high. Freshness measures how many
          feeds are live vs stale or offline. Source Quality weights authoritative
          sources (FRED/BLS = 100) higher than estimated sources (= 20).
        </p>

        <div style={sectionDivider} />

        {/* ─── SECTION 3: CAUSAL CHAIN ─── */}
        <h2 style={h2Style}>Second and Third Order Effects</h2>
        <p style={bodyStyle}>
          CASCADE doesn&rsquo;t just score your thesis. It generates the downstream
          consequences &mdash; and scores those too.
        </p>
        <p style={bodyStyle}>
          Child thesis THI is not inherited blindly. It blends parent signal
          with the child&rsquo;s own indicator data:
        </p>
        <div style={formulaBoxStyle}>
          Child THI = (Parent THI &times; 0.40) + (Child Indicators &times; 0.60)
        </div>
        <p style={bodyStyle}>
          A 2nd order effect that has weak supporting data will score lower
          than its parent even if the parent thesis is strong. This is intentional &mdash;
          certainty should decay as you move downstream.
        </p>

        <div style={sectionDivider} />

        {/* ─── SECTION 4: EFS ─── */}
        <h2 style={h2Style}>Equity Fit Score</h2>
        <p style={{
          fontFamily: monoFont,
          fontSize: "10px", letterSpacing: "0.1em",
          color: "#555", textTransform: "uppercase",
          margin: "0 0 16px",
        }}>
          How purely does this stock capture the thesis? 0&ndash;100.
        </p>
        <p style={bodyStyle}>
          The EFS measures how well a specific equity position would express
          your macro thesis &mdash; not just whether the stock is good, but whether
          it is a clean vehicle for this specific bet.
        </p>
        <div style={formulaBoxStyle}>
          {"EFS = (Revenue Alignment \u00D7 0.30) + (Thesis Beta \u00D7 0.25) +\n      (Momentum Alignment \u00D7 0.20) + (Valuation Buffer \u00D7 0.15) +\n      (Signal Purity \u00D7 0.10)"}
        </div>

        {[
          {
            label: "REVENUE ALIGNMENT", pct: "30%",
            text: "What % of the company's revenue is directly exposed to the thesis theme? Sourced from SEC 10-K filings. A company deriving 80% of revenue from thesis-aligned segments scores high here.",
          },
          {
            label: "THESIS BETA", pct: "25%",
            text: "How correlated are this stock's returns with the THI over the past 12 months? High positive correlation = the stock moves with thesis confirmation. Negative correlation flags a potential hedge or canary.",
          },
          {
            label: "MOMENTUM ALIGNMENT", pct: "20%",
            text: "Is the stock's price momentum pointing in the same direction as the THI trend? Both rising = aligned. Divergence = a flag worth investigating.",
          },
          {
            label: "VALUATION BUFFER", pct: "15%",
            text: "Forward P/E vs sector median. A stock trading at a discount to its sector has more room to run if the thesis plays out. This is not a value signal \u2014 it's a margin of safety signal.",
          },
          {
            label: "SIGNAL PURITY", pct: "10%",
            text: "Fewer business segments = cleaner thesis expression. A pure-play company with one segment scores 100. A conglomerate with 8 divisions scores low \u2014 too much noise dilutes the signal.",
          },
        ].map((comp) => (
          <div key={comp.label} style={{ marginBottom: "20px" }}>
            <h3 style={{ ...h3Style, margin: "24px 0 6px" }}>{comp.label} ({comp.pct})</h3>
            <p style={bodyStyle}>{comp.text}</p>
          </div>
        ))}

        <p style={{ ...bodyStyle, marginTop: "8px" }}>Bet type labels:</p>
        <div style={{ margin: "8px 0 0" }}>
          <span style={pillStyle("#FF4500")}>BENEFICIARY</span>
          <span style={{ fontFamily: bodyFont, fontSize: "0.9rem", color: "#888", marginRight: "24px" }}>
            thesis directly expands this company&rsquo;s market
          </span>
        </div>
        <div style={{ margin: "8px 0" }}>
          <span style={pillStyle("#F59E0B")}>CANARY</span>
          <span style={{ fontFamily: bodyFont, fontSize: "0.9rem", color: "#888", marginRight: "24px" }}>
            early warning indicator; will move before the thesis is obvious
          </span>
        </div>
        <div style={{ margin: "8px 0" }}>
          <span style={pillStyle("#666")}>HEADWIND</span>
          <span style={{ fontFamily: bodyFont, fontSize: "0.9rem", color: "#888" }}>
            thesis creates pressure on this business model
          </span>
        </div>

        <div style={sectionDivider} />

        {/* ─── SECTION 5: DATA SOURCES ─── */}
        <h2 style={h2Style}>Public Data, Verifiable by Anyone</h2>
        <p style={bodyStyle}>
          CASCADE uses only free, public data sources. Every score can be
          independently verified. No proprietary feeds. No black boxes.
        </p>

        {[
          {
            name: "FRED (Federal Reserve)",
            desc: "750,000+ economic time series. Primary source for macro indicators: interest rates, money supply, employment, inflation, yield curves.",
            url: "fredapi.stlouisfed.org",
            note: "Free, no rate limit in practice",
          },
          {
            name: "Google Trends",
            desc: "Search interest as a proxy for behavioral adoption. When people start searching for a thesis theme at scale, adoption is beginning.",
            url: "trends.google.com",
            note: "Free, no API key required",
          },
          {
            name: "SEC EDGAR",
            desc: "10-K filings for revenue segment data used in EFS Revenue Alignment and Signal Purity scoring.",
            url: "data.sec.gov",
            note: "Free, no API key required",
          },
          {
            name: "Yahoo Finance",
            desc: "Price and momentum data for EFS Thesis Beta and Momentum Alignment.",
            url: "Public market data",
            note: "Free",
          },
          {
            name: "BLS (Bureau of Labor Statistics)",
            desc: "Employment and wage data for labor-related theses.",
            url: "api.bls.gov",
            note: "Free",
          },
        ].map((src) => (
          <div key={src.name} style={sourceCardStyle}>
            <div style={{
              fontFamily: monoFont,
              fontSize: "11px", fontWeight: 700,
              letterSpacing: "0.06em", color: "#fff",
              marginBottom: "6px",
            }}>
              {src.name}
            </div>
            <p style={{ fontFamily: bodyFont, fontSize: "0.9rem", color: "#888", margin: "0 0 6px", lineHeight: 1.6 }}>
              {src.desc}
            </p>
            <div style={{
              fontFamily: monoFont,
              fontSize: "9px", color: "#444",
            }}>
              {src.url} &mdash; {src.note}
            </div>
          </div>
        ))}

        <div style={sectionDivider} />

        {/* ─── SECTION 6: WHAT CASCADE IS NOT ─── */}
        <h2 style={h2Style}>What This Is Not</h2>
        <p style={bodyStyle}>
          CASCADE is not a stock screener. It is not a trading signal.
          It is not financial advice.
        </p>
        <p style={bodyStyle}>
          It is a structured thinking tool. The scores tell you whether the
          data currently supports your view &mdash; not whether you will make money.
          Markets can stay wrong longer than models stay solvent.
        </p>
        <p style={bodyStyle}>
          The non-obvious equity picks are intentional. If the first-order
          play is obvious, everyone is already in it. CASCADE is built to find
          the second-order expression of a thesis that hasn&rsquo;t been priced yet.
        </p>
      </div>
    </div>
  );
}
