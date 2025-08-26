from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Autoriser les requêtes CORS depuis StackBlitz ou localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplace "*" par l'URL de ton front si tu veux restreindre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Swap(BaseModel):
    spotRate: float
    forwardRate: float

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    points = swap.forwardRate - swap.spotRate
    return {"points": round(points, 4)}
