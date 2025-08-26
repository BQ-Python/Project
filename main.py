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
    currency: str

@app.post("/calculate-points")
def calculate_points(swap: Swap):
    pair = f"EUR{swap.currency}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(period="1d")

    if data.empty or 'Close' not in data.columns:
        return {"error": f"Aucune donnée disponible pour la paire {pair}"}

    conversion_rate = data['Close'].iloc[-1]

    spot_amount_eur = (swap.nominal / swap.spotRate) * conversion_rate
    forward_amount_eur = (swap.nominal / swap.forwardRate) * conversion_rate
    points_eur = forward_amount_eur - spot_amount_eur

    return {
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2),
        "conversionRate": round(conversion_rate, 4),
        "pairUsed": pair
    }

@app.get("/historical-eurfx")
def get_historical_eurfx(currency: str, start: date, end: date):
    pair = f"EUR{currency}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(start=start.isoformat(), end=end.isoformat())
    if data.empty:
        return {"error": f"Aucune donnée disponible pour la paire {pair}"}
    return {
        "pair": pair,
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "rates": data['Close'].round(4).tolist()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
