# CASCADE — Progress & Handoff Document

**Date:** 2026-03-10

---

## Project Overview

CASCADE is a macro investing tool that lets users enter investment theses as plain English sentences, then automatically generates:

1. **Second and third order causal effects** (via Claude AI)
2. **Data-driven health scores** (THI — Thesis Health Index) from public economic data
3. **Equity positions** with fit scores (EFS) measuring how purely each stock expresses the thesis
4. **Startup opportunities** with timing scores (STS)

The core idea: you write "The US dollar is being debased" and CASCADE generates downstream effects ("gold prices rise", "Bitcoin adoption accelerates"), assigns real FRED/Google Trends data feeds to each, computes a 0–100 health score, and suggests non-obvious equity plays ranked by thesis fit.

Built for macro investors who want structured, data-backed conviction tracking — not a stock screener or trading signal.

---

## Current State

### Working

- Full thesis CRUD (create, read, update, delete, archive, reorder)
- Claude-powered thesis generation from single sentence input
- Claude-powered 2nd/3rd order effect generation
- Cascading tree layout with depth-indented cards that expand/collapse independently
- THI scoring pipeline: FRED feeds fetch → percentile normalization → evidence/momentum/data quality → composite score
- Google Trends integration for adoption feeds
- EFS scoring: Yahoo Finance fundamentals + SEC EDGAR segments + price history correlation
- STS scoring for startup opportunities
- Macro header (FFR, 10Y-2Y spread, VIX) from FRED
- Dashboard with filter (all/active/archived), sort (THI/recent/alpha), tag filtering
- Canvas-based THI gauge with animated needle sweep
- Canvas-based gradient progress bars with staggered animation
- Equity bet cards with EFS breakdown, expandable sub-scores, role badges — on both hero and effect cards
- Startup cards with STS scores and timing labels
- Per-card refresh feeds button + global refresh button on thesis tree page
- THI breakdown panel (evidence/momentum/data quality) with formula row
- Methodology page explaining all scoring formulas
- Portfolio position tracking with P&L
- Conviction slider with divergence warnings
- 16 seeded theses with effects, equity bets, and startup opportunities

### Partially Working

- **Momentum scoring**: Formula is correct but shows 0/neutral for all theses because there are only 1-2 THI snapshots in history. Needs multiple feed refresh cycles over days/weeks to build meaningful deltas. The UI gracefully shows "Builds after first feed refresh" when no history exists.
- **EFS Revenue Alignment**: Uses keyword matching + hardcoded ticker overrides rather than actual SEC 10-K segment parsing. The SEC EDGAR integration fetches SIC codes and estimates segment count but doesn't parse actual revenue breakdowns.
- **EFS Thesis Beta**: Requires 6+ THI snapshots to compute meaningful correlation. Returns 0.5 (neutral) with insufficient data.
- **Data quality scoring**: Backend computes it correctly, but the freshness score display on frontend was overridden to compute `live/total*100` locally because the backend value seemed wrong (showed 20 when 1/1 feeds were live).

### Broken / Missing

- **Backend won't start with current schema changes**: The `evidence_explanation`, `momentum_explanation`, and `conviction_explanation` columns were added to models.py but the SQLite DB needs manual ALTER TABLE statements. If the DB file is deleted, it recreates cleanly on startup via `create_all()`.
- **No database migrations**: Using SQLAlchemy `create_all()` only. Schema changes require manual `ALTER TABLE` or deleting the DB. No Alembic.
- **APScheduler not wired**: The scheduler is imported in main.py but feed refresh is only triggered manually (via button or after generation). No automatic periodic refresh.
- **Several component files are unused legacy**: `Header.tsx`, `EffectChain.tsx`, `NewThesisPanel.tsx`, `ThemeToggle.tsx` are from earlier iterations and may not be used by current pages.
- **Effect detail page is just a redirect**: `/thesis/[id]/effect/[effectId]` redirects back to the thesis page, doesn't have its own view.
- **No authentication or multi-user support**
- **No error toasts/notifications**: Errors are console.error'd or briefly shown in button labels

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) | 14.2.35 |
| Frontend | React | ^18 |
| Frontend | TypeScript | ^5 |
| Frontend | Tailwind CSS | ^3.4.1 |
| Frontend | Recharts | ^3.7.0 |
| Backend | FastAPI | 0.115.6 |
| Backend | Python | 3.11 |
| Backend | SQLAlchemy | 2.0.36 |
| Backend | Anthropic SDK | 0.40.0 |
| Database | SQLite | (via SQLAlchemy) |
| Data | FRED API | fredapi via httpx |
| Data | Google Trends | pytrends 4.9.2 |
| Data | Yahoo Finance | yfinance (via pip, not in requirements.txt) |
| Data | SEC EDGAR | Direct httpx calls |
| Scheduler | APScheduler | 3.10.4 (imported, not actively scheduling) |
| Fonts | Bricolage Grotesque 800, Inter, JetBrains Mono | Google Fonts |

