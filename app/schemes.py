from pydantic import BaseModel
from datetime import date
from typing import Literal, List, Dict

# ---------------------
# Modèles pour les prêts
# ---------------------

class LoanBase(BaseModel):
    currency: str
    nominal: float
    rate: float
    start_date: date
    maturity_date: date
    payment_frequency: Literal["in_fine", "1 mois", "3 mois", "6 mois", "12 mois"]
    conversion_rate: float

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int
    number_of_days: int
    total_interest: float
    nominal_in_eur: float
    repayment_schedule: List[Dict]

    class Config:
        orm_mode = True  # Pydantic v1
        # from_attributes = True  # Pydantic v2

# ---------------------
# Modèles pour les swaps
# ---------------------

class SwapBase(BaseModel):
    currency: str
    nominal: float
    start_date: date
    maturity_date: date
    spot_rate: float
    forward_rate: float
    bank_id: int

class SwapCreate(SwapBase):
    pass

class Swap(SwapBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------
# Modèles pour les banques
# ---------------------

class BankBase(BaseModel):
    name: str

class BankCreate(BankBase):
    pass

class Bank(BankBase):
    id: int

    class Config:
        orm_mode = True
