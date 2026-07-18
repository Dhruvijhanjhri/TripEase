from datetime import timedelta

from django.db.models import Q

from flights.models import Flight
from reviews.models import FlightReview
from django.db.models import Avg

from ml.recommendation import calculate_recommendation_score


def get_similar_flights(current_flight, cabin_class, passengers=1):
    """
    Returns up to 5 similar flights ranked by AI score.
    """

    start_time = current_flight.departure_time - timedelta(hours=4)
    end_time = current_flight.departure_time + timedelta(hours=4)

    flights = Flight.objects.filter(
        source=current_flight.source,
        destination=current_flight.destination,
        available_seats__gte=passengers,
        departure_time__range=(start_time, end_time),
    ).exclude(
        id=current_flight.id
    )

    results = []

    current_price = current_flight.get_price(cabin_class)

    for flight in flights:

        average_rating = (
            FlightReview.objects
            .filter(flight=flight)
            .aggregate(Avg("rating"))["rating__avg"]
        )

        cabin_price = flight.get_price(cabin_class)
        flight.cabin_price = cabin_price

        score = calculate_recommendation_score(
            price=cabin_price,
            duration=flight.duration_minutes,
            rating=average_rating,
            stops=0,
            available_seats=flight.available_seats,
        )

        flight.similar_score = score

        # AI Badge
        if score >= 90:
            flight.recommendation_badge = "🏆 AI Recommended"
        elif score >= 80:
            flight.recommendation_badge = "⭐ Best Value"
        elif score >= 70:
            flight.recommendation_badge = "👍 Good Choice"
        else:
            flight.recommendation_badge = "Standard Option"
        
        reasons = []

        reasons.append("Same route")

        if flight.airline == current_flight.airline:
            reasons.append("Same airline")

        if abs(flight.duration_minutes - current_flight.duration_minutes) <= 30:
            reasons.append("Similar journey duration")

        if flight.available_seats >= 50:
            reasons.append("Good seat availability")

        if flight.get_price(cabin_class) <= current_price:
            reasons.append("Competitive fare")

        if not reasons:
            reasons.append("Overall similar travel option")

        flight.recommendation_reason = reasons

        results.append(flight)

    results.sort(
        key=lambda x: x.similar_score,
        reverse=True,
    )

    return results[:5]