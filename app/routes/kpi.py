from fastapi import APIRouter
from app.supabase_client import supabase

router = APIRouter()

@router.get("/kpi/hedging-ratio")
def get_hedging_ratio():
    loans_count = supabase.table("loans").select("id", count="exact").execute().count
    swaps_count = supabase.table("swaps").select("id", count="exact").execute().count
    if loans_count == 0:
        return {"hedging_ratio": 0}
    return {"hedging_ratio": swaps_count / loans_count}

@router.get("/kpi/mtm")
def get_mtm():
    swaps = supabase.table("swaps").select("*").execute().data
    mtm_total = sum((swap["forward_rate"] - swap["spot_rate"]) * swap["nominal"] for swap in swaps)
    return {"mtm": mtm_total}

@router.get("/kpi/exposure")
def get_exposure():
    loans = supabase.table("loans").select("*").execute().data
    exposure_total = sum(loan["amount"] * loan["conversion_rate"] for loan in loans)
    return {"exposure": exposure_total}
