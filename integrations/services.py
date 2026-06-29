import requests


class LocationService:

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    @staticmethod
    def get_coordinates(city):

        try:

            response = requests.get(

                LocationService.BASE_URL,

                params={
                    "q": city,
                    "format": "json",
                    "limit": 1
                },

                headers={
                    "User-Agent": "TripEase"
                },

                timeout=10

            )

            response.raise_for_status()

            data = response.json()

            if not data:
                return None

            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_name": data[0]["display_name"]
            }

        except Exception:

            return None