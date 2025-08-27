from fastapi import FastAPI
from app.routes import loans_router, swaps_router, banks_router, kpi_router

# Initialisation de l'application FastAPI
app = FastAPI()

# Inclusion des routes
app.include_router(loans_router)
app.include_router(swaps_router)
app.include_router(banks_router)
app.include_router(kpi_router)

# Route de test
@app.get("/")
def read_root():
    return {"message": "API Supabase opérationnelle 🎉"}
