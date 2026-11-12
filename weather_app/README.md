# Weather Information App

**Auspify Internship | Task 4 (Medium)**

A Python desktop app that fetches real-time weather for any city using a REST API. Type a city name and it shows the current temperature, conditions, humidity and wind speed.

## What it does

- Search any city in the world by name
- Shows live temperature, weather condition and an icon
- Shows "feels like" temperature, humidity and wind speed
- Switch between °C and °F with one click
- Shows the city's local time for the reading
- Handles errors with clear messages: empty input, city not found, no internet, timeout, server problems and bad data

## Skills used

- REST APIs
- JSON handling
- `requests` library
- Tkinter GUI
- Error handling with `try` / `except`

## API used

[Open-Meteo](https://open-meteo.com/) is a free weather API and **needs no API key**. The app makes two calls:

1. **Geocoding API** turns the city name into latitude and longitude.
2. **Forecast API** returns the current weather for those coordinates.

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Install the requirement:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python weather_app.py
```

You need an internet connection. On Linux, install Tkinter with `sudo apt install python3-tk` if it is missing.

## How to use

1. Type a city name, for example `Nagpur`.
2. Press Enter or click **Search**.
3. Use the °C / °F buttons to change the unit.

## Testing

The API code is kept separate from the window so it can be tested without internet. The tests use pretend API responses to check normal results and every error case:

```bash
python -m unittest -v
```

Manual checks on the interface:

| Input | Expected result |
|-------|-----------------|
| `Nagpur` | Shows temperature, condition, humidity, wind |
| `nagpur` (lowercase) | Same result |
| Empty box | "Please enter a city name." |
| `asdfghjkl` | "Could not find a city named 'asdfghjkl'." |
| Internet turned off | "No internet connection. Please check your network." |
| Click °F after a search | Temperatures change to Fahrenheit, no new request |

## Project structure

```
task4-weather-app/
├── weather_app.py          (the window)
├── weather_api.py          (API calls and data handling)
├── test_weather_api.py     (unit tests)
├── requirements.txt
└── README.md
```

## Author

Darshan, Auspify Internship