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

_EDGAR_CACHE_MAX_AGE = 7 * 24 * 3600
_EDGAR_URL = "https://www.sec.gov/files/company_tickers.json"
_EDGAR_HEADERS = {"User-Agent": "TangentBook research@tangentbook.com", "Accept": "application/json"}

_edgar_universe = None
_sector_cache = None
_sector_cache_dirty = False

# ── SIC-to-sector mapping ────────────────────────────────────────────────────

_SIC_SECTOR_RANGES = [
    (1000, 1499, "materials"),
    (1500, 1799, "industrials"),
    (2000, 2199, "consumer staples"),
    (2200, 2799, "consumer staples"),
    (2800, 2899, "materials"),
    (2900, 2999, "energy"),
    (3000, 3199, "materials"),
    (3200, 3499, "materials"),
    (3500, 3599, "industrials"),
    (3600, 3669, "technology"),
    (3670, 3679, "technology"),
    (3680, 3699, "technology"),
    (3700, 3799, "industrials"),
    (3800, 3899, "technology"),
    (3900, 3999, "consumer discretionary"),
    (4000, 4499, "industrials"),
    (4500, 4599, "industrials"),
    (4600, 4699, "energy"),
    (4700, 4799, "industrials"),
    (4800, 4899, "technology"),
    (4900, 4999, "utilities"),
    (5000, 5199, "consumer discretionary"),
    (5200, 5999, "consumer discretionary"),
    (6000, 6199, "financials"),
    (6200, 6299, "financials"),
    (6300, 6499, "financials"),
    (6500, 6599, "real estate"),
    (6600, 6699, "financials"),
    (6700, 6799, "financials"),
    (7000, 7299, "consumer discretionary"),
    (7300, 7369, "industrials"),
    (7370, 7379, "technology"),
    (7380, 7399, "industrials"),
    (7500, 7599, "consumer discretionary"),
    (7600, 7699, "consumer discretionary"),
    (7800, 7999, "consumer discretionary"),
    (8000, 8099, "healthcare"),
    (8100, 8199, "financials"),
    (8200, 8299, "consumer discretionary"),
    (8700, 8799, "industrials"),
]

_SIC_INDUSTRY_MAP = {
    "3674": "Semiconductors",
    "3672": "Printed Circuit Boards",
    "3679": "Electronic Components",
    "3559": "Semiconductor Equipment",
    "3825": "Instruments for Measuring",
    "3669": "Communications Equipment",
    "2836": "Pharmaceutical Preparations",
    "2830": "Drugs",
    "1311": "Crude Petroleum and Natural Gas",
    "1382": "Oil and Gas Field Services",
    "4911": "Electric Services",
    "4931": "Electric and Other Services Combined",
    "6022": "State Commercial Banks",
    "6021": "National Commercial Banks",
    "7372": "Prepackaged Software",
    "7371": "Computer Programming Services",
    "6726": "Investment Offices",
    "5912": "Drug Stores and Proprietary Stores",
    "8011": "Offices and Clinics of Doctors",
    "8051": "Skilled Nursing Care Facilities",
}


def _sic_to_sector(sic_code):
    try:
        sic_int = int(sic_code)
    except (ValueError, TypeError):
        return "other"
    for low, high, sector in _SIC_SECTOR_RANGES:
        if low <= sic_int <= high:
            return sector
    return "other"


def _sic_to_industry(sic_code, sic_description=""):
    mapped = _SIC_INDUSTRY_MAP.get(str(sic_code))
    if mapped:
        return mapped
    if sic_description:
        return sic_description
    return ""


# ── Cache helpers ────────────────────────────────────────────────────────────

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


# ── EDGAR fetch ──────────────────────────────────────────────────────────────

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
            cik = entry.get("cik_str")
            if ticker and name and cik is not None:
                tickers.append({"ticker": ticker.upper(), "name": name, "cik": int(cik)})

        _save_edgar_cache(tickers)
        logger.info(f"EDGAR universe fetched: {len(tickers)} tickers")
        return tickers
    except Exception as e:
        logger.warning(f"EDGAR fetch error: {e}, falling back to static universe")
        return None


# ── EDGAR SIC-based sector lookup ────────────────────────────────────────────

async def _fetch_sic_from_edgar(cik, client, retries=2):
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    for attempt in range(retries + 1):
        try:
            resp = await client.get(url, headers=_EDGAR_HEADERS)
            if resp.status_code == 429:
                await asyncio.sleep(2.0 * (attempt + 1))
                continue
            if resp.status_code != 200:
                return None, None
            data = resp.json()
            sic = data.get("sic", "")
            sic_desc = data.get("sicDescription", "")
            return sic, sic_desc
        except Exception:
            if attempt < retries:
                await asyncio.sleep(1.0)
                continue
            return None, None
    return None, None


