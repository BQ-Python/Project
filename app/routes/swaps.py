from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Swap
from schemas import SwapCreate, Swap

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/swaps", response_model=list[Swap])
def get_swaps(db: Session = Depends(get_db)):
    return db.query(Swap).all()

@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate, db: Session = Depends(get_db)):
    db_swap = Swap(**swap.dict())
    db.add(db_swap)
    db.commit()
    db.refresh(db_swap)
    return db_swap

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate, db: Session = Depends(get_db)):
    db_swap = db.query(Swap).filter(Swap.id == swap_id).first()
    if not db_swap:
        raise HTTPException(status_code=404, detail="Swap not found")
    for key, value in swap.dict().items():
        setattr(db_swap, key, value)
    db.commit()
    db.refresh(db_swap)
    return db_swap

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int, db: Session = Depends(get_db)):
    db_swap = db.query(Swap).filter(Swap.id == swap_id).first()
    if not db_swap:
        raise HTTPException(status_code=404, detail="Swap not found")
    db.delete(db_swap)
    db.commit()
    return {"message": "Swap deleted"}
