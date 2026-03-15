from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData


class RetailStrategy(BaseStrategy):
    def predict(self, data: WeatherData) -> dict:
        items = []
        surge_level = "LOW"

        if data.rainfall > 10:
            items += ["umbrellas", "raincoats", "waterproof boots"]
            surge_level = "HIGH"
        elif data.rainfall > 2:
            items += ["umbrellas", "light jackets"]
            surge_level = "MEDIUM"

        if data.temperature > 38:
            items += ["cold drinks", "ice cream", "fans", "sunscreen"]
            surge_level = "HIGH"
        elif data.temperature > 28:
            items += ["cold drinks", "sunscreen"]

        if data.windspeed > 50:
            items += ["generators", "emergency supplies", "candles"]
            surge_level = "HIGH"

        if data.temperature < 5:
            items += ["heaters", "hot beverages", "blankets"]
            surge_level = "MEDIUM" if surge_level == "LOW" else surge_level

        items = list(dict.fromkeys(items))  # deduplicate

        return {
            "surge_level":    surge_level,
            "demand_items":   items if items else ["No unusual demand expected"],
            "advice": f"Stock up on: {', '.join(items)}" if items else "Normal inventory levels sufficient.",
        }