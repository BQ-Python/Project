import yfinance as yf

def get_spot_rate(base_currency, quote_currency):
    pair = f"{base_currency}{quote_currency}=X"  # Exemple : "EURUSD=X"
    ticker = yf.Ticker(pair)
    data = ticker.history(period="1d")
    return data["Close"].iloc[-1]

def calculate_mtm(nominal, forward, base_currency, quote_currency):
    spot = get_spot_rate(base_currency, quote_currency)
    return (forward - spot) * nominal

def calculate_hedging_ratio(total_covered, total_exposure):
    return total_covered / total_exposure if total_exposure else 0

def stress_test_mtm(nominal, forward, base_currency, quote_currency, variation=0.05):
    stressed_forward = forward * (1 + variation)
    spot = get_spot_rate(base_currency, quote_currency)
    return (stressed_forward - spot) * nominal

def calculate_var(mtm_values):
    import numpy as np
    return np.percentile(mtm_values, 5)