---

## File Structure

### Backend (`backend/`)

```
backend/
├── main.py                    — FastAPI app, CORS, lifespan startup (create tables + seed), router registration
├── config.py                  — Env vars (FRED_API_KEY, ANTHROPIC_API_KEY, etc.), loads formulas.json
├── database.py                — SQLAlchemy engine + SessionLocal for SQLite (tangentbook.db)
├── models.py                  — All SQLAlchemy models (15 tables)
├── seed.py                    — Seeds 16 theses with effects, bets, opportunities, feeds (~960 lines)
├── requirements.txt           — Python dependencies
├── routers/
│   ├── theses.py              — Thesis/Effect/Bet/Opportunity CRUD + conviction + formulas endpoint
│   ├── feeds.py               — Feed listing, refresh, scoring breakdown, macro header
│   ├── efs.py                 — EFS and STS score retrieval and refresh
│   ├── generate.py            — Claude AI thesis + effect generation
│   └── portfolio.py           — Portfolio position CRUD and P&L
├── services/
│   ├── scoring_engine.py      — THI math: evidence, momentum, conviction, child THI
│   ├── feed_refresh.py        — Orchestrates feed fetch → normalize → score → snapshot
│   ├── efs_service.py         — EFS/STS calculation with Yahoo/SEC/Crunchbase
│   ├── fred_client.py         — FRED API client (fetch series, macro header data)
│   └── gtrends_client.py      — Google Trends client (pytrends wrapper)
├── clean_bet_descriptions.py  — One-off script to clean bet descriptions
├── regenerate_descriptions.py — One-off script to regenerate descriptions
├── dedup_tickers.py           — One-off script to deduplicate tickers
├── fix_effect_thi_scores.py   — One-off script to fix effect THI scores
├── fix_names_and_descriptions.py — One-off script to fix names
├── refresh_all.py             — Standalone script to trigger full refresh
├── seed_9bets.py              — One-off script to seed 9 bets per node
├── seed_effect_feeds.py       — One-off script to seed feeds for effects
├── seed_gaps.py               — One-off gap-filling seed script
├── seed_gaps2.py              — One-off gap-filling seed script
└── seed_gaps3.py              — One-off gap-filling seed script
```

### Frontend (`frontend/`)

```
frontend/
├── app/
│   ├── layout.tsx                           — Root layout: Inter + JetBrains Mono fonts, Bricolage Grotesque via CDN
│   ├── globals.css                          — CSS vars, dark theme defaults
│   ├── page.tsx                             — Dashboard: thesis cards, macro header, filter/sort/tags, new thesis input
│   ├── methodology/
│   │   └── page.tsx                         — Static methodology page explaining all scoring formulas
│   └── thesis/
│       └── [id]/
│           ├── page.tsx                     — Thesis tree: cascading cards, THI gauge, breakdown, EFS, refresh
│           └── effect/
│               └── [effectId]/
│                   └── page.tsx             — Redirect to parent thesis page
├── components/
│   ├── CascadeLogo.tsx                      — SVG logo: cascading bars + wordmark
│   ├── ConvictionSlider.tsx                 — 1-10 slider with note field and divergence warning
│   ├── EffectChain.tsx                      — Legacy: vertical accordion effect chain (not used in current tree)
│   ├── EquityBetCard.tsx                    — Equity bet card with EFS bar, role badge, expandable breakdown
│   ├── ErrorBoundary.tsx                    — React error boundary with fallback UI
│   ├── GradientBar.tsx                      — Canvas progress bar with orange gradient, animation support
│   ├── Header.tsx                           — Legacy: app header (dashboard has its own inline header now)
│   ├── Needle.tsx                           — Canvas semicircular gauge (sm/md/lg), used on dashboard cards
│   ├── NewThesisPanel.tsx                   — Legacy: slide-down thesis creation panel
│   ├── Skeleton.tsx                         — Loading skeleton placeholders
│   ├── Sparkline.tsx                        — Recharts mini line chart for data series
│   ├── StartupCard.tsx                      — Startup opportunity card with STS score
│   ├── StockSparkline.tsx                   — Stock price sparkline via Recharts
│   ├── ThemeToggle.tsx                      — Legacy: dark/light theme toggle
│   └── TrashIcon.tsx                        — SVG trash icon
├── lib/
│   └── api.ts                               — API client + all TypeScript interfaces (465 lines)
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.mjs
```

