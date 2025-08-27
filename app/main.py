from fastapi import FastAPI
from supabase import create_client
from app.routes import loans_router, swaps_router, banks_router, kpi_router

# Initialisation du client Supabase
SUPABASE_URL = "https://gchxuxnhwkusymfbnjmj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjaHh1eG5od2t1c3ltZmJuam1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyODAwMDIsImV4cCI6MjA3MTg1NjAwMn0.m2mC_kCzlPh_eknpqzQEKiNiuDc_BqZD7GT8UJLYROQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
