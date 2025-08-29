from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import date, datetime, timedelta
from typing import List, Optional
import yfinance as yf
import numpy as np
from app.supabase_client import supabase
from app.utils import get_spot_rate, calculate_mtm, stress_test_mtm, calculate_var
import logging

router = APIRouter()
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
def get_risk_dashboard(
    deal_ids: Optional[List[int]] = Query(None),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    try:
        swaps_response = supabase.table("swaps").select("*").execute()
        loans_response = supabase.table("loans").select("*").execute()

        swaps = swaps_response.data
        loans = loans_response.data

        # Filtrage par deal_id
        if deal_ids:
            swaps = [s for s in swaps if s["id"] in deal_ids]
            loans = [l for l in loans if l["id"] in deal_ids]

        # Filtrage par période
        if start_date:
            swaps = [s for s in swaps if datetime.fromisoformat(s["start_date"]).date() >= start_date]
            loans = [l for l in loans if datetime.fromisoformat(l["start_date"]).date() >= start_date]
        if end_date:
            swaps = [s for s in swaps if datetime.fromisoformat(s["maturity_date"]).date() <= end_date]
            loans = [l for l in loans if datetime.fromisoformat(l["maturity_date"]).date() <= end_date]

        dashboard_data = {
            "mtm_summary": {"total_mtm_eur": 0.0, "by_currency": {}},
            "stress_test": {"up_5_percent": 0.0, "down_5_percent": 0.0},
            "var": {"var_5_percent": 0.0},
            "weighted_maturity": {"days": 0.0, "total_nominal_eur": 0.0},
            "exposure_by_currency": {},
            "mtm_timeseries": [],
            "stress_test_timeseries": []
        }

        mtm_values = []
        stress_up_values = []
        stress_down_values = []
        total_nominal_eur = 0.0
        weighted_days = 0.0
        today = date.today()

        for swap in swaps:
            currency = swap["currency"].upper()
            try:
                spot = get_spot_rate("EUR", currency)
                mtm = calculate_mtm(swap["nominal"], swap["forward_rate"], "EUR", currency)
                mtm_values.append(mtm)
                dashboard_data["mtm_summary"]["total_mtm_eur"] += mtm
                dashboard_data["mtm_summary"]["by_currency"][currency] = dashboard_data["mtm_summary"]["by_currency"].get(currency, 0.0) + mtm

                stress_up = stress_test_mtm(swap["nominal"], swap["forward_rate"], "EUR", currency, 0.05)
                stress_down = stress_test_mtm(swap["nominal"], swap["forward_rate"], "EUR", currency, -0.05)
                stress_up_values.append(stress_up)
                stress_down_values.append(stress_down)

                maturity_date = datetime.fromisoformat(swap["maturity_date"]).date()
                remaining_days = (maturity_date - today).days
                nominal_eur = swap["nominal"] * spot
                weighted_days += remaining_days * nominal_eur
                total_nominal_eur += nominal_eur

                dashboard_data["exposure_by_currency"][currency] = dashboard_data["exposure_by_currency"].get(currency, 0.0) + nominal_eur
            except Exception as e:
                logging.error(f"Erreur swap {swap['id']}: {e}")

        for loan in loans:
            currency = loan["currency"].upper()
            try:
                spot = get_spot_rate("EUR", currency)
                mtm = (loan["nominal"] * spot) - (loan["nominal"] * loan["conversion_rate"])
                mtm_values.append(mtm)
                dashboard_data["mtm_summary"]["total_mtm_eur"] += mtm
                dashboard_data["mtm_summary"]["by_currency"][currency] = dashboard_data["mtm_summary"]["by_currency"].get(currency, 0.0) + mtm

                maturity_date = datetime.fromisoformat(loan["maturity_date"]).date()
                remaining_days = (maturity_date - today).days
                nominal_eur = loan["nominal"] * loan["conversion_rate"]
                weighted_days += remaining_days * nominal_eur
                total_nominal_eur += nominal_eur

                dashboard_data["exposure_by_currency"][currency] = dashboard_data["exposure_by_currency"].get(currency, 0.0) + nominal_eur
            except Exception as e:
                logging.error(f"Erreur loan {loan['id']}: {e}")

        dashboard_data["stress_test"]["up_5_percent"] = sum(stress_up_values)
        dashboard_data["stress_test"]["down_5_percent"] = sum(stress_down_values)
        dashboard_data["var"]["var_5_percent"] = calculate_var(mtm_values)

        if total_nominal_eur > 0:
            dashboard_data["weighted_maturity"]["days"] = weighted_days / total_nominal_eur
        dashboard_data["weighted_maturity"]["total_nominal_eur"] = total_nominal_eur

        # Séries temporelles
        for i in range(7):
            day = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            mtm_day = sum(mtm_values)
            stress_up_day = sum(stress_up_values)
            stress_down_day = sum(stress_down_values)
            dashboard_data["mtm_timeseries"].append({"date": day, "mtm": mtm_day})
            dashboard_data["stress_test_timeseries"].append({"date": day, "up_5_percent": stress_up_day, "down_5_percent": stress_down_day})

        return cors_response(dashboard_data)

    except Exception as e:
        logging.error(f"Erreur dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
