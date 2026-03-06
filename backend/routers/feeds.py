from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import DataFeed, FeedCache, Thesis, MacroHeader, THISnapshot
from services.feed_refresh import refresh_thesis_feeds, refresh_macro_header
from services.scoring_engine import clamp

router = APIRouter(prefix="/api", tags=["feeds"])


def feed_to_dict(f: DataFeed) -> dict:
    return {
        "id": f.id,
        "name": f.name,
        "description": f.description,
        "source": f.source,
        "sourceType": f.source_type,
        "seriesId": f.series_id,
        "keyword": f.keyword,
        "ticker": f.ticker,
        "updateFrequency": f.update_frequency,
        "status": f.status,
        "lastFetched": f.last_fetched.isoformat() if f.last_fetched else None,
        "rawValue": f.raw_value,
        "normalizedScore": f.normalized_score,
        "confirmingDirection": f.confirming_direction,
        "weight": f.weight,
    }


@router.get("/theses/{thesis_id}/feeds")
def list_feeds(thesis_id: str, db: Session = Depends(get_db)):
    feeds = db.query(DataFeed).filter(DataFeed.thesis_id == thesis_id).all()
    return [feed_to_dict(f) for f in feeds]


@router.post("/theses/{thesis_id}/feeds/refresh")
async def refresh_feeds(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    await refresh_thesis_feeds(thesis_id, db)
    db.refresh(thesis)
    return {
        "status": "refreshed",
        "thesisId": thesis_id,
        "thiScore": thesis.thi_score,
    }


@router.post("/feeds/refresh-all")
async def refresh_all_feeds_endpoint(db: Session = Depends(get_db)):
    """Refresh all thesis feeds and macro header."""
    from services.feed_refresh import refresh_all_theses
    await refresh_all_theses(db)
    theses = db.query(Thesis).all()
    return {
        "status": "refreshed",
        "theses": [{"id": t.id, "thiScore": t.thi_score} for t in theses],
    }


@router.post("/macro/refresh")
async def refresh_macro(db: Session = Depends(get_db)):
    await refresh_macro_header(db)
    header = db.query(MacroHeader).order_by(MacroHeader.last_updated.desc()).first()
    return {
        "regime": header.regime if header else "NEUTRAL",
        "ffr": header.ffr if header else None,
        "tenYearTwoYearSpread": header.ten_year_two_year_spread if header else None,
        "vix": header.vix if header else None,
    }


@router.get("/feeds/{feed_id}/history")
def feed_history(feed_id: str, db: Session = Depends(get_db)):
    cached = db.query(FeedCache).filter(
        FeedCache.feed_id == feed_id
    ).order_by(FeedCache.fetched_at).all()
    return [
        {
            "fetchedAt": c.fetched_at.isoformat(),
            "rawValue": c.raw_value,
            "normalizedScore": c.normalized_score,
        }
        for c in cached
    ]


@router.get("/macro/header")
async def macro_header(db: Session = Depends(get_db)):
    header = db.query(MacroHeader).order_by(MacroHeader.last_updated.desc()).first()

    # If no header exists or data is missing, try fetching fresh
    if not header or header.ffr is None:
        try:
            await refresh_macro_header(db)
            header = db.query(MacroHeader).order_by(MacroHeader.last_updated.desc()).first()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Macro header fetch failed: {e}")

    if not header:
        return {
            "regime": "NEUTRAL",
            "ffr": None,
            "tenYearTwoYearSpread": None,
            "vix": None,
            "lastUpdated": None,
        }
    return {
        "regime": header.regime,
        "ffr": header.ffr,
        "tenYearTwoYearSpread": header.ten_year_two_year_spread,
        "vix": header.vix,
        "lastUpdated": header.last_updated.isoformat() if header.last_updated else None,
    }


# Source quality mapping
SOURCE_QUALITY = {
    "FRED": 100,
    "ALPHA_VANTAGE": 85,
    "GTRENDS": 65,
    "EDGAR": 90,
    "ESTIMATED": 20,
}

# Dimension weight configs
EVIDENCE_DIMENSIONS = {
    "flow": {"weight": 0.35, "description": "Measures capital movement into thesis-confirming assets — money supply growth, debt expansion, currency weakness."},
    "structural": {"weight": 0.30, "description": "Measures lasting systemic changes that don't reverse quickly — inflation regimes, real interest rates, policy shifts."},
    "adoption": {"weight": 0.20, "description": "Measures behavioral change — are people actually acting on this theme? Search trends, product usage, consumer behavior signals."},
    "policy": {"weight": 0.15, "description": "Measures regulatory and government signals that accelerate or block the thesis — legislation, Fed policy, executive actions."},
}


@router.get("/theses/{thesis_id}/scoring-breakdown")
def scoring_breakdown(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    feeds = db.query(DataFeed).filter(DataFeed.thesis_id == thesis_id).all()

    # ── EVIDENCE BREAKDOWN ────────────────────────────────────────────────
    dimensions: dict[str, dict] = {}
    # Build a map of feed_id -> historical cache entries for comparisons
    all_cache = db.query(FeedCache).filter(
        FeedCache.feed_id.in_([f.id for f in feeds])
    ).order_by(FeedCache.fetched_at).all()
    cache_by_feed: dict[str, list] = {}
    for c in all_cache:
        cache_by_feed.setdefault(c.feed_id, []).append(c)

    # Unit mapping for known FRED series
    SERIES_UNITS = {
        "M2SL": ("$T", 1e-3, "trillion"),
        "WALCL": ("$T", 1e-3, "trillion"),
        "BOGMBASE": ("$T", 1e-3, "trillion"),
        "TCMDO": ("$T", 1e-3, "trillion"),
        "GFDEBTN": ("$T", 1e-3, "trillion"),
        "DGS10": ("%", 1, "percent"),
        "DGS2": ("%", 1, "percent"),
        "DFEDTARU": ("%", 1, "percent"),
        "FEDFUNDS": ("%", 1, "percent"),
        "T10Y2Y": ("bps", 100, "basis points"),
        "T10YIE": ("%", 1, "percent"),
        "CPIAUCSL": ("idx", 1, "index"),
        "CPILFESL": ("idx", 1, "index"),
        "PCEPI": ("idx", 1, "index"),
        "PCEPILFE": ("idx", 1, "index"),
        "UNRATE": ("%", 1, "percent"),
        "PAYEMS": ("K", 1, "thousand"),
        "ICSA": ("K", 1, "thousand"),
        "UMCSENT": ("idx", 1, "index"),
        "VIXCLS": ("idx", 1, "index"),
        "DTWEXBGS": ("idx", 1, "index"),
        "MORTGAGE30US": ("%", 1, "percent"),
        "HOUST": ("K", 1, "thousand"),
        "PERMIT": ("K", 1, "thousand"),
        "INDPRO": ("idx", 1, "index"),
        "RSAFS": ("$B", 1e-3, "billion"),
        "RETAILSMNSA": ("$B", 1e-3, "billion"),
        "TOTALSA": ("M", 1, "million"),
        "JTSJOL": ("K", 1, "thousand"),
        "DCOILWTICO": ("$/bbl", 1, "per barrel"),
        "GASREGW": ("$/gal", 1, "per gallon"),
        "DEXUSEU": ("$/€", 1, "per euro"),
        "DEXJPUS": ("¥/$", 1, "yen per dollar"),
    }

    def format_value(f_obj):
        """Format raw value with appropriate units."""
        if f_obj.raw_value is None:
            return None
        sid = f_obj.series_id or ""
        if sid in SERIES_UNITS:
            unit, scale, _ = SERIES_UNITS[sid]
            if scale != 1:
                return f"{f_obj.raw_value * scale:.2f}{unit}"
            if unit == "%":
                return f"{f_obj.raw_value:.2f}%"
            if unit == "bps":
                return f"{f_obj.raw_value * 100:.0f}bps"
            return f"{f_obj.raw_value:.2f} {unit}"
        if f_obj.source == "GTRENDS":
            return f"{f_obj.raw_value:.0f}/100"
        return f"{f_obj.raw_value:.2f}"

    def get_context_sentence(f_obj, thesis_obj):
        """Generate a plain-English context sentence for this feed relative to the thesis."""
        if f_obj.raw_value is None:
            return "No data available yet."
        direction = f_obj.confirming_direction or "higher"
        score = f_obj.normalized_score
        if score is None:
            return "Awaiting normalization."
        if score >= 70:
            strength = "strongly confirming"
        elif score >= 55:
            strength = "mildly confirming"
        elif score >= 45:
            strength = "neutral for"
        elif score >= 30:
            strength = "mildly refuting"
        else:
            strength = "strongly refuting"
        dir_explanation = f"({direction} = confirming)" if direction == "higher" else f"({direction} = confirming)"
        return f"Currently {strength} this thesis. {dir_explanation}"

    for dim_key, dim_cfg in EVIDENCE_DIMENSIONS.items():
        dim_feeds = [f for f in feeds if f.source_type == dim_key]
        feed_list = []
        scores = []
        latest_update = None
        for f in dim_feeds:
            score = f.normalized_score
            if score is not None:
                scores.append(score)
            lu = f.last_fetched
            if lu and (latest_update is None or lu > latest_update):
                latest_update = lu

            # Historical comparison from cache
            history = cache_by_feed.get(f.id, [])
            one_year_ago_val = None
            five_year_avg = None
            if history:
                one_yr_target = now - timedelta(days=365)
                candidates_1yr = [c for c in history if c.raw_value is not None]
                if candidates_1yr:
                    closest_1yr = min(candidates_1yr, key=lambda c: abs((c.fetched_at - one_yr_target).total_seconds()))
                    if abs((closest_1yr.fetched_at - one_yr_target).total_seconds()) < 90 * 86400:
                        one_year_ago_val = closest_1yr.raw_value
                five_yr_target = now - timedelta(days=5*365)
                five_yr_vals = [c.raw_value for c in candidates_1yr if c.fetched_at >= five_yr_target and c.raw_value is not None] if candidates_1yr else []
                if five_yr_vals:
                    five_year_avg = sum(five_yr_vals) / len(five_yr_vals)

            pct_vs_1yr = None
            if one_year_ago_val and f.raw_value is not None and one_year_ago_val != 0:
                pct_vs_1yr = round(((f.raw_value - one_year_ago_val) / abs(one_year_ago_val)) * 100, 1)
            pct_vs_5yr = None
            if five_year_avg and f.raw_value is not None and five_year_avg != 0:
                pct_vs_5yr = round(((f.raw_value - five_year_avg) / abs(five_year_avg)) * 100, 1)

            feed_list.append({
                "name": f.name.replace("Fred ", "").replace("Gtrends ", ""),
                "value": f.raw_value,
                "formattedValue": format_value(f),
                "normalizedScore": round(score) if score is not None else None,
                "status": f.status,
                "lastUpdated": lu.isoformat() if lu else None,
                "seriesId": f.series_id,
                "keyword": f.keyword,
                "source": f.source,
                "confirmingDirection": f.confirming_direction,
                "pctVs1yr": pct_vs_1yr,
                "pctVs5yrAvg": pct_vs_5yr,
                "context": get_context_sentence(f, thesis),
            })
        dim_score = round(sum(scores) / len(scores), 1) if scores else None
        dimensions[dim_key] = {
            "weight": dim_cfg["weight"],
            "description": dim_cfg["description"],
            "score": dim_score,
            "feeds": feed_list,
            "lastUpdated": latest_update.isoformat() if latest_update else None,
        }

    # ── MOMENTUM BREAKDOWN ────────────────────────────────────────────────
    now = datetime.utcnow()
    snapshots = (
        db.query(THISnapshot)
        .filter(THISnapshot.thesis_id == thesis_id)
        .order_by(THISnapshot.computed_at.desc())
        .all()
    )

    def find_snapshot_near(target_dt):
        best = None
        best_diff = None
        for s in snapshots:
            diff = abs((s.computed_at - target_dt).total_seconds())
            if best_diff is None or diff < best_diff:
                best = s
                best_diff = diff
        return best

    current_evidence = thesis.evidence_score
    snap_30d = find_snapshot_near(now - timedelta(days=30))
    snap_90d = find_snapshot_near(now - timedelta(days=90))
    snap_1yr = find_snapshot_near(now - timedelta(days=365))

    def momentum_entry(snap, label_days):
        if not snap or snap.evidence_score is None:
            return {"delta": None, "score": 50.0}
        delta = round(current_evidence - snap.evidence_score, 1)
        score = clamp(round(50 + delta * 2.5, 1))
        return {"delta": delta, "score": score}

    momentum_30d = momentum_entry(snap_30d, 30)
    momentum_90d = momentum_entry(snap_90d, 90)
    momentum_1yr = momentum_entry(snap_1yr, 365)

    # ── DATA QUALITY BREAKDOWN ────────────────────────────────────────────
    live_feeds = [f for f in feeds if f.status == "live"]
    stale_feeds = [f for f in feeds if f.status == "stale"]
    degraded_feeds = [f for f in feeds if f.status == "degraded"]
    offline_feeds = [f for f in feeds if f.status == "offline"]
    total = len(feeds) or 1

    # Agreement
    scored_feeds = [f for f in feeds if f.normalized_score is not None]
    confirming_count = sum(1 for f in scored_feeds if f.normalized_score >= 50)
    pct_confirming = round((confirming_count / len(scored_feeds)) * 100) if scored_feeds else None
    if len(scored_feeds) >= 2:
        mean = sum(f.normalized_score for f in scored_feeds) / len(scored_feeds)
        variance = sum((f.normalized_score - mean) ** 2 for f in scored_feeds) / len(scored_feeds)
        std = variance ** 0.5
        agreement_score = clamp(round(100 - std * 2))
    else:
        agreement_score = 75.0

    # Freshness
    ages_days = []
    for f in feeds:
        if f.last_fetched:
            age = (now - f.last_fetched).total_seconds() / 86400
            ages_days.append(age)
    avg_age = round(sum(ages_days) / len(ages_days), 1) if ages_days else None
    freshness_score = clamp(round((len(live_feeds) / total) * 100))

    # Source quality
    sq_values = [SOURCE_QUALITY.get(f.source, 50) for f in feeds]
    weighted_sq = round(sum(sq_values) / len(sq_values)) if sq_values else 50
    sq_score = float(weighted_sq)

    return {
        "evidence": {
            "score": thesis.evidence_score,
            "flow": dimensions.get("flow"),
            "structural": dimensions.get("structural"),
            "adoption": dimensions.get("adoption"),
            "policy": dimensions.get("policy"),
        },
        "momentum": {
            "score": thesis.momentum_score,
            "thirtyDay": momentum_30d,
            "ninetyDay": momentum_90d,
            "oneYear": momentum_1yr,
        },
        "dataQuality": {
            "score": thesis.conviction_data_score,
            "agreement": {
                "pctConfirming": pct_confirming,
                "score": agreement_score,
            },
            "freshness": {
                "avgAgeDays": avg_age,
                "live": len(live_feeds),
                "stale": len(stale_feeds),
                "degraded": len(degraded_feeds),
                "offline": len(offline_feeds),
                "score": freshness_score,
            },
            "sourceQuality": {
                "weightedAvg": weighted_sq,
                "score": sq_score,
            },
        },
    }
