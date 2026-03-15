from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData


class EnergyStrategy(BaseStrategy):
    def predict(self, data: WeatherData) -> dict:
        demand_change = 0
        reasons = []

        if data.temperature > 38:
            demand_change += 35
            reasons.append("extreme heat — AC surge")
        elif data.temperature > 30:
            demand_change += 20
            reasons.append("high heat — elevated AC usage")
        elif data.temperature < 5:
            demand_change += 25
            reasons.append("cold snap — heating surge")
        elif data.temperature < 15:
            demand_change += 10
            reasons.append("cool weather — moderate heating")

        if data.windspeed > 50:
            demand_change += 5
            reasons.append("strong winds affecting grid")

        level = "HIGH" if demand_change >= 30 else "MEDIUM" if demand_change >= 10 else "LOW"

        return {
            "demand_change_pct": demand_change,
            "alert_level":       level,
            "reasons":           reasons,
            "advice": f"Grid load expected to change by +{demand_change}%. "
                      f"{'Alert operators.' if level == 'HIGH' else 'Monitor closely.' if level == 'MEDIUM' else 'Normal operations.'}",
        }