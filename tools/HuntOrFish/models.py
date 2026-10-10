"""
Data Models
"""

#dataclass for the day
from dataclasses import dataclass
#standard calendar date format date(2026,10,9) ETC.
from datetime import date


@dataclass(frozen=True)
class WeatherDay:
    forecast_date: date
    high_temp_f: float
    previous_high_temp_f: float
    wind_speed_mph: float
    cloud_cover_pct: float
    dew_point_f: float | None = None

    @property
    def weekday(self)-> str:
        return self.forecast_date.strftime("%A") #get full weekday name

    @property
    def temperature_change_f(self) -> float:
        return self.high_temp_f - self.previous_high_temp_f

    def __post_init__(self) -> None:
        if self.wind_speed_mph < 0:
            raise ValueError("Wind speed cannot be negative.")
    
        if not 0 <= self.cloud_cover_pct <= 100:
            raise ValueError("Cloud cover must be between 0 and 100.")


# SCORED WEATHER DAY MODEL
@dataclass(frozen=True)
class ScoredDay:

    weather: WeatherDay

    temperature_points: float
    cloud_points: float
    wind_points: float
    weekday_points: float

    base_score: float
    stars: int
