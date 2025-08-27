from fastapi import FastAPI
from routes import loan, swap, kpi

app = FastAPI()

app.include_router(loan.router, prefix="/loan")
app.include_router(swap.router, prefix="/swap")
app.include_router(kpi.router, prefix="/kpi")
