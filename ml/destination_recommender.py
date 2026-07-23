POPULAR_DESTINATIONS = {
    "Goa": {"score": 92, "reason": "Matches your beach travel preference"},
    "Manali": {"score": 86, "reason": "Great for mountain and leisure trips"},
    "Jaipur": {"score": 78, "reason": "Excellent value destination"},
    "Kochi": {"score": 74, "reason": "Good for cultural and food experiences"},
    "Srinagar": {"score": 88, "reason": "High-rated scenic destination"},
    "Udaipur": {"score": 84, "reason": "Romantic lakeside destination"},
    "Darjeeling": {"score": 82, "reason": "Perfect for scenic mountain travel"},
    "Mysuru": {"score": 76, "reason": "Great weekend cultural getaway"},
    "Pondicherry": {"score": 80, "reason": "Relaxing coastal destination"},
    "Rishikesh": {"score": 83, "reason": "Adventure and wellness destination"},
    "Andaman": {"score": 90, "reason": "Premium beach and island experience"},
    "Leh": {"score": 87, "reason": "Ideal for adventure seekers"},
}


def recommend_destinations(flight_bookings, hotel_bookings, package_bookings, limit=3):
    """
    Generate destination recommendations from booking history.
    """

    visited = []

    # Flights
    for booking in flight_bookings:
        try:
            visited.append(booking.flight.destination.city)
        except Exception:
            pass

    # Hotels
    for booking in hotel_bookings:
        try:
            visited.append(booking.hotel.city)
        except Exception:
            pass

    # Packages
    for booking in package_bookings:
        try:
            visited.append(booking.package.destination)
        except Exception:
            pass

    # Normalize
    visited_normalized = [str(v).strip().lower() for v in visited if v]

    recommendations = []

    for destination, info in POPULAR_DESTINATIONS.items():

        destination_lower = destination.lower()

        # Skip already visited destinations
        already_visited = any(
            destination_lower in v or v in destination_lower for v in visited_normalized
        )

        if already_visited:
            continue

        recommendations.append(
            {
                "destination": destination,
                "match_score": info["score"],
                "reason": info["reason"],
            }
        )

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)

    return recommendations[:limit]
