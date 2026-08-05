from datetime import timedelta

from django.db.models import Avg

from flights.models import Flight
from reviews.models import FlightReview
from ml.recommendation import calculate_recommendation_score


def get_similar_flights(current_flight, cabin_class, passengers=1):
    """
    Returns up to 5 similar flights ranked by AI score.
    """

    start_time = current_flight.departure_time - timedelta(hours=6)
    end_time = current_flight.departure_time + timedelta(hours=6)

    flights = (
        Flight.objects.filter(
            source=current_flight.source,
            destination=current_flight.destination,
            available_seats__gte=passengers,
            departure_time__range=(start_time, end_time),
        )
        .exclude(id=current_flight.id)
    )

    results = []

    current_price = current_flight.get_price(cabin_class)

    for flight in flights:

        average_rating = FlightReview.objects.filter(
            flight=flight
        ).aggregate(
            Avg("rating")
        )["rating__avg"]

        cabin_price = flight.get_price(cabin_class)
        flight.cabin_price = cabin_price

        score = calculate_recommendation_score(
            price=cabin_price,
            duration=flight.duration_minutes,
            rating=average_rating,
            stops=0,
            available_seats=flight.available_seats,
        )

        # Bonus if cheaper
        if cabin_price < current_price:
            score += 5

        # Bonus if different airline
        if flight.airline != current_flight.airline:
            score += 3

        # Bonus if departure within 2 hours
        time_diff = abs(
            (
                flight.departure_time
                - current_flight.departure_time
            ).total_seconds()
        ) / 3600

        if time_diff <= 2:
            score += 2

        flight.similar_score = min(score, 100)

        if flight.similar_score >= 90:
            flight.recommendation_badge = "🏆 AI Recommended"
        elif flight.similar_score >= 80:
            flight.recommendation_badge = "⭐ Best Value"
        elif flight.similar_score >= 70:
            flight.recommendation_badge = "👍 Good Choice"
        else:
            flight.recommendation_badge = "Standard Option"

        reasons = [
            "Same route",
        ]

        if cabin_price < current_price:
            reasons.append("Lower fare")

        if flight.airline != current_flight.airline:
            reasons.append("Alternative airline")

        if abs(
            flight.duration_minutes
            - current_flight.duration_minutes
        ) <= 20:
            reasons.append("Similar journey duration")

        if time_diff <= 2:
            reasons.append("Nearby departure time")

        if flight.available_seats >= 40:
            reasons.append("Good seat availability")

        flight.recommendation_reason = reasons

        results.append(flight)

    results.sort(
        key=lambda x: (
            -x.similar_score,
            x.cabin_price,
            x.departure_time,
        )
    )

    return results[:5]