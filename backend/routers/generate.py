"""AI-powered thesis generation endpoint.

Accepts a single sentence, calls Claude to generate the full thesis
with effects, equity bets, and startup opportunities in one shot.
"""

import json
import logging
import os
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Thesis, Effect, EquityBet, StartupOpportunity,
    EquityFitScore, StartupTimingScore, THISnapshot,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class GenerateRequest(BaseModel):
    raw_thesis: str
    conviction: int = 5


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


SYSTEM_PROMPT = """You are a macro investing analyst. Given a thesis sentence, generate a complete thesis object.

Return ONLY a single valid JSON object. No markdown, no preamble, no explanation.

The JSON must have this exact structure:

{
  "title": "short punchy title (3-6 words, ALL CAPS)",
  "subtitle": "the core claim rewritten clearly in one sentence",
  "summary": "2-3 sentence executive summary of the thesis",
  "description": "2-3 paragraph macro analysis of why this thesis is compelling. Include data points, trends, and reasoning.",
  "tags": ["tag1", "tag2", "tag3", "tag4"],
  "time_horizon": "1-3yr",
  "thi_score": 65.0,
  "equity_bets": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc",
      "company_description": "Brief description of what the company does and why it matters for this thesis",
      "role": "BENEFICIARY",
      "rationale": "Why this stock captures the thesis — specific and data-driven",
      "time_horizon": "1-3yr",
      "efs_score": 72.0
    }
  ],
  "startup_opportunities": [
    {
      "name": "Startup Name",
      "one_liner": "One sentence describing the startup opportunity",
      "timing": "RIGHT_TIMING",
      "time_horizon": "1-3yr",
      "sts_score": 68.0
    }
  ],
  "second_order_effects": [
    {
      "title": "Effect title",
      "description": "2-3 sentence description of this second-order effect",
      "thi_score": 60.0,
      "equity_bets": [],
      "startup_opportunities": []
    }
  ],
  "third_order_effects": [
    {
      "title": "Effect title",
      "description": "2-3 sentence description of this third-order effect",
      "thi_score": 55.0,
      "equity_bets": [],
      "startup_opportunities": []
    }
  ]
}

Rules:
- "title" must be 3-6 words, punchy, ALL CAPS style
- "role" must be one of: BENEFICIARY, HEADWIND, CANARY
- "timing" must be one of: TOO_EARLY, RIGHT_TIMING, CROWDING
- "time_horizon" must be one of: 0-6mo, 6-18mo, 1-3yr, 3-7yr, 7yr+
- Generate exactly 9 equity_bets for the main thesis
- Generate exactly 9 startup_opportunities for the main thesis
- Generate exactly 2 second_order_effects, each with 9 equity_bets and 9 startup_opportunities
- Generate exactly 2 third_order_effects, each with 9 equity_bets and 9 startup_opportunities
- thi_score should be 0-100 reflecting how strong the evidence is
- efs_score should be 0-100 reflecting how well the stock captures the thesis
- sts_score should be 0-100 reflecting timing quality
- Equity bets should include a mix of BENEFICIARY (6-7), HEADWIND (1-2), and CANARY (1) roles
- Use real tickers. Include company_name and company_description for each.
- company_description should be 1-2 sentences about what they do + why relevant to thesis
- Startup opportunities should be creative, specific, and actionable
- Tags should be lowercase, 3-5 tags
- Be specific and data-driven in rationales. Reference real market dynamics.

CRITICAL — THI SCORE INDEPENDENCE:
- Each 2nd and 3rd order effect MUST have its own independently reasoned thi_score between 0-100.
- Do NOT copy the parent thesis thi_score. Do NOT make effect scores within 5 points of the parent.
- Score each effect based on how much real-world evidence currently supports THAT SPECIFIC effect, independent of the parent.
- 2nd order effects should typically score 60-90% of the parent thesis score (more speculative = lower).
- 3rd order effects should typically score 40-75% of the parent thesis score (further downstream = lower).
- Every effect's thi_score MUST differ from the parent by at least 10 points.
- Effect scores should also differ from each other — no two effects should have the same thi_score."""


