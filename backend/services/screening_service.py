import asyncio
import json
import logging
import os
import re
import time

import httpx
from sqlalchemy.orm import Session

from models import Thesis, Effect, EquityBet, EquityFitScore

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

_DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
_STATIC_UNIVERSE_PATH = os.path.join(_DATA_DIR, "ticker_universe.json")
_EDGAR_CACHE_PATH = os.path.join(_DATA_DIR, "edgar_universe_cache.json")
_SECTOR_CACHE_PATH = os.path.join(_DATA_DIR, "sector_cache.json")

_EDGAR_CACHE_MAX_AGE = 7 * 24 * 3600  # 7 days
_EDGAR_URL = "https://www.sec.gov/files/company_tickers.json"
_EDGAR_HEADERS = {"User-Agent": "TangentBook research@tangentbook.com", "Accept": "application/json"}

# In-memory caches loaded lazily
_edgar_universe = None
_sector_cache = None
_sector_cache_dirty = False


def _load_static_universe():
    with open(_STATIC_UNIVERSE_PATH) as f:
        return json.load(f)


def _load_sector_cache():
    global _sector_cache
    if _sector_cache is not None:
        return _sector_cache
    if os.path.exists(_SECTOR_CACHE_PATH):
        try:
            with open(_SECTOR_CACHE_PATH) as f:
                _sector_cache = json.load(f)
                return _sector_cache
        except (json.JSONDecodeError, IOError):
            pass
    _sector_cache = {}
    return _sector_cache


def _save_sector_cache():
    global _sector_cache_dirty
    if not _sector_cache_dirty or _sector_cache is None:
        return
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_SECTOR_CACHE_PATH, "w") as f:
            json.dump(_sector_cache, f)
        _sector_cache_dirty = False
    except IOError as e:
        logger.error(f"Failed to write sector cache: {e}")


def _update_sector_cache(ticker, sector, industry):
    global _sector_cache_dirty
    cache = _load_sector_cache()
    cache[ticker.upper()] = {"sector": sector, "industry": industry}
    _sector_cache_dirty = True


def _load_edgar_cache():
    global _edgar_universe
    if _edgar_universe is not None:
        return _edgar_universe

    if os.path.exists(_EDGAR_CACHE_PATH):
        try:
            with open(_EDGAR_CACHE_PATH) as f:
                data = json.load(f)
            cached_at = data.get("cached_at", 0)
            if time.time() - cached_at < _EDGAR_CACHE_MAX_AGE:
                _edgar_universe = data.get("tickers", [])
                return _edgar_universe
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _save_edgar_cache(tickers):
    global _edgar_universe
    _edgar_universe = tickers
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_EDGAR_CACHE_PATH, "w") as f:
            json.dump({"cached_at": time.time(), "tickers": tickers}, f)
    except IOError as e:
        logger.error(f"Failed to write EDGAR cache: {e}")


async def fetch_edgar_universe():
    cached = _load_edgar_cache()
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(_EDGAR_URL, headers=_EDGAR_HEADERS)
        if resp.status_code != 200:
            logger.warning(f"EDGAR fetch failed with status {resp.status_code}, falling back to static universe")
            return None

        raw = resp.json()
        tickers = []
        for entry in raw.values():
            ticker = entry.get("ticker", "").strip()
            name = entry.get("title", "").strip()
            if ticker and name:
                tickers.append({"ticker": ticker.upper(), "name": name})

        _save_edgar_cache(tickers)
        logger.info(f"EDGAR universe fetched: {len(tickers)} tickers")
        return tickers
    except Exception as e:
        logger.warning(f"EDGAR fetch error: {e}, falling back to static universe")
        return None


async def _yf_fetch_sector(ticker):
    import yfinance as yf
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None, lambda t=ticker: dict(yf.Ticker(t).info or {})
        )
        return info.get("sector", ""), info.get("industry", "")
    except Exception:
        return "", ""


