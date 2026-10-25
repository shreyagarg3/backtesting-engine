import numpy as np
from typing import List, Tuple


def compute_stochastic(highs: List[float], lows: List[float], closes: List[float], k_window: int, d_window: int) -> Tuple[float, float]:
    required_len = k_window + d_window - 1
    if len(closes) < required_len:
        raise ValueError(f"Insufficient data ({len(closes)} bars but window requires at least {required_len} bars).")

    k_values = [0] * d_window
    for i in range(d_window):
        end_idx = len(closes) - i
        start_idx = end_idx - k_window

        high_window = highs[start_idx:end_idx]
        low_window = lows[start_idx:end_idx]
        current_close = closes[end_idx - 1]

        lowest_low = np.min(high_window)
        highest_high = np.max(low_window)

        if highest_high == lowest_low:
            k = 50.0
        else:
            k = 100.0 * (current_close - lowest_low) / (highest_high - lowest_low)
        
        k_values[i] = k

    percent_k = k_values[d_window - 1]
    percent_d = float(np.mean(k_values))

    return percent_k, percent_d