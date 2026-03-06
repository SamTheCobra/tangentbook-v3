"""API endpoints for Equity Fit Score and Startup Timing Score."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import EquityBet, EquityFitScore, StartupOpportunity, StartupTimingScore, Thesis, Effect
from services.efs_service import (
    calculate_efs, calculate_sts, efs_to_dict, sts_to_dict, THESIS_KEYWORDS,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["efs"])


def _get_thesis_keywords(thesis_id: str, db: Session) -> list[str]:
    """Get keywords for a thesis."""
    # Check direct mapping first
    keywords = THESIS_KEYWORDS.get(thesis_id, [])
    if keywords:
        return keywords

    # Fallback: use thesis tags and title
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if thesis:
        words = (thesis.tags or []) + thesis.title.lower().split()
        return list(set(words))
    return []


@router.get("/theses/{thesis_id}/equity-scores")
def get_thesis_equity_scores(thesis_id: str, db: Session = Depends(get_db)):
    """Get all EFS scores for a thesis's equity bets, sorted by score desc."""
    bets = db.query(EquityBet).filter(EquityBet.thesis_id == thesis_id).all()
    bet_ids = [b.id for b in bets]

    scores = db.query(EquityFitScore).filter(
        EquityFitScore.equity_bet_id.in_(bet_ids)
    ).all()

    score_map = {s.equity_bet_id: s for s in scores}
    result = []
    for bet in bets:
        efs = score_map.get(bet.id)
        result.append({
            "ticker": bet.ticker,
            "companyName": bet.company_name,
            "role": bet.role,
            "betId": bet.id,
            "efs": efs_to_dict(efs) if efs else None,
        })

    result.sort(key=lambda x: (x["efs"]["efsScore"] if x["efs"] else 0), reverse=True)
    return result


@router.post("/theses/{thesis_id}/equity-scores/refresh")
async def refresh_thesis_equity_scores(thesis_id: str, db: Session = Depends(get_db)):
    """Recalculate EFS for all equity bets in this thesis."""
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    keywords = _get_thesis_keywords(thesis_id, db)
    bets = db.query(EquityBet).filter(EquityBet.thesis_id == thesis_id).all()

    results = []
    for bet in bets:
        try:
            efs = await calculate_efs(bet, thesis_id, keywords, db)
            results.append(efs_to_dict(efs))
        except Exception as e:
            logger.error(f"Error calculating EFS for {bet.ticker}: {e}")

    return {"calculated": len(results), "results": results}


@router.get("/equity-bet/{bet_id}/efs")
def get_bet_efs(bet_id: str, db: Session = Depends(get_db)):
    """Get full EFS breakdown for one equity bet."""
    bet = db.query(EquityBet).filter(EquityBet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Equity bet not found")

    efs = db.query(EquityFitScore).filter(EquityFitScore.equity_bet_id == bet_id).first()
    if not efs:
        return {"betId": bet_id, "ticker": bet.ticker, "efs": None}

    return {"betId": bet_id, "ticker": bet.ticker, "efs": efs_to_dict(efs)}


@router.get("/startup/{opp_id}/sts")
def get_startup_sts(opp_id: str, db: Session = Depends(get_db)):
    """Get full STS for one startup opportunity."""
    opp = db.query(StartupOpportunity).filter(StartupOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Startup opportunity not found")

    sts = db.query(StartupTimingScore).filter(
        StartupTimingScore.startup_opp_id == opp_id
    ).first()
    if not sts:
        return {"oppId": opp_id, "name": opp.name, "sts": None}

    return {"oppId": opp_id, "name": opp.name, "sts": sts_to_dict(sts)}


@router.get("/effects/{effect_id}/equity-scores")
def get_effect_equity_scores(effect_id: str, db: Session = Depends(get_db)):
    """Get all EFS scores for an effect's equity bets."""
    bets = db.query(EquityBet).filter(EquityBet.effect_id == effect_id).all()
    bet_ids = [b.id for b in bets]

    scores = db.query(EquityFitScore).filter(
        EquityFitScore.equity_bet_id.in_(bet_ids)
    ).all()

    score_map = {s.equity_bet_id: s for s in scores}
    result = []
    for bet in bets:
        efs = score_map.get(bet.id)
        result.append({
            "ticker": bet.ticker,
            "companyName": bet.company_name,
            "role": bet.role,
            "betId": bet.id,
            "efs": efs_to_dict(efs) if efs else None,
        })

    result.sort(key=lambda x: (x["efs"]["efsScore"] if x["efs"] else 0), reverse=True)
    return result
