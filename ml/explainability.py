def explain_recommendation(
    *,
    price,
    duration,
    rating,
    stops,
    available_seats,
    preferred_airline=False,
):
    """
    Generate human-readable explanations for AI recommendations.
    """

    reasons = []

    # -----------------------
    # Price
    # -----------------------

    if price <= 5000:
        reasons.append("💰 Lowest fare among similar flights")

    elif price <= 7000:
        reasons.append("💵 Competitive fare")

    elif price <= 9000:
        reasons.append("💳 Fair value for this route")

    else:
        reasons.append("✨ Premium cabin experience")

    # -----------------------
    # Duration
    # -----------------------

    if duration <= 120:
        reasons.append("⚡ Very short journey")

    elif duration <= 180:
        reasons.append("⏱ Short journey duration")

    elif duration <= 300:
        reasons.append("🕒 Comfortable travel time")

    else:
        reasons.append("🌍 Long-distance route")

    # -----------------------
    # Stops
    # -----------------------

    if stops == 0:
        reasons.append("✈ Non-stop flight")

    elif stops == 1:
        reasons.append("🛫 Convenient one-stop connection")

    else:
        reasons.append("🛬 Multiple connections")

    # -----------------------
    # Seat Availability
    # -----------------------

    if available_seats >= 120:
        reasons.append("💺 Plenty of seats available")

    elif available_seats >= 60:
        reasons.append("💺 Good seat availability")

    elif available_seats >= 20:
        reasons.append("🔥 Seats filling quickly")

    else:
        reasons.append("⚠ Few seats remaining")

    # -----------------------
    # Ratings
    # -----------------------

    if rating:

        if rating >= 4.8:
            reasons.append("⭐ Exceptional passenger ratings")

        elif rating >= 4.5:
            reasons.append("⭐ Highly rated by travellers")

        elif rating >= 4:
            reasons.append("👍 Positive customer reviews")

    # -----------------------
    # Personalization
    # -----------------------

    if preferred_airline:
        reasons.append("❤️ Matches your preferred airline")

    return reasons