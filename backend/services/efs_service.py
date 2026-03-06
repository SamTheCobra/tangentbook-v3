"""
Equity Fit Score (EFS) and Startup Timing Score (STS) service.
Fetches data from Yahoo Finance, SEC EDGAR, and optionally Crunchbase.
"""

import json
import logging
import math
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import asyncio

import httpx
import yfinance as yf
from sqlalchemy.orm import Session

from models import (
    EquityBet, EquityFitScore, StartupOpportunity, StartupTimingScore,
    Thesis, Effect, THISnapshot,
)

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache: dict[str, tuple[float, any]] = {}

def _get_cached(key: str, max_age_seconds: int) -> any:
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < max_age_seconds:
            return val
    return None

def _set_cache(key: str, val: any):
    _cache[key] = (time.time(), val)


# ── SECTOR ETF MAPPING ──
SECTOR_ETFS = {
    "Technology": "XLK", "Healthcare": "XLV", "Financial Services": "XLF",
    "Energy": "XLE", "Utilities": "XLU", "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP", "Industrials": "XLI", "Basic Materials": "XLB",
    "Real Estate": "XLRE", "Communication Services": "XLC",
}

# ── THESIS KEYWORDS (maps thesis_id to keywords for revenue alignment) ──
THESIS_KEYWORDS = {
    "thesis_usd_debasement": ["gold", "bitcoin", "precious metals", "hard assets", "commodities", "inflation hedge", "monetary", "treasury"],
    "thesis_ai_compute": ["artificial intelligence", "machine learning", "gpu", "data center", "cloud computing", "ai chips", "neural network", "inference"],
    "thesis_energy_grid": ["energy", "grid", "power", "electricity", "utility", "renewable", "nuclear", "solar", "battery", "transmission"],
    "thesis_glp1_revolution": ["glp-1", "obesity", "diabetes", "semaglutide", "tirzepatide", "weight loss", "metabolic", "pharmaceutical"],
    "thesis_reskilling": ["education", "training", "reskilling", "workforce", "career", "learning", "credential", "bootcamp", "upskilling"],
    "thesis_sleep_economy": ["sleep", "rest", "circadian", "mattress", "melatonin", "insomnia", "wellness", "recovery"],
    "thesis_physical_revival": ["vinyl", "analog", "physical media", "record", "film photography", "board game", "print", "tangible"],
    "thesis_luxury_repricing": ["luxury", "premium", "fashion", "designer", "haute couture", "heritage brand", "aspirational"],
    "thesis_chip_wars": ["semiconductor", "chip", "fabrication", "wafer", "TSMC", "foundry", "integrated circuit", "silicon"],
    "thesis_authenticity": ["authentic", "human-made", "artisan", "handcraft", "provenance", "genuine", "ai detection", "creator"],
    "thesis_us_reshoring": ["reshoring", "manufacturing", "domestic production", "factory", "supply chain", "made in usa", "onshoring"],
    "thesis_multipolar": ["geopolitical", "trade", "sanctions", "reserve currency", "defense", "nato", "brics", "deglobalization"],
    "thesis_longevity": ["longevity", "aging", "anti-aging", "lifespan", "biotech", "senior", "geriatric", "healthspan"],
    "thesis_senior_economy": ["senior", "elderly", "aging population", "retirement", "assisted living", "medicare", "65+"],
    "thesis_food_revolution": ["food", "nutrition", "functional food", "ultra-processed", "organic", "clean label", "gut health"],
    "thesis_defense_tech": ["defense", "military", "dual-use", "national security", "weapons", "cybersecurity", "intelligence"],
}

# ── ETFs that should be treated as pure-play single assets ──
SINGLE_ASSET_ETFS = {"GLD", "SLV", "TLT", "IEF", "USO", "UNG", "IBIT", "GBTC", "BITX", "BITO", "MSOS", "WEAT", "DBA", "URA"}


