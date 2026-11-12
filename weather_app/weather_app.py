import tkinter as tk

from weather_api import WeatherError, find_city, get_weather, to_fahrenheit

BG = "#eaf4fb"
CARD = "#ffffff"
DARK = "#1f3a5f"
BLUE = "#2f7de1"
RED = "#d64545"
GREY = "#6f7f90"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Information")
        self.root.geometry("420x600")
        self.root.configure(bg=BG)

        self.place = None      
        self.weather = None    
        self.unit = tk.StringVar(value="C")

        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.root, text="Weather App",
            font=("Segoe UI", 20, "bold"), bg=BG, fg=DARK,
        ).pack(pady=(18, 10))

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=20)

        self.entry = tk.Entry(top, font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.entry.bind("<Return>", lambda event: self.search())
        self.entry.focus()

        tk.Button(
            top, text="Search", command=self.search,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=4,
        ).pack(side="left", padx=(8, 0))

        self.message = tk.Label(
            self.root, text="", font=("Segoe UI", 10),
            bg=BG, fg=GREY, wraplength=380,
        )
        self.message.pack(pady=(10, 0))

        card = tk.Frame(
            self.root, bg=CARD,
            highlightthickness=1, highlightbackground="#d5e0ea",
        )
        card.pack(fill="both", expand=True, padx=20, pady=15)

        self.city_label = tk.Label(
            card, text="Search for a city", wraplength=360,
            font=("Segoe UI", 15, "bold"), bg=CARD, fg=DARK,
        )
        self.city_label.pack(pady=(20, 0))

        self.time_label = tk.Label(
            card, text="", font=("Segoe UI", 9), bg=CARD, fg=GREY,
        )
        self.time_label.pack()

        self.icon_label = tk.Label(
            card, text="🌍", font=("Segoe UI Emoji", 48), bg=CARD,
        )
        self.icon_label.pack(pady=(10, 0))

        self.temp_label = tk.Label(
            card, text="--", font=("Segoe UI", 40, "bold"), bg=CARD, fg=DARK,
        )
        self.temp_label.pack()

        self.condition_label = tk.Label(
            card, text="", font=("Segoe UI", 13), bg=CARD, fg=GREY,
        )
        self.condition_label.pack(pady=(0, 15))

        details = tk.Frame(card, bg=CARD)
        details.pack(fill="x", padx=30)
        self.feels_label = self.make_row(details, "Feels like")
        self.humidity_label = self.make_row(details, "Humidity")
        self.wind_label = self.make_row(details, "Wind speed")

        # temperature unit switch
        units = tk.Frame(card, bg=CARD)
        units.pack(pady=15)
        for text, value in (("°C", "C"), ("°F", "F")):
            tk.Radiobutton(
                units, text=text, value=value, variable=self.unit,
                command=self.show_weather, bg=CARD, fg=DARK,
                font=("Segoe UI", 10), selectcolor=CARD,
            ).pack(side="left", padx=10)

    def make_row(self, parent, name):
        """One 'name .... value' line. Returns the label that holds the value."""
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=name, font=("Segoe UI", 11), bg=CARD, fg=GREY,
        ).pack(side="left")
        value = tk.Label(
            row, text="--", font=("Segoe UI", 11, "bold"), bg=CARD, fg=DARK,
        )
        value.pack(side="right")
        return value

    def set_message(self, text, color=GREY):
        self.message.config(text=text, fg=color)

    def search(self):
        city = self.entry.get()
        self.set_message("Searching...")
        self.root.update_idletasks() 

        try:
            place = find_city(city)
            weather = get_weather(place["lat"], place["lon"])
        except WeatherError as error:
            self.set_message(str(error), RED)
            return

        self.place = place
        self.weather = weather
        self.set_message("")
        self.show_weather()

    def show_weather(self):
        if self.weather is None:
            return

        weather = self.weather
        unit = self.unit.get()

        def temp_text(celsius):
            value = to_fahrenheit(celsius) if unit == "F" else celsius
            return f"{round(value)}°{unit}"

        parts = [self.place["name"]]
        if self.place["region"] and self.place["region"] != self.place["name"]:
            parts.append(self.place["region"])
        if self.place["country"]:
            parts.append(self.place["country"])

        self.city_label.config(text=", ".join(parts))
        self.time_label.config(text=f"Local time: {weather['time']}")
        self.icon_label.config(text=weather["icon"])
        self.temp_label.config(text=temp_text(weather["temperature"]))
        self.condition_label.config(text=weather["condition"])
        self.feels_label.config(text=temp_text(weather["feels_like"]))
        self.humidity_label.config(text=f"{weather['humidity']}%")
        self.wind_label.config(text=f"{weather['wind']} km/h")


def main():
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()