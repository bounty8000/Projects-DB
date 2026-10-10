import streamlit as st
from datetime import date, timedelta

from models import WeatherDay
from weather_api import find_locations, get_forecast
from scoring import calculate_weather_score, apply_rut_factor, score_to_stars


st.set_page_config(page_title="Hunt or Fish?", layout="wide")


@st.cache_data(ttl=3600)
def cached_locations(search_text):
    return find_locations(search_text)


@st.cache_data(ttl=3600)
def cached_forecast(latitude, longitude):
    return get_forecast(latitude, longitude)


def build_ranked_days(forecast_days, rut_enabled, rut_start, rut_end):
    rankings = []

    for days_ahead, day in enumerate(forecast_days):
        result = calculate_weather_score(day)
        final_score = apply_rut_factor(
            base_score=result.base_score,
            forecast_date=day.forecast_date,
            enabled=rut_enabled,
            start_date=rut_start,
            end_date=rut_end,
        )
        stars = score_to_stars(final_score)

        if days_ahead <= 2:
            confidence = "Higher"
        elif days_ahead <= 5:
            confidence = "Moderate"
        else:
            confidence = "Lower"

        rankings.append({
            "Date": day.forecast_date.isoformat(),
            "Day": day.weekday,
            "Temperature Change (°F)": round(day.temperature_change_f, 1),
            "Wind (mph)": round(day.wind_speed_mph, 1),
            "Cloud Cover (%)": round(day.cloud_cover_pct, 1),
            "Base Score": result.base_score,
            "Rut Bonus": final_score - result.base_score,
            "Final Index": final_score,
            "Stars": "★" * stars + "☆" * (5 - stars),
            "Confidence": confidence,
        })

    rankings.sort(key=lambda row: (-row["Final Index"], row["Date"]))
    for rank, row in enumerate(rankings, start=1):
        row["Rank"] = rank
        for key in ("Base Score", "Rut Bonus", "Final Index"):
            row[key] = round(row[key], 2)

    return rankings


# MAIN INTERFACE
st.title("Hunt or Fish?")
st.caption("10-day deer-hunting opportunity forecast based on weather, weekday, and optional rut dates.")

# SIDEBAR CONTROLS
with st.sidebar:
    st.header("Forecast Settings")
    location_search = st.text_input(
        "City or ZIP Code",
        placeholder="Example: Madison or 53703",
    )

    st.subheader("Rut Adjustment")
    rut_enabled = st.checkbox("Include Rut Factor (+40%)", value=False)
    rut_start = None
    rut_end = None

    if rut_enabled:
        rut_start = st.date_input("Rut Start", value=date.today(), key="rut_start")
        rut_end = st.date_input(
            "Rut End", value=date.today() + timedelta(days=9), key="rut_end"
        )

if rut_enabled and rut_start > rut_end:
    st.error("Rut End must be on or after Rut Start.")
elif not location_search.strip():
    st.info("Enter a city or ZIP code in the sidebar to load the forecast.")
else:
    try:
        locations = cached_locations(location_search.strip())

        if not locations:
            st.warning("No matching locations found.")
        else:
            selected_location = st.selectbox(
                "Select Location (this could be a drop down menu)",
                locations,
                format_func=lambda place: (
                    f"{place['name']}, "
                    f"{place.get('admin1', '')}, "
                    f"{place.get('country', '')}"
                ),
            )

            forecast_days = cached_forecast(
                selected_location["latitude"], selected_location["longitude"]
            )
            ranked_days = build_ranked_days(
                forecast_days, rut_enabled, rut_start, rut_end
            )

            if not ranked_days:
                st.warning("No forecast days were returned.")
            else:
                best_day = ranked_days[0]
                st.subheader("Best Upcoming Day")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Date", f"{best_day['Day']}, {best_day['Date']}")
                with col2:
                    st.metric("Opportunity Index", f"{best_day['Final Index']:g}")
                with col3:
                    st.metric("Rating", best_day["Stars"])
                st.caption(
                    f"Forecast confidence: {best_day['Confidence']}. "
                    "Confidence is separate from the opportunity score."
                )

                st.subheader("10-Day Hunting Rankings")
                view = st.radio(
                    "Display order",
                    ["Best first", "Calendar order"],
                    horizontal=True,
                )
                displayed_days = (
                    ranked_days if view == "Best first"
                    else sorted(ranked_days, key=lambda row: row["Date"])
                )
                columns = [
                    "Rank", "Date", "Day", "Temperature Change (°F)",
                    "Wind (mph)", "Cloud Cover (%)", "Base Score",
                    "Rut Bonus", "Final Index", "Stars", "Confidence",
                ]
                st.dataframe(
                    [{key: row[key] for key in columns} for row in displayed_days],
                    hide_index=True,
                    use_container_width=True,
                )

                with st.expander("Raw forecast measurements"):
                    st.dataframe([
                        {
                            "Date": day.forecast_date.isoformat(),
                            "Day": day.weekday,
                            "High (°F)": day.high_temp_f,
                            "Previous High (°F)": day.previous_high_temp_f,
                            "Wind (mph)": round(day.wind_speed_mph, 1),
                            "Cloud Cover (%)": round(day.cloud_cover_pct, 1),
                            "Dew Point (°F)": (
                                round(day.dew_point_f, 1)
                                if day.dew_point_f is not None else None
                            ),
                        }
                        for day in forecast_days
                    ], hide_index=True, use_container_width=True)

    except (RuntimeError, ValueError, KeyError, TypeError) as error:
        st.error(f"Forecast request failed: {error}")

# OPTIONAL MANUAL SCORE INSPECTOR
with st.expander("Manual Score Inspector (optional)"):
    manual_date = st.date_input("Date", value=date.today(), key="manual_date")
    col1, col2 = st.columns(2)
    with col1:
        previous_high = st.number_input("Previous high (°F)", value=67.0)
        wind_speed = st.number_input("Wind (mph)", min_value=0.0, value=18.0)
    with col2:
        today_high = st.number_input("Today's high (°F)", value=58.0)
        cloud_cover = st.slider("Daytime cloud cover (%)", 0, 100, 20)

    manual_day = WeatherDay(
        forecast_date=manual_date,
        high_temp_f=today_high,
        previous_high_temp_f=previous_high,
        wind_speed_mph=wind_speed,
        cloud_cover_pct=cloud_cover,
    )
    score = calculate_weather_score(manual_day)
    st.metric("Base Weather Score", f"{score.base_score:.2f} / 100")
    st.write("Score breakdown:")
    st.table([
        {"Factor": "Temperature", "Points": round(score.temperature_points, 2)},
        {"Factor": "Cloud cover", "Points": round(score.cloud_points, 2)},
        {"Factor": "Wind", "Points": round(score.wind_points, 2)},
        {"Factor": "Weekday", "Points": round(score.weekday_points, 2)},
    ])
