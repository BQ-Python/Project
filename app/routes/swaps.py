from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.supabase_client import supabase
from app.schemes import SwapCreate, Swap

router = APIRouter()

def cors_response(data):
    return JSONResponse(
        content=data,
        headers={"Access-Control-Allow-Origin": "*"}
    )

@router.get("/swaps", response_model=list[Swap])
def get_swaps():
    response = supabase.table("swaps").select("*").execute()
    return cors_response(response.data)

@router.post("/swaps", response_model=Swap)
def create_swap(swap: SwapCreate):
    data = swap.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()
    response = supabase.table("swaps").insert(data).execute()
    return cors_response(response.data[0])

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate):
    data = swap.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()
    response = supabase.table("swaps").update(data).eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return cors_response(response.data[0])

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int):
    response = supabase.table("swaps").delete().eq("id", swap_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Swap not found")
    return cors_response({"message": "Swap deleted"})
