import joblib
import pandas as pd
from datetime import datetime
from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData
import config


class MLTrafficStrategy(BaseStrategy):
    """Uses the trained Random Forest model to predict congestion."""

    def __init__(self):
        self.model        = joblib.load(config.MODEL_PATH)
        self.city_enc     = joblib.load(config.CITY_ENCODER_PATH)
        self.country_enc  = joblib.load(config.COUNTRY_ENCODER_PATH)
        self.features     = joblib.load(config.FEATURE_LIST_PATH)

    def predict(self, data: WeatherData) -> dict:
        now = datetime.now()
        hour        = now.hour
        day_of_week = now.weekday()
        month       = now.month
        is_rush     = 1 if hour in range(7, 10) or hour in range(17, 20) else 0
        is_weekend  = 1 if day_of_week >= 5 else 0

        city_info = config.CITIES.get(data.city, {})
        rain_sensitivity = city_info.get("rain_sensitivity", 0.5)

        try:
            city_encoded    = self.city_enc.transform([data.city])[0]
        except ValueError:
            city_encoded    = 0

        try:
            country_encoded = self.country_enc.transform([data.country])[0]
        except ValueError:
            country_encoded = 0

        row = pd.DataFrame([[
            data.temperature, data.rainfall, data.windspeed,
            data.visibility, data.humidity,
            hour, day_of_week, month, is_rush, is_weekend,
            city_encoded, country_encoded, rain_sensitivity
        ]], columns=self.features)

        prediction = self.model.predict(row)[0]
        proba      = self.model.predict_proba(row)[0]
        classes    = self.model.classes_
        confidence = {c: round(float(p), 2) for c, p in zip(classes, proba)}

        advice = {
            "HIGH":   "Avoid highways. Expect 30–50 min delays. Use alternate routes.",
            "MEDIUM": "Moderate slowdowns expected. Allow extra 15–20 mins.",
            "LOW":    "Traffic flowing normally.",
        }

        return {
            "congestion":  prediction,
            "confidence":  confidence,
            "advice":      advice.get(prediction, ""),
            "is_rush_hour": bool(is_rush),
        }


class RuleBasedTrafficStrategy(BaseStrategy):
    """Fallback strategy if ML model is unavailable."""

    def predict(self, data: WeatherData) -> dict:
        if data.rainfall > 15 or data.visibility < 1000:
            level = "HIGH"
        elif data.rainfall > 5 or data.windspeed > 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "congestion": level,
            "confidence": {},
            "advice": f"Rule-based prediction for {data.city}.",
            "is_rush_hour": False,
        }