from fastapi import FastAPI
from app.routes import loans_router, swaps_router, banks_router, kpi_router


# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Supabase Trésorerie",
    description="API de gestion des prêts, swaps, banques et KPI via Supabase",
    version="1.0.0"
)

# Inclusion des routes
app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
