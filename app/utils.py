from datetime import datetime, date
from typing import Dict, List
import logging
import yfinance as yf
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.WARNING)

# ---------------------
# Fonctions pour les prêts
# ---------------------

def calculate_loan_characteristics(currency: str, nominal: float, rate: float, start_date: str, maturity_date: str, payment_frequency: str, conversion_rate: float) -> Dict:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    maturity = datetime.strptime(maturity_date, "%Y-%m-%d")
    num_days = (maturity - start).days
    total_interest = nominal * rate * num_days / 36000
    nominal_eur = nominal * conversion_rate

    schedule = []
    if payment_frequency == "in_fine":
        schedule.append({
            "date": maturity_date,
            "principal_payment": nominal,
            "interest_payment": round(total_interest, 2)
        })
    else:
        freq_map = {
            "1 mois": 1,
            "3 mois": 3,
            "6 mois": 6,
            "12 mois": 12
        }
        months = freq_map.get(payment_frequency, 12)
        total_months = (maturity.year - start.year) * 12 + (maturity.month - start.month)
        num_payments = max(total_months // months, 1)
        principal_payment = nominal / num_payments
        interest_payment = total_interest / num_payments

        for i in range(num_payments):
            payment_month = (start.month + months * i - 1) % 12 + 1
            payment_year = start.year + (start.month + months * i - 1) // 12
            payment_date = start.replace(day=1).replace(year=payment_year, month=payment_month)
            schedule.append({
                "date": payment_date.strftime("%Y-%m-%d"),
                "principal_payment": round(principal_payment, 2),
                "interest_payment": round(interest_payment, 2)
            })

    return {
        "number_of_days": num_days,
        "total_interest": round(total_interest, 2),
        "nominal_in_eur": round(nominal_eur, 2),
        "repayment_schedule": schedule
    }

# ---------------------
# Fonctions pour les swaps
# ---------------------

def get_spot_rate(base_currency: str, quote_currency: str) -> float:
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
    spot = get_spot_rate(base_currency, quote_currency)
    return (forward - spot) * nominal

def calculate_hedging_ratio(total_covered: float, total_exposure: float) -> float:
    return total_covered / total_exposure if total_exposure else 0.0

def stress_test_mtm(nominal: float, forward: float, base_currency: str, quote_currency: str, variation: float = 0.05) -> float:
    stressed_forward = forward * (1 + variation)
    spot = get_spot_rate(base_currency, quote_currency)
    return (stressed_forward - spot) * nominal

def calculate_var(mtm_values: List[float]) -> float:
    if not mtm_values:
        return 0.0
    return float(np.percentile(mtm_values, 5))