async def fetch_stock_fundamentals(ticker: str) -> dict:
    """Fetch fundamentals via yfinance library."""
    cache_key = f"fundamentals:{ticker}"
    cached = _get_cached(cache_key, 86400)  # 24h cache
    if cached:
        return cached

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _yf_get_info, ticker)
        if not info:
            return {}

        result = {
            "forwardPE": info.get("forwardPE"),
            "trailingPE": info.get("trailingPE"),
            "revenueGrowth": info.get("revenueGrowth"),
            "grossMargins": info.get("grossMargins"),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        }
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {e}")
        return {}


def _yf_get_info(ticker: str) -> dict:
    """Synchronous yfinance info fetch (run in executor)."""
    try:
        t = yf.Ticker(ticker)
        return dict(t.info) if t.info else {}
    except Exception:
        return {}


def _yf_get_history(ticker: str, period: str) -> list:
    """Synchronous yfinance history fetch (run in executor)."""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval="1mo")
        if df.empty:
            return []
        history = []
        closes = df["Close"].tolist()
        dates = df.index.tolist()
        for i in range(len(closes)):
            pct_change = 0.0
            if i > 0 and closes[i-1] and closes[i-1] != 0:
                pct_change = (closes[i] - closes[i-1]) / closes[i-1] * 100
            history.append({
                "date": str(dates[i].date()),
                "close": round(closes[i], 2),
                "pctChange": round(pct_change, 2),
            })
        return history
    except Exception:
        return []


async def fetch_stock_price_history(ticker: str, period: str = "1y") -> list:
    """Fetch monthly price history via yfinance."""
    cache_key = f"price_history:{ticker}:{period}"
    cached = _get_cached(cache_key, 86400)
    if cached:
        return cached

    try:
        loop = asyncio.get_event_loop()
        history = await loop.run_in_executor(None, _yf_get_history, ticker, period)
        if history:
            _set_cache(cache_key, history)
        return history
    except Exception as e:
        logger.error(f"Error fetching price history for {ticker}: {e}")
        return []


async def fetch_sector_median_pe(sector: str) -> float:
    """Fetch sector ETF forward P/E as proxy for sector median."""
    etf = SECTOR_ETFS.get(sector)
    if not etf:
        return 20.0  # default fallback

    cache_key = f"sector_pe:{sector}"
    cached = _get_cached(cache_key, 604800)  # 7 day cache
    if cached:
        return cached

    fundamentals = await fetch_stock_fundamentals(etf)
    pe = fundamentals.get("forwardPE") or fundamentals.get("trailingPE") or 20.0
    if isinstance(pe, str):
        try:
            pe = float(pe)
        except ValueError:
            pe = 20.0

    _set_cache(cache_key, pe)
    return pe


async def fetch_sec_segment_count(ticker: str) -> dict:
    """Fetch segment info from SEC EDGAR company data."""
    cache_key = f"sec_segments:{ticker}"
    cached = _get_cached(cache_key, 7776000)  # 90 day cache
    if cached:
        return cached

    headers = {"User-Agent": "TangentBook research@tangentbook.com", "Accept": "application/json"}

    try:
        # Step 1: Get CIK from ticker
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK="
                f"{ticker}&type=10-K&dateb=&owner=include&count=1&search_text=&action=getcompany&output=atom",
                headers=headers,
            )

        # Simpler approach: use the company tickers JSON
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
            if resp.status_code != 200:
                return {"segmentCount": 3, "segments": []}

            tickers_data = resp.json()
            cik = None
            for entry in tickers_data.values():
                if entry.get("ticker", "").upper() == ticker.upper():
                    cik = str(entry["cik_str"]).zfill(10)
                    break

            if not cik:
                result = {"segmentCount": 3, "segments": []}
                _set_cache(cache_key, result)
                return result

            # Step 2: Fetch company filing data
            resp = await client.get(
                f"https://data.sec.gov/submissions/CIK{cik}.json",
                headers=headers,
            )
            if resp.status_code != 200:
                result = {"segmentCount": 3, "segments": []}
                _set_cache(cache_key, result)
                return result

            filing_data = resp.json()
            sic = filing_data.get("sic", "")
            sic_desc = filing_data.get("sicDescription", "")

            # Parse SIC to estimate segment complexity
            # Companies with single SIC codes tend to be more focused
            # We also look at recent filing count as a proxy for complexity
            recent_filings = filing_data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])

            # Count 10-K filings as a basic indicator
            ten_k_count = sum(1 for f in forms[:20] if f in ("10-K", "10-K/A"))

            # Heuristic: pure-play ETFs = 1, known conglomerates get higher counts
            # For a real implementation, we'd parse the actual 10-K segment disclosures
            # For now, use industry + filing pattern as proxy
            segment_count = _estimate_segments_from_sic(sic, sic_desc, ticker)

            result = {"segmentCount": segment_count, "segments": [sic_desc], "sic": sic}
            _set_cache(cache_key, result)
            return result

    except Exception as e:
        logger.error(f"Error fetching SEC data for {ticker}: {e}")
        return {"segmentCount": 3, "segments": []}


