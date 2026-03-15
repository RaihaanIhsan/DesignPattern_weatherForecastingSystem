from weather.weather_station import WeatherStation
from monitors.traffic_monitor import TrafficMonitor
from monitors.energy_monitor import EnergyMonitor
from monitors.retail_monitor import RetailMonitor
from strategies.traffic_strategies import MLTrafficStrategy, RuleBasedTrafficStrategy
from strategies.energy_strategies import EnergyStrategy
from strategies.retail_strategies import RetailStrategy
from reports.report_factory import ReportFactory
from api.weather_api import fetch_live_weather
import config


def run_cli():
    print("=" * 50)
    print("   Weather Impact Monitoring System (CLI)")
    print("=" * 50)

    # Setup station (Singleton)
    station = WeatherStation()

    # Setup monitors with strategies
    try:
        traffic_strategy = MLTrafficStrategy()
        print("  ML model loaded successfully.")
    except Exception as e:
        print(f"  ML model failed to load ({e}), using rule-based fallback.")
        traffic_strategy = RuleBasedTrafficStrategy()

    traffic = TrafficMonitor(traffic_strategy)
    energy  = EnergyMonitor(EnergyStrategy())
    retail  = RetailMonitor(RetailStrategy())

    station.register(traffic)
    station.register(energy)
    station.register(retail)

    while True:
        print("\nOptions:")
        print("  1. Fetch live weather for a city")
        print("  2. Generate PDF report")
        print("  3. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            city = input("Enter city name: ").strip()
            print(f"\nFetching live weather for {city}...")
            data = fetch_live_weather(city)
            if data:
                print(f"\nWeather: {data.temperature}°C | Rain: {data.rainfall}mm | "
                      f"Wind: {data.windspeed}km/h | Severity: {data.severity}")
                print(f"Conditions: {data.description}")
                station.set_weather(data)

        elif choice == "2":
            if not station.current_data:
                print("  No weather data yet. Fetch a city first.")
                continue
            factory = ReportFactory()
            report  = factory.create("pdf")
            report.generate(station.current_data, [traffic, energy, retail])

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run_cli()