from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from schemas import SwapCreate, Swap

router = APIRouter()

@router.get("/swaps", response_model=list[Swap])
def get_swaps():
    response = supabase.table("swaps").select("*").execute()
    return response.data

@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate):
    response = supabase.table("swaps").insert(swap.dict()).execute()
    return response.data[0]

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate):
    response = supabase.table("swaps").update(swap.dict()).eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return response.data[0]

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int):
    response = supabase.table("swaps").delete().eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return {"message": "Swap deleted"}
