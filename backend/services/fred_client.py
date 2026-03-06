"""
FRED API Client
- Fetches economic time series from the Federal Reserve
- Caches responses in SQLite (60 min window)
- Rate limit: 120 req/min (no practical constraint)
"""

import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from config import FRED_API_KEY
from models import DataFeed, FeedCache

logger = logging.getLogger(__name__)

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
CACHE_WINDOW_MINUTES = 60


async def fetch_fred_series(
    series_id: str,
    feed: DataFeed,
    db: Session,
    observation_start: str | None = None,
) -> dict | None:
    """Fetch a FRED series. Returns {value, observations} or None on failure."""

    # Check cache first
    latest_cache = (
        db.query(FeedCache)
        .filter(FeedCache.feed_id == feed.id)
        .order_by(FeedCache.fetched_at.desc())
        .first()
    )

    if latest_cache and latest_cache.fetched_at:
        age = datetime.utcnow() - latest_cache.fetched_at
        if age < timedelta(minutes=CACHE_WINDOW_MINUTES):
            logger.info(f"FRED cache hit for {series_id} (age: {age})")
            return {
                "value": latest_cache.raw_value,
                "observations": latest_cache.raw_data or [],
            }

    # Fetch from API
    if not FRED_API_KEY or FRED_API_KEY == "your_fred_key_here":
        logger.warning(f"FRED API key not configured, skipping {series_id}")
        feed.status = "degraded"
        db.commit()
        return _return_cached(latest_cache)

    if not observation_start:
        observation_start = (datetime.utcnow() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": observation_start,
        "sort_order": "desc",
        "limit": 1000,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(FRED_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        observations = data.get("observations", [])
        if not observations:
            logger.warning(f"FRED returned no observations for {series_id}")
            feed.status = "stale"
            db.commit()
            return _return_cached(latest_cache)

        # Get latest non-missing value
        latest_value = None
        for obs in observations:
            if obs.get("value") and obs["value"] != ".":
                try:
                    latest_value = float(obs["value"])
                    break
                except (ValueError, TypeError):
                    continue

        if latest_value is None:
            logger.warning(f"No valid values in FRED response for {series_id}")
            feed.status = "stale"
            db.commit()
            return _return_cached(latest_cache)

        # Parse all historical values for normalization
        historical = []
        for obs in observations:
            if obs.get("value") and obs["value"] != ".":
                try:
                    historical.append(float(obs["value"]))
                except (ValueError, TypeError):
                    continue

        # Cache result
        cache_entry = FeedCache(
            feed_id=feed.id,
            raw_value=latest_value,
            raw_data=historical,
            normalized_score=None,  # Will be set by scoring engine
        )
        db.add(cache_entry)

        feed.raw_value = latest_value
        feed.last_fetched = datetime.utcnow()
        feed.status = "live"
        db.commit()

        logger.info(f"FRED fetched {series_id}: {latest_value} ({len(historical)} historical points)")

        return {
            "value": latest_value,
            "observations": historical,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"FRED HTTP error for {series_id}: {e.response.status_code}")
        feed.status = "degraded"
        db.commit()
        return _return_cached(latest_cache)
    except Exception as e:
        logger.error(f"FRED error for {series_id}: {e}")
        feed.status = "degraded"
        db.commit()
        return _return_cached(latest_cache)


def _return_cached(cache_entry: FeedCache | None) -> dict | None:
    if cache_entry:
        return {
            "value": cache_entry.raw_value,
            "observations": cache_entry.raw_data or [],
        }
    return None


async def fetch_macro_header_data() -> dict:
    """Fetch FFR, 10Y-2Y spread, and VIX from FRED."""
    results = {}

    if not FRED_API_KEY or FRED_API_KEY == "your_fred_key_here":
        logger.warning("FRED API key not configured — skipping macro header fetch")
        return results

    series_map = {
        "ffr": "FEDFUNDS",
        "spread": "T10Y2Y",
        "vix": "VIXCLS",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        for key, series_id in series_map.items():
            try:
                params = {
                    "series_id": series_id,
                    "api_key": FRED_API_KEY,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 10,
                }
                resp = await client.get(FRED_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                found = False
                for obs in data.get("observations", []):
                    if obs.get("value") and obs["value"] != ".":
                        results[key] = float(obs["value"])
                        found = True
                        logger.info(f"FRED macro {series_id}: {obs['value']} (date: {obs.get('date', '?')})")
                        break
                if not found:
                    logger.warning(f"FRED macro {series_id}: no valid observations in response")
            except httpx.HTTPStatusError as e:
                logger.error(f"FRED macro header HTTP error for {series_id}: {e.response.status_code} - {e.response.text[:200]}")
            except Exception as e:
                logger.error(f"FRED macro header error for {series_id}: {type(e).__name__}: {e}")

    return results