async def _batch_fetch_sectors(tickers, batch_size=50):
    cache = _load_sector_cache()
    missing = [t for t in tickers if t.upper() not in cache]
    if not missing:
        return

    for i in range(0, len(missing), batch_size):
        batch = missing[i:i + batch_size]
        tasks = [_yf_fetch_sector(t) for t in batch]
        results = await asyncio.gather(*tasks)
        for ticker, (sector, industry) in zip(batch, results):
            _update_sector_cache(ticker, sector, industry)

    _save_sector_cache()


async def prepopulate_sector_cache(count=500):
    edgar = await fetch_edgar_universe()
    if not edgar:
        return

    sorted_tickers = sorted(edgar, key=lambda x: x["ticker"])[:count]
    cache = _load_sector_cache()
    need = [t["ticker"] for t in sorted_tickers if t["ticker"].upper() not in cache]

    if not need:
        logger.info("Sector cache already has first 500 tickers")
        return

    logger.info(f"Pre-populating sector cache for {len(need)} tickers...")
    await _batch_fetch_sectors(need, batch_size=50)
    logger.info(f"Sector cache pre-populated, total entries: {len(_load_sector_cache())}")


def _clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


SCREENING_SYSTEM_PROMPT = """You are a macro investing analyst. Given a thesis and its causal effects, generate a screening profile to find stocks that express this thesis.

Return ONLY a single valid JSON object. No markdown, no preamble, no explanation.

{
  "sector_tags": ["sectors or sub-sectors that would benefit from or be impacted by this thesis"],
  "revenue_keywords": ["specific business activities, products, or revenue streams that align with this thesis"],
  "business_model_types": ["pure-play", "diversified", or "inverse"],
  "anti_tags": ["sectors, business characteristics, or revenue streams that would make a stock a POOR fit — use these to filter out false positives"],
  "notes": "One sentence explaining the screening rationale"
}

Rules:
- sector_tags: 3-8 tags for relevant sectors/sub-sectors (e.g. "gold mining", "semiconductor fab", "obesity drug")
- revenue_keywords: 5-15 specific keywords that would appear in a relevant company's business description (e.g. "semaglutide", "uranium enrichment", "GPU compute")
- business_model_types: which types of companies to prefer. "pure-play" = focused on thesis. "diversified" = conglomerates with some exposure. "inverse" = companies hurt by the thesis (for HEADWIND/CANARY bets).
- anti_tags: 3-8 characteristics that disqualify a stock (e.g. for a hard asset thesis: "subscription software", "ad-supported media"; for a GLP-1 thesis: "high-calorie packaged goods")
- Be specific. Generic tags like "technology" or "healthcare" are less useful than "GLP-1 therapeutics" or "lithium mining"."""