### Project Root

```
tangentbook-v3/
├── formulas.json              — Single source of truth for all scoring weights (THI, EFS, STS, macro)
├── PROGRESS.md                — Session progress notes
├── HANDOFF.md                 — This file
└── .gitignore
```

---

## API Endpoints

All endpoints prefixed with `/api`. Base URL: `http://localhost:8000/api`

### Theses Router (`routers/theses.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/formulas` | Return full formulas.json (all scoring weights) |
| GET | `/theses` | List all theses ordered by display_order |
| POST | `/theses` | Create a new thesis |
| GET | `/theses/{thesis_id}` | Get thesis detail with THI history and all relations |
| PUT | `/theses/{thesis_id}` | Update thesis fields |
| DELETE | `/theses/{thesis_id}` | Delete thesis and all children |
| PATCH | `/theses/{thesis_id}/archive` | Toggle archived status |
| PATCH | `/theses/{thesis_id}/collapse` | Toggle collapsed status |
| PATCH | `/theses/{thesis_id}/reorder` | Update display_order |
| PUT | `/theses/{thesis_id}/conviction` | Update user conviction score (1-10) |
| GET | `/theses/{thesis_id}/effects` | List effects for thesis |
| POST | `/theses/{thesis_id}/effects` | Create new effect |
| GET | `/effects/{effect_id}` | Get single effect |
| PUT | `/effects/{effect_id}` | Update effect |
| DELETE | `/effects/{effect_id}` | Delete effect |
| PUT | `/effects/{effect_id}/conviction` | Update effect conviction |
| POST | `/theses/{thesis_id}/bets` | Create equity bet on thesis |
| POST | `/effects/{effect_id}/bets` | Create equity bet on effect |
| PUT | `/bets/{bet_id}` | Update equity bet |
| DELETE | `/bets/{bet_id}` | Delete equity bet |
| POST | `/theses/{thesis_id}/opportunities` | Create startup opportunity on thesis |
| POST | `/effects/{effect_id}/opportunities` | Create startup opportunity on effect |
| PUT | `/opportunities/{opp_id}` | Update startup opportunity |
| DELETE | `/opportunities/{opp_id}` | Delete startup opportunity |

### Feeds Router (`routers/feeds.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/theses/{thesis_id}/feeds` | List feeds for thesis (not effect feeds) |
| POST | `/theses/{thesis_id}/feeds/refresh` | Refresh all thesis feeds, recompute THI |
| POST | `/feeds/refresh-all` | Refresh all theses + macro header |
| POST | `/macro/refresh` | Refresh macro header only |
| POST | `/feeds/{feed_id}/refresh` | Refresh single feed |
| GET | `/feeds/{feed_id}/history` | Get feed cache history |
| GET | `/macro/header` | Get current macro regime/FFR/spread/VIX |
| GET | `/theses/{thesis_id}/scoring-breakdown` | Full scoring breakdown by evidence dimension |
| GET | `/effects/{effect_id}/scoring-breakdown` | Scoring breakdown for an effect |
| POST | `/effects/{effect_id}/feeds/refresh` | Refresh effect feeds |

### EFS Router (`routers/efs.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/theses/{thesis_id}/equity-scores` | Get EFS for all thesis equity bets |
| POST | `/theses/{thesis_id}/equity-scores/refresh` | Recalculate all thesis EFS scores |
| GET | `/equity-bet/{bet_id}/efs` | Get single bet EFS breakdown |
| GET | `/startup/{opp_id}/sts` | Get single startup STS |
| GET | `/effects/{effect_id}/equity-scores` | Get EFS for all effect equity bets |

### Generate Router (`routers/generate.py`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/theses/generate` | Generate full thesis from sentence (Claude AI) |
| POST | `/theses/{thesis_id}/generate-effects` | Generate 2nd/3rd order effects (Claude AI) |

