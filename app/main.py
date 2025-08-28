from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import loans_router, swaps_router, banks_router, kpi_router

app = FastAPI(
    title="API Supabase Trésorerie",
    description="API de gestion des prêts, swaps, banques et KPI via Supabase",
    version="1.0.0"
)

# Configuration CORS corrigée
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou spécifie ton domaine StackBlitz si besoin
    allow_credentials=False,  # ← corrigé ici
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
