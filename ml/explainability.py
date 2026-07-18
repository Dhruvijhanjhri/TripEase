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

    if price <= 5000:
        reasons.append("💰 Lower fare than many similar flights")

    elif price <= 7000:
        reasons.append("💵 Competitive fare")

    if duration <= 180:
        reasons.append("⏱ Short journey duration")

    elif duration <= 300:
        reasons.append("🕒 Reasonable travel time")

    if stops == 0:
        reasons.append("✈ Non-stop flight")

    else:
        reasons.append("🛫 One-stop connection")

    if available_seats >= 100:
        reasons.append("💺 High seat availability")

    elif available_seats >= 40:
        reasons.append("💺 Good seat availability")

    if rating:

        if rating >= 4.5:
            reasons.append("⭐ Excellent passenger ratings")

        elif rating >= 4:
            reasons.append("⭐ Highly rated by travellers")

    if preferred_airline:
        reasons.append("❤️ Matches your preferred airline")

    return reasons