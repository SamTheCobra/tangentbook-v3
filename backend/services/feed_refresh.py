"""
Feed Refresh Service
- Orchestrates fetching from all data sources
- Runs scoring engine after fetch
- Updates THI scores for all theses
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from models import DataFeed, Thesis, Effect, MacroHeader, THISnapshot
from services.scoring_engine import (
    normalize_percentile, compute_evidence_score, compute_thi,
    compute_child_thi, score_to_direction, compute_trend, clamp,
)
from services.fred_client import fetch_fred_series, fetch_macro_header_data
from services.gtrends_client import fetch_google_trends

logger = logging.getLogger(__name__)


async def refresh_thesis_feeds(thesis_id: str, db: Session):
    """Refresh all feeds for a single thesis and recompute THI."""
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        return

    feeds = db.query(DataFeed).filter(DataFeed.thesis_id == thesis_id).all()
    if not feeds:
        return

    feed_scores: dict[str, float] = {}
    feed_weights: dict[str, float] = {}
    offline_feeds: set[str] = set()

    for feed in feeds:
        result = await _fetch_single_feed(feed, db)

        if result and result.get("observations"):
            score = normalize_percentile(result["value"], result["observations"])

            # Flip score if confirming direction is "lower"
            if feed.confirming_direction == "lower":
                score = 100.0 - score

            feed.normalized_score = score
            feed_scores[feed.id] = score
            feed_weights[feed.id] = feed.weight
            db.commit()
        else:
            offline_feeds.add(feed.id)
            feed_weights[feed.id] = feed.weight

    # Compute evidence score
    total_feeds = len(feeds)
    if feed_scores:
        evidence = compute_evidence_score(feed_scores, feed_weights, offline_feeds)
    else:
        evidence = thesis.evidence_score  # Keep existing when all feeds are down

    # Momentum: use THI snapshot history for real deltas
    momentum = _compute_momentum_from_snapshots(thesis_id, evidence, db)

    # Conviction from data quality
    live_feeds = total_feeds - len(offline_feeds)
    freshness = clamp((live_feeds / total_feeds) * 100) if total_feeds > 0 else 50
    signal_values = list(feed_scores.values())
    agreement = _compute_signal_agreement(signal_values) if signal_values else 50
    conviction_data = (agreement * 0.40 + freshness * 0.35 + 70 * 0.25)  # 70 = base source quality
    conviction_data = clamp(conviction_data)

    # Compute THI
    thi = compute_thi(evidence, momentum, conviction_data)

    # Update thesis
    old_thi = thesis.thi_score
    thesis.evidence_score = evidence
    thesis.momentum_score = momentum
    thesis.conviction_data_score = conviction_data
    thesis.thi_score = thi
    thesis.thi_direction = score_to_direction(thi)
    thesis.thi_trend = compute_trend(thi, old_thi)
    thesis.updated_at = datetime.utcnow()

    # Snapshot
    db.add(THISnapshot(
        thesis_id=thesis.id,
        score=thi,
        evidence_score=evidence,
        momentum_score=momentum,
        conviction_score=conviction_data,
    ))

    db.commit()

    # Update child effects
    for effect in thesis.effects:
        _update_effect_thi(effect, thi, db)

    logger.info(f"Thesis '{thesis.title}' THI updated: {old_thi} -> {thi}")


def _update_effect_thi(effect: Effect, parent_thi: float, db: Session):
    """Update an effect's THI based on parent inheritance."""
    old = effect.thi_score
    child_score = effect.thi_score  # Use existing as child's own indicator score
    new_thi = compute_child_thi(parent_thi, child_score, effect.inheritance_weight)
    effect.thi_score = new_thi
    effect.thi_direction = score_to_direction(new_thi)
    effect.thi_trend = compute_trend(new_thi, old)
    db.commit()

    for child in (effect.child_effects or []):
        _update_effect_thi(child, new_thi, db)