### Portfolio Router (`routers/portfolio.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/theses/{thesis_id}/portfolio` | Get portfolio positions + P&L |
| POST | `/theses/{thesis_id}/portfolio/positions` | Add position |
| PUT | `/portfolio/positions/{position_id}` | Update position |
| DELETE | `/portfolio/positions/{position_id}` | Delete position |

---

## Frontend Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Thesis card grid, macro header, filter/sort/tags, new thesis input |
| `/thesis/[id]` | Thesis Tree | Cascading card tree with THI gauges, breakdowns, EFS, refresh |
| `/thesis/[id]/effect/[effectId]` | Effect Redirect | Redirects to `/thesis/[id]` (no standalone effect page) |
| `/methodology` | Methodology | Static page explaining THI, EFS, STS formulas and data sources |

---

## Component Inventory

| Component | File | Description |
|-----------|------|-------------|
| CascadeLogo | `CascadeLogo.tsx` | SVG cascading bars mark + "CASCADE" wordmark |
| ConvictionSlider | `ConvictionSlider.tsx` | 1–10 horizontal slider with optional note, divergence warning |
| EffectChain | `EffectChain.tsx` | **Legacy** — vertical accordion for effects, replaced by tree layout |
| EquityBetCard | `EquityBetCard.tsx` | Stock card: ticker, name, role badge, EFS bar, expandable breakdown |
| ErrorBoundary | `ErrorBoundary.tsx` | React error boundary with fallback |
| GradientBar | `GradientBar.tsx` | Canvas progress bar — orange cubic ease-in gradient, animation + delay |
| Header | `Header.tsx` | **Legacy** — standalone header, replaced by inline nav per page |
| Needle | `Needle.tsx` | Canvas semicircular gauge (sm 80px / md 120px / lg 200px) |
| NewThesisPanel | `NewThesisPanel.tsx` | **Legacy** — slide panel for thesis creation, may not be used |
| Skeleton | `Skeleton.tsx` | Loading skeleton lines + `ThesisCardSkeleton` |
| Sparkline | `Sparkline.tsx` | Recharts mini line chart for generic data series |
| StartupCard | `StartupCard.tsx` | Startup card: name, one-liner, timing badge, STS score + bar |
| StockSparkline | `StockSparkline.tsx` | Recharts stock price sparkline by ticker |
| ThemeToggle | `ThemeToggle.tsx` | **Legacy** — dark/light toggle via localStorage |
| TrashIcon | `TrashIcon.tsx` | Simple SVG trash icon |

**Inline components** (defined in `thesis/[id]/page.tsx`, not separate files):

- `THIGauge` — Canvas semicircular gauge with animated needle sweep (1.2s ease-out)
- `THIBreakdownPanel` — Evidence/Momentum/Data Quality rows with gradient bars + formula
- `BreakdownRow` — Single score row (label + weight + score + bar + detail text)
- `PillButton` — Toggle pill for panel sections
- `ExpandableText` — Clamped text with "Read more" toggle

---

## Data Model

### Core Tables

| Table | Purpose |
|-------|---------|
| `theses` | Parent investment theses with THI score, direction, trend, component scores/weights, explanation text, user conviction |
| `effects` | 2nd/3rd order causal effects linked to theses, with own THI, inheritance weight, explanation text |
| `equity_bets` | Stock positions linked to thesis OR effect (ticker, role, rationale) |
| `startup_opportunities` | Startup ideas linked to thesis OR effect (name, one-liner, timing) |
| `data_feeds` | FRED/Google Trends feeds linked to thesis OR effect (series_id, keyword, normalized_score, weight, status) |

### Scoring Tables

| Table | Purpose |
|-------|---------|
| `equity_fit_scores` | EFS per equity bet (5 sub-scores + composite, raw data fields) |
| `startup_timing_scores` | STS per startup (3 sub-scores + composite) |
| `thi_snapshots` | Historical THI scores per thesis (for momentum calculation) |
| `indicators` | Abstraction layer for feed groups (not heavily used) |

### Supporting Tables

| Table | Purpose |
|-------|---------|
| `feed_cache` | Historical raw + normalized values per feed fetch |
| `conviction_snapshots` | History of user conviction changes |
| `macro_header` | Current macro regime (FFR, 10Y-2Y spread, VIX) |
| `portfolio_positions` | User's actual positions with entry price and P&L |
| `portfolio_snapshots` | Historical portfolio value snapshots |

