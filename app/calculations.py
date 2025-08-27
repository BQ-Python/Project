import yfinance as yf

import logging
logging.basicConfig(level=logging.WARNING)  # Limiter les journaux au niveau WARNING

def get_spot_rate(base_currency, quote_currency):
    pair = f"{base_currency}{quote_currency}=X"
    logging.info(f"Récupération du taux pour {pair}")
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
