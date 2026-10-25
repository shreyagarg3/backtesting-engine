import numpy as np
from typing import Tuple, List


def compute_bollinger_bands(closes: List[float], window: int, num_std: float) -> Tuple[float, float, float]:
    if len(closes) < window:
        raise ValueError(f"Insufficient data ({len(closes)} bars but window requires at least {window} bars).")

    window_closes = closes[-window:]
    middle_band = float(np.mean(window_closes))
    std_dev = float(np.std(window_closes))
    
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)

    return middle_band, upper_band, lower_band