from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
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

@app.post("/calculate-mtm")
def calculate_mtm(swap: Swap):
    ticker = yf.Ticker("EURUSD=X")
    data = ticker.history(period="1d")
    if data.empty:
        return {"error": "Impossible de récupérer le cours EUR/USD"}

    current_rate = data['Close'].iloc[-1]
    current_value_eur = swap.nominal / current_rate
    initial_value_eur = swap.nominal / swap.spotRate
    mtm = current_value_eur - initial_value_eur

    return {
        "currentRate": round(current_rate, 4),
        "markToMarket": round(mtm, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
