from django.shortcuts import render, get_object_or_404

from bookings.models import Booking
from integrations.flight_status_service import (
    FlightStatusService,
    normalize_flight_number,
)


def track_booking_flight(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
    )

    original_number = booking.flight.flight_number

    tracking_number = booking.flight.tracking_flight_number

    api_number = normalize_flight_number(tracking_number)

    response = FlightStatusService.get_flight_status(api_number)

    live_flight = None

    if response and response.get("data"):

        booking_source = booking.flight.source.code.upper()
        booking_destination = booking.flight.destination.code.upper()

        for flight in response["data"]:

            departure = flight.get("departure", {}).get("iata", "").upper()

            arrival = flight.get("arrival", {}).get("iata", "").upper()

            airline = flight.get("airline", {}).get("name", "")

            if (
                departure == booking_source
                and arrival == booking_destination
                and airline.lower() == booking.flight.airline.lower()
            ):

                live_flight = flight
                break

    context = {
        "booking": booking,
        "original_number": original_number,
        "tracking_number": tracking_number,
        "api_number": api_number,
        "live_flight": live_flight,
    }

    return render(
        request,
        "integrations/track_booking_flight.html",
        context,
    )
