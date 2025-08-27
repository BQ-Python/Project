from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from app.schemas import BankCreate, Bank

router = APIRouter()

@router.get("/banks", response_model=list[Bank])
def get_banks():
    response = supabase.table("banks").select("*").execute()
    return response.data

@router.post("/banks", response_model=Bank)
def create_bank(bank: BankCreate):
    response = supabase.table("banks").insert(bank.dict()).execute()
    return response.data[0]
