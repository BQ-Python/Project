from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Autoriser les appels CORS depuis StackBlitz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Swap(BaseModel):
    spotRate: float     # taux spot (ex: 1.10 USD/EUR)
    forwardRate: float  # taux forward (ex: 1.12 USD/EUR)
    nominal: float      # montant en devise étrangère (ex: 100000 USD)

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    # Conversion du nominal en EUR
    spot_amount_eur = swap.nominal / swap.spotRate
    forward_amount_eur = swap.nominal / swap.forwardRate

    # Points de swap en EUR
    points_eur = forward_amount_eur - spot_amount_eur

    return {
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2)
    }

# Démarrage pour Railway
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
