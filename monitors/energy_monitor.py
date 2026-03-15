from monitors.base_observer import BaseObserver
from weather.weather_data import WeatherData


class EnergyMonitor(BaseObserver):
    def update(self, data: WeatherData):
        self.last_result = self.strategy.predict(data)
        self.last_result["city"] = data.city
        self._print_result()

    def _print_result(self):
        r = self.last_result
        print(f"\n[ENERGY — {r['city']}]")
        print(f"  Alert level    : {r['alert_level']}")
        print(f"  Demand change  : +{r['demand_change_pct']}%")
        print(f"  Reasons        : {', '.join(r['reasons']) if r['reasons'] else 'None'}")
        print(f"  Advice         : {r['advice']}")