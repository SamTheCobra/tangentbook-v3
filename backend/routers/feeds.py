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
                "normalizedScore": round(score) if score is not None else None,
                "status": f.status,
                "lastUpdated": lu.isoformat() if lu else None,
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
