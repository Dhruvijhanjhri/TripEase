import requests
from django.conf import settings
import re


def normalize_flight_number(flight_number):
    """
    Convert TripEase flight numbers to API format.

    Examples:
    6E-449 -> 6E449
    AI-203 -> AI203
    SG-8169 -> SG8169
    """

    if not flight_number:
        return ""

    return re.sub(r"[^A-Za-z0-9]", "", flight_number).upper()


class FlightStatusService:

    BASE_URL = "https://api.aviationstack.com/v1/flights"

    @staticmethod
    def get_flight_status(flight_iata):

        import certifi

        response = requests.get(
            FlightStatusService.BASE_URL,
            params={
                "access_key": settings.AVIATIONSTACK_API_KEY,
                "flight_iata": flight_iata,
            },
            timeout=20,
            verify=certifi.where(),
        )

        response.raise_for_status()

        return response.json()