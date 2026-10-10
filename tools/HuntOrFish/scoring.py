"""
Scoring and calculations
"""

from datetime import date
from models import WeatherDay, ScoredDay

RUT_MULTIPLIER = 1.40

# WEATHER SCORING WEIGHTS
# =Adjust if needed
WEIGHTS = {
    "temperature_drop": 40,
    "cloud_cover": 30,
    "wind_speed": 20,
    "day_of_week": 10
}

# DAY OF WEEK POINTS
# Adjust if needed

WEEKDAY_POINTS = {
    "Monday": 1.0,
    "Tuesday": 4.5,
    "Wednesday": 7.5,
    "Thursday": 10.0,
    "Friday": 8.5,
    "Saturday": 3.0,
    "Sunday": 2.0
}


# TEMPERATURE SCORING
# (Temperature drop in F, Points)
# Adjust if needed

TEMPERATURE_THRESHOLDS = [
    (0, 0),
    (5, 20),
    (10, 30),
    (15, 40)
]

# CLOUD SCORING

CLOUD_CLEAR_POINTS = 30
CLOUD_OVERCAST_POINTS = 15



# RUT ADJUSTMENT
# 40% multiplier

RUT_MULTIPLIER = 1.40


# STAR RATING THRESHOLDS

STAR_THRESHOLDS = {
    5: 85,
    4: 70,
    3: 50,
    2: 30,
    1: 0
}


# WEEKDAY SCORING FUNCTION

def score_weekday(forecast_date: date) -> float:

    weekday_name = forecast_date.strftime("%A")

    return WEEKDAY_POINTS[weekday_name]

# TEMPERATURE SCORING
def score_temperature(today_high, previous_high):

    # Calculate how much colder today is
    temp_drop = previous_high - today_high

    # No cooling means no points
    if temp_drop <= 0:
        return 0.0

    # Evaluate each pair of thresholds
    for i in range(len(TEMPERATURE_THRESHOLDS) - 1):

        low_drop, low_points = TEMPERATURE_THRESHOLDS[i]

        high_drop, high_points = TEMPERATURE_THRESHOLDS[i + 1]

        # Find the range containing our temperature drop
        if temp_drop <= high_drop:

            fraction = (
                (temp_drop - low_drop) /
                (high_drop - low_drop)
            )

            points = low_points + fraction * (
                high_points - low_points
            )

            return points

    # Cap the score at 40 points, -1 selects from last item, it's point value
    # which should be 40
    return float(TEMPERATURE_THRESHOLDS[-1][1])


# WIND SPEED SCORING FUNCTION
def score_wind(wind_speed):

    if wind_speed < 0:
        raise ValueError("Wind cannot be negative.")

    points = (wind_speed - 8) * 2

    return max(0, min(points, 20))


# CLOUD COVER SCORING FUNCTION
def score_cloud(cloud_cover):

    # Cloud coverage must be between 0 and 100
    if not 0 <= cloud_cover <= 100:
        raise ValueError(
            "Cloud coverage must be between 0 and 100."
        )

    # Convert percentage to decimal
    cloud_fraction = cloud_cover / 100

    # Calculate points using linear interpolation
    points = CLOUD_CLEAR_POINTS - cloud_fraction * (
        CLOUD_CLEAR_POINTS - CLOUD_OVERCAST_POINTS
    )

    return points


# STAR RATING FUNCTION
def score_to_stars(score):

    for stars in sorted(STAR_THRESHOLDS, reverse=True):

        if score >= STAR_THRESHOLDS[stars]:
            return stars

    return 1



# COMPOSITE WEATHER SCORING
def calculate_weather_score(day: WeatherDay) -> ScoredDay:

    # Calculate each scoring component

    temperature_points = score_temperature(
        day.high_temp_f,
        day.previous_high_temp_f
    )

    cloud_points = score_cloud(
        day.cloud_cover_pct
    )

    wind_points = score_wind(
        day.wind_speed_mph
    )

    weekday_points = score_weekday(
        day.forecast_date
    )

    # Combine all components

    base_score = (
        temperature_points
        + cloud_points
        + wind_points
        + weekday_points
    )

    # Convert numerical score to stars

    stars = score_to_stars(base_score)

    # Return the complete result

    return ScoredDay(
        weather=day,
        temperature_points=temperature_points,
        cloud_points=cloud_points,
        wind_points=wind_points,
        weekday_points=weekday_points,
        base_score=base_score,
        stars=stars
    )


# RUT FACTOR FUNCTION
# ==========================================

def apply_rut_factor(
    base_score,
    forecast_date,
    enabled,
    start_date=None,
    end_date=None
):

    # If rut is disabled, return the original score
    if not enabled:
        return base_score
    # Require both dates when rut is enabled
    if start_date is None or end_date is None:
        raise ValueError("Rut dates are required.")
    # Validate the date range
    if start_date > end_date:
        raise ValueError(
            "Rut start date cannot exceed end date."
        )
    # Check whether the forecast date is in range
    if start_date <= forecast_date <= end_date:
        return base_score * RUT_MULTIPLIER

    # Date is outside rut range
    return base_score