def _estimate_segments_from_sic(sic: str, sic_desc: str, ticker: str) -> int:
    """Estimate number of business segments from SIC code and ticker."""
    # ETFs are single-asset
    if ticker.upper() in SINGLE_ASSET_ETFS:
        return 1

    # Known conglomerates
    CONGLOMERATES = {"AMZN": 7, "GOOG": 5, "GOOGL": 5, "META": 3, "MSFT": 6, "AAPL": 5,
                     "JPM": 6, "BRK.B": 8, "JNJ": 3, "GE": 4, "MMM": 4, "HON": 4,
                     "PEP": 3, "PG": 5, "UNH": 4}
    if ticker.upper() in CONGLOMERATES:
        return CONGLOMERATES[ticker.upper()]

    # Pharma/biotech with SIC 2830-2836 tend to have fewer segments
    if sic and sic.startswith("283"):
        return 2

    # Software SIC 7372 tends to be focused
    if sic and sic.startswith("737"):
        return 2

    # Mining/extraction tends to be focused
    if sic and (sic.startswith("10") or sic.startswith("13")):
        return 2

    # Default: assume moderate diversification
    return 3


def estimate_revenue_alignment(ticker: str, thesis_keywords: list[str], sector: str, industry: str) -> float:
    """Estimate what % of revenue is thesis-relevant using industry and keyword matching."""
    if ticker.upper() in SINGLE_ASSET_ETFS:
        return 100.0

    # Industry/sector matching
    combined_text = f"{sector} {industry}".lower()
    matches = sum(1 for kw in thesis_keywords if kw.lower() in combined_text)
    base_score = min(100.0, (matches / max(len(thesis_keywords), 1)) * 200)

    # Known high-alignment tickers
    HIGH_ALIGNMENT = {
        "NVO": 72, "LLY": 65, "NVDA": 85, "AMD": 75, "AVGO": 60,
        "GLD": 100, "SLV": 100, "IBIT": 100, "MSTR": 90, "COIN": 80,
        "NEE": 80, "CEG": 85, "VST": 75, "FSLR": 80,
        "COUR": 70, "DUOL": 60, "UPWK": 55,
        "SONO": 50, "TPX": 75, "SNBR": 80,
    }
    if ticker.upper() in HIGH_ALIGNMENT:
        return float(HIGH_ALIGNMENT[ticker.upper()])

    # If keyword matching found something, use it
    if base_score > 0:
        return min(100.0, base_score + 20)  # boost for any match

    # Default: moderate alignment assumed (they were selected for the thesis)
    return 45.0


async def calculate_thesis_beta(ticker: str, thesis_id: str, db: Session) -> float:
    """Compute correlation between stock price changes and THI changes."""
    # Get THI snapshots
    snapshots = (
        db.query(THISnapshot)
        .filter(THISnapshot.thesis_id == thesis_id)
        .order_by(THISnapshot.computed_at)
        .all()
    )

    if len(snapshots) < 6:
        return 0.5  # neutral when insufficient data

    # Get stock price history
    price_history = await fetch_stock_price_history(ticker, "1y")
    if len(price_history) < 6:
        return 0.5

    # Align monthly data points
    thi_changes = []
    for i in range(1, len(snapshots)):
        delta = snapshots[i].score - snapshots[i-1].score
        thi_changes.append(delta)

    price_changes = [p["pctChange"] for p in price_history if p.get("pctChange") is not None]

    # Use the shorter of the two lists
    n = min(len(thi_changes), len(price_changes))
    if n < 3:
        return 0.5

    thi_changes = thi_changes[-n:]
    price_changes = price_changes[-n:]

    # Pearson correlation
    correlation = _pearson_correlation(thi_changes, price_changes)
    if correlation is None:
        return 0.5

    # Normalize -1..1 to 0..100
    return round((correlation + 1) / 2 * 100, 1)


