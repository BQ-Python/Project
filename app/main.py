from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import loans_router, swaps_router, banks_router, kpi_router

app = FastAPI(
    title="API Supabase Trésorerie",
    description="API de gestion des prêts, swaps, banques et KPI via Supabase",
    version="1.0.0"
)

# Middleware CORS global
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le dev, sinon spécifie ton domaine StackBlitz
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de test CORS
@app.get("/test-cors")
def test_cors():
    return JSONResponse(content={"message": "CORS headers are working!"})

# Inclusion des routers
app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)
