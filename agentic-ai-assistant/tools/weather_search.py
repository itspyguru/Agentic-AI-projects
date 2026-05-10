import os
import requests

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


@tool
def weather_tool(city: str) -> str:
    """
    Get current weather information for a city.
    """

    try:

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
        )

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        # city not found
        if response.status_code != 200:

            return (
                f"Could not fetch weather for "
                f"{city}: {data.get('message')}"
            )

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return f"""
        Current weather in {city}:

        - Condition: {weather}
        - Temperature: {temp}°C
        - Feels Like: {feels_like}°C
        - Humidity: {humidity}%
        - Wind Speed: {wind_speed} m/s
        """

    except Exception as e:

        return f"Weather tool error: {str(e)}"