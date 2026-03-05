from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import DataFeed, FeedCache, Thesis, MacroHeader

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
def refresh_feeds(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    # Actual refresh logic will be implemented in Phase 1
    return {"status": "refresh_queued", "thesisId": thesis_id}


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
def macro_header(db: Session = Depends(get_db)):
    header = db.query(MacroHeader).order_by(MacroHeader.last_updated.desc()).first()
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
