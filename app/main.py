from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    allow_origins=["*"],  # ou spécifie ton domaine StackBlitz si besoin
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de test CORS
@app.get("/test-cors")
def test_cors():
    return JSONResponse(content={"message": "CORS headers are working!"})

# Inclusion des routes
app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
