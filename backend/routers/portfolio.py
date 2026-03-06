from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import PortfolioPosition, PortfolioSnapshot, Thesis

router = APIRouter(prefix="/api", tags=["portfolio"])


class PositionCreate(BaseModel):
    ticker: str
    shares: float
    entry_price: float
    is_short: bool = False


class PositionUpdate(BaseModel):
    shares: float | None = None
    current_price: float | None = None
    is_closed: bool | None = None
    close_price: float | None = None


def position_to_dict(p: PortfolioPosition) -> dict:
    return {
        "id": p.id,
        "thesisId": p.thesis_id,
        "ticker": p.ticker,
        "shares": p.shares,
        "entryPrice": p.entry_price,
        "entryDate": p.entry_date.isoformat() if p.entry_date else None,
        "isShort": p.is_short,
        "currentPrice": p.current_price,
        "currentValue": p.current_value,
        "pnl": p.pnl,
        "pnlPct": p.pnl_pct,
        "lastUpdated": p.last_updated.isoformat() if p.last_updated else None,
        "isClosed": p.is_closed,
        "closedAt": p.closed_at.isoformat() if p.closed_at else None,
        "closePrice": p.close_price,
    }


@router.get("/theses/{thesis_id}/portfolio")
def get_portfolio(thesis_id: str, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    positions = db.query(PortfolioPosition).filter(
        PortfolioPosition.thesis_id == thesis_id,
        PortfolioPosition.is_closed == False,
    ).all()

    snapshots = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.thesis_id == thesis_id,
    ).order_by(PortfolioSnapshot.computed_at).all()

    total_value = sum(p.current_value or (p.shares * p.entry_price) for p in positions)
    total_cost = sum(p.shares * p.entry_price for p in positions)
    total_pnl = total_value - total_cost if positions else 0
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0

    # THI vs portfolio interpretation
    thi_score = thesis.thi_score
    interpretation = "NEUTRAL"
    if thi_score >= 65 and total_pnl_pct >= 5:
        interpretation = "ALIGNED_WINNING"
    elif thi_score >= 65 and total_pnl_pct < -5:
        interpretation = "THESIS_STRONG_PORTFOLIO_WEAK"
    elif thi_score < 35 and total_pnl_pct >= 5:
        interpretation = "THESIS_WEAK_PORTFOLIO_STRONG"
    elif thi_score < 35 and total_pnl_pct < -5:
        interpretation = "ALIGNED_LOSING"

    return {
        "positions": [position_to_dict(p) for p in positions],
        "totalValue": round(total_value, 2),
        "totalCost": round(total_cost, 2),
        "totalPnl": round(total_pnl, 2),
        "totalPnlPct": round(total_pnl_pct, 2),
        "thiScore": thi_score,
        "interpretation": interpretation,
        "history": [
            {
                "date": s.computed_at.isoformat(),
                "totalValue": s.total_value,
                "totalPnl": s.total_pnl,
                "totalPnlPct": s.total_pnl_pct,
                "thiScore": s.thi_score,
            }
            for s in snapshots
        ],
    }


@router.post("/theses/{thesis_id}/portfolio/positions")
def add_position(thesis_id: str, data: PositionCreate, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Thesis not found")

    position = PortfolioPosition(
        thesis_id=thesis_id,
        ticker=data.ticker.upper(),
        shares=data.shares,
        entry_price=data.entry_price,
        is_short=data.is_short,
        current_price=data.entry_price,
        current_value=data.shares * data.entry_price,
        pnl=0,
        pnl_pct=0,
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position_to_dict(position)


@router.put("/portfolio/positions/{position_id}")
def update_position(position_id: str, data: PositionUpdate, db: Session = Depends(get_db)):
    position = db.query(PortfolioPosition).filter(PortfolioPosition.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    if data.shares is not None:
        position.shares = data.shares
    if data.current_price is not None:
        position.current_price = data.current_price
        position.current_value = position.shares * data.current_price
        if position.is_short:
            position.pnl = (position.entry_price - data.current_price) * position.shares
        else:
            position.pnl = (data.current_price - position.entry_price) * position.shares
        cost = position.shares * position.entry_price
        position.pnl_pct = (position.pnl / cost * 100) if cost else 0
        position.last_updated = datetime.utcnow()
    if data.is_closed:
        position.is_closed = True
        position.closed_at = datetime.utcnow()
        if data.close_price:
            position.close_price = data.close_price
    db.commit()
    db.refresh(position)
    return position_to_dict(position)


@router.delete("/portfolio/positions/{position_id}")
def delete_position(position_id: str, db: Session = Depends(get_db)):
    position = db.query(PortfolioPosition).filter(PortfolioPosition.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(position)
    db.commit()
    return {"status": "deleted"}