async def call_claude(raw_thesis: str) -> dict:
    import httpx

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 16000,
                "system": SYSTEM_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate a complete macro thesis from this sentence:\n\n\"{raw_thesis}\"",
                    }
                ],
            },
        )

    if resp.status_code != 200:
        logger.error(f"Claude API error {resp.status_code}: {resp.text}")
        raise HTTPException(status_code=502, detail=f"Claude API error: {resp.status_code}")

    data = resp.json()
    text = data["content"][0]["text"]
    cleaned = _clean_json(text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw text: {cleaned[:500]}")
        raise HTTPException(status_code=502, detail="Claude returned invalid JSON")


def save_generated_thesis(gen: dict, conviction: int, db: Session) -> str:
    max_order = db.query(Thesis.display_order).order_by(Thesis.display_order.desc()).first()
    order = (max_order[0] + 1) if max_order else 0

    thi_score = float(gen.get("thi_score", 50.0))

    thesis = Thesis(
        title=gen["title"],
        subtitle=gen.get("subtitle", ""),
        summary=gen.get("summary", ""),
        description=gen.get("description", ""),
        time_horizon=gen.get("time_horizon", "1-3yr"),
        tags=gen.get("tags", []),
        user_conviction_score=max(1, min(10, conviction)),
        display_order=order,
        thi_score=thi_score,
    )
    db.add(thesis)
    db.flush()

    snapshot = THISnapshot(thesis_id=thesis.id, score=thi_score)
    db.add(snapshot)

    _save_bets(gen.get("equity_bets", []), thesis.id, None, db)
    _save_startups(gen.get("startup_opportunities", []), thesis.id, None, db)

    for so in gen.get("second_order_effects", []):
        effect = Effect(
            thesis_id=thesis.id,
            parent_effect_id=None,
            order=2,
            title=so["title"],
            description=so.get("description", ""),
            thi_score=float(so.get("thi_score", 50.0)),
        )
        db.add(effect)
        db.flush()
        _save_bets(so.get("equity_bets", []), thesis.id, effect.id, db)
        _save_startups(so.get("startup_opportunities", []), thesis.id, effect.id, db)

    for to in gen.get("third_order_effects", []):
        effect = Effect(
            thesis_id=thesis.id,
            parent_effect_id=None,
            order=3,
            title=to["title"],
            description=to.get("description", ""),
            thi_score=float(to.get("thi_score", 50.0)),
        )
        db.add(effect)
        db.flush()
        _save_bets(to.get("equity_bets", []), thesis.id, effect.id, db)
        _save_startups(to.get("startup_opportunities", []), thesis.id, effect.id, db)

    db.commit()
    return thesis.id


def _save_bets(bets: list, thesis_id: str, effect_id: str | None, db: Session):
    for b in bets:
        bet = EquityBet(
            thesis_id=thesis_id if not effect_id else None,
            effect_id=effect_id,
            ticker=b.get("ticker", "???"),
            company_name=b.get("company_name", ""),
            company_description=b.get("company_description", ""),
            role=b.get("role", "BENEFICIARY"),
            rationale=b.get("rationale", ""),
            time_horizon=b.get("time_horizon", "1-3yr"),
        )
        db.add(bet)
        db.flush()

        efs_score = float(b.get("efs_score", 50.0))
        efs = EquityFitScore(
            equity_bet_id=bet.id,
            thesis_id=thesis_id,
            effect_id=effect_id,
            efs_score=efs_score,
            revenue_alignment_score=efs_score * 1.05,
            thesis_beta_score=efs_score * 0.95,
            momentum_alignment_score=efs_score * 1.0,
            valuation_buffer_score=efs_score * 0.90,
            signal_purity_score=efs_score * 1.10,
        )
        db.add(efs)


def _save_startups(opps: list, thesis_id: str, effect_id: str | None, db: Session):
    for o in opps:
        opp = StartupOpportunity(
            thesis_id=thesis_id if not effect_id else None,
            effect_id=effect_id,
            name=o.get("name", "Unnamed"),
            one_liner=o.get("one_liner", ""),
            timing=o.get("timing", "RIGHT_TIMING"),
            time_horizon=o.get("time_horizon", "1-3yr"),
        )
        db.add(opp)
        db.flush()

        sts_score = float(o.get("sts_score", 50.0))
        sts = StartupTimingScore(
            startup_opp_id=opp.id,
            sts_score=sts_score,
            thi_alignment_score=sts_score * 1.0,
            thi_velocity_score=sts_score * 0.95,
            competition_density_score=sts_score * 1.05,
            timing_label=o.get("timing", "RIGHT_TIMING"),
        )
        db.add(sts)


@router.post("/theses/generate")
async def generate_thesis(data: GenerateRequest, db: Session = Depends(get_db)):
    if not data.raw_thesis.strip():
        raise HTTPException(status_code=400, detail="Thesis sentence is required")

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "test":
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    gen = await call_claude(data.raw_thesis)
    thesis_id = save_generated_thesis(gen, data.conviction, db)
    return {"id": thesis_id}


# ── Generate more causal effects ─────────────────────────────────────────────

class GenerateEffectsRequest(BaseModel):
    order: int = 2
    count: int = 3


EFFECTS_SYSTEM_PROMPT = """You are a macro investing analyst. Given a thesis and its existing effects, generate NEW causal effects that are DISTINCT from the existing ones.

Return ONLY a valid JSON array. No markdown, no preamble, no explanation.

Each effect must have this structure:
{
  "title": "Effect title (concise, specific)",
  "description": "2-3 sentence description of this causal effect and why it follows from the thesis",
  "thi_score": <float 0-100>,
  "equity_bets": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc",
      "company_description": "Brief description of what the company does and why it matters",
      "role": "BENEFICIARY",
      "rationale": "Why this stock captures the effect — specific and data-driven",
      "time_horizon": "1-3yr",
      "efs_score": 72.0
    }
  ],
  "startup_opportunities": [
    {
      "name": "Startup Name",
      "one_liner": "One sentence describing the startup opportunity",
      "timing": "RIGHT_TIMING",
      "time_horizon": "1-3yr",
      "sts_score": 68.0
    }
  ]
}

Rules:
- Each effect must have exactly 9 equity_bets and 9 startup_opportunities
- "role" must be one of: BENEFICIARY, HEADWIND, CANARY
- "timing" must be one of: TOO_EARLY, RIGHT_TIMING, CROWDING
- Use real tickers with company_name and company_description
- Effects must be DISTINCT from the existing ones listed
- Be specific and data-driven in rationales

CRITICAL — THI SCORE INDEPENDENCE:
- Each effect MUST have its own independently reasoned thi_score between 0-100.
- Do NOT copy the parent thesis thi_score. Do NOT make effect scores within 5 points of the parent.
- Score each effect based on how much real-world evidence currently supports THAT SPECIFIC effect, independent of the parent.
- Effects that are more speculative or further downstream should generally score lower than the parent thesis.
- Every effect's thi_score MUST differ from the parent by at least 10 points.
- Effect scores should also differ from each other — no two effects should have the same thi_score."""


@router.post("/theses/{thesis_id}/generate-effects")
async def generate_effects(thesis_id: str, data: GenerateEffectsRequest, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "test":
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    existing_effects = db.query(Effect).filter(
        Effect.thesis_id == thesis_id,
        Effect.order == data.order,
    ).all()
    existing_titles = [e.title for e in existing_effects]

    order_label = "2nd" if data.order == 2 else "3rd"
    user_msg = f"""Thesis: "{thesis.title}"
Subtitle: "{thesis.subtitle}"
Description: "{thesis.description}"

Existing {order_label}-order effects (DO NOT repeat these):
{chr(10).join(f'- {t}' for t in existing_titles) if existing_titles else '(none yet)'}

Generate {data.count} new {order_label}-order causal effects for this thesis. Return a JSON array of {data.count} effect objects."""

    import httpx
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 12000,
                "system": EFFECTS_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_msg}],
            },
        )

    if resp.status_code != 200:
        logger.error(f"Claude API error {resp.status_code}: {resp.text}")
        raise HTTPException(status_code=502, detail=f"Claude API error: {resp.status_code}")

    text = resp.json()["content"][0]["text"]
    cleaned = _clean_json(text)

    try:
        effects_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw: {cleaned[:500]}")
        raise HTTPException(status_code=502, detail="Claude returned invalid JSON")

    if not isinstance(effects_data, list):
        effects_data = [effects_data]

    created_ids = []
    for eff in effects_data:
        effect = Effect(
            thesis_id=thesis_id,
            parent_effect_id=None,
            order=data.order,
            title=eff["title"],
            description=eff.get("description", ""),
            thi_score=float(eff.get("thi_score", 50.0)),
        )
        db.add(effect)
        db.flush()
        _save_bets(eff.get("equity_bets", []), thesis_id, effect.id, db)
        _save_startups(eff.get("startup_opportunities", []), thesis_id, effect.id, db)
        created_ids.append(effect.id)

    db.commit()
    return {"created": len(created_ids), "ids": created_ids}
