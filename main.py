from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loans_data = []
swaps_data = []

class Loan(BaseModel):
    startDate: str
    maturityDate: str
    currency: str
    rate: float
    nominal: float
    conversionRate: float

class Swap(BaseModel):
    startDate: str
    maturityDate: str
    spotRate: float
    forwardRate: float
    nominal: float
    currency: str
    bank: str

    @field_validator("currency")
    @classmethod
    def validate_ccy(cls, v):
        v = v.upper()
        if v not in {"USD", "GBP", "JPY", "CNY"}:
            raise ValueError("currency must be one of USD, GBP, JPY, CNY")
        return v

def get_market_rate(ccy: str) -> tuple[float, str]:
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
    market_rate, pair = get_market_rate(swap.currency)
    spot_amount_eur = swap.nominal / swap.spotRate
    forward_amount_eur = swap.nominal / swap.forwardRate
    points_eur = forward_amount_eur - spot_amount_eur
    mtm_vs_market_eur = forward_amount_eur - (swap.nominal / market_rate)

    swap_dict = swap.dict()
    swap_dict.update({
        "spotAmountEUR": round(spot_amount_eur, 2),
        "forwardAmountEUR": round(forward_amount_eur, 2),
        "pointsEUR": round(points_eur, 2),
        "mtmVsMarketEUR": round(mtm_vs_market_eur, 2),
        "conversionRate": round(market_rate, 6),
        "marketRate": round(market_rate, 6),
        "pairUsed": pair
    })

    swaps_data.append(swap_dict)
    return {"message": "Swap ajouté", "swap": swap_dict}

@app.get("/kpi/advanced")
def get_advanced_kpi():
    currency_pairs = ["JPY", "CHF", "USD", "CNY", "GBP", "BRL", "MXN", "AUD", "CAD"]
    volatilities = {}

    for ccy in currency_pairs:
        pair = f"EUR{ccy}=X"
        ticker = yf.Ticker(pair)
        data = ticker.history(period="7d")
        if data.empty or "Close" not in data.columns:
            volatilities[ccy] = None
            continue
        returns = data["Close"].pct_change().dropna()
        volatility = np.std(returns[-5:]) * 100
        volatilities[ccy] = round(volatility, 2)

    if not swaps_data:
        return JSONResponse(content={
            "message": "Pas de swaps disponibles pour calculer la VaR",
            "volatilities": volatilities,
            "VaR_95": None,
            "VaR_99": None
        })

    exposures = []
    returns_matrix = []

    for swap in swaps_data:
        ccy = swap["currency"]
        pair = f"EUR{ccy}=X"
        ticker = yf.Ticker(pair)
        data = ticker.history(period="7d")
        if data.empty or "Close" not in data.columns:
            continue
        returns = data["Close"].pct_change().dropna()
        if len(returns) < 5:
            continue
        exposures.append(swap["nominal"] / swap["forwardRate"])
        returns_matrix.append(returns[-5:].values)

    if not exposures or not returns_matrix:
        return JSONResponse(content={
            "message": "Données insuffisantes pour calculer la VaR",
            "volatilities": volatilities,
            "VaR_95": None,
            "VaR_99": None
        })

    exposures = np.array(exposures)
    returns_matrix = np.array(returns_matrix)
    cov_matrix = np.cov(returns_matrix)
    portfolio_variance = exposures @ cov_matrix @ exposures.T
    portfolio_std = np.sqrt(portfolio_variance)

    VaR_95 = round(portfolio_std * 1.65, 2)
    VaR_99 = round(portfolio_std * 2.33, 2)

    return {
        "volatilities": volatilities,
        "VaR_95": VaR_95,
        "VaR_99": VaR_99
    }

@app.get("/var/history")
def get_var_history(confidence: int = Query(95), horizon: int = Query(30)):
    if not swaps_data:
        return JSONResponse(content={"labels": [], "datasets": []})

    confidence_multiplier = {95: 1.65, 99: 2.33}.get(confidence, 1.65)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    date_range = [start_date + timedelta(days=i) for i in range(31)]
    date_labels = [d.strftime("%Y-%m-%d") for d in date_range]
    var_values = []

    for current_date in date_range:
        exposures = []
        returns_matrix = []

        for swap in swaps_data:
            ccy = swap["currency"]
            pair = f"EUR{ccy}=X"
            ticker = yf.Ticker(pair)
            history_start = current_date - timedelta(days=horizon + 5)
            history_end = current_date
            data = ticker.history(start=history_start.strftime("%Y-%m-%d"), end=history_end.strftime("%Y-%m-%d"))

            if data.empty or "Close" not in data.columns:
                continue

            returns = data["Close"].pct_change().dropna()
            if len(returns) < 5:
                continue

            exposures.append(swap["nominal"] / swap["forwardRate"])
            returns_matrix.append(returns[-5:].values)

        if not exposures or not returns_matrix:
            var_values.append(None)
            continue

        exposures = np.array(exposures)
        returns_matrix = np.array(returns_matrix)
        cov_matrix = np.cov(returns_matrix)
        portfolio_variance = exposures @ cov_matrix @ exposures.T
        portfolio_std = np.sqrt(portfolio_variance)
        var_value = round(portfolio_std * confidence_multiplier, 2)
        var_values.append(var_value)

    filtered_labels = [label for label, value in zip(date_labels, var_values) if value is not None]
    filtered_values = [value for value in var_values if value is not None]

    chart_data = {
        "labels": filtered_labels,
        "datasets": [{
            "label": f"VaR {confidence}% EUR",
            "data": filtered_values,
            "borderColor": "#F44336",
            "fill": False
        }]
    }

    return JSONResponse(content=chart_data)

@app.get("/historical-eurfx")
def get_historical_fx(currency: str, start: str, end: str):
    pair = f"EUR{currency}=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(start=start, end=end)
    if data.empty or "Close" not in data.columns:
        raise HTTPException(status_code=404, detail="Données introuvables")
    return {
        "dates": data.index.strftime("%Y-%m-%d").tolist(),
        "values": data["Close"].round(4).tolist()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
