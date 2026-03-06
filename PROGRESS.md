# TangentBook v3 — Progress Log

## Session: 2026-03-06

### 1. Equity Fit Score (EFS) System — Full Implementation

**Decision:** Add a scoring layer that rates how well each equity bet captures its parent thesis, and a Startup Timing Score (STS) for startup opportunities.

**EFS Formula (weighted composite, 0–100):**
- Revenue Alignment (30%) — % of revenue thesis-aligned via SEC 10-K
- Thesis Beta (25%) — 12-month Pearson correlation with THI
- Momentum Alignment (20%) — stock return vs THI delta over 90 days
- Valuation Buffer (15%) — forward P/E vs sector median
- Signal Purity (10%) — number of business segments (fewer = purer)

**STS Formula (weighted composite, 0–100):**
- THI Alignment (40%) — correlation with thesis health
- Velocity (30%) — funding/traction momentum
- Competition Density (30%) — inverted (less competition = better)

**Files created/modified:**
- `backend/models.py` — EquityFitScore and StartupTimingScore SQLAlchemy models
- `backend/services/efs_service.py` — calculation engine using yfinance, SEC EDGAR, in-memory cache with TTL
- `backend/routers/efs.py` — 6 API endpoints (GET/POST per thesis, per bet, per startup, per effect)
- `backend/scripts/calculate_all_efs.py` — batch script, scored 632 bets (avg 50.1) and 1872 startups (avg 56.4)
- `backend/config.py` — added CRUNCHBASE_API_KEY
- `backend/main.py` — registered efs router
- `frontend/lib/api.ts` — EFSScore, STSScore, EquityScoreResult types + API methods
- `frontend/components/EquityBetCard.tsx` — EFS bar, expandable breakdown, HIGHEST CONVICTION label, divergence warning
- `frontend/components/StartupCard.tsx` — STS score display with timing label

**Data sources:**
- Yahoo Finance (via `yfinance` library) — fundamentals, price history, sector PE
- SEC EDGAR — segment count for signal purity
- Crunchbase — competition density (optional, requires API key)

**Key fix:** Raw HTTP to Yahoo Finance returned 401; switched to `yfinance` library with `asyncio.run_in_executor` for sync calls.

---

### 2. Category Layout Revert

**Decision:** Remove 3-column category layout (RIDE THE WAVE / FIGHT THE TIDE / WATCH THIS SPACE) because category counts are unbalanced, making columns lopsided.

**Reverted to:** Simple `grid grid-cols-1 md:grid-cols-3 gap-0` for both equity bets and startups.

**Sort order:**
- Equity bets: BENEFICIARY first → HEADWIND → CANARY, then by EFS descending within each group
- Startups: STS descending

**Files modified:**
- `frontend/app/thesis/[id]/page.tsx` — replaced CategoryColumns with flat grid, deleted CATEGORY_COLUMNS const
- `frontend/app/thesis/[id]/effect/[effectId]/page.tsx` — same changes
- `frontend/components/EquityBetCard.tsx` — added role badge back to card footer (color-coded: BENEFICIARY=#FF4500, HEADWIND=#5A5A5A, CANARY=var(--text))

---

### 3. Equity Bet Card Layout Fix

**Problem:** Cards had wildly different heights due to varying description lengths, making the grid look uneven.

**Fix:**
- Company description clamped to 2 lines (`-webkit-line-clamp: 2`)
- Rationale clamped to 3 lines (`-webkit-line-clamp: 3`)
- Card uses `flex flex-col`, body uses `flex-1`, footer pinned with `mt-auto`
- Added `border-r` for vertical column separation

**File:** `frontend/components/EquityBetCard.tsx`

---

### 4. Gradient Reveal Progress Bars

**Decision:** Replace block-character EFS bars (█░) with canvas-based gradient bars using the same 100-stop cubic ease-in as the needle.

**Specs:**
- Static gradient fixed to full bar width; filled portion reveals it like a window/mask
- Track: #1A1A1A, pill-shaped (border-radius: height/2)
- Gradient: left transparent → right rgba(232, 68, 10), cubic ease-in
- `fullAt: 0.72` — full brightness at 72% position (matches needle)
- `maxOpacity: 0.85` — slightly brighter than needle for smaller bars
- 8px height for main EFS summary bar
- 6px height for EFS breakdown rows and STS bars

**Files created/modified:**
- `frontend/components/GradientBar.tsx` — new canvas component
- `frontend/components/EquityBetCard.tsx` — replaced EFSBar with GradientBar
- `frontend/components/StartupCard.tsx` — added GradientBar to STS display

---

### Commits (chronological)

1. `fix: ai prompts, plain startup names, column layout by category with context`
2. `feat: equity fit score system — EFS + STS with Yahoo/SEC/Crunchbase data`
3. `revert: equity bets back to 3-col grid, sort by EFS`
4. `fix: equity bet card layout — consistent heights with line clamping`
5. `feat: gradient reveal progress bars — 100-stop cubic ease-in`
