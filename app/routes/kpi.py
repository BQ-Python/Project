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

def save_kpi_history(deal_id: int, mtm_eur: float, var_5: float, stress_mtm: float, exposure: float, maturity_weighted: float):
    """Sauvegarde les KPI dans la table deal_kpi_history."""
    try:
        supabase.table("deal_kpi_history").insert({
            "deal_id": deal_id,
            "date": date.today().isoformat(),
            "mtm_eur": mtm_eur,
            "var_5": var_5,
            "stress_mtm": stress_mtm,
            "exposure": exposure,
            "maturity_weighted": maturity_weighted
        }).execute()
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde des KPI pour deal {deal_id}: {e}")

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

        # Cache des taux spot pour éviter les appels multiples
        spot_cache = {}

        for swap in swaps:
            if not swap.get("nominal") or not swap.get("forward_rate") or not swap.get("currency"):
                logging.warning(f"Swap {swap['id']} a des données manquantes")
                continue

            currency = swap["currency"].upper()
            pair = f"EUR{currency}=X"
            if pair not in spot_cache:
                spot_cache[pair] = get_spot_rate("EUR", currency)

            try:
                spot = spot_cache[pair]
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

                # Mise à jour des champs calculés dans la table swaps
                supabase.table("swaps").update({
                    "mtm_eur": mtm,
                    "spot_value_eur": nominal_eur
                }).eq("id", swap["id"]).execute()

                # Sauvegarde dans deal_kpi_history
                save_kpi_history(
                    deal_id=swap["id"],
                    mtm_eur=mtm,
                    var_5=calculate_var([mtm]),
                    stress_mtm=stress_up,
                    exposure=nominal_eur,
                    maturity_weighted=remaining_days
                )
            except ValueError as ve:
                logging.error(f"Erreur swap {swap['id']}: {ve}")
                continue

        for loan in loans:
            if not loan.get("nominal") or not loan.get("conversion_rate") or not loan.get("currency"):
                logging.warning(f"Loan {loan['id']} a des données manquantes")
                continue

            currency = loan["currency"].upper()
            pair = f"EUR{currency}=X"
            if pair not in spot_cache:
                spot_cache[pair] = get_spot_rate("EUR", currency)

            try:
                spot = spot_cache[pair]
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

                # Sauvegarde dans deal_kpi_history
                save_kpi_history(
                    deal_id=loan["id"],
                    mtm_eur=mtm,
                    var_5=calculate_var([mtm]),
                    stress_mtm=0.0,  # Pas de stress test pour les loans
                    exposure=nominal_eur,
                    maturity_weighted=remaining_days
                )
            except ValueError as ve:
                logging.error(f"Erreur loan {loan['id']}: {ve}")
                continue

        dashboard_data["stress_test"]["up_5_percent"] = sum(stress_up_values)
        dashboard_data["stress_test"]["down_5_percent"] = sum(stress_down_values)
        dashboard_data["var"]["var_5_percent"] = calculate_var(mtm_values)

        if total_nominal_eur > 0:
            dashboard_data["weighted_maturity"]["days"] = weighted_days / total_nominal_eur
        dashboard_data["weighted_maturity"]["total_nominal_eur"] = total_nominal_eur

        # Séries temporelles avec données historiques
        for i in range(7):
            day = (datetime.today() - timedelta(days=i)).date()
            mtm_day = 0.0
            stress_up_day = 0.0
            stress_down_day = 0.0
            for swap in swaps:
                if not swap.get("nominal") or not swap.get("forward_rate") or not swap.get("currency"):
                    continue
                currency = swap["currency"].upper()
                pair = f"EUR{currency}=X"
                try:
                    ticker = yf.Ticker(pair)
                    data = ticker.history(period="7d")
                    spot = data["Close"].loc[day.strftime("%Y-%m-%d")]
                    mtm_day += (swap["forward_rate"] - spot) * swap["nominal"]
                    stress_up_day += stress_test_mtm(swap["nominal"], swap["forward_rate"], "EUR", currency, 0.05)
                    stress_down_day += stress_test_mtm(swap["nominal"], swap["forward_rate"], "EUR", currency, -0.05)
                except Exception as e:
                    logging.error(f"Erreur série temporelle swap {swap['id']} pour {day}: {e}")
                    continue
            dashboard_data["mtm_timeseries"].append({"date": day.isoformat(), "mtm": mtm_day})
            dashboard_data["stress_test_timeseries"].append({"date": day.isoformat(), "up_5_percent": stress_up_day, "down_5_percent": stress_down_day})

        return cors_response(dashboard_data)

    except ValueError as ve:
        logging.error(f"Erreur de validation: {ve}")
        raise HTTPException(status_code=400, detail=f"Erreur de validation des données: {str(ve)}")
    except Exception as e:
        logging.error(f"Erreur dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur, veuillez réessayer plus tard")