async def _fetch_single_feed(feed: DataFeed, db: Session) -> dict | None:
    """Route feed to appropriate client."""
    if feed.source == "FRED" and feed.series_id:
        return await fetch_fred_series(feed.series_id, feed, db)
    elif feed.source == "GTRENDS" and feed.keyword:
        # pytrends is synchronous, run in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, fetch_google_trends, feed.keyword, feed, db
        )
    else:
        logger.debug(f"Skipping feed {feed.id} (source: {feed.source})")
        return None


def _compute_momentum_from_snapshots(thesis_id: str, current_evidence: float, db: Session) -> float:
    """Compute momentum from THI snapshot history using 30d/90d/1yr deltas."""
    snapshots = (
        db.query(THISnapshot)
        .filter(THISnapshot.thesis_id == thesis_id)
        .order_by(THISnapshot.computed_at.desc())
        .all()
    )
    if len(snapshots) < 2:
        return 50.0  # Neutral when insufficient history

    now = datetime.utcnow()
    max_delta = 30.0  # Points

    def find_nearest(target_dt):
        best = None
        best_diff = None
        for s in snapshots:
            diff = abs((s.computed_at - target_dt).total_seconds())
            if best_diff is None or diff < best_diff:
                best = s
                best_diff = diff
        return best

    def delta_to_score(snap):
        if not snap or snap.evidence_score is None:
            return 50.0
        delta = current_evidence - snap.evidence_score
        return clamp(round(50 + (delta / max_delta) * 50, 1))

    s30 = delta_to_score(find_nearest(now - timedelta(days=30)))
    s90 = delta_to_score(find_nearest(now - timedelta(days=90)))
    s1y = delta_to_score(find_nearest(now - timedelta(days=365)))

    return clamp(round(s30 * 0.50 + s90 * 0.30 + s1y * 0.20, 1))


def _compute_simple_momentum(current: float, previous: float) -> float:
    """Simple momentum based on change from previous evidence score."""
    if previous == 0:
        return 50.0
    delta = current - previous
    # Map delta to 0-100 scale: +20 delta = 100, -20 delta = 0
    momentum = 50 + (delta * 2.5)
    return clamp(momentum)


def _compute_signal_agreement(scores: list[float]) -> float:
    """How much do feed signals agree? Low variance = high agreement."""
    if len(scores) < 2:
        return 75.0
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = variance ** 0.5
    # Map std to agreement: std=0 -> 100, std=50 -> 0
    agreement = 100 - (std * 2)
    return clamp(agreement)


async def refresh_macro_header(db: Session):
    """Refresh the macro header data from FRED."""
    data = await fetch_macro_header_data()
    if not data:
        return

    header = db.query(MacroHeader).order_by(MacroHeader.last_updated.desc()).first()

    ffr = data.get("ffr")
    spread = data.get("spread")
    vix = data.get("vix")

    # Determine regime
    regime = "NEUTRAL"
    if spread is not None:
        if spread < -0.5:
            regime = "RISK OFF"
        elif spread > 1.0:
            regime = "RISK ON"

    if header:
        header.ffr = ffr
        header.ten_year_two_year_spread = spread
        header.vix = vix
        header.regime = regime
        header.last_updated = datetime.utcnow()
    else:
        db.add(MacroHeader(
            ffr=ffr,
            ten_year_two_year_spread=spread,
            vix=vix,
            regime=regime,
        ))

    db.commit()
    logger.info(f"Macro header updated: FFR={ffr}, 10Y-2Y={spread}, VIX={vix}, regime={regime}")


async def refresh_all_theses(db: Session):
    """Refresh all thesis feeds and macro header."""
    logger.info("Starting full feed refresh...")

    await refresh_macro_header(db)

    theses = db.query(Thesis).filter(Thesis.is_archived == False).all()
    for thesis in theses:
        try:
            await refresh_thesis_feeds(thesis.id, db)
        except Exception as e:
            logger.error(f"Error refreshing thesis '{thesis.title}': {e}")

    logger.info(f"Feed refresh complete for {len(theses)} theses.")
