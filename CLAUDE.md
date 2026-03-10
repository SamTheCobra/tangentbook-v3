# TangentBook v3 — Project Handoff

## What Is This?

TangentBook is a personal macro investing tool. You input investment theses (e.g., "USD Debasement & Hard Asset Premium"), and the system tracks evidence via FRED data, Google Trends, conviction sliders, and composite health scores (THI). Each thesis has a causal tree of 2nd/3rd-order effects, equity bets with fit scores, and startup opportunity timing scores.

16 theses are seeded on first run with initial scores, effects, equity bets, and startup opportunities.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (`tangentbook.db`, gitignored) |
| AI | Anthropic Claude Sonnet 4 (`anthropic` SDK) |
| Market Data | yfinance |
| Macro Data | FRED API, EIA API |
| Trends | Google Trends (pytrends) |
| Scheduler | APScheduler (async, feed refresh) |
| Fonts | Inter (headings/body), JetBrains Mono (all numbers/data) |
| Design | Dark theme, Swiss brutalist editorial |

---

## Hard Constraints — READ THESE

- **No TypeScript in backend.** Backend is pure Python.
- **No tests.** Zero test files exist. Don't create any.
- **No Alembic.** Migrations are manual ALTER TABLEs in `database.py`.
- **SQLite only.** Single-user app, no Postgres.
- **Inline styles.** Frontend uses CSS variables + inline style objects. No CSS modules, no styled-components. Tailwind for layout utilities only.
- **No border-radius, no shadows, no gradients** in the design system (except the GradientBar progress bar component which is intentionally gradient).
- **Don't add docstrings, comments, or type annotations to code you didn't change.**

---

## How to Start

```bash
# Both servers
make dev

# Or separately:
make backend     # uvicorn on :8000
make frontend    # next.js on :3000

# Setup (first time)
make setup-backend   # creates venv, installs deps
make setup-frontend  # npm install
```

Backend requires env vars: `FRED_API_KEY`, `EIA_API_KEY`, `ANTHROPIC_API_KEY`. Copy `.env.example` to `.env`.

For quick local dev without real API keys:
```bash
cd backend && source venv/bin/activate && FRED_API_KEY=test EIA_API_KEY=test ANTHROPIC_API_KEY=test python3.11 -m uvicorn main:app --reload --port 8000
```

Python venv lives at `backend/venv/`, using `python3.11` at `/usr/local/bin/python3.11`.

---

## File Structure

```
tangentbook-v3/
├── Makefile                        # make dev / make backend / make frontend
├── backend/
│   ├── main.py                     # FastAPI app, CORS, router registration, scheduler
│   ├── models.py                   # 13 SQLAlchemy models
│   ├── database.py                 # Engine, SessionLocal, init_db()
│   ├── config.py                   # Env validation, constants
│   ├── seed.py                     # Seeds 16 theses with effects, bets, startups
│   ├── routers/
│   │   ├── theses.py               # Thesis/Effect/EquityBet/StartupOpp CRUD
│   │   ├── feeds.py                # FRED data feeds, macro header
│   │   ├── portfolio.py            # Portfolio positions
│   │   └── efs.py                  # EFS and STS score endpoints
│   └── services/
│       ├── scoring_engine.py       # THI formula implementation
│       ├── efs_service.py          # EFS/STS calculation (Yahoo, SEC, Crunchbase)
│       ├── fred_client.py          # FRED API client
│       ├── gtrends_client.py       # Google Trends client
│       └── feed_refresh.py         # Background feed refresh logic
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Dashboard — thesis grid with filter/sort/tags
│   │   ├── thesis/[id]/page.tsx    # Thesis detail — needle, effects, bets, startups
│   │   └── thesis/[id]/effect/[effectId]/page.tsx  # Effect detail
│   ├── components/
│   │   ├── Needle.tsx              # Canvas THI gauge (sm/md/lg)
│   │   ├── Header.tsx              # App header with new thesis button
│   │   ├── ConvictionSlider.tsx    # 1-10 slider with history sparkline + note prompt
│   │   ├── EquityBetCard.tsx       # Ticker card with sparkline, EFS bar, breakdown
│   │   ├── StartupCard.tsx         # Startup opp with STS bar + timing badge
│   │   ├── GradientBar.tsx         # Canvas progress bar — 100-stop cubic ease-in gradient
│   │   ├── StockSparkline.tsx      # Real price sparkline via yfinance
│   │   ├── Sparkline.tsx           # Generic sparkline component
│   │   ├── EffectChain.tsx         # Visual effect chain diagram
│   │   ├── NewThesisPanel.tsx      # Slide-out panel for thesis creation
│   │   ├── Skeleton.tsx            # Loading skeleton components
│   │   ├── ErrorBoundary.tsx       # Error boundary wrapper
│   │   └── ThemeToggle.tsx         # Dark/light theme toggle
│   └── lib/
│       └── api.ts                  # API client — all fetch calls + TypeScript types
```