def _pearson_correlation(x: list[float], y: list[float]) -> Optional[float]:
    """Calculate Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return None

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    denom = math.sqrt(var_x * var_y)
    if denom == 0:
        return 0.0

    return cov / denom


async def calculate_momentum_alignment(ticker: str, thesis_id: str, db: Session) -> dict:
    """Compare 90-day direction of stock vs thesis."""
    # Get THI 90 days ago
    now = datetime.utcnow()
    target_date = now - timedelta(days=90)

    snapshots = (
        db.query(THISnapshot)
        .filter(THISnapshot.thesis_id == thesis_id)
        .order_by(THISnapshot.computed_at.desc())
        .all()
    )

    thi_today = snapshots[0].score if snapshots else 50.0
    thi_90d = thi_today  # default
    for s in snapshots:
        if s.computed_at <= target_date:
            thi_90d = s.score
            break

    thi_delta = thi_today - thi_90d

    # Get stock return 90d
    price_history = await fetch_stock_price_history(ticker, "6mo")
    stock_return = 0.0
    if len(price_history) >= 2:
        recent = price_history[-1]["close"]
        # Find price ~90 days ago (roughly 3 months back)
        idx = max(0, len(price_history) - 4)  # monthly data, 3 months back
        older = price_history[idx]["close"]
        if older > 0:
            stock_return = (recent - older) / older * 100

    # Determine alignment
    stock_pos = stock_return > 2
    stock_neg = stock_return < -2
    thi_pos = thi_delta > 3
    thi_neg = thi_delta < -3

    if stock_pos and thi_pos:
        if stock_return > abs(thi_delta) * 4:
            score, label = 60, "OVERHEATED"
        else:
            score, label = 90, "ALIGNED"
    elif stock_pos and thi_neg:
        score, label = 20, "DIVERGING"
    elif stock_pos and not thi_pos and not thi_neg:
        score, label = 55, "DECOUPLED"
    elif stock_neg and thi_neg:
        score, label = 40, "ALIGNED_DOWN"
    elif stock_neg and thi_pos:
        score, label = 70, "LAGGING"
    elif not stock_pos and not stock_neg:
        score, label = 50, "NEUTRAL"
    else:
        score, label = 50, "NEUTRAL"

    return {
        "score": score,
        "direction": label,
        "stockReturn90d": round(stock_return, 2),
        "thiDelta90d": round(thi_delta, 2),
    }


def _compute_valuation_score(forward_pe: Optional[float], sector_pe: float) -> float:
    """Score valuation buffer: lower premium = higher score."""
    if forward_pe is None or forward_pe <= 0:
        return 40.0  # unprofitable or N/A

    if sector_pe <= 0:
        sector_pe = 20.0

    premium = forward_pe / sector_pe

    if premium <= 1.0:
        return 100.0
    elif premium <= 1.25:
        return 75.0
    elif premium <= 1.5:
        return 50.0
    elif premium <= 2.0:
        return 25.0
    else:
        return 10.0


def _compute_purity_score(segment_count: int) -> float:
    """Score signal purity based on business segment count."""
    if segment_count <= 1:
        return 100.0
    elif segment_count <= 3:
        return 75.0
    elif segment_count <= 6:
        return 50.0
    else:
        return 25.0


async def calculate_efs(
    bet: EquityBet,
    thesis_id: str,
    thesis_keywords: list[str],
    db: Session,
) -> EquityFitScore:
    """Orchestrate all data fetches and compute final EFS."""
    ticker = bet.ticker
    sources_used = []

    # 1. Fundamentals from Yahoo Finance
    fundamentals = await fetch_stock_fundamentals(ticker)
    if fundamentals:
        sources_used.append("yahoo_finance")

    sector = fundamentals.get("sector", "")
    industry = fundamentals.get("industry", "")
    forward_pe = fundamentals.get("forwardPE")
    if isinstance(forward_pe, str):
        try:
            forward_pe = float(forward_pe)
        except ValueError:
            forward_pe = None

    # 2. Sector median P/E
    sector_pe = await fetch_sector_median_pe(sector) if sector else 20.0
    if sector_pe != 20.0:
        sources_used.append("sector_etf")

    # 3. SEC segment data
    sec_data = await fetch_sec_segment_count(ticker)
    segment_count = sec_data.get("segmentCount", 3)
    if sec_data.get("sic"):
        sources_used.append("sec_edgar")

    # 4. Revenue alignment
    revenue_pct = estimate_revenue_alignment(ticker, thesis_keywords, sector, industry)

    # 5. Thesis beta
    beta_raw = await calculate_thesis_beta(ticker, thesis_id, db)
    sources_used.append("thi_snapshots")

    # 6. Momentum alignment
    momentum = await calculate_momentum_alignment(ticker, thesis_id, db)
    sources_used.append("price_history")

    # Compute component scores
    revenue_score = min(100.0, revenue_pct * 1.4)
    beta_score = beta_raw  # already 0-100
    momentum_score = float(momentum["score"])
    valuation_score = _compute_valuation_score(forward_pe, sector_pe)
    purity_score = _compute_purity_score(segment_count)

    # Weighted composite: EFS
    efs = (
        revenue_score * 0.30 +
        beta_score * 0.25 +
        momentum_score * 0.20 +
        valuation_score * 0.15 +
        purity_score * 0.10
    )
    efs = round(efs, 1)

    # Upsert
    existing = db.query(EquityFitScore).filter(EquityFitScore.equity_bet_id == bet.id).first()
    if existing:
        score_obj = existing
    else:
        score_obj = EquityFitScore(equity_bet_id=bet.id)
        db.add(score_obj)

    score_obj.thesis_id = bet.thesis_id
    score_obj.effect_id = bet.effect_id
    score_obj.revenue_alignment_score = round(revenue_score, 1)
    score_obj.thesis_beta_score = round(beta_score, 1)
    score_obj.momentum_alignment_score = round(momentum_score, 1)
    score_obj.valuation_buffer_score = round(valuation_score, 1)
    score_obj.signal_purity_score = round(purity_score, 1)
    score_obj.efs_score = efs
    score_obj.revenue_alignment_pct = round(revenue_pct, 1)
    score_obj.forward_pe = round(forward_pe, 1) if forward_pe else None
    score_obj.sector_median_pe = round(sector_pe, 1)
    score_obj.segment_count = segment_count
    score_obj.thesis_beta_raw = round((beta_raw / 50 - 1), 3)  # convert back to -1..1
    score_obj.momentum_direction = momentum["direction"]
    score_obj.stock_return_90d = momentum["stockReturn90d"]
    score_obj.thi_delta_90d = momentum["thiDelta90d"]
    score_obj.last_updated = datetime.utcnow()
    score_obj.data_sources_used = sources_used

    db.commit()
    db.refresh(score_obj)
    return score_obj


async def calculate_sts(opp: StartupOpportunity, db: Session) -> StartupTimingScore:
    """Calculate Startup Timing Score."""
    # Get parent thesis or effect THI
    thesis = None
    if opp.thesis_id:
        thesis = db.query(Thesis).filter(Thesis.id == opp.thesis_id).first()
    elif opp.effect_id:
        effect = db.query(Effect).filter(Effect.id == opp.effect_id).first()
        if effect:
            thesis = db.query(Thesis).filter(Thesis.id == effect.thesis_id).first()

    thi_score = thesis.thi_score if thesis else 50.0

    # THI alignment = current THI (already 0-100)
    thi_alignment = thi_score

    # THI velocity: look at 30-day delta
    thi_velocity = 50.0
    if thesis:
        snapshots = (
            db.query(THISnapshot)
            .filter(THISnapshot.thesis_id == thesis.id)
            .order_by(THISnapshot.computed_at.desc())
            .all()
        )
        if len(snapshots) >= 2:
            target = datetime.utcnow() - timedelta(days=30)
            old_snap = None
            for s in snapshots:
                if s.computed_at <= target:
                    old_snap = s
                    break
            if old_snap:
                delta = snapshots[0].score - old_snap.score
                if delta > 5:
                    thi_velocity = 90.0
                elif delta > 0:
                    thi_velocity = 70.0
                elif delta == 0:
                    thi_velocity = 50.0
                elif delta > -10:
                    thi_velocity = 30.0
                else:
                    thi_velocity = 10.0

    # Competition density: use Crunchbase if available, otherwise estimate from timing
    competition_score = _estimate_competition_from_timing(opp.timing)

    # STS calculation
    sts = (
        thi_alignment * 0.40 +
        thi_velocity * 0.30 +
        (100 - competition_score) * 0.30
    )
    sts = round(sts, 1)

    # Timing label
    if competition_score < 30 and thi_alignment < 40:
        timing_label = "TOO_EARLY"
    elif competition_score > 70:
        timing_label = "CROWDING"
    else:
        timing_label = "RIGHT_TIMING"

    # Upsert
    existing = db.query(StartupTimingScore).filter(
        StartupTimingScore.startup_opp_id == opp.id
    ).first()
    if existing:
        score_obj = existing
    else:
        score_obj = StartupTimingScore(startup_opp_id=opp.id)
        db.add(score_obj)

    score_obj.thi_alignment_score = round(thi_alignment, 1)
    score_obj.thi_velocity_score = round(thi_velocity, 1)
    score_obj.competition_density_score = round(competition_score, 1)
    score_obj.sts_score = sts
    score_obj.timing_label = timing_label
    score_obj.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(score_obj)
    return score_obj


def _estimate_competition_from_timing(timing: str) -> float:
    """Estimate competition density from existing timing label as fallback."""
    mapping = {"TOO_EARLY": 15.0, "RIGHT_TIMING": 45.0, "CROWDING": 80.0}
    return mapping.get(timing, 45.0)


def efs_to_dict(efs: EquityFitScore) -> dict:
    return {
        "id": efs.id,
        "equityBetId": efs.equity_bet_id,
        "thesisId": efs.thesis_id,
        "effectId": efs.effect_id,
        "revenueAlignmentScore": efs.revenue_alignment_score,
        "thesisBetaScore": efs.thesis_beta_score,
        "momentumAlignmentScore": efs.momentum_alignment_score,
        "valuationBufferScore": efs.valuation_buffer_score,
        "signalPurityScore": efs.signal_purity_score,
        "efsScore": efs.efs_score,
        "revenueAlignmentPct": efs.revenue_alignment_pct,
        "forwardPE": efs.forward_pe,
        "sectorMedianPE": efs.sector_median_pe,
        "segmentCount": efs.segment_count,
        "thesisBetaRaw": efs.thesis_beta_raw,
        "momentumDirection": efs.momentum_direction,
        "stockReturn90d": efs.stock_return_90d,
        "thiDelta90d": efs.thi_delta_90d,
        "lastUpdated": efs.last_updated.isoformat() if efs.last_updated else None,
        "dataSourcesUsed": efs.data_sources_used or [],
    }


def sts_to_dict(sts: StartupTimingScore) -> dict:
    return {
        "id": sts.id,
        "startupOppId": sts.startup_opp_id,
        "thiAlignmentScore": sts.thi_alignment_score,
        "thiVelocityScore": sts.thi_velocity_score,
        "competitionDensityScore": sts.competition_density_score,
        "stsScore": sts.sts_score,
        "competitorCount": sts.competitor_count,
        "fundedStartupsInCategory": sts.funded_startups_in_category,
        "totalFundingInCategory": sts.total_funding_in_category,
        "timingLabel": sts.timing_label,
        "lastUpdated": sts.last_updated.isoformat() if sts.last_updated else None,
    }
