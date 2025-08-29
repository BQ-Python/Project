import numpy as np
import logging
from app.utils.exchange import get_spot_rate

logging.basicConfig(level=logging.WARNING)

def calculate_mtm(nominal: float, forward: float, base_currency: str, quote_currency: str) -> float:
    """
    Calcule le MTM (Mark-to-Market) d'un swap.
    
    Args:
        nominal: Montant notionnel du swap
        forward: Taux forward du swap
        base_currency: Devise de base (ex. EUR)
        quote_currency: Devise de cotation (ex. USD)
    
    Returns:
        float: Valeur MTM en devise de base
    """
    spot = get_spot_rate(base_currency, quote_currency)
    return (forward - spot) * nominal

def calculate_hedging_ratio(total_covered: float, total_exposure: float) -> float:
    """
    Calcule le ratio de couverture.
    
    Args:
        total_covered: Montant couvert
        total_exposure: Exposition totale
    
    Returns:
        float: Ratio de couverture
    """
    return total_covered / total_exposure if total_exposure else 0.0

def stress_test_mtm(nominal: float, forward: float, base_currency: str, quote_currency: str, variation: float = 0.05) -> float:
    """
    Calcule le MTM en situation de stress (variation du taux forward).
    
    Args:
        nominal: Montant notionnel
        forward: Taux forward
        base_currency: Devise de base
        quote_currency: Devise de cotation
        variation: Variation appliquée au taux forward (ex. 0.05 pour +5%)
    
    Returns:
        float: MTM stressé
    """
    stressed_forward = forward * (1 + variation)
    spot = get_spot_rate(base_currency, quote_currency)
    return (stressed_forward - spot) * nominal

def calculate_var(mtm_values: list[float]) -> float:
    """
    Calcule la Value-at-Risk (VaR) à 5% sur une liste de MTM.
    
    Args:
        mtm_values: Liste des valeurs MTM
    
    Returns:
        float: VaR à 5%
    """
    if not mtm_values:
        return 0.0
    return float(np.percentile(mtm_values, 5))
