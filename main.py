from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # OK tant qu'on n'utilise pas de cookies
    allow_credentials=False,    # True => préciser les origines
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
    spotRate: float          # taux EUR/CCY saisi
    forwardRate: float       # taux EUR/CCY saisi
    nominal: float           # nominal en devise CCY
    currency: str            # USD, GBP, JPY, CNY
    bank: str
    maturity: str            # format YYYY-MM

    @field_validator("currency")
    @classmethod
    def validate_ccy(cls, v):
        v = v.upper()
        if v not in {"USD", "GBP", "JPY", "CNY"}:
            raise ValueError("currency must be one of USD, GBP, JPY, CNY")
        return v

def get_market_rate(ccy: str) -> tuple[float, str]:
    """Récupère le taux spot marché EUR/CCY (Close du jour) via yfinance."""
    pair = f"EUR{ccy}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(period="1d")
    if data.empty or "Close" not in data.columns:
        raise HTTPException(status_code=502, detail=f"Aucune donnée disponible pour la paire {pair}")
    return float(data["Close"].iloc[-1]), pair

@app.post("/add-loan")
def add_loan(loan: Loan):
    loans_data.append(loan.dict())
    return {"message": "Loan ajouté", "loan": loan}

@app.post("/add-swap")
def add_swap(swap: Swap):
    # 1) Taux marché actuel EUR/CCY
    market_rate, pair = get_market_rate(swap.currency)

    # 2) Montants en EUR basés sur les taux saisis
    spot_amount_eur = swap.nominal / swap.spotRate
    forward_amount_eur = swap.nominal / swap.forwardRate
    points_eur = forward_amount_eur - spot_amount_eur

    # 3) MtM vs marché (positif = favorable)
    mtm_vs_market_eur = forward_amount_eur - (swap.nominal / market_rate)

    swap_dict = swap.dict()
    swap_dict.update({
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2),
        "mtmVsMarketEUR": round(mtm_vs_market_eur, 2),   # <-- NEW
        "conversionRate": round(market_rate, 6),          # conservé pour compat front
        "marketRate": round(market_rate, 6),              # info explicite
        "pairUsed": pair
    })

    swaps_data.append(swap_dict)
    return {"message": "Swap ajouté", "swap": swap_dict}

@app.post("/calculate-eur-values")
def calculate_eur_values(swap: Swap):
    market_rate, pair = get_market_rate(swap.currency)

    spot_amount_eur = swap.nominal / swap.spotRate
    forward_amount_eur = swap.nominal / swap.forwardRate
    points_eur = forward_amount_eur - spot_amount_eur
    mtm_vs_market_eur = forward_amount_eur - (swap.nominal / market_rate)  # <-- NEW

    return {
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2),
        "mtmVsMarketEUR": round(mtm_vs_market_eur, 2),    # <-- NEW
        "conversionRate": round(market_rate, 6),
        "marketRate": round(market_rate, 6),
        "pairUsed": pair
    }

@app.get("/historical-eurfx")
def get_historical_eurfx(currency: str, start: date, end: date):
    pair = f"EUR{currency}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(start=start.isoformat(), end=end.isoformat())
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée disponible pour la paire {pair}")
    return {
        "pair": pair,
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "rates": data['Close'].round(4).tolist()
    }

@app.get("/kpi")
def get_kpi():
    if not loans_data or not swaps_data:
        raise HTTPException(status_code=400, detail="Pas assez de données pour calculer les KPI")

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

    # Agrégats MtM
    total_mtm_points = round(sum(s.get("pointsEUR", 0.0) for s in swaps_data), 2)
    total_mtm_vs_market = round(sum(s.get("mtmVsMarketEUR", 0.0) for s in swaps_data), 2)  # <-- NEW

    # Charts
    exposure_chart_data = {
        "labels": list(swap_by_currency.keys()),
        "datasets": [{
            "label": "Exposition par devise",
            "data": [swap_by_currency[currency] for currency in swap_by_currency],
            "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"]
        }]
    }

    maturity_counts = {}
    for s in swaps_data:
        maturity = s.get("maturity", "N/A")
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
    for s in swaps_data:
        bank = s.get("bank", "N/A")
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
        "totalMtM": total_mtm_points,             # historique (points EUR contract vs spot saisi)
        "totalMtMVsMarket": total_mtm_vs_market,  # <-- NEW (contract vs marché actuel)
        "exposureChartData": exposure_chart_data,
        "maturityChartData": maturity_chart_data,
        "bankChartData": bank_chart_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
