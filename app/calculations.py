def calculate_mtm(nominal, spot, forward):
    return (forward - spot) * nominal

def calculate_hedging_ratio(total_covered, total_exposure):
    return total_covered / total_exposure if total_exposure else 0

def stress_test_mtm(nominal, spot, forward, variation=0.05):
    stressed_forward = forward * (1 + variation)
    return calculate_mtm(nominal, spot, stressed_forward)

def calculate_var(mtm_values):
    import numpy as np
    return np.percentile(mtm_values, 5)

