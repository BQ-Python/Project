from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Swap(BaseModel):
    spotRate: float
    forwardRate: float
    nominal: float

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    spot_amount_eur = swap.nominal / swap.spotRate
    forward_amount_eur = swap.nominal / swap.forwardRate
    points_eur = forward_amount_eur - spot_amount_eur

    return {
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2)
    }

@app.get("/historical-eurusd")
def get_historical_eurusd(start: date, end: date):
    ticker = yf.Ticker("EURUSD=X")
    data = ticker.history(start=start.isoformat(), end=end.isoformat())
    if data.empty:
        return {"error": "Aucune donnée disponible"}
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "rates": data['Close'].round(4).tolist()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
