from monitors.base_observer import BaseObserver
from weather.weather_data import WeatherData


class TrafficMonitor(BaseObserver):
    def update(self, data: WeatherData):
        self.last_result = self.strategy.predict(data)
        self.last_result["city"] = data.city
        self._print_result()

    def _print_result(self):
        r = self.last_result
        print(f"\n[TRAFFIC — {r['city']}]")
        print(f"  Congestion : {r['congestion']}")
        if r.get("confidence"):
            conf_str = " | ".join(f"{k}: {v:.0%}" for k, v in r["confidence"].items())
            print(f"  Confidence : {conf_str}")
        print(f"  Rush hour  : {'Yes' if r.get('is_rush_hour') else 'No'}")
        print(f"  Advice     : {r['advice']}")