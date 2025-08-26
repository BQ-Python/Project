from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuration CORS pour autoriser les appels depuis StackBlitz
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vitejsviteugrwopkm-vrkx--5173--96435430.local-credentialless.webcontainer.io",
        "https://stackblitz.com",
        "*",  # à utiliser temporairement pour tester, mais à restreindre en production
    ],
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
