from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from app.schemas import LoanCreate, Loan

router = APIRouter()

@router.get("/loans", response_model=list[Loan])
def get_loans():
    response = supabase.table("loans").select("*").execute()
    return response.data

@router.post("/loans", response_model=Loan)
def create_loan(loan: LoanCreate):
    response = supabase.table("loans").insert(loan.dict()).execute()
    return response.data[0]

@router.put("/loans/{loan_id}", response_model=Loan)
def update_loan(loan_id: int, loan: LoanCreate):
    response = supabase.table("loans").update(loan.dict()).eq("id", loan_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Loan not found")
    return response.data[0]

@router.delete("/loans/{loan_id}")
def delete_loan(loan_id: int):
    response = supabase.table("loans").delete().eq("id", loan_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"message": "Loan deleted"}