async def _batch_fetch_sic_from_edgar(entries, batch_size=5):
    cache = _load_sector_cache()
    missing = [(e["ticker"], e["cik"]) for e in entries if e["ticker"].upper() not in cache]
    if not missing:
        return

    populated = 0
    failed = 0
    consecutive_429s = 0
    async with httpx.AsyncClient(timeout=15.0) as client:
        for i in range(0, len(missing), batch_size):
            batch = missing[i:i + batch_size]

            # Fetch sequentially within each batch to stay under rate limits
            batch_failed = 0
            for ticker, cik in batch:
                sic, sic_desc = await _fetch_sic_from_edgar(cik, client)
                if sic:
                    sector = _sic_to_sector(sic)
                    industry = _sic_to_industry(sic, sic_desc)
                    _update_sector_cache(ticker, sector, industry)
                    populated += 1
                    consecutive_429s = 0
                else:
                    batch_failed += 1
                    failed += 1
                # Small delay between individual requests
                await asyncio.sleep(0.15)

            # Adaptive backoff based on failure rate
            if batch_failed == len(batch):
                consecutive_429s += 1
                backoff = min(10.0, 2.0 * consecutive_429s)
                await asyncio.sleep(backoff)
            elif batch_failed > 0:
                consecutive_429s = 0
                await asyncio.sleep(0.5)
            else:
                consecutive_429s = 0

            # Abort if we're consistently rate-limited
            if consecutive_429s >= 10:
                logger.warning(f"EDGAR rate limit: aborting after {populated} populated, {failed} failed")
                break

            if (i // batch_size) % 100 == 0 and i > 0:
                _save_sector_cache()
                logger.info(f"Sector cache progress: {min(i + batch_size, len(missing))}/{len(missing)} fetched, {populated} populated, {failed} failed")

    _save_sector_cache()
    logger.info(f"Sector cache batch complete: {populated} populated, {failed} failed out of {len(missing)}")


async def prepopulate_sector_cache_from_edgar():
    cache = _load_sector_cache()
    logger.info(f"Sector cache loaded with {len(cache)} entries (on-demand population enabled)")


# ── Claude screening profile ────────────────────────────────────────────────

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


# ── Screening logic ──────────────────────────────────────────────────────────

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

    # Phase 1: Score all tickers using cached sector data + company name matching
    pre_scored = []
    uncached_with_name_match = []

    for entry in edgar:
        ticker_upper = entry["ticker"].upper()
        name_lower = entry["name"].lower()
        cached_entry = cache.get(ticker_upper)

        score = 0.0
        sector_str = ""
        industry_str = ""

        # Name-based matching (works without cache)
        for kw in revenue_keywords:
            if kw in name_lower:
                score += 1.5
        for st in sector_tags:
            if st in name_lower:
                score += 1.0

        # Anti-tag check on name
        anti_hit = any(anti in name_lower for anti in anti_tags)
        if anti_hit:
            continue

        # Sector-based matching (requires cache)
        if cached_entry:
            sector_str = cached_entry.get("sector", "")
            industry_str = cached_entry.get("industry", "")
            combined = f"{sector_str} {industry_str}".lower()

            for st in sector_tags:
                if st in combined:
                    score += 2.0
            for kw in revenue_keywords:
                if kw in combined:
                    score += 3.0

            anti_hit = any(anti in combined for anti in anti_tags)
            if anti_hit:
                continue
        elif score > 0 and "cik" in entry:
            # Has a name match but no cached sector — fetch SIC on demand
            uncached_with_name_match.append(entry)

        if score > 0:
            pre_scored.append({
                "ticker": entry["ticker"],
                "name": entry["name"],
                "cik": entry.get("cik"),
                "sector": sector_str,
                "industry": industry_str,
                "tags": [],
                "match_score": score,
            })

    # Phase 2: Fetch SIC for uncached tickers that had name matches (up to 200)
    if uncached_with_name_match:
        to_fetch = uncached_with_name_match[:200]
        logger.info(f"Fetching SIC codes for {len(to_fetch)} uncached name-matched tickers")
        await _batch_fetch_sic_from_edgar(to_fetch)
        cache = _load_sector_cache()

        # Re-score the ones we just fetched
        for item in pre_scored:
            ticker_upper = item["ticker"].upper()
            cached_entry = cache.get(ticker_upper)
            if cached_entry and not item["sector"]:
                sector_str = cached_entry.get("sector", "")
                industry_str = cached_entry.get("industry", "")
                combined = f"{sector_str} {industry_str}".lower()
                item["sector"] = sector_str
                item["industry"] = industry_str

                for st in sector_tags:
                    if st in combined:
                        item["match_score"] += 2.0
                for kw in revenue_keywords:
                    if kw in combined:
                        item["match_score"] += 3.0

                anti_hit = any(anti in combined for anti in anti_tags)
                if anti_hit:
                    item["match_score"] = -1

        pre_scored = [p for p in pre_scored if p["match_score"] > 0]

    if not pre_scored:
        return _screen_static_fallback(profile)

    pre_scored.sort(key=lambda x: x["match_score"], reverse=True)
    # Remove internal fields
    for item in pre_scored[:20]:
        item.pop("cik", None)
    return pre_scored[:20]


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
        except Exception:
            candidate["yf_sector"] = cached.get("sector", "") if cached else ""
            candidate["yf_industry"] = cached.get("industry", "") if cached else ""
            candidate["yf_description"] = ""
            candidate["company_name"] = candidate["name"]

    tasks = [_fetch_one(c) for c in candidates]
    await asyncio.gather(*tasks)
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
