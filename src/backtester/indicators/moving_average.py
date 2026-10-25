import numpy as np
from typing import List


def compute_sma(closes: List[float], window: int) -> float:
    if len(closes) < window:
        raise ValueError(f"Insufficient data ({len(closes)} bars but window requires at least {window} bars).")

    return float(np.mean(closes[-window:]))