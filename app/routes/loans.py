from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from app.schemes import LoanCreate, Loan
from app.utils import calculate_loan_characteristics

router = APIRouter()

@router.get("/loans", response_model=list[Loan])
def get_loans():
    response = supabase.table("loans").select("*").execute()
    return response.data

@router.post("/loans", response_model=Loan)
def create_loan(loan: LoanCreate):
    data = loan.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()

    # Calcul des champs supplémentaires
    calculated = calculate_loan_characteristics(
        currency=data["currency"],
        nominal=data["nominal"],
        rate=data["rate"],
        start_date=data["start_date"],
        maturity_date=data["maturity_date"],
        payment_frequency=data["payment_frequency"],
        conversion_rate=data["conversion_rate"]
    )
    data.update(calculated)

    response = supabase.table("loans").insert(data).execute()
    return response.data[0]

@router.put("/loans/{loan_id}", response_model=Loan)
def update_loan(loan_id: int, loan: LoanCreate):
    data = loan.dict()
    data["start_date"] = data["start_date"].isoformat()
    data["maturity_date"] = data["maturity_date"].isoformat()

    calculated = calculate_loan_characteristics(
        currency=data["currency"],
        nominal=data["nominal"],
        rate=data["rate"],
        start_date=data["start_date"],
        maturity_date=data["maturity_date"],
        payment_frequency=data["payment_frequency"],
        conversion_rate=data["conversion_rate"]
    )
    data.update(calculated)

    response = supabase.table("loans").update(data).eq("id", loan_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Loan not found")
    return response.data[0]

@router.delete("/loans/{loan_id}")
def delete_loan(loan_id: int):
    response = supabase.table("loans").delete().eq("id", loan_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Loan not found")