async def generate_screening_profile(thesis, effects):
    effect_mechanisms = []
    for e in effects:
        if e.causal_mechanism:
            effect_mechanisms.append(f"- {e.title}: {e.causal_mechanism}")
        else:
            effect_mechanisms.append(f"- {e.title}: {e.description[:200]}")

    user_msg = f"""Thesis: "{thesis.title}"
Description: {thesis.description}

Top-level causal effects:
{chr(10).join(effect_mechanisms) if effect_mechanisms else '(none yet)'}

Generate a screening profile to find stocks that express this thesis."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "system": SCREENING_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_msg}],
            },
        )

    if resp.status_code != 200:
        logger.error(f"Claude screening API error {resp.status_code}: {resp.text}")
        return None

    text = resp.json()["content"][0]["text"]
    cleaned = _clean_json(text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Screening profile JSON parse error: {e}")
        return None


def _screen_static_fallback(profile):
    logger.warning("Using static ticker_universe.json as fallback for screening")
    static = _load_static_universe()

    sector_tags = [t.lower() for t in profile.get("sector_tags", [])]
    revenue_keywords = [k.lower() for k in profile.get("revenue_keywords", [])]
    anti_tags = [a.lower() for a in profile.get("anti_tags", [])]

    scored = []
    for entry in static:
        ticker_tags = [t.lower() for t in entry.get("tags", [])]
        ticker_sector = entry.get("sector", "").lower()
        ticker_name = entry.get("name", "").lower()

        anti_match = any(
            anti in tag or anti in ticker_name
            for anti in anti_tags
            for tag in ticker_tags
        )
        if anti_match:
            continue

        score = 0.0
        for st in sector_tags:
            if st in ticker_sector:
                score += 2.0
            for tag in ticker_tags:
                if st in tag or tag in st:
                    score += 3.0

        for kw in revenue_keywords:
            for tag in ticker_tags:
                if kw in tag or tag in kw:
                    score += 2.0
            if kw in ticker_name:
                score += 1.0

        if score > 0:
            scored.append({
                "ticker": entry["ticker"],
                "name": entry["name"],
                "sector": entry.get("sector", ""),
                "tags": entry.get("tags", []),
                "match_score": score,
            })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:20]


async def screen_ticker_universe(profile):
    if not profile:
        return []

    edgar = await fetch_edgar_universe()
    if edgar is None:
        return _screen_static_fallback(profile)

    sector_tags = [t.lower() for t in profile.get("sector_tags", [])]
    revenue_keywords = [k.lower() for k in profile.get("revenue_keywords", [])]
    anti_tags = [a.lower() for a in profile.get("anti_tags", [])]
    cache = _load_sector_cache()

    sector_filtered = []
    for entry in edgar:
        ticker_upper = entry["ticker"].upper()
        cached_entry = cache.get(ticker_upper)
        if not cached_entry:
            continue

        sector_lower = cached_entry.get("sector", "").lower()
        industry_lower = cached_entry.get("industry", "").lower()
        combined = f"{sector_lower} {industry_lower}"

        sector_match = any(st in combined for st in sector_tags)
        if sector_match:
            sector_filtered.append({
                "ticker": entry["ticker"],
                "name": entry["name"],
                "sector": cached_entry.get("sector", ""),
                "industry": cached_entry.get("industry", ""),
            })

        if len(sector_filtered) >= 300:
            break

    if not sector_filtered:
        return _screen_static_fallback(profile)

    uncached = [e["ticker"] for e in sector_filtered if e["ticker"].upper() not in cache]
    if uncached:
        await _batch_fetch_sectors(uncached, batch_size=50)
        cache = _load_sector_cache()

    scored = []
    for entry in sector_filtered:
        ticker_upper = entry["ticker"].upper()
        cached_entry = cache.get(ticker_upper, {})
        sector_lower = cached_entry.get("sector", "").lower()
        industry_lower = cached_entry.get("industry", "").lower()
        combined = f"{sector_lower} {industry_lower}"
        name_lower = entry["name"].lower()

        anti_hit = any(anti in combined or anti in name_lower for anti in anti_tags)
        if anti_hit:
            continue

        score = 0.0
        for st in sector_tags:
            if st in combined:
                score += 2.0
        for kw in revenue_keywords:
            if kw in combined:
                score += 3.0
            if kw in name_lower:
                score += 1.5

        if score > 0:
            scored.append({
                "ticker": entry["ticker"],
                "name": entry["name"],
                "sector": cached_entry.get("sector", ""),
                "industry": cached_entry.get("industry", ""),
                "tags": [],
                "match_score": score,
            })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:20]


async def enrich_with_yfinance(candidates):
    import yfinance as yf

    cache = _load_sector_cache()

    async def _fetch_one(candidate):
        ticker_upper = candidate["ticker"].upper()
        cached = cache.get(ticker_upper)

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: dict(yf.Ticker(candidate["ticker"]).info or {}))
            candidate["yf_sector"] = info.get("sector", "")
            candidate["yf_industry"] = info.get("industry", "")
            candidate["yf_description"] = (info.get("longBusinessSummary") or "")[:300]
            candidate["company_name"] = info.get("shortName") or info.get("longName") or candidate["name"]

            if not cached or not cached.get("sector"):
                _update_sector_cache(ticker_upper, candidate["yf_sector"], candidate["yf_industry"])
        except Exception:
            candidate["yf_sector"] = cached.get("sector", "") if cached else ""
            candidate["yf_industry"] = cached.get("industry", "") if cached else ""
            candidate["yf_description"] = ""
            candidate["company_name"] = candidate["name"]

    tasks = [_fetch_one(c) for c in candidates]
    await asyncio.gather(*tasks)
    _save_sector_cache()
    return candidates


def rescore_with_yfinance_data(candidates, profile):
    sector_tags = [t.lower() for t in profile.get("sector_tags", [])]
    revenue_keywords = [k.lower() for k in profile.get("revenue_keywords", [])]
    anti_tags = [a.lower() for a in profile.get("anti_tags", [])]

    filtered = []
    for c in candidates:
        industry_text = f"{c.get('yf_sector', '')} {c.get('yf_industry', '')} {c.get('yf_description', '')}".lower()

        anti_hit = any(anti in industry_text for anti in anti_tags)
        if anti_hit:
            continue

        bonus = 0.0
        for kw in revenue_keywords:
            if kw in industry_text:
                bonus += 2.0
        for st in sector_tags:
            if st in industry_text:
                bonus += 1.5

        c["match_score"] = c.get("match_score", 0) + bonus
        filtered.append(c)

    filtered.sort(key=lambda x: x["match_score"], reverse=True)
    return filtered[:20]


def _assign_role(candidate, profile):
    bm_types = profile.get("business_model_types", ["pure-play"])
    if "inverse" in bm_types:
        anti_tags = [a.lower() for a in profile.get("anti_tags", [])]
        ticker_tags = [t.lower() for t in candidate.get("tags", [])]
        if any(anti in tag for anti in anti_tags for tag in ticker_tags):
            return "HEADWIND"
    return "BENEFICIARY"


async def screen_and_score(thesis_id, db):
    from services.efs_service import calculate_efs

    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        return []

    effects = db.query(Effect).filter(
        Effect.thesis_id == thesis_id,
        Effect.parent_effect_id.is_(None),
    ).all()

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "test":
        logger.warning("ANTHROPIC_API_KEY not configured, skipping screening")
        return []

    profile = await generate_screening_profile(thesis, effects)
    if not profile:
        logger.error(f"Failed to generate screening profile for thesis {thesis_id}")
        return []

    candidates = await screen_ticker_universe(profile)
    if not candidates:
        logger.warning(f"No ticker candidates found for thesis {thesis_id}")
        return []

    candidates = await enrich_with_yfinance(candidates)
    candidates = rescore_with_yfinance_data(candidates, profile)

    if not candidates:
        return []

    existing_screened_tickers = {
        b.ticker.upper()
        for b in db.query(EquityBet).filter(
            EquityBet.thesis_id == thesis_id,
            EquityBet.effect_id.is_(None),
            EquityBet.source == "screened",
        ).all()
    }

    new_candidates = [c for c in candidates if c["ticker"].upper() not in existing_screened_tickers]

    thesis_keywords = (
        profile.get("revenue_keywords", []) + profile.get("sector_tags", [])
    )

    created_bets = []
    for c in new_candidates:
        role = _assign_role(c, profile)
        bet = EquityBet(
            thesis_id=thesis_id,
            effect_id=None,
            ticker=c["ticker"],
            company_name=c.get("company_name", c["name"]),
            company_description=c.get("yf_description", "")[:500],
            role=role,
            rationale=f"Screened via thesis fit: matched on {c.get('industry', c.get('sector', 'sector match'))}",
            time_horizon="1-3yr",
            source="screened",
        )
        db.add(bet)
        db.flush()

        try:
            efs_result = await calculate_efs(bet, thesis_id, thesis_keywords, db)
            created_bets.append((bet, efs_result.efs_score))
        except Exception as e:
            logger.error(f"EFS calculation failed for {c['ticker']}: {e}")
            efs = EquityFitScore(
                equity_bet_id=bet.id,
                thesis_id=thesis_id,
                efs_score=c.get("match_score", 50.0),
            )
            db.add(efs)
            created_bets.append((bet, c.get("match_score", 50.0)))

    db.commit()

    created_bets.sort(key=lambda x: x[1], reverse=True)

    if len(created_bets) > 9:
        for bet, _ in created_bets[9:]:
            efs_row = db.query(EquityFitScore).filter(
                EquityFitScore.equity_bet_id == bet.id
            ).first()
            if efs_row:
                db.delete(efs_row)
            db.delete(bet)
        db.commit()
        created_bets = created_bets[:9]

    return [bet for bet, _ in created_bets]
