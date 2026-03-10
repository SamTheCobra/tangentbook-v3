from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import FORMULAS
from database import get_db
from models import (
    Thesis, Effect, EquityBet, StartupOpportunity,
    ConvictionSnapshot, THISnapshot
)

router = APIRouter(prefix="/api", tags=["theses"])


@router.get("/formulas")
async def get_formulas():
    """Return the full formulas.json — single source of truth for all scoring weights."""
    return FORMULAS


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ThesisCreate(BaseModel):
    title: str
    subtitle: str
    summary: str = ""
    description: str
    time_horizon: str
    tags: list[str] = []
    user_conviction_score: int = 5

class ThesisUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    time_horizon: Optional[str] = None
    tags: Optional[list[str]] = None

class ConvictionUpdate(BaseModel):
    score: int
    note: Optional[str] = None

class ReorderUpdate(BaseModel):
    display_order: int

class EffectCreate(BaseModel):
    title: str
    description: str
    order: int = 2
    parent_effect_id: Optional[str] = None

class EffectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    inheritance_weight: Optional[float] = None

class EquityBetCreate(BaseModel):
    ticker: str
    company_name: str = ""
    role: str
    rationale: str
    time_horizon: str = "1-3yr"
    is_feedback_indicator: bool = False
    feedback_weight: float = 0.0

class EquityBetUpdate(BaseModel):
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    role: Optional[str] = None
    rationale: Optional[str] = None
    time_horizon: Optional[str] = None
    is_feedback_indicator: Optional[bool] = None
    feedback_weight: Optional[float] = None

class StartupCreate(BaseModel):
    name: str
    one_liner: str
    timing: str = "RIGHT_TIMING"
    time_horizon: str = "1-3yr"

class StartupUpdate(BaseModel):
    name: Optional[str] = None
    one_liner: Optional[str] = None
    timing: Optional[str] = None
    time_horizon: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def thesis_to_dict(t: Thesis) -> dict:
    divergence = abs(t.user_conviction_score * 10 - t.thi_score)
    divergence_warning = None
    if divergence > 30:
        divergence_warning = f"Conviction diverges from data by {int(divergence)} points."

    return {
        "id": t.id,
        "title": t.title,
        "subtitle": t.subtitle,
        "summary": t.summary or "",
        "description": t.description,
        "timeHorizon": t.time_horizon,
        "tags": t.tags or [],
        "isArchived": t.is_archived,
        "isCollapsed": t.is_collapsed,
        "displayOrder": t.display_order,
        "createdAt": t.created_at.isoformat() if t.created_at else None,
        "updatedAt": t.updated_at.isoformat() if t.updated_at else None,
        "thi": {
            "score": t.thi_score,
            "direction": t.thi_direction,
            "trend": t.thi_trend,
            "evidence": {"score": t.evidence_score, "weight": t.evidence_weight, "explanation": getattr(t, "evidence_explanation", None)},
            "momentum": {"score": t.momentum_score, "weight": t.momentum_weight, "explanation": getattr(t, "momentum_explanation", None)},
            "conviction": {"score": t.conviction_data_score, "weight": t.conviction_data_weight, "explanation": getattr(t, "conviction_explanation", None)},
        },
        "userConviction": {
            "score": t.user_conviction_score,
            "note": t.user_conviction_note,
            "updatedAt": t.user_conviction_updated_at.isoformat() if t.user_conviction_updated_at else None,
            "divergenceWarning": divergence_warning,
        },
        "effects": [effect_to_dict(e) for e in t.effects if e.parent_effect_id is None],
        "equityBets": [bet_to_dict(b) for b in t.equity_bets],
        "startupOpportunities": [opp_to_dict(o) for o in t.startup_opportunities],
    }


def effect_to_dict(e: Effect) -> dict:
    return {
        "id": e.id,
        "thesisId": e.thesis_id,
        "parentEffectId": e.parent_effect_id,
        "order": e.order,
        "title": e.title,
        "description": e.description,
        "inheritanceWeight": e.inheritance_weight,
        "isCollapsed": e.is_collapsed,
        "thi": {
            "score": e.thi_score,
            "direction": e.thi_direction,
            "trend": e.thi_trend,
            "evidenceExplanation": getattr(e, "evidence_explanation", None),
            "momentumExplanation": getattr(e, "momentum_explanation", None),
            "convictionExplanation": getattr(e, "conviction_explanation", None),
        },
        "userConviction": {
            "score": e.user_conviction_score,
            "note": e.user_conviction_note,
            "updatedAt": e.user_conviction_updated_at.isoformat() if e.user_conviction_updated_at else None,
        },
        "equityBets": [bet_to_dict(b) for b in e.equity_bets],
        "startupOpportunities": [opp_to_dict(o) for o in e.startup_opportunities],
        "childEffects": [effect_to_dict(c) for c in (e.child_effects or [])],
    }


