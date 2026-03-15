from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WeatherData:
    city: str
    country: str
    temperature: float
    rainfall: float
    windspeed: float
    visibility: float
    humidity: float
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "UNKNOWN"
    description: str = ""


# ── Decorator Pattern ─────────────────────────────────────────────────────────

class WeatherDecorator:
    """Base decorator — wraps a WeatherData and delegates all attribute access."""
    def __init__(self, weather_data: WeatherData):
        self._data = weather_data

    def __getattr__(self, name):
        return getattr(self._data, name)


class SeverityDecorator(WeatherDecorator):
    """Enriches WeatherData with a severity label."""
    def __init__(self, weather_data: WeatherData):
        super().__init__(weather_data)
        self._data.severity = self._compute_severity()

    def _compute_severity(self):
        r = self._data.rainfall
        w = self._data.windspeed
        v = self._data.visibility
        if r > 20 or w > 60 or v < 500:
            return "EXTREME"
        elif r > 10 or w > 40 or v < 2000:
            return "HIGH"
        elif r > 2 or w > 20:
            return "MODERATE"
        return "LOW"


class DescriptionDecorator(WeatherDecorator):
    """Adds a human-readable description based on conditions."""
    def __init__(self, weather_data: WeatherData):
        super().__init__(weather_data)
        self._data.description = self._compute_description()

    def _compute_description(self):
        parts = []
        if self._data.rainfall > 10:
            parts.append("heavy rain")
        elif self._data.rainfall > 2:
            parts.append("light rain")
        if self._data.windspeed > 50:
            parts.append("strong winds")
        if self._data.visibility < 1000:
            parts.append("low visibility")
        if self._data.temperature > 40:
            parts.append("extreme heat")
        elif self._data.temperature < 0:
            parts.append("freezing temperatures")
        return ", ".join(parts) if parts else "clear conditions"


def enrich_weather(data: WeatherData) -> WeatherData:
    """Apply all decorators to a WeatherData object."""
    data = SeverityDecorator(data)
    data = DescriptionDecorator(data)
    return data