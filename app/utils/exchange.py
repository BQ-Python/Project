import yfinance as yf
import logging

# Configuration du logging
logging.basicConfig(level=logging.WARNING)

def get_spot_rate(base_currency: str, quote_currency: str) -> float:
    """
    Récupère le taux spot à partir de Yahoo Finance pour une paire de devises.
    Exemple : EURUSD -> EURUSD=X
    """
    pair = f"{base_currency}{quote_currency}=X"
    logging.info(f"Récupération du taux pour {pair}")
    try:
        data = yf.download(pair, period="1d", interval="1d")
        spot = data["Close"].iloc[-1]
        return float(spot)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du taux spot : {e}")
        raise ValueError(f"Impossible de récupérer le taux spot pour {pair}")
