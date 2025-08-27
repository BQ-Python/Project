from pydantic import BaseModel
from datetime import date
from typing import Literal

class LoanInput(BaseModel):
    interest_rate: float
    nominal: float
    currency: Literal["USD", "GBP", "JPY", "CNY"]
    initial_conversion_rate: float
    payment_interval: Literal["1M", "3M", "6M", "in_fine"]
    start_date: date
    maturity_date: date

class SwapInput(BaseModel):
    nominal: float
    currency: Literal["USD", "GBP", "JPY", "CNY"]
    spot_rate: float
    forward_rate: float
    start_date: date
    maturity_date: date

