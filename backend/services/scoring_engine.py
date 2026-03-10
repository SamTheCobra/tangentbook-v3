"""
THI Scoring Engine

Evidence Score  = weighted average of all active indicators (normalized 0-100)
Momentum Score  = computed from 30d/90d/1yr rate-of-change of evidence components
Conviction Score = f(signal_agreement, data_freshness, source_quality)

THI = (Evidence x 0.50) + (Momentum x 0.30) + (Conviction x 0.20)

Child THI = (Parent THI x inheritance_weight) + (Child's own indicator score x (1 - inheritance_weight))
"""

from datetime import datetime, timedelta

from config import FORMULAS

THI_WEIGHTS = FORMULAS["thi"]["weights"]
MOM_WEIGHTS = FORMULAS["thi"]["components"]["momentum"]["weights"]
CONV_WEIGHTS = FORMULAS["thi"]["components"]["conviction"]["weights"]
EFS_WEIGHTS = FORMULAS["efs"]["weights"]


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def normalize_percentile(current_value: float, historical_values: list[float]) -> float:
    if not historical_values or len(historical_values) < 3:
        return 50.0  # Insufficient data for meaningful percentile
    below = sum(1 for v in historical_values if v < current_value)
    return clamp(round((below / len(historical_values)) * 100))


def redistribute_weights(
    indicators: dict[str, float],
    offline_feed_ids: set[str],
) -> dict[str, float]:
    active = {k: v for k, v in indicators.items() if k not in offline_feed_ids}
    total_active_weight = sum(active.values())
    if total_active_weight == 0:
        return {}
    return {k: v / total_active_weight for k, v in active.items()}


def compute_evidence_score(
    feed_scores: dict[str, float],
    feed_weights: dict[str, float],
    offline_feeds: set[str],
) -> float:
    weights = redistribute_weights(feed_weights, offline_feeds)
    if not weights:
        return 50.0

    total = sum(feed_scores.get(fid, 50.0) * w for fid, w in weights.items())
    return clamp(round(total, 1))


def compute_momentum_score(
    short_term: float,
    medium_term: float,
    long_term: float,
) -> float:
    score = (short_term * MOM_WEIGHTS["30d"]) + (medium_term * MOM_WEIGHTS["90d"]) + (long_term * MOM_WEIGHTS["1yr"])
    return clamp(round(score, 1))


def compute_conviction_score(
    signal_agreement: float,
    data_freshness: float,
    source_quality: float,
) -> float:
    score = (signal_agreement * CONV_WEIGHTS["signal_agreement"]) + (data_freshness * CONV_WEIGHTS["freshness"]) + (source_quality * CONV_WEIGHTS["source_quality"])
    return clamp(round(score, 1))


def compute_thi(
    evidence: float,
    momentum: float,
    conviction: float,
    evidence_weight: float = None,
    momentum_weight: float = None,
    conviction_weight: float = None,
) -> float:
    ew = evidence_weight if evidence_weight is not None else THI_WEIGHTS["evidence"]
    mw = momentum_weight if momentum_weight is not None else THI_WEIGHTS["momentum"]
    cw = conviction_weight if conviction_weight is not None else THI_WEIGHTS["conviction"]
    score = (evidence * ew) + (momentum * mw) + (conviction * cw)
    return clamp(round(score, 1))


def compute_child_thi(
    parent_thi: float,
    child_indicator_score: float,
    inheritance_weight: float = None,
) -> float:
    if inheritance_weight is None:
        inheritance_weight = FORMULAS["thi"]["child_thi"]["default_inheritance_weight"]
    score = (parent_thi * inheritance_weight) + (child_indicator_score * (1 - inheritance_weight))
    return clamp(round(score, 1))


def score_to_direction(score: float) -> str:
    if score >= 60:
        return "confirming"
    elif score <= 40:
        return "refuting"
    return "neutral"


def compute_trend(current: float, previous: float | None) -> str:
    if previous is None:
        return "stable"
    delta = current - previous
    if abs(delta) < 2:
        return "stable"
    if delta > 5:
        return "accelerating"
    if delta > 0:
        return "stable"
    if delta < -5:
        return "reversing"
    return "decelerating"


def check_conviction_divergence(user_conviction_1_to_10: int, thi_score: float) -> str | None:
    scaled = user_conviction_1_to_10 * 10
    diff = abs(scaled - thi_score)
    if diff > 30:
        return f"Conviction diverges from data by {int(diff)} points."
    return None
