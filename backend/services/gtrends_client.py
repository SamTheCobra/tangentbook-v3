"""
Google Trends Client via pytrends
- No API key needed
- Aggressive rate limiting to avoid 429s: 10s between requests
- Cache window: 7 days
- Retries with exponential backoff on failure
"""

import logging
import time
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import DataFeed, FeedCache

logger = logging.getLogger(__name__)

CACHE_WINDOW_DAYS = 7
REQUEST_DELAY_SECONDS = 10
MAX_RETRIES = 3

# Global rate limiter
_last_request_time = 0.0


def _rate_limit(delay: float = REQUEST_DELAY_SECONDS):
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    # Add jitter to avoid pattern detection
    actual_delay = delay + random.uniform(0.5, 2.0)
    if elapsed < actual_delay:
        time.sleep(actual_delay - elapsed)
    _last_request_time = time.time()


def fetch_google_trends(
    keyword: str,
    feed: DataFeed,
    db: Session,
) -> dict | None:
    """Fetch Google Trends data for a keyword. Returns {value, observations} or None."""

    # Check cache first
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

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            from pytrends.request import TrendReq

            _rate_limit(REQUEST_DELAY_SECONDS * attempt)

            pytrends = TrendReq(
                hl="en-US",
                tz=360,
                timeout=(10, 30),
            )
            pytrends.build_payload([keyword], timeframe="today 52-w", geo="US")

            _rate_limit(3)
            interest_df = pytrends.interest_over_time()

            if interest_df is None or interest_df.empty:
                logger.warning(f"GTrends returned no data for '{keyword}' (attempt {attempt})")
                if attempt == MAX_RETRIES:
                    feed.status = "stale"
                    db.commit()
                    return _return_cached(latest_cache)
                continue

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
            error_str = str(e)
            is_rate_limited = "429" in error_str or "Too Many" in error_str
            logger.warning(
                f"GTrends {'rate limited' if is_rate_limited else 'error'} for '{keyword}' "
                f"(attempt {attempt}/{MAX_RETRIES}): {e}"
            )
            if attempt < MAX_RETRIES and is_rate_limited:
                backoff = REQUEST_DELAY_SECONDS * (2 ** attempt) + random.uniform(1, 5)
                logger.info(f"GTrends backing off {backoff:.0f}s before retry...")
                time.sleep(backoff)
                continue
            elif attempt == MAX_RETRIES:
                feed.status = "degraded"
                db.commit()
                return _return_cached(latest_cache)

    return _return_cached(latest_cache)


def _return_cached(cache_entry: FeedCache | None) -> dict | None:
    if cache_entry:
        return {
            "value": cache_entry.raw_value,
            "observations": cache_entry.raw_data or [],
        }
    return None