def bet_to_dict(b: EquityBet) -> dict:
    return {
        "id": b.id,
        "ticker": b.ticker,
        "companyName": b.company_name,
        "companyDescription": b.company_description,
        "role": b.role,
        "rationale": b.rationale,
        "timeHorizon": b.time_horizon,
        "isFeedbackIndicator": b.is_feedback_indicator,
        "feedbackWeight": b.feedback_weight,
        "currentPrice": b.current_price,
        "priceChange12mPct": b.price_change_12m_pct,
        "priceHistory": b.price_history,
    }


def opp_to_dict(o: StartupOpportunity) -> dict:
    return {
        "id": o.id,
        "name": o.name,
        "oneLiner": o.one_liner,
        "timing": o.timing,
        "timeHorizon": o.time_horizon,
    }


# ── Thesis CRUD ───────────────────────────────────────────────────────────────

@router.get("/theses")
def list_theses(db: Session = Depends(get_db)):
    theses = db.query(Thesis).order_by(Thesis.display_order, Thesis.created_at).all()
    return [thesis_to_dict(t) for t in theses]


@router.post("/theses", status_code=201)
def create_thesis(data: ThesisCreate, db: Session = Depends(get_db)):
    max_order = db.query(Thesis.display_order).order_by(Thesis.display_order.desc()).first()
    order = (max_order[0] + 1) if max_order else 0

    thesis = Thesis(
        title=data.title,
        subtitle=data.subtitle,
        summary=data.summary,
        description=data.description,
        time_horizon=data.time_horizon,
        tags=data.tags,
        user_conviction_score=data.user_conviction_score,
        display_order=order,
        thi_score=50.0,
    )
    db.add(thesis)
    db.commit()
    db.refresh(thesis)

    snapshot = THISnapshot(thesis_id=thesis.id, score=50.0)
    db.add(snapshot)
    db.commit()

    return thesis_to_dict(thesis)


