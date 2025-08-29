from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import date, datetime, timedelta
import yfinance as yf
import numpy as np
from app.supabase_client import supabase
from app.utils import get_spot_rate, calculate_mtm, stress_test_mtm, calculate_var
import logging
from typing import Dict, List

router = APIRouter()

# Configuration du logging
logging.basicConfig(level=logging.INFO)

def cors_response(content):
    return JSONResponse(
        content=content,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get("/kpi/dashboard")
def get_risk_dashboard():
    try:
        # Récupérer les données des swaps et prêts depuis Supabase
        swaps_response = supabase.table("swaps").select("*").execute()
        loans_response = supabase.table("loans").select("*").execute()

        swaps = swaps_response.data
        loans = loans_response.data

        # Initialisation des métriques
        dashboard_data = {
            "mtm_summary": {"total_mtm_eur": 0.0, "by_currency": {}},
            "stress_test": {"up_5_percent": 0.0, "down_5_percent": 0.0},
            "var": {"var_5_percent": 0.0},
            "weighted_maturity": {"days": 0.0, "total_nominal_eur": 0.0},
            "exposure_by_currency": {},
            "mtm_timeseries": [],
            "stress_test_timeseries": []
        }

        # 1. Calcul du MTM total et par devise
        mtm_values = []
        for swap in swaps:
            base_currency = "EUR"
            quote_currency = swap["currency"].upper()
            try:
                mtm = calculate_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency)
                mtm_values.append(mtm)
                dashboard_data["mtm_summary"]["total_mtm_eur"] += mtm
                dashboard_data["mtm_summary"]["by_currency"][quote_currency] = (
                    dashboard_data["mtm_summary"]["by_currency"].get(quote_currency, 0.0) + mtm
                )
            except Exception as e:
                logging.error(f"Erreur calcul MTM pour swap {swap['id']}: {e}")

        for loan in loans:
            base_currency = "EUR"
            quote_currency = loan["currency"].upper()
            try:
                spot_rate = get_spot_rate(base_currency, quote_currency)
                mtm = (loan["nominal"] * spot_rate) - (loan["nominal"] * loan["conversion_rate"])
                mtm_values.append(mtm)
                dashboard_data["mtm_summary"]["total_mtm_eur"] += mtm
                dashboard_data["mtm_summary"]["by_currency"][quote_currency] = (
                    dashboard_data["mtm_summary"]["by_currency"].get(quote_currency, 0.0) + mtm
                )
            except Exception as e:
                logging.error(f"Erreur calcul MTM pour loan {loan['id']}: {e}")

        # 2. Stress Test (±5%)
        stress_up_values = []
        stress_down_values = []
        for swap in swaps:
            base_currency = "EUR"
            quote_currency = swap["currency"].upper()
            try:
                stress_up = stress_test_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency, variation=0.05)
                stress_down = stress_test_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency, variation=-0.05)
                stress_up_values.append(stress_up)
                stress_down_values.append(stress_down)
            except Exception as e:
                logging.error(f"Erreur stress test pour swap {swap['id']}: {e}")

        dashboard_data["stress_test"]["up_5_percent"] = sum(stress_up_values)
        dashboard_data["stress_test"]["down_5_percent"] = sum(stress_down_values)

        # 3. Calcul de la VaR à 5%
        dashboard_data["var"]["var_5_percent"] = calculate_var(mtm_values)

        # 4. Maturité pondérée par le capital
        total_nominal_eur = 0.0
        weighted_days = 0.0
        today = date.today()
        for swap in swaps:
            try:
                maturity_date = datetime.fromisoformat(swap["maturity_date"]).date()
                remaining_days = (maturity_date - today).days
                nominal_eur = swap["nominal"] * get_spot_rate("EUR", swap["currency"].upper())
                weighted_days += remaining_days * nominal_eur
                total_nominal_eur += nominal_eur
            except Exception as e:
                logging.error(f"Erreur maturité pour swap {swap['id']}: {e}")

        for loan in loans:
            try:
                maturity_date = datetime.fromisoformat(loan["maturity_date"]).date()
                remaining_days = (maturity_date - today).days
                nominal_eur = loan["nominal"] * loan["conversion_rate"]
                weighted_days += remaining_days * nominal_eur
                total_nominal_eur += nominal_eur
            except Exception as e:
                logging.error(f"Erreur maturité pour loan {loan['id']}: {e}")

        if total_nominal_eur > 0:
            dashboard_data["weighted_maturity"]["days"] = weighted_days / total_nominal_eur
        dashboard_data["weighted_maturity"]["total_nominal_eur"] = total_nominal_eur

        # 5. Exposition par devise
        for swap in swaps:
            currency = swap["currency"].upper()
            nominal_eur = swap["nominal"] * get_spot_rate("EUR", currency)
            dashboard_data["exposure_by_currency"][currency] = (
                dashboard_data["exposure_by_currency"].get(currency, 0.0) + nominal_eur
            )

        for loan in loans:
            currency = loan["currency"].upper()
            nominal_eur = loan["nominal"] * loan["conversion_rate"]
            dashboard_data["exposure_by_currency"][currency] = (
                dashboard_data["exposure_by_currency"].get(currency, 0.0) + nominal_eur
            )

        # 6. Séries temporelles pour MTM et Stress Test
        periods = 7  # Données sur 7 jours
        for i in range(periods):
            day = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            mtm_day = 0.0
            stress_up_day = 0.0
            stress_down_day = 0.0
            for swap in swaps:
                try:
                    base_currency = "EUR"
                    quote_currency = swap["currency"].upper()
                    mtm_day += calculate_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency)
                    stress_up_day += stress_test_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency, 0.05)
                    stress_down_day += stress_test_mtm(swap["nominal"], swap["forward_rate"], base_currency, quote_currency, -0.05)
                except Exception:
                    continue
            dashboard_data["mtm_timeseries"].append({"date": day, "mtm": mtm_day})
            dashboard_data["stress_test_timeseries"].append({"date": day, "up_5_percent": stress_up_day, "down_5_percent": stress_down_day})

        return cors_response(dashboard_data)
    except Exception as e:
        logging.error(f"Erreur dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
