import unittest
from unittest.mock import Mock, patch

import requests

from weather_api import (
    WeatherError,
    describe_code,
    find_city,
    get_weather,
    to_fahrenheit,
    weather_icon,
)


def fake_response(json_data):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestHelpers(unittest.TestCase):
    def test_known_weather_code(self):
        self.assertEqual(describe_code(0), "Clear sky")
        self.assertEqual(describe_code(95), "Thunderstorm")

    def test_unknown_weather_code(self):
        self.assertEqual(describe_code(1234), "Unknown")

    def test_icon_for_rain_and_unknown(self):
        self.assertEqual(weather_icon(63), "🌧️")
        self.assertEqual(weather_icon(1234), "🌡️")

    def test_celsius_to_fahrenheit(self):
        self.assertEqual(to_fahrenheit(0), 32)
        self.assertEqual(to_fahrenheit(100), 212)


class TestFindCity(unittest.TestCase):
    def test_empty_city_name(self):
        with self.assertRaises(WeatherError):
            find_city("   ")

    @patch("weather_api.requests.get")
    def test_city_found(self, mock_get):
        mock_get.return_value = fake_response({
            "results": [{
                "name": "Nagpur", "admin1": "Maharashtra", "country": "India",
                "latitude": 21.14, "longitude": 79.08,
            }]
        })
        place = find_city("Nagpur")
        self.assertEqual(place["name"], "Nagpur")
        self.assertEqual(place["country"], "India")
        self.assertEqual(place["lat"], 21.14)

    @patch("weather_api.requests.get")
    def test_city_not_found(self, mock_get):
        mock_get.return_value = fake_response({}) 
        with self.assertRaises(WeatherError) as context:
            find_city("Notarealcity")
        self.assertIn("Could not find", str(context.exception))


class TestGetWeather(unittest.TestCase):
    @patch("weather_api.requests.get")
    def test_weather_parsed(self, mock_get):
        mock_get.return_value = fake_response({
            "current": {
                "time": "2026-11-12T13:00",
                "temperature_2m": 28.4,
                "apparent_temperature": 30.1,
                "relative_humidity_2m": 45,
                "wind_speed_10m": 9.7,
                "weather_code": 1,
            }
        })
        weather = get_weather(21.14, 79.08)
        self.assertEqual(weather["temperature"], 28.4)
        self.assertEqual(weather["condition"], "Mainly clear")
        self.assertEqual(weather["time"], "2026-11-12 13:00")

    @patch("weather_api.requests.get")
    def test_missing_current_data(self, mock_get):
        mock_get.return_value = fake_response({})
        with self.assertRaises(WeatherError):
            get_weather(0, 0)

    @patch("weather_api.requests.get")
    def test_incomplete_data(self, mock_get):
        mock_get.return_value = fake_response({"current": {"temperature_2m": 20}})
        with self.assertRaises(WeatherError):
            get_weather(0, 0)


class TestApiErrors(unittest.TestCase):
    @patch("weather_api.requests.get", side_effect=requests.exceptions.Timeout)
    def test_timeout(self, mock_get):
        with self.assertRaises(WeatherError) as context:
            find_city("Pune")
        self.assertIn("timed out", str(context.exception))

    @patch("weather_api.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_no_internet(self, mock_get):
        with self.assertRaises(WeatherError) as context:
            find_city("Pune")
        self.assertIn("internet", str(context.exception))

    @patch("weather_api.requests.get")
    def test_server_error(self, mock_get):
        response = fake_response({})
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=500)
        )
        mock_get.return_value = response
        with self.assertRaises(WeatherError) as context:
            find_city("Pune")
        self.assertIn("500", str(context.exception))

    @patch("weather_api.requests.get")
    def test_bad_json(self, mock_get):
        response = fake_response({})
        response.json.side_effect = ValueError("not json")
        mock_get.return_value = response
        with self.assertRaises(WeatherError):
            find_city("Pune")


if __name__ == "__main__":
    unittest.main()