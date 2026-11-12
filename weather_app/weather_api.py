import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8  

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherError(Exception):
    """Any problem we want to show to the user as a simple message."""
def describe_code(code):
    return WEATHER_CODES.get(code, "Unknown")


def weather_icon(code):
    if code == 0:
        return "☀️"
    if code in (1, 2):
        return "🌤️"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌡️"


def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def _get_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise WeatherError("The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise WeatherError("No internet connection. Please check your network.")
    except requests.exceptions.HTTPError as err:
        status = getattr(err.response, "status_code", "unknown")
        raise WeatherError(f"Weather service error (code {status}). Try again later.")
    except ValueError:
        raise WeatherError("Got an unreadable response from the server.")
    except requests.exceptions.RequestException:
        raise WeatherError("Something went wrong while contacting the server.")


def find_city(city):
    city = city.strip()
    if not city:
        raise WeatherError("Please enter a city name.")

    data = _get_json(
        GEOCODE_URL,
        {"name": city, "count": 1, "language": "en", "format": "json"},
    )

    results = data.get("results")
    if not results:
        raise WeatherError(f"Could not find a city named '{city}'.")

    place = results[0]
    return {
        "name": place.get("name", city),
        "region": place.get("admin1", ""),
        "country": place.get("country", ""),
        "lat": place["latitude"],
        "lon": place["longitude"],
    }


def get_weather(lat, lon):
    data = _get_json(
        WEATHER_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                       "wind_speed_10m,weather_code",
            "timezone": "auto",
        },
    )

    current = data.get("current")
    if not current:
        raise WeatherError("Weather data is not available for this location.")

    try:
        code = current["weather_code"]
        return {
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind": current["wind_speed_10m"],
            "condition": describe_code(code),
            "icon": weather_icon(code),
            "time": current.get("time", "").replace("T", " "),
        }
    except KeyError:
        raise WeatherError("The weather data came back incomplete.")