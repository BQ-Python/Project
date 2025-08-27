import yfinance as yf
import logging
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.WARNING)  # Niveau par défaut : WARNING

def get_spot_rate(base_currency: str, quote_currency: str) -> float:
    """
    Récupère le taux spot à partir de Yahoo Finance pour une paire de devises.
    Exemple : EURUSD -> EURUSD=X
    """
    pair = f"{base_currency}{quote_currency}=X"
    logging.info(f"Récupération du taux pour {pair}")
    try:
        ticker = yf.Ticker(pair)
        data = ticker.history(period="1d")
        spot = data["Close"].iloc[-1]
        return float(spot)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du taux spot : {e}")
        raise ValueError(f"Impossible de récupérer le taux spot pour {pair}")

def calculate_mtm(nominal: float, forward: float, base_currency: str, quote_currency: str) -> float:
    """
    Calcule le MTM (Mark-to-Market) d'un swap.
    """
    spot = get_spot_rate(base_currency, quote_currency)
    return (forward - spot) * nominal

def calculate_hedging_ratio(total_covered: float, total_exposure: float) -> float:
    """
    Calcule le ratio de couverture.
    """
    return total_covered / total_exposure if total_exposure else 0.0

def stress_test_mtm(nominal: float, forward: float, base_currency: str, quote_currency: str, variation: float = 0.05) -> float:
    """
    Calcule le MTM en situation de stress (variation du taux forward).
    """
    stressed_forward = forward * (1 + variation)
    spot = get_spot_rate(base_currency, quote_currency)
    return (stressed_forward - spot) * nominal

def calculate_var(mtm_values: list[float]) -> float:
    """
    Calcule la Value-at-Risk (VaR) à 5% sur une liste de MTM.
    """
    if not mtm_values:
        return 0.0
    return float(np.percentile(mtm_values, 5))
