# app/database.py (optionnel, uniquement pour documentation ou validation)

from pydantic import BaseModel
from datetime import date

class BankModel(BaseModel):
    id: int
    name: str

class LoanModel(BaseModel):
    id: int
    currency: str
    amount: float
    interest_rate: float
    start_date: date
    maturity_date: date
    conversion_rate: float
    payment_frequency: str

class SwapModel(BaseModel):
    id: int
    start_date: date
    maturity_date: date
    currency: str
    spot_rate: float
    forward_rate: float
    nominal: float
    bank_id: int
