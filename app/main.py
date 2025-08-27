from fastapi import FastAPI
from .routes import loans, swaps, banks, kpi
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(loans.router)
app.include_router(swaps.router)
app.include_router(banks.router)
app.include_router(kpi.router)

