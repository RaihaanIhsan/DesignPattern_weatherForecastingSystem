from abc import ABC, abstractmethod
from weather.weather_data import WeatherData


class BaseObserver(ABC):
    """Observer interface — all monitors implement this."""

    def __init__(self, strategy):
        self.strategy = strategy
        self.last_result: dict = {}

    @abstractmethod
    def update(self, weather_data: WeatherData):
        pass

    def set_strategy(self, strategy):
        self.strategy = strategy