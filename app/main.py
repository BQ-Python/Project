from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import loans_router, swaps_router, banks_router, kpi_router

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Supabase Trésorerie",
    description="API de gestion des prêts, swaps, banques et KPI via Supabase",
    version="1.0.0"
)

# Configuration CORS pour autoriser les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://vitejsvitengttu2fx-ngpy--5173--96435430.local-credentialless.webcontainer.io",
    "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
