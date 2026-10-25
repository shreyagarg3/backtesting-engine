import numpy as np
from typing import List

def calculate_sharpe_ratio(equity_curve: List[float], risk_free_rate: float = 0.0, periods_per_year: int = 365) -> float:
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