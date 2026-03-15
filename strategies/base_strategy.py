from abc import ABC, abstractmethod
from weather.weather_data import WeatherData


class BaseStrategy(ABC):
    @abstractmethod
    def predict(self, weather_data: WeatherData) -> dict:
        pass