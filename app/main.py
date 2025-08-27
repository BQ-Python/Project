from fastapi import FastAPI
from app.routes import loans_router, swaps_router, banks_router, kpi_router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
