from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.supabase_client import supabase
from app.schemes import SwapCreate, Swap

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
        data = swap.dict()
        data["start_date"] = data["start_date"].isoformat()
        data["maturity_date"] = data["maturity_date"].isoformat()
        response = supabase.table("swaps").insert(data).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Insertion failed or no data returned")

        return cors_response(response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/swaps/{swap_id}", response_model=Swap)
def update_swap(swap_id: int, swap: SwapCreate):
    try:
        data = swap.dict()
        data["start_date"] = data["start_date"].isoformat()
        data["maturity_date"] = data["maturity_date"].isoformat()
        response = supabase.table("swaps").update(data).eq("id", swap_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Swap not found")

        return cors_response(response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/swaps/{swap_id}")
def delete_swap(swap_id: int):
    try:
        response = supabase.table("swaps").delete().eq("id", swap_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Swap not found")

        return cors_response({"message": "Swap deleted"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