---

## Scoring Formulas

### THI (Thesis Health Index) — 0 to 100

```
THI = (Evidence × 0.50) + (Momentum × 0.30) + (DataQuality × 0.20)
```

When user conviction is updated, THI blends:
```
Final THI = (Data-driven THI × 0.70) + (User Conviction scaled to 0-100 × 0.30)
```

**Evidence Score** (0-100): Weighted average of all active data feed normalized scores. Offline feeds have their weights redistributed to active feeds.

**Momentum Score** (0-100):
```
Momentum = (Short-term × 0.50) + (Medium-term × 0.30) + (Long-term × 0.20)
```
Short = 30d rate-of-change, Medium = 90d, Long = 1yr.

**Data Quality / Conviction Score** (0-100):
```
DataQuality = (Signal Agreement × 0.40) + (Data Freshness × 0.35) + (Source Quality × 0.25)
```

**Child THI** (for effects):
```
Child THI = (Parent THI × inheritance_weight) + (Child indicator score × (1 - inheritance_weight))
```
Default `inheritance_weight` = 0.40.

**Direction**: score >= 60 → "confirming", <= 40 → "refuting", else "neutral"

**Divergence Warning**: Fires when `|user_conviction × 10 - THI| > 30`.

### EFS (Equity Fit Score) — 0 to 100

How purely a stock captures a thesis. Displayed on EquityBetCard with expandable breakdown.

```
EFS = (Revenue Alignment × 0.30) + (Thesis Beta × 0.25) + (Momentum Alignment × 0.20)
    + (Valuation Buffer × 0.15) + (Signal Purity × 0.10)
```

| Component | Weight | Source | What It Measures |
|-----------|--------|--------|-----------------|
| Revenue Alignment | 30% | SEC 10-K filings | % of revenue that is thesis-aligned |
| Thesis Beta | 25% | Yahoo Finance price history | 12-month correlation between stock and THI |
| Momentum Alignment | 20% | Yahoo Finance + THI snapshots | Whether 90d stock return and THI delta move together |
| Valuation Buffer | 15% | Yahoo Finance key stats | Forward P/E vs sector median — discount = good |
| Signal Purity | 10% | SEC 10-K filings | Fewer business segments = purer thesis signal |

ETFs in `SINGLE_ASSET_ETFS` set (GLD, SLV, IBIT, etc.) get auto-scored as pure-play.

### STS (Startup Timing Score) — 0 to 100

Is now the right time for this startup idea?

```
STS = (THI Alignment × weight) + (THI Velocity × weight) + (Competition Density × weight)
```

| Component | What It Measures |
|-----------|-----------------|
| THI Alignment | Is the thesis score high enough to support this idea? |
| THI Velocity | Is the thesis score accelerating? |
| Competition Density | How crowded is the space? (Crunchbase data) |

Timing labels: `TOO_EARLY`, `RIGHT_TIMING`, `CROWDING`.

---

## What's Built

