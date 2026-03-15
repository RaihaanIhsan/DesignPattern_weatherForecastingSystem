from monitors.base_observer import BaseObserver
from weather.weather_data import WeatherData


class RetailMonitor(BaseObserver):
    def update(self, data: WeatherData):
        self.last_result = self.strategy.predict(data)
        self.last_result["city"] = data.city
        self._print_result()

    def _print_result(self):
        r = self.last_result
        print(f"\n[RETAIL — {r['city']}]")
        print(f"  Surge level   : {r['surge_level']}")
        print(f"  Demand items  : {', '.join(r['demand_items'])}")
        print(f"  Advice        : {r['advice']}")