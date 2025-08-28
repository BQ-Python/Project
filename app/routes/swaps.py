from fastapi import APIRouter, HTTPException, Response
from app.supabase_client import supabase
from app.schemes import SwapCreate, Swap

router = APIRouter()

# Routes OPTIONS pour CORS
@router.options("/swaps")
def options_swaps():
    return Response(status_code=204)

@router.options("/swaps/{swap_id}")
def options_swap_id(swap_id: int):
    return Response(status_code=204)

@router.get("/swaps", response_model=list[Swap])
def get_swaps():
    response = supabase.table("swaps").select("*").execute()
    return response.data

@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate):
    data = swap.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()
    response = supabase.table("swaps").insert(data).execute()
    return response.data[0]

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate):
    data = swap.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()
    response = supabase.table("swaps").update(data).eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return response.data[0]

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int):
    response = supabase.table("swaps").delete().eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return {"message": "Swap deleted"}
