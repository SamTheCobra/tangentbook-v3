"""
Google Trends Client via pytrends
- No API key needed
- Strict rate limiting: 1s sleep between requests
- Cache window: 7 days
- Normalizes weekly interest to 0-100 percentile
"""

import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import DataFeed, FeedCache

logger = logging.getLogger(__name__)

CACHE_WINDOW_DAYS = 7

# Global rate limiter
_last_request_time = 0.0


def _rate_limit():
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_request_time = time.time()


def fetch_google_trends(
    keyword: str,
    feed: DataFeed,
    db: Session,
) -> dict | None:
    """Fetch Google Trends data for a keyword. Returns {value, observations} or None."""

    # Check cache
    latest_cache = (
        db.query(FeedCache)
        .filter(FeedCache.feed_id == feed.id)
        .order_by(FeedCache.fetched_at.desc())
        .first()
    )

    if latest_cache and latest_cache.fetched_at:
        age = datetime.utcnow() - latest_cache.fetched_at
        if age < timedelta(days=CACHE_WINDOW_DAYS):
            logger.info(f"GTrends cache hit for '{keyword}' (age: {age})")
            return {
                "value": latest_cache.raw_value,
                "observations": latest_cache.raw_data or [],
            }

    try:
        from pytrends.request import TrendReq

        _rate_limit()

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        pytrends.build_payload([keyword], timeframe="today 52-w", geo="US")

        _rate_limit()
        interest_df = pytrends.interest_over_time()

        if interest_df is None or interest_df.empty:
            logger.warning(f"GTrends returned no data for '{keyword}'")
            feed.status = "stale"
            db.commit()
            return _return_cached(latest_cache)

        # Extract values
        values = interest_df[keyword].tolist()
        latest_value = values[-1] if values else 0

        # Cache
        cache_entry = FeedCache(
            feed_id=feed.id,
            raw_value=float(latest_value),
            raw_data=[float(v) for v in values],
        )
        db.add(cache_entry)

        feed.raw_value = float(latest_value)
        feed.last_fetched = datetime.utcnow()
        feed.status = "live"
        db.commit()

        logger.info(f"GTrends fetched '{keyword}': {latest_value} ({len(values)} weeks)")

        return {
            "value": float(latest_value),
            "observations": [float(v) for v in values],
        }

    except Exception as e:
        logger.error(f"GTrends error for '{keyword}': {e}")
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
