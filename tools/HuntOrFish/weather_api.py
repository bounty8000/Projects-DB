"""
Weather API Module
"""


import json
import ssl
from collections import defaultdict
from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError

import truststore

from models import WeatherDay


# ==========================================
# API CONFIGURATION
# ==========================================

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

# Use Windows' trusted certificates
SSL_CONTEXT = truststore.SSLContext(
    ssl.PROTOCOL_TLS_CLIENT
)


# ==========================================
# API REQUEST FUNCTION
# ==========================================

def fetch_json(url, parameters):

    full_url = url + "?" + urlencode(parameters)

    try:
        with urlopen(
            full_url,
            timeout=20,
            context=SSL_CONTEXT
        ) as response:
            data = json.load(response)

    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"Weather API connection failed: {error}"
        ) from error

    if data.get("error"):
        raise ValueError(
            data.get("reason", "Weather API error")
        )

    return data


# LOCATION SEARCH
def find_locations(search_text):

    parameters = {
        "name": search_text,
        "count": 10,
        "language": "en",
        "format": "json"
    }

    data = fetch_json(
        GEOCODING_URL,
        parameters
    )

    return data.get("results", [])



# RETRIEVE 10-DAY FORECAST
def get_forecast(latitude, longitude):

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "hourly": (
            "wind_speed_10m,"
            "cloud_cover,"
            "dew_point_2m,"
            "is_day"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto",
        "past_days": 1,
        "forecast_days": 10
    }

    data = fetch_json(
        FORECAST_URL,
        parameters
    )

    daily = data["daily"]
    hourly = data["hourly"]

    # Group hourly measurements by calendar date
    hourly_data = defaultdict(
        lambda: {
            "wind": [],
            "cloud": [],
            "dew_point": []
        }
    )

    for time, wind, cloud, dew, is_day in zip(
        hourly["time"],
        hourly["wind_speed_10m"],
        hourly["cloud_cover"],
        hourly["dew_point_2m"],
        hourly["is_day"],
        strict=True
    ):

        day_key = time[:10]

        # Wind: evaluate all 24 hours
        if wind is not None:
            hourly_data[day_key]["wind"].append(wind)

        # Clouds and dew point: daylight only
        if is_day == 1:

            if cloud is not None:
                hourly_data[day_key]["cloud"].append(cloud)

            if dew is not None:
                hourly_data[day_key]["dew_point"].append(dew)

    # Convert daily forecast into WeatherDay objects
    forecast = []

    dates = daily["time"]
    high_temps = daily["temperature_2m_max"]

    if len(dates) != len(high_temps) or len(dates) < 11:
        raise ValueError(
            "Incomplete 10-day temperature forecast."
        )

    # Index 0 is yesterday; indices 1–10 are forecast days
    for i in range(1, 11):

        day_key = dates[i]
        measurements = hourly_data[day_key]

        wind_values = measurements["wind"]
        cloud_values = measurements["cloud"]
        dew_values = measurements["dew_point"]

        if (
            high_temps[i] is None
            or high_temps[i - 1] is None
            or not wind_values
            or not cloud_values
        ):
            raise ValueError(
                f"Incomplete weather data for {day_key}"
            )

        max_wind = max(wind_values)

        average_cloud = (
            sum(cloud_values) / len(cloud_values)
        )

        average_dew = (
            sum(dew_values) / len(dew_values)
            if dew_values else None
        )

        weather_day = WeatherDay(
            forecast_date=date.fromisoformat(day_key),
            high_temp_f=high_temps[i],
            previous_high_temp_f=high_temps[i - 1],
            wind_speed_mph=max_wind,
            cloud_cover_pct=average_cloud,
            dew_point_f=average_dew
        )

        forecast.append(weather_day)

    return forecast
