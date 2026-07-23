import requests
import certifi
from django.conf import settings


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):

    try:

        params = {
            "q": city,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }


        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        print("verify=False is being used")
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
            verify=False
        )

        data = response.json()

        if response.status_code != 200:
            return None

        return {

            "city": data["name"],

            "temperature": round(
                data["main"]["temp"]
            ),

            "feels_like": round(
                data["main"]["feels_like"]
            ),

            "humidity": data["main"]["humidity"],

            "wind_speed": round(
                data["wind"]["speed"] * 3.6,
                1
            ),

            "description": data["weather"][0]["description"].title(),

            "icon": data["weather"][0]["icon"],

        }

    except Exception as e:

        print("Weather API Error:", e)

        return None

def get_weather_by_coordinates(latitude, longitude):

    try:

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }

        import urllib3
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
            verify=False
        )

        data = response.json()

        if response.status_code != 200:
            return None

        return {

            "city": data["name"],

            "temperature": round(data["main"]["temp"]),

            "feels_like": round(data["main"]["feels_like"]),

            "humidity": data["main"]["humidity"],

            "wind_speed": round(
                data["wind"]["speed"] * 3.6,
                1
            ),

            "description": data["weather"][0]["description"].title(),

            "icon": data["weather"][0]["icon"],

        }

    except Exception as e:

        print("Weather API Error:", e)

        return None