import numpy as np
from typing import List


def compute_sharpe_ratio(equity_curve: List[float], risk_free_rate: float = 0.0, periods_per_year: int = 365) -> float:
    if len(equity_curve) < 2:
        return 0.0

    returns = np.diff(equity_curve) / equity_curve[:-1]
    if len(returns) == 0 or np.std(returns, ddof=1) == 0:
        return 0.0

    avg_return = np.mean(returns)
    std_dev = np.std(returns, ddof=1)

    daily_sharpe = (avg_return - (risk_free_rate / periods_per_year)) / std_dev
    annualised_sharpe = daily_sharpe * np.sqrt(periods_per_year)

    return float(annualised_sharpe)

def compute_max_drawdown(equity_curve: List[float]) -> float:
    if len(equity_curve) < 2:
        return 0.0

    # Track the running maximum equity peak
    running_peak = np.maximum.accumulate(equity_curve)
    
    drawdowns = (equity_curve - running_peak) / running_peak
    return float(np.min(drawdowns) * 100.0)

def compute_volatility(equity_curve: List[float], periods_per_year: int = 365) -> float:
    if len(equity_curve) < 2:
        return 0.0

    returns = np.diff(equity_curve) / equity_curve[:-1]
    if len(returns) == 0:
        return 0.0

    daily_std = np.std(returns, ddof=1)
    annualised_vol = daily_std * np.sqrt(periods_per_year)

    return float(annualised_vol * 100.0)