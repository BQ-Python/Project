from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Bank
from schemas import BankCreate, Bank

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/banks", response_model=list[Bank])
def get_banks(db: Session = Depends(get_db)):
    return db.query(Bank).all()

@router.post("/banks", response_model=Bank)
def create_bank(bank: BankCreate, db: Session = Depends(get_db)):
    db_bank = Bank(**bank.dict())
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank
