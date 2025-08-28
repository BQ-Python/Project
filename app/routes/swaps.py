from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import date
from app.supabase_client import supabase
from app.schemes import SwapCreate, Swap
from app.calculations import calculate_mtm

router = APIRouter()

def cors_response(content):
    return JSONResponse(
        content=content,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get("/swaps", response_model=list[Swap])
def get_swaps():
    try:
        response = supabase.table("swaps").select("*").execute()
        return cors_response(response.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate):
    try:
        start_date = swap.start_date
        maturity_date = swap.maturity_date
        today = date.today()

        spot_value_eur = swap.nominal * swap.spot_rate
        forward_value_eur = swap.nominal * swap.forward_rate
        swap_points_eur = forward_value_eur - spot_value_eur
        total_days = (maturity_date - start_date).days
        remaining_days = (maturity_date - today).days

        base_currency = "EUR"
        quote_currency = swap.currency.upper()

        try:
            mtm_eur = calculate_mtm(swap.nominal, swap.forward_rate, base_currency, quote_currency)
        except Exception:
            mtm_eur = None

        data = swap.dict()
        data["start_date"] = start_date.isoformat()
        data["maturity_date"] = maturity_date.isoformat()
        data["spot_value_eur"] = spot_value_eur
        data["forward_value_eur"] = forward_value_eur
        data["swap_points_eur"] = swap_points_eur
        data["mtm_eur"] = mtm_eur
        data["total_days"] = total_days
        data["remaining_days"] = remaining_days

        response = supabase.table("swaps").insert(data).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Insertion échouée")

        return cors_response(response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate):
    try:
        start_date = swap.start_date
        maturity_date = swap.maturity_date
        today = date.today()

        spot_value_eur = swap.nominal * swap.spot_rate
        forward_value_eur = swap.nominal * swap.forward_rate
        swap_points_eur = forward_value_eur - spot_value_eur
        total_days = (maturity_date - start_date).days
        remaining_days = (maturity_date - today).days

        base_currency = "EUR"
        quote_currency = swap.currency.upper()

        try:
            mtm_eur = calculate_mtm(swap.nominal, swap.forward_rate, base_currency, quote_currency)
        except Exception:
            mtm_eur = None

        data = swap.dict()
        data["start_date"] = start_date.isoformat()
        data["maturity_date"] = maturity_date.isoformat()
        data["spot_value_eur"] = spot_value_eur
        data["forward_value_eur"] = forward_value_eur
        data["swap_points_eur"] = swap_points_eur
        data["mtm_eur"] = mtm_eur
        data["total_days"] = total_days
        data["remaining_days"] = remaining_days

        response = supabase.table("swaps").update(data).eq("id", swap_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Swap introuvable")

        return cors_response(response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int):
    try:
        response = supabase.table("swaps").delete().eq("id", swap_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Swap introuvable")

        return cors_response({"message": "Swap supprimé"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
