from django.db.models import Count

from bookings.models import Booking


def get_trending_flights():

    bookings = (
        Booking.objects.filter(
            booking_status="confirmed"
        )
        .values("flight")
        .annotate(total=Count("flight"))
    )

    trending = {}

    for row in bookings:
        trending[row["flight"]] = row["total"]

    return trending