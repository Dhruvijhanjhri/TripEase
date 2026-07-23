"""
Revenue Forecasting using Weighted Moving Average (WMA)

Formula:

Forecast =
0.4 * Yesterday +
0.3 * Day-2 +
0.2 * Day-3 +
0.1 * Day-4

Generates:
- Forecast values
- Upper confidence band (+10%)
- Lower confidence band (-10%)
"""

from typing import List


class RevenueForecaster:

    def __init__(self):

        self.weights = [0.4, 0.3, 0.2, 0.1]

    def forecast(self, revenue_history: List[float], future_days: int = 30):

        history = revenue_history.copy()

        predictions = []

        for _ in range(future_days):

            if len(history) >= 4:

                next_value = (
                    history[-1] * self.weights[0]
                    + history[-2] * self.weights[1]
                    + history[-3] * self.weights[2]
                    + history[-4] * self.weights[3]
                )

            elif history:

                next_value = sum(history) / len(history)

            else:

                next_value = 0

            predictions.append(round(next_value, 2))

            history.append(next_value)

        upper = [round(x * 1.10, 2) for x in predictions]

        lower = [round(x * 0.90, 2) for x in predictions]

        return predictions, upper, lower