- **Dashboard** (`/`): Thesis cards in 3-column grid with THI needle. Filter by ALL/ACTIVE/ARCHIVED. Sort by default order, THI score, conviction, or recently updated. Filter by tag via dropdown.
- **Thesis Detail** (`/thesis/[id]`): Hero section with large needle, subtitle, summary. Effects as expandable cards with child effects. Equity bets sorted by EFS in 3-column grid. Startup opportunities with STS scores and timing badges.
- **Effect Detail** (`/thesis/[id]/effect/[effectId]`): Effect-specific bets, startups, and child effects with EffectChain diagram.
- **ConvictionSlider**: 1-10 range input. Changes >= 2 points prompt for a note. Shows conviction history sparkline. Reset to default button.
- **EquityBetCard**: Ticker with Yahoo Finance link, real stock sparkline (StockSparkline via yfinance), EFS gradient bar. Click to expand full 5-component breakdown with source links to SEC/Yahoo. Divergence warning when momentum direction is DIVERGING. Top 3 badge.
- **StartupCard**: Name, one-liner, STS gradient bar, timing badge (TOO_EARLY/RIGHT_TIMING/CROWDING).
- **GradientBar**: Canvas-rendered progress bar. 100-stop cubic ease-in from transparent to `rgba(232, 68, 10, 0.85)`. Full gradient at 72% width. Dark track background.
- **Needle**: Canvas SVG-style gauge showing THI score in sm/md/lg sizes.
- **CORS**: Backend allows `localhost:3000` and `localhost:3001`.
- **Thesis fields**: `summary` (short, shown on dashboard cards, 2-line clamp) vs `description` (detailed, shown on thesis detail page).
- **Background scheduler**: APScheduler refreshes all feeds every 60 minutes (configurable via `FEED_REFRESH_INTERVAL_MINUTES`).

---

## CORS Configuration

Backend (`main.py`) allows origins:
- `http://localhost:3000` (Next.js default)
- `http://localhost:3001` (Next.js fallback port)

If frontend runs on a different port, add it to the `allow_origins` list in `main.py`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/theses` | List all theses |
| POST | `/api/theses` | Create thesis |
| GET | `/api/theses/:id` | Get thesis with THI + conviction history |
| PUT | `/api/theses/:id` | Update thesis fields |
| DELETE | `/api/theses/:id` | Delete thesis |
| PATCH | `/api/theses/:id/archive` | Toggle archived |
| PATCH | `/api/theses/:id/collapse` | Toggle collapsed |
| PATCH | `/api/theses/:id/reorder` | Set display order |
| PUT | `/api/theses/:id/conviction` | Update conviction (recalculates THI) |
| GET | `/api/theses/:id/effects` | List effects |
| POST | `/api/theses/:id/effects` | Create effect |
| GET/PUT/DELETE | `/api/effects/:id` | Effect CRUD |
| PUT | `/api/effects/:id/conviction` | Update effect conviction |
| POST | `/api/theses/:id/bets` | Create equity bet on thesis |
| POST | `/api/effects/:id/bets` | Create equity bet on effect |
| PUT/DELETE | `/api/bets/:id` | Update/delete equity bet |
| POST | `/api/theses/:id/opportunities` | Create startup opp |
| POST | `/api/effects/:id/opportunities` | Create startup opp on effect |
| PUT/DELETE | `/api/opportunities/:id` | Update/delete startup opp |
| GET | `/api/theses/:id/equity-scores` | Get all EFS scores for thesis |
| POST | `/api/theses/:id/equity-scores/refresh` | Recalculate all EFS for thesis |
| GET | `/api/equity-bet/:id/efs` | Get single EFS breakdown |
| GET | `/api/effects/:id/equity-scores` | Get EFS scores for effect |
| GET | `/api/startup/:id/sts` | Get STS for startup |
| GET | `/api/health` | Health check |

---

## Known Issues / Next TODOs

1. **EFS/STS scores are seeded with defaults** — need to trigger `/refresh` to get real Yahoo Finance/SEC data.
2. **StockSparkline** fetches from a backend proxy to yfinance — can be slow or rate-limited.
3. **Google Trends rate limiting** — pytrends gets 429'd frequently. 60s retry backoff.
4. **No authentication** — single-user app.
5. **No tests** — zero test files.
6. **SQLite create_all won't add columns** — must manually add ALTER TABLE to `database.py`.
7. **Seed data is re-inserted on every startup** if the DB is empty — delete `tangentbook.db` to reset.

---

## Git Remote

`origin`: https://github.com/SamTheCobra/tangentbook-v3.git