@router.get("/theses/{thesis_id}")
def get_thesis(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    result = thesis_to_dict(thesis)

    # Include THI history
    snapshots = db.query(THISnapshot).filter(
        THISnapshot.thesis_id == thesis_id
    ).order_by(THISnapshot.computed_at).all()
    result["thiHistory"] = [
        {
            "date": s.computed_at.isoformat(),
            "score": s.score,
            "evidenceScore": s.evidence_score,
            "momentumScore": s.momentum_score,
            "convictionScore": s.conviction_score,
        }
        for s in snapshots
    ]

    # Include conviction history
    conv_snapshots = db.query(ConvictionSnapshot).filter(
        ConvictionSnapshot.thesis_id == thesis_id
    ).order_by(ConvictionSnapshot.updated_at).all()
    result["userConviction"]["history"] = [
        {"score": c.score, "updatedAt": c.updated_at.isoformat(), "note": c.note}
        for c in conv_snapshots
    ]

    return result


@router.put("/theses/{thesis_id}")
def update_thesis(thesis_id: str, data: ThesisUpdate, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "time_horizon":
            setattr(thesis, "time_horizon", value)
        else:
            setattr(thesis, field, value)

    db.commit()
    db.refresh(thesis)
    return thesis_to_dict(thesis)


@router.delete("/theses/{thesis_id}")
def delete_thesis(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    db.delete(thesis)
    db.commit()
    return {"status": "deleted"}


@router.patch("/theses/{thesis_id}/archive")
def toggle_archive(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    thesis.is_archived = not thesis.is_archived
    db.commit()
    return {"isArchived": thesis.is_archived}


@router.patch("/theses/{thesis_id}/collapse")
def toggle_collapse(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    thesis.is_collapsed = not thesis.is_collapsed
    db.commit()
    return {"isCollapsed": thesis.is_collapsed}


@router.patch("/theses/{thesis_id}/reorder")
def reorder_thesis(thesis_id: str, data: ReorderUpdate, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")
    thesis.display_order = data.display_order
    db.commit()
    return {"displayOrder": thesis.display_order}


@router.put("/theses/{thesis_id}/conviction")
def update_thesis_conviction(thesis_id: str, data: ConvictionUpdate, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    thesis.user_conviction_score = max(1, min(10, data.score))
    thesis.user_conviction_note = data.note
    thesis.user_conviction_updated_at = datetime.utcnow()

    # Recalculate THI: blend data-driven score with user conviction
    # Data components: evidence (50%) + momentum (30%) + data quality (20%)
    data_thi = (
        thesis.evidence_score * thesis.evidence_weight
        + thesis.momentum_score * thesis.momentum_weight
        + thesis.conviction_data_score * thesis.conviction_data_weight
    )
    # User conviction scaled to 0-100, blended at 30% weight
    user_scaled = thesis.user_conviction_score * 10
    thesis.thi_score = round(data_thi * 0.7 + user_scaled * 0.3, 1)

    snapshot = ConvictionSnapshot(
        thesis_id=thesis_id,
        score=thesis.user_conviction_score,
        note=data.note,
    )
    db.add(snapshot)

    # Also snapshot the new THI
    thi_snap = THISnapshot(
        thesis_id=thesis_id,
        score=thesis.thi_score,
        evidence_score=thesis.evidence_score,
        momentum_score=thesis.momentum_score,
        conviction_score=thesis.conviction_data_score,
    )
    db.add(thi_snap)

    db.commit()
    db.refresh(thesis)
    return thesis_to_dict(thesis)


# ── Effect CRUD ───────────────────────────────────────────────────────────────

@router.get("/theses/{thesis_id}/effects")
def list_effects(thesis_id: str, db: Session = Depends(get_db)):
    effects = db.query(Effect).filter(Effect.thesis_id == thesis_id).all()
    return [effect_to_dict(e) for e in effects]


@router.post("/theses/{thesis_id}/effects", status_code=201)
def create_effect(thesis_id: str, data: EffectCreate, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    effect = Effect(
        thesis_id=thesis_id,
        parent_effect_id=data.parent_effect_id,
        order=data.order,
        title=data.title,
        description=data.description,
        thi_score=50.0,
    )
    db.add(effect)
    db.commit()
    db.refresh(effect)
    return effect_to_dict(effect)


@router.get("/effects/{effect_id}")
def get_effect(effect_id: str, db: Session = Depends(get_db)):
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")
    return effect_to_dict(effect)


@router.put("/effects/{effect_id}")
def update_effect(effect_id: str, data: EffectUpdate, db: Session = Depends(get_db)):
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(effect, field, value)
    db.commit()
    db.refresh(effect)
    return effect_to_dict(effect)


@router.delete("/effects/{effect_id}")
def delete_effect(effect_id: str, db: Session = Depends(get_db)):
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")
    db.delete(effect)
    db.commit()
    return {"status": "deleted"}


@router.put("/effects/{effect_id}/conviction")
def update_effect_conviction(effect_id: str, data: ConvictionUpdate, db: Session = Depends(get_db)):
    effect = db.query(Effect).filter(Effect.id == effect_id).first()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")

    effect.user_conviction_score = max(1, min(10, data.score))
    effect.user_conviction_note = data.note
    effect.user_conviction_updated_at = datetime.utcnow()

    snapshot = ConvictionSnapshot(
        effect_id=effect_id,
        score=effect.user_conviction_score,
        note=data.note,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(effect)
    return effect_to_dict(effect)


# ── Equity Bets CRUD ──────────────────────────────────────────────────────────

@router.post("/theses/{thesis_id}/bets", status_code=201)
def create_bet(thesis_id: str, data: EquityBetCreate, db: Session = Depends(get_db)):
    bet = EquityBet(thesis_id=thesis_id, **data.model_dump())
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet_to_dict(bet)


@router.post("/effects/{effect_id}/bets", status_code=201)
def create_effect_bet(effect_id: str, data: EquityBetCreate, db: Session = Depends(get_db)):
    bet = EquityBet(effect_id=effect_id, **data.model_dump())
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet_to_dict(bet)


@router.put("/bets/{bet_id}")
def update_bet(bet_id: str, data: EquityBetUpdate, db: Session = Depends(get_db)):
    bet = db.query(EquityBet).filter(EquityBet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(bet, field, value)
    db.commit()
    db.refresh(bet)
    return bet_to_dict(bet)


@router.delete("/bets/{bet_id}")
def delete_bet(bet_id: str, db: Session = Depends(get_db)):
    bet = db.query(EquityBet).filter(EquityBet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    db.delete(bet)
    db.commit()
    return {"status": "deleted"}


# ── Startup Opportunities CRUD ────────────────────────────────────────────────

@router.post("/theses/{thesis_id}/opportunities", status_code=201)
def create_opportunity(thesis_id: str, data: StartupCreate, db: Session = Depends(get_db)):
    opp = StartupOpportunity(thesis_id=thesis_id, **data.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp_to_dict(opp)


@router.post("/effects/{effect_id}/opportunities", status_code=201)
def create_effect_opportunity(effect_id: str, data: StartupCreate, db: Session = Depends(get_db)):
    opp = StartupOpportunity(effect_id=effect_id, **data.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp_to_dict(opp)


@router.put("/opportunities/{opp_id}")
def update_opportunity(opp_id: str, data: StartupUpdate, db: Session = Depends(get_db)):
    opp = db.query(StartupOpportunity).filter(StartupOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(opp, field, value)
    db.commit()
    db.refresh(opp)
    return opp_to_dict(opp)


@router.delete("/opportunities/{opp_id}")
def delete_opportunity(opp_id: str, db: Session = Depends(get_db)):
    opp = db.query(StartupOpportunity).filter(StartupOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db.delete(opp)
    db.commit()
    return {"status": "deleted"}
