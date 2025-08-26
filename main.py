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

# Stockage en mémoire
loans_data = []
swaps_data = []

# Modèles
class Loan(BaseModel):
    startDate: str
    maturityDate: str
    currency: str
    rate: float
    nominal: float
    conversionRate: float

class Swap(BaseModel):
    spotRate: float
    forwardRate: float
    nominal: float
    currency: str
    bank: str
    maturity: str  # format YYYY-MM

# Routes
@app.post("/add-loan")
def add_loan(loan: Loan):
    loans_data.append(loan.dict())
    return {"message": "Loan ajouté", "loan": loan}

@app.post("/add-swap")
def add_swap(swap: Swap):
    pair = f"EUR{swap.currency}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(period="1d")

    if data.empty or 'Close' not in data.columns:
        return {"error": f"Aucune donnée disponible pour la paire {pair}"}

    conversion_rate = data['Close'].iloc[-1]
    spot_amount_eur = (swap.nominal / swap.spotRate) * conversion_rate
    forward_amount_eur = (swap.nominal / swap.forwardRate) * conversion_rate
    mtm = forward_amount_eur - spot_amount_eur

    swap_dict = swap.dict()
    swap_dict["mtm"] = mtm
    swap_dict["conversionRate"] = conversion_rate

    swaps_data.append(swap_dict)
    return {"message": "Swap ajouté", "swap": swap_dict}

@app.get("/calculate-points")
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

@app.get("/kpi")
def get_kpi():
    if not loans_data or not swaps_data:
        return {"error": "Pas assez de données pour calculer les KPI"}

    loan_by_currency = {}
    for loan in loans_data:
        loan_by_currency[loan["currency"]] = loan_by_currency.get(loan["currency"], 0) + loan["nominal"]

    swap_by_currency = {}
    for swap in swaps_data:
        swap_by_currency[swap["currency"]] = swap_by_currency.get(swap["currency"], 0) + swap["nominal"]

    hedging_ratios = {}
    for currency in loan_by_currency:
        loan_nominal = loan_by_currency[currency]
        swap_nominal = swap_by_currency.get(currency, 0)
        ratio = (swap_nominal / loan_nominal) * 100 if loan_nominal > 0 else 0
        hedging_ratios[currency] = round(ratio, 2)

    total_mtm = sum(swap["mtm"] for swap in swaps_data)

    exposure_chart_data = {
        "labels": list(swap_by_currency.keys()),
        "datasets": [{
            "label": "Exposition par devise",
            "data": [swap_by_currency[currency] for currency in swap_by_currency],
            "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"]
        }]
    }

    maturity_counts = {}
    for swap in swaps_data:
        maturity = swap.get("maturity", "N/A")
        maturity_counts[maturity] = maturity_counts.get(maturity, 0) + 1

    maturity_chart_data = {
        "labels": list(maturity_counts.keys()),
        "datasets": [{
            "label": "Nombre de swaps par maturité",
            "data": list(maturity_counts.values()),
            "backgroundColor": "#4BC0C0"
        }]
    }

    bank_counts = {}
    for swap in swaps_data:
        bank = swap.get("bank", "N/A")
        bank_counts[bank] = bank_counts.get(bank, 0) + 1

    bank_chart_data = {
        "labels": list(bank_counts.keys()),
        "datasets": [{
            "label": "Répartition par banque",
            "data": list(bank_counts.values()),
            "backgroundColor": ["#9966FF", "#FF9F40", "#FF6384", "#36A2EB"]
        }]
    }

    return {
        "hedgingRatio": hedging_ratios,
        "totalMtM": round(total_mtm, 2),
        "exposureChartData": exposure_chart_data,
        "maturityChartData": maturity_chart_data,
        "bankChartData": bank_chart_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