### Key Relationships

- Thesis → many Effects (cascade delete)
- Thesis → many EquityBets (direct thesis bets)
- Effect → many EquityBets (effect-level bets)
- Thesis → many StartupOpportunities (direct)
- Effect → many StartupOpportunities (effect-level)
- Thesis → many DataFeeds (thesis-level feeds)
- Effect → many DataFeeds (effect-level feeds)
- EquityBet → one EquityFitScore (1:1)
- StartupOpportunity → one StartupTimingScore (1:1)
- Effect → parent Effect (self-referencing for 3rd order)

### Schema Changes Without Alembic

The following columns were added via raw `ALTER TABLE` on the SQLite DB (no Alembic migration exists):

```sql
ALTER TABLE theses ADD COLUMN evidence_explanation TEXT;
ALTER TABLE theses ADD COLUMN momentum_explanation TEXT;
ALTER TABLE theses ADD COLUMN conviction_explanation TEXT;
ALTER TABLE effects ADD COLUMN evidence_explanation TEXT;
ALTER TABLE effects ADD COLUMN momentum_explanation TEXT;
ALTER TABLE effects ADD COLUMN conviction_explanation TEXT;
```

If the DB is deleted, `Base.metadata.create_all()` recreates everything cleanly.

---

## Scoring System

All weights are defined in `formulas.json` at the project root and loaded by `backend/config.py` at startup.

### THI — Thesis Health Index (0–100)

```
THI = (Evidence × 0.50) + (Momentum × 0.30) + (Data Quality × 0.20)
```

**Evidence** (real data-driven): Weighted average of normalized DataFeed scores. Each feed is percentile-ranked against its own 5-year history from FRED. Feeds grouped by type: Flow (35%), Structural (30%), Adoption (20%), Policy (15%). Offline feeds have their weight redistributed to active ones.

**Momentum** (real data-driven, but needs history): Rate of change of evidence score over 30d/90d/1yr from THI snapshots. `Momentum = (30d_Δ × 0.50) + (90d_Δ × 0.30) + (1yr_Δ × 0.20)`. Delta of ±30 evidence points maps to 0–100 momentum. Returns 50 (neutral) with <2 snapshots. **Currently shows neutral for all theses due to insufficient snapshot history.**

**Data Quality** (real data-driven): `(Signal Agreement × 0.40) + (Freshness × 0.35) + (Source Quality × 0.25)`. Agreement = low variance among feed scores. Freshness = % of feeds currently live. Source quality base = 70.

**Direction thresholds**: ≥60 = CONFIRMING, ≤40 = REFUTING, 40–60 = NEUTRAL.

**Child THI**: `Child THI = (Parent THI × 0.40) + (Child's own score × 0.60)`. Default inheritance weight is 0.40.

### EFS — Equity Fit Score (0–100)

```
EFS = (Revenue Alignment × 0.30) + (Thesis Beta × 0.25) + (Momentum Alignment × 0.20)
    + (Valuation Buffer × 0.15) + (Signal Purity × 0.10)
```

| Component | Data Source | Real vs Estimated |
|-----------|-----------|-------------------|
| Revenue Alignment | SEC EDGAR SIC + keyword matching | **Estimated** — uses industry keywords + hardcoded overrides, not actual 10-K segment parsing |
| Thesis Beta | THI snapshots + Yahoo Finance price history | **Real** when ≥6 snapshots exist, otherwise returns 50 (neutral) |
| Momentum Alignment | Yahoo Finance 6mo prices + THI snapshots | **Real** — compares 90d stock return vs THI delta |
| Valuation Buffer | Yahoo Finance forward P/E vs sector ETF P/E | **Real** |
| Signal Purity | SEC EDGAR SIC + hardcoded conglomerate map | **Partially estimated** — SIC-based heuristic, not actual segment count |

### STS — Startup Timing Score (0–100)

```
STS = (THI Alignment × 0.40) + (THI Velocity × 0.35) + (Competition Density Inverted × 0.25)
```

| Component | Data Source | Real vs Estimated |
|-----------|-----------|-------------------|
| THI Alignment | Current thesis THI score | **Real** |
| THI Velocity | THI 30-day delta from snapshots | **Real** when history exists, otherwise 50 |
| Competition Density | Crunchbase (optional) or timing label heuristic | **Estimated** — falls back to mapping TOO_EARLY=15, RIGHT_TIMING=45, CROWDING=80 |

