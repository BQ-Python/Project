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
    spot_value_eur: float | None = None
    forward_value_eur: float | None = None
    swap_points_eur: float | None = None
    mtm_eur: float | None = None
    total_days: int | None = None
    remaining_days: int | None = None

    model_config = {
        "from_attributes": True
    }
