from bookings.models import Booking
from django.db.models import Count


def get_user_preferences(user):
    """
    Learn user preferences from previous bookings.
    """

    bookings = Booking.objects.filter(
        user=user, booking_status__in=["confirmed", "completed"]
    )

    if not bookings.exists():
        return None

    preferred_airline = (
        bookings.values("flight__airline")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    return {
        "preferred_airline": (
            preferred_airline["flight__airline"] if preferred_airline else None
        )
    }
