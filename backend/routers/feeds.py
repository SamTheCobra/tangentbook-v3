from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import DataFeed, FeedCache, Thesis, Effect, MacroHeader, THISnapshot
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
    feeds = db.query(DataFeed).filter(
        DataFeed.thesis_id == thesis_id,
        DataFeed.effect_id.is_(None),
    ).all()
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


@router.post("/feeds/{feed_id}/refresh")
async def refresh_single_feed(feed_id: str, db: Session = Depends(get_db)):
    """Refresh a single feed."""
    feed = db.query(DataFeed).filter(DataFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    from services.feed_refresh import _fetch_single_feed
    from services.scoring_engine import normalize_percentile
    result = await _fetch_single_feed(feed, db)
    if result and result.get("observations"):
        score = normalize_percentile(result["value"], result["observations"])
        if feed.confirming_direction == "lower":
            score = 100.0 - score
        feed.normalized_score = score
        db.commit()
    return feed_to_dict(feed)


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

    feeds = db.query(DataFeed).filter(
        DataFeed.thesis_id == thesis_id,
        DataFeed.effect_id.is_(None),
    ).all()
    now = datetime.utcnow()

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
            return {
                "delta": None,
                "score": 50.0,
                "prevEvidence": None,
                "prevDate": None,
            }
        delta = round(current_evidence - snap.evidence_score, 1)
        score = clamp(round(50 + delta * 2.5, 1))
        return {
            "delta": delta,
            "score": score,
            "prevEvidence": round(snap.evidence_score, 1),
            "prevDate": snap.computed_at.isoformat() if snap.computed_at else None,
        }

    momentum_30d = momentum_entry(snap_30d, 30)
    momentum_90d = momentum_entry(snap_90d, 90)
    momentum_1yr = momentum_entry(snap_1yr, 365)

    # Compute actual momentum score
    m_score = round(
        momentum_30d["score"] * 0.50 +
        momentum_90d["score"] * 0.35 +
        momentum_1yr["score"] * 0.15, 1
    )

    # First snapshot date for "momentum will unlock" message
    first_snapshot = snapshots[-1] if snapshots else None
    first_snapshot_date = first_snapshot.computed_at.isoformat() if first_snapshot else None
    has_enough_history = len(snapshots) >= 2

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

    # Compute actual data quality score
    dq_score = round(agreement_score * 0.50 + freshness_score * 0.30 + sq_score * 0.20, 1)

    # Dimension contribution calculations
    ev_score = thesis.evidence_score
    dim_contributions = {}
    for dim_key in ["flow", "structural", "adoption", "policy"]:
        d = dimensions.get(dim_key, {})
        w = d.get("weight", 0)
        s = d.get("score")
        contrib = round(s * w, 1) if s is not None else 0
        dim_contributions[dim_key] = contrib

    # Evidence formula string
    ev_formula_parts = []
    for dim_key in ["flow", "structural", "adoption", "policy"]:
        d = dimensions.get(dim_key, {})
        s = d.get("score")
        w = d.get("weight", 0)
        s_str = str(round(s)) if s is not None else "0"
        ev_formula_parts.append(f"({s_str}×{w})")
    ev_formula = " + ".join(ev_formula_parts)

    # THI formula
    thi_score = thesis.thi_score
    ev_contrib = round(ev_score * 0.50, 1)
    m_contrib = round(thesis.momentum_score * 0.30, 1)
    dq_contrib = round(thesis.conviction_data_score * 0.20, 1)

    return _build_breakdown_response(
        thi_score, ev_score, thesis.momentum_score, thesis.conviction_data_score,
        ev_contrib, m_contrib, dq_contrib, ev_formula, dimensions, dim_contributions,
        has_enough_history, first_snapshot_date, current_evidence,
        momentum_30d, momentum_90d, momentum_1yr,
        total, scored_feeds, agreement_score, pct_confirming,
        avg_age, live_feeds, stale_feeds, degraded_feeds, offline_feeds,
        freshness_score, weighted_sq, sq_score,
    )


@router.get("/effects/{effect_id}/scoring-breakdown")
def effect_scoring_breakdown(effect_id: str, db: Session = Depends(get_db)):
    """Scoring breakdown for an effect using its own feeds."""
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")

    feeds = db.query(DataFeed).filter(DataFeed.effect_id == effect_id).all()

    # If effect has no feeds, return a minimal breakdown with defaults
    if not feeds:
        return _empty_breakdown(effect.thi_score)

    now = datetime.utcnow()

    # Reuse same logic as thesis breakdown
    all_cache = db.query(FeedCache).filter(
        FeedCache.feed_id.in_([f.id for f in feeds])
    ).order_by(FeedCache.fetched_at).all()
    cache_by_feed: dict[str, list] = {}
    for c in all_cache:
        cache_by_feed.setdefault(c.feed_id, []).append(c)

    dimensions: dict[str, dict] = {}
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
            feed_list.append({
                "name": f.name.replace("Fred ", "").replace("Gtrends ", ""),
                "value": f.raw_value,
                "formattedValue": _format_feed_value(f),
                "normalizedScore": round(score) if score is not None else None,
                "status": f.status,
                "lastUpdated": lu.isoformat() if lu else None,
                "seriesId": f.series_id,
                "keyword": f.keyword,
                "source": f.source,
                "confirmingDirection": f.confirming_direction,
                "pctVs1yr": None,
                "pctVs5yrAvg": None,
                "context": _get_feed_context(f),
            })
        dim_score = round(sum(scores) / len(scores), 1) if scores else None
        dimensions[dim_key] = {
            "weight": dim_cfg["weight"],
            "description": dim_cfg["description"],
            "score": dim_score,
            "feeds": feed_list,
            "lastUpdated": latest_update.isoformat() if latest_update else None,
        }

    # Evidence
    all_dim_scores = []
    for dk in ["flow", "structural", "adoption", "policy"]:
        d = dimensions.get(dk, {})
        if d.get("score") is not None:
            all_dim_scores.append((d["score"], d["weight"]))
    if all_dim_scores:
        ev_score = round(sum(s * w for s, w in all_dim_scores) / sum(w for _, w in all_dim_scores) if all_dim_scores else 50, 1)
    else:
        ev_score = 50.0

    # Momentum: effects don't have snapshots yet, default to 50
    m_score = 50.0

    # Data quality
    live_feeds_list = [f for f in feeds if f.status == "live"]
    stale_feeds_list = [f for f in feeds if f.status == "stale"]
    degraded_feeds_list = [f for f in feeds if f.status == "degraded"]
    offline_feeds_list = [f for f in feeds if f.status == "offline"]
    total = len(feeds) or 1
    scored_feeds_list = [f for f in feeds if f.normalized_score is not None]
    confirming = sum(1 for f in scored_feeds_list if f.normalized_score >= 50)
    pct_conf = round((confirming / len(scored_feeds_list)) * 100) if scored_feeds_list else None
    agr_score = 75.0
    if len(scored_feeds_list) >= 2:
        mean = sum(f.normalized_score for f in scored_feeds_list) / len(scored_feeds_list)
        var = sum((f.normalized_score - mean) ** 2 for f in scored_feeds_list) / len(scored_feeds_list)
        agr_score = clamp(round(100 - var ** 0.5 * 2))
    ages = [(now - f.last_fetched).total_seconds() / 86400 for f in feeds if f.last_fetched]
    avg_age = round(sum(ages) / len(ages), 1) if ages else None
    fresh_score = clamp(round((len(live_feeds_list) / total) * 100))
    sq_vals = [SOURCE_QUALITY.get(f.source, 50) for f in feeds]
    wsq = round(sum(sq_vals) / len(sq_vals)) if sq_vals else 50
    dq_score = round(agr_score * 0.50 + fresh_score * 0.30 + float(wsq) * 0.20, 1)

    # Compute THI
    thi = round(ev_score * 0.50 + m_score * 0.30 + dq_score * 0.20, 1)

    ev_contrib = round(ev_score * 0.50, 1)
    m_contrib = round(m_score * 0.30, 1)
    dq_contrib = round(dq_score * 0.20, 1)

    dim_contribs = {}
    ev_parts = []
    for dk in ["flow", "structural", "adoption", "policy"]:
        d = dimensions.get(dk, {})
        s = d.get("score")
        w = d.get("weight", 0)
        dim_contribs[dk] = round(s * w, 1) if s is not None else 0
        ev_parts.append(f"({round(s) if s is not None else 0}×{w})")

    return _build_breakdown_response(
        thi, ev_score, m_score, dq_score,
        ev_contrib, m_contrib, dq_contrib,
        " + ".join(ev_parts), dimensions, dim_contribs,
        False, None, ev_score,
        {"delta": None, "score": 50.0, "prevEvidence": None, "prevDate": None},
        {"delta": None, "score": 50.0, "prevEvidence": None, "prevDate": None},
        {"delta": None, "score": 50.0, "prevEvidence": None, "prevDate": None},
        total, scored_feeds_list, agr_score, pct_conf,
        avg_age, live_feeds_list, stale_feeds_list, degraded_feeds_list, offline_feeds_list,
        fresh_score, wsq, float(wsq),
    )


@router.post("/effects/{effect_id}/feeds/refresh")
async def refresh_effect_feeds(effect_id: str, db: Session = Depends(get_db)):
    """Refresh all feeds for a single effect and recompute its THI."""
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")

    feeds = db.query(DataFeed).filter(DataFeed.effect_id == effect_id).all()
    if not feeds:
        return {"status": "no_feeds", "effectId": effect_id}

    from services.feed_refresh import _fetch_single_feed
    from services.scoring_engine import normalize_percentile, clamp, score_to_direction, compute_trend

    for feed in feeds:
        result = await _fetch_single_feed(feed, db)
        if result and result.get("observations"):
            score = normalize_percentile(result["value"], result["observations"])
            if feed.confirming_direction == "lower":
                score = 100.0 - score
            feed.normalized_score = score
            db.commit()

    # Recompute effect THI from its own feeds
    scored = [f for f in feeds if f.normalized_score is not None]
    if scored:
        ev = round(sum(f.normalized_score for f in scored) / len(scored), 1)
    else:
        ev = 50.0
    old = effect.thi_score
    thi = clamp(round(ev * 0.50 + 50 * 0.30 + 50 * 0.20, 1))
    effect.thi_score = thi
    effect.thi_direction = score_to_direction(thi)
    effect.thi_trend = compute_trend(thi, old)
    db.commit()

    return {"status": "refreshed", "effectId": effect_id, "thiScore": thi}


def _format_feed_value(f_obj):
    if f_obj.raw_value is None:
        return None
    if f_obj.source == "GTRENDS":
        return f"{f_obj.raw_value:.0f}/100"
    return f"{f_obj.raw_value:.2f}"


def _get_feed_context(f_obj):
    if f_obj.raw_value is None:
        return "No data available yet."
    score = f_obj.normalized_score
    if score is None:
        return "Awaiting normalization."
    direction = f_obj.confirming_direction or "higher"
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
    return f"Currently {strength} this thesis. ({direction} = confirming)"


def _empty_breakdown(thi_score):
    """Return a minimal breakdown when no feeds exist."""
    empty_dim = {"weight": 0, "description": "No feeds configured", "score": None, "feeds": [], "lastUpdated": None}
    return {
        "thiScore": thi_score,
        "thiFormula": {"evidenceScore": 50, "momentumScore": 50, "qualityScore": 50, "evidenceContrib": 25, "momentumContrib": 15, "qualityContrib": 10},
        "evidence": {"score": 50, "contribution": 25, "formula": "(50×0.35) + (50×0.30) + (50×0.20) + (50×0.15)", "flow": empty_dim, "structural": empty_dim, "adoption": empty_dim, "policy": empty_dim, "dimContributions": {"flow": 0, "structural": 0, "adoption": 0, "policy": 0}},
        "momentum": {"score": 50, "contribution": 15, "hasEnoughHistory": False, "firstSnapshotDate": None, "currentEvidence": 50, "thirtyDay": {"delta": None, "score": 50, "prevEvidence": None, "prevDate": None}, "ninetyDay": {"delta": None, "score": 50, "prevEvidence": None, "prevDate": None}, "oneYear": {"delta": None, "score": 50, "prevEvidence": None, "prevDate": None}},
        "dataQuality": {"score": 50, "contribution": 10, "totalFeeds": 0, "scoredFeeds": 0, "agreement": {"pctConfirming": None, "score": 75, "scoredCount": 0, "totalCount": 0}, "freshness": {"avgAgeDays": None, "live": 0, "stale": 0, "degraded": 0, "offline": 0, "score": 0}, "sourceQuality": {"weightedAvg": 50, "score": 50, "activeSources": []}},
    }


def _build_breakdown_response(
    thi_score, ev_score, m_score, dq_score,
    ev_contrib, m_contrib, dq_contrib,
    ev_formula, dimensions, dim_contributions,
    has_enough_history, first_snapshot_date, current_evidence,
    momentum_30d, momentum_90d, momentum_1yr,
    total, scored_feeds, agreement_score, pct_confirming,
    avg_age, live_feeds, stale_feeds, degraded_feeds, offline_feeds,
    freshness_score, weighted_sq, sq_score,
):
    return {
        "thiScore": thi_score,
        "thiFormula": {
            "evidenceScore": round(ev_score, 1),
            "momentumScore": round(m_score, 1),
            "qualityScore": round(dq_score, 1),
            "evidenceContrib": ev_contrib,
            "momentumContrib": m_contrib,
            "qualityContrib": dq_contrib,
        },
        "evidence": {
            "score": ev_score,
            "contribution": ev_contrib,
            "formula": ev_formula,
            "flow": dimensions.get("flow"),
            "structural": dimensions.get("structural"),
            "adoption": dimensions.get("adoption"),
            "policy": dimensions.get("policy"),
            "dimContributions": dim_contributions,
        },
        "momentum": {
            "score": m_score,
            "contribution": m_contrib,
            "hasEnoughHistory": has_enough_history,
            "firstSnapshotDate": first_snapshot_date,
            "currentEvidence": round(current_evidence, 1),
            "thirtyDay": momentum_30d,
            "ninetyDay": momentum_90d,
            "oneYear": momentum_1yr,
        },
        "dataQuality": {
            "score": dq_score,
            "contribution": dq_contrib,
            "totalFeeds": total,
            "scoredFeeds": len(scored_feeds),
            "agreement": {
                "pctConfirming": pct_confirming,
                "score": agreement_score,
                "scoredCount": len(scored_feeds),
                "totalCount": total,
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
                "activeSources": list(set(f.source for f in scored_feeds)),
            },
        },
    }