---

## Data Pipeline

### Feed Refresh Flow

1. User clicks REFRESH FEEDS (or it's triggered after thesis generation)
2. `POST /api/theses/{id}/feeds/refresh` → `feed_refresh.refresh_thesis_feeds()`
3. For each DataFeed linked to the thesis:
   - FRED feeds: `fred_client.fetch_fred_series()` → fetches 5yr history → `normalize_percentile()` → score 0-100
   - Google Trends feeds: `gtrends_client.fetch_google_trends()` → normalize → score
   - Feeds with `confirming_direction: "lower"` get score flipped (100 - score)
4. Compute evidence = weighted average of feed scores (redistributing offline weights)
5. Compute momentum from THI snapshot deltas (30d/90d/1yr)
6. Compute data quality (agreement + freshness + source quality)
7. Compute THI = weighted composite
8. Save THI snapshot for future momentum calculation
9. Update child effect THIs via inheritance formula
10. Return updated thesis

### Data Sources

| Source | Status | API Key Required | What It Provides |
|--------|--------|-----------------|-----------------|
| FRED | **Wired** | Yes (`FRED_API_KEY`) | Economic time series (rates, money supply, employment, CPI, yield curves) |
| Google Trends | **Wired** | No | Search interest as adoption proxy |
| Yahoo Finance | **Wired** | No (via `yfinance` library) | Stock fundamentals, price history, sector P/E |
| SEC EDGAR | **Wired** | No | Company SIC codes, segment count estimation |
| Crunchbase | **Stubbed** | Optional (`CRUNCHBASE_API_KEY`) | Competition density for STS — falls back to heuristic |
| BLS | **Not wired** | Would need `BLS_API_KEY` | Referenced in methodology page but not implemented |
| Alpha Vantage | **Not wired** | Would need `ALPHA_VANTAGE_API_KEY` | Referenced in config but not used |
| Polygon | **Not wired** | Would need `POLYGON_API_KEY` | Referenced in config but not used |

### Required Environment Variables

```bash
FRED_API_KEY=<required>        # Federal Reserve Economic Data
EIA_API_KEY=<required>         # Energy Information Administration (checked at startup)
ANTHROPIC_API_KEY=<required>   # Claude AI for thesis/effect generation
```

Optional:
```bash
POLYGON_API_KEY=<optional>
CRUNCHBASE_API_KEY=<optional>
ALPHA_VANTAGE_API_KEY=<optional>
```

---

## Known Issues & Bugs

1. **Backend startup crash if DB has old schema**: Adding explanation columns to models.py without Alembic means existing DBs crash with `no such column: theses.evidence_explanation`. Fix: delete `tangentbook.db` or run manual ALTER TABLE statements.

2. **yfinance not in requirements.txt**: The `yfinance` library is used by `efs_service.py` but not listed in `requirements.txt`. Install manually: `pip install yfinance`.

3. **Momentum always shows neutral**: All theses have <2 THI snapshots. Need multiple feed refresh cycles over time to build history. The UI handles this gracefully but the data is always 50.

4. **Revenue alignment is keyword-estimated, not real**: SEC 10-K segment revenue parsing is not implemented. Uses SIC code + keyword matching + hardcoded ticker-to-alignment overrides.

5. **No automatic feed refresh**: APScheduler is in requirements but not wired. Feeds only refresh on manual button click or after thesis generation.

6. **Several one-off scripts in backend/**: `seed_9bets.py`, `seed_gaps.py`, `seed_gaps2.py`, `seed_gaps3.py`, `dedup_tickers.py`, `fix_effect_thi_scores.py`, etc. These were used during development and could be cleaned up.

7. **Legacy components not cleaned up**: `Header.tsx`, `EffectChain.tsx`, `NewThesisPanel.tsx`, `ThemeToggle.tsx` are from earlier iterations. Some may still be imported somewhere but the current pages have inline equivalents.

8. **Effect detail page is a redirect**: `/thesis/[id]/effect/[effectId]` just redirects to the thesis page. No standalone effect view.

9. **No database backups or migration system**: SQLite file can be wiped accidentally. No Alembic.

10. **CORS allows all origins**: `allow_origins=["*"]` in main.py. Fine for local dev, needs restricting for production.

11. **Frontend port conflict**: If port 3000 is in use, Next.js silently falls back to 3001. Can cause confusion.

12. **Freshness score mismatch**: Backend computes freshness one way, frontend overrides the display calculation. These should be reconciled.

---

## Immediate Next Steps

1. **Wire up APScheduler for periodic feed refresh** — Run `refresh_all_theses()` every 6 hours to build THI snapshot history for momentum scoring. This is the single highest-impact change: it makes momentum scoring real.

2. **Add Alembic for migrations** — Prevent future schema change crashes. Generate initial migration from current models.

3. **Implement real SEC 10-K revenue segment parsing** — Replace keyword-matching revenue alignment with actual segment revenue extraction from EDGAR XBRL filings.

4. **Add `yfinance` to requirements.txt** — Simple fix, currently missing.

5. **Clean up one-off scripts** — Move `seed_*.py`, `fix_*.py`, `dedup_*.py` to a `scripts/` directory or delete them.

6. **Remove legacy components** — Audit `Header.tsx`, `EffectChain.tsx`, `NewThesisPanel.tsx`, `ThemeToggle.tsx` for any remaining imports, then delete unused ones.

7. **Build standalone effect detail page** — Replace the redirect with a real page showing effect-specific feeds, scoring breakdown, and bets.

8. **Add error toast notifications** — Replace console.error and brief button label changes with a proper toast system.

9. **Reconcile freshness score calculation** — Make backend and frontend agree on how freshness is computed and displayed.

10. **Add basic auth** — Even a simple API key or session token to prevent open access.

---

## How to Run

### Prerequisites

- Python 3.11
- Node.js 18+
- FRED API key (free from https://fred.stlouisfed.org/docs/api/api_key.html)
- Anthropic API key (for thesis generation)

### Backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install yfinance  # Not in requirements.txt yet

# Set environment variables
export FRED_API_KEY=your_key_here
export EIA_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here

# Start server (creates tangentbook.db and seeds on first run)
python3.11 -m uvicorn main:app --port 8000
```

Backend runs on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` (or 3001 if 3000 is occupied).

### First Run

1. Start backend — it creates the DB and seeds 16 theses automatically
2. Start frontend — dashboard shows seeded theses
3. Click any thesis to see the tree view
4. Click REFRESH FEEDS on a thesis to trigger first data fetch
5. Generate a new thesis by typing a sentence in the dashboard input

### Ports

| Service | Port |
|---------|------|
| Backend (FastAPI) | 8000 |
| Frontend (Next.js) | 3000 (or 3001) |

---

## Git History Summary

Last 20 commits (newest first):

1. **formulas.json as single source of truth** — Created formulas.json, backend services load weights from it, exposed GET /api/formulas, added explanation fields to models, trigger feed refresh after generation
2. **Dashboard polish** — All-caps titles, card padding, equal height cards, logo sizing
3. **Multi-card expand** — Independent card toggle (multiple open simultaneously)
4. **PROGRESS.md** — Added progress documentation
5. **Gradient progress bars** — Canvas-based gradient bars replacing block characters, 100-stop cubic ease-in
6. **Equity bet card layout** — Fixed inconsistent heights with line clamping
7. **Revert to 3-col grid** — Removed category columns, back to flat grid sorted by EFS
8. **EFS + STS system** — Full Equity Fit Score and Startup Timing Score with Yahoo/SEC/Crunchbase
9. **AI prompt fixes** — Plain startup names, category layout with context
10. **Unique tickers** — No parent/child overlap, validation script
11. **Feeds root cause fix** — Explicit formulas, bespoke effect scores, refresh buttons
12. **Scoring breakdown** — 2nd/3rd order breakdown, feed context stats, 3x3 bet grid, portfolio tracker
13. **Feed pipeline fix** — Scoring engine connected, refresh all, full 2nd/3rd order effects seeded
14. **Thesis detail redesign** — Hero/breakdown/tabs/feeds/effect thumbnails + scoring API
15. **Effect chain redesign** — Vertical accordion + equity bet diversification
16. **2nd order effect cards** — Collapsed clean, expand for detail
17. **Sparkline tooltip** — Canary feedback indicator, GLP-1 evidence score fix
18. **Yahoo Finance sparklines** — Real price data sparklines + feedback indicator fix
19. **Feedback indicator logic** — Canary only, audit roles
20. **Sparkline layout** — Moved to full-width row below header
