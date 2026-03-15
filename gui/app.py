import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os

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


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Impact Monitoring System")
        self.root.geometry("820x640")
        self.root.configure(bg="#1a1a2e")

        self._setup_station()
        self._build_ui()

    def _setup_station(self):
        self.station = WeatherStation()
        try:
            traffic_strategy = MLTrafficStrategy()
        except Exception:
            traffic_strategy = RuleBasedTrafficStrategy()

        self.traffic = TrafficMonitor(traffic_strategy)
        self.energy  = EnergyMonitor(EnergyStrategy())
        self.retail  = RetailMonitor(RetailStrategy())

        self.station.register(self.traffic)
        self.station.register(self.energy)
        self.station.register(self.retail)

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f3460", pady=12)
        header.pack(fill="x")
        tk.Label(header, text="🌦  Weather Impact Monitoring System",
                 font=("Helvetica", 16, "bold"),
                 bg="#0f3460", fg="white").pack()

        # Input row
        input_frame = tk.Frame(self.root, bg="#16213e", pady=10, padx=16)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="City:", bg="#16213e", fg="white",
                 font=("Helvetica", 11)).pack(side="left")

        self.city_var = tk.StringVar(value="Karachi")
        city_options = list(config.CITIES.keys())
        self.city_combo = ttk.Combobox(input_frame, textvariable=self.city_var,
                                        values=city_options, width=18,
                                        font=("Helvetica", 11))
        self.city_combo.pack(side="left", padx=8)

        # allow typing any city
        self.city_combo.configure(state="normal")

        tk.Button(input_frame, text="Fetch Weather",
                  command=self._fetch_weather,
                  bg="#e63946", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=12, pady=4).pack(side="left", padx=6)

        tk.Button(input_frame, text="Generate PDF Report",
                  command=self._generate_report,
                  bg="#2a9d8f", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=12, pady=4).pack(side="left", padx=6)

        # Weather summary strip
        self.summary_var = tk.StringVar(value="No data yet.")
        summary_bar = tk.Frame(self.root, bg="#0f3460", pady=6, padx=16)
        summary_bar.pack(fill="x")
        tk.Label(summary_bar, textvariable=self.summary_var,
                 bg="#0f3460", fg="#a8dadc",
                 font=("Helvetica", 10)).pack(anchor="w")

        # Tabs for each monitor
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)

        self.traffic_text = self._make_tab(notebook, "Traffic")
        self.energy_text  = self._make_tab(notebook, "Energy")
        self.retail_text  = self._make_tab(notebook, "Retail")
        self.log_text     = self._make_tab(notebook, "Log")

    def _make_tab(self, notebook, label):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=f"  {label}  ")
        text = scrolledtext.ScrolledText(frame, wrap="word",
                                          font=("Courier", 10),
                                          bg="#0d0d1a", fg="#e0e0e0",
                                          insertbackground="white",
                                          relief="flat", padx=10, pady=10)
        text.pack(fill="both", expand=True)
        return text

    def _fetch_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input needed", "Please enter a city name.")
            return
        self._log(f"Fetching weather for {city}...")
        threading.Thread(target=self._fetch_thread, args=(city,), daemon=True).start()

    def _fetch_thread(self, city):
        data = fetch_live_weather(city)
        if not data:
            self._log(f"Could not fetch weather for '{city}'.")
            return

        self.root.after(0, lambda: self._update_ui(data))

    def _update_ui(self, data):
        self.summary_var.set(
            f"{data.city}, {data.country}  |  {data.temperature}°C  |  "
            f"Rain: {data.rainfall}mm  |  Wind: {data.windspeed}km/h  |  "
            f"Severity: {data.severity}  |  {data.description.capitalize()}"
        )

        self.station.set_weather(data)

        self._write_tab(self.traffic_text, self.traffic.last_result)
        self._write_tab(self.energy_text,  self.energy.last_result)
        self._write_tab(self.retail_text,  self.retail.last_result)
        self._log(f"Updated: {data.city} @ {data.timestamp.strftime('%H:%M:%S')}")

    def _write_tab(self, widget, result: dict):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        if not result:
            widget.insert("end", "No data.")
        else:
            for k, v in result.items():
                if isinstance(v, dict):
                    v = "\n    " + "\n    ".join(f"{a}: {b}" for a, b in v.items())
                elif isinstance(v, list):
                    v = ", ".join(str(i) for i in v)
                widget.insert("end", f"{k.replace('_',' ').upper():<20} {v}\n\n")
        widget.configure(state="disabled")

    def _generate_report(self):
        if not self.station.current_data:
            messagebox.showwarning("No data", "Fetch weather data first.")
            return
        try:
            factory = ReportFactory()
            report  = factory.create("pdf")
            path    = report.generate(
                self.station.current_data,
                [self.traffic, self.energy, self.retail]
            )
            self._log(f"PDF saved → {path}")
            messagebox.showinfo("Report Ready", f"PDF saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _log(self, msg):
        self.log_text.configure(state="normal")
        from datetime import datetime
        self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


def run_gui():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()