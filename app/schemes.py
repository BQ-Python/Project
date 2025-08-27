from pydantic import BaseModel
from datetime import date
from typing import Literal

class LoanBase(BaseModel):
    currency: str
    nominal: float
    rate: float
    start_date: date
    maturity_date: date
    payment_frequency: Literal["in_fine", "1 mois", "3 mois", "6 mois", "12 mois"]
    conversion_rate: float

class LoanCreate(LoanBase): pass

class Loan(LoanBase):
    id: int
    class Config:
        orm_mode = True  # ⚠️ En Pydantic v2, utiliser `from_attributes = True`

class SwapBase(BaseModel):
    currency: str
    nominal: float
    start_date: date
    maturity_date: date
    spot_rate: float
    forward_rate: float
    bank_id: int

class SwapCreate(SwapBase): pass

class Swap(SwapBase):
    id: int
    class Config:
        orm_mode = True

class BankBase(BaseModel):
    name: str

class BankCreate(BankBase): pass

class Bank(BankBase):
    id: int
    class Config:
        orm_mode = True
