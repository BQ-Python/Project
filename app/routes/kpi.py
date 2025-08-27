from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Loan, Swap, Bank

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/kpi/hedging-ratio")
def get_hedging_ratio(db: Session = Depends(get_db)):
    total_loans = db.query(Loan).count()
    total_swaps = db.query(Swap).count()
    if total_loans == 0:
        return {"hedging_ratio": 0}
    return {"hedging_ratio": total_swaps / total_loans}

@router.get("/kpi/mtm")
def get_mtm(db: Session = Depends(get_db)):
    swaps = db.query(Swap).all()
    mtm_total = sum((swap.forward_rate - swap.spot_rate) * swap.nominal for swap in swaps)
    return {"mtm": mtm_total}

@router.get("/kpi/exposure")
def get_exposure(db: Session = Depends(get_db)):
    loans = db.query(Loan).all()
    exposure_total = sum(loan.amount * loan.conversion_rate for loan in loans)
    return {"exposure": exposure_total}
