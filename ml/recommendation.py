def calculate_recommendation_score(
    price,
    duration,
    rating,
    stops,
    available_seats,
):
    score = 0

    # Price (40 points)
    if price <= 5000:
        score += 40
    elif price <= 5500:
        score += 35
    elif price <= 6000:
        score += 30
    elif price <= 7000:
        score += 25
    else:
        score += 15

    # Duration (20 points)
    if duration <= 180:
        score += 20
    elif duration <= 300:
        score += 15
    elif duration <= 420:
        score += 10
    else:
        score += 5

    # Stops (20 points)
    if stops == 0:
        score += 20
    elif stops == 1:
        score += 10
    else:
        score += 5

    # Rating (15 points)
    if rating:
        score += rating * 3
    else:
        score += 8

    # Seat availability (5 points)
    if available_seats >= 150:
        score += 5
    elif available_seats >= 80:
        score += 3
    else:
        score += 1

    return round(min(score, 100), 1)

def get_confidence(score):
    """
    Converts recommendation score into AI confidence.
    """

    if score >= 90:
        return (
            "★★★★★",
            "Very High"
        )

    elif score >= 80:
        return (
            "★★★★☆",
            "High"
        )

    elif score >= 70:
        return (
            "★★★☆☆",
            "Medium"
        )

    elif score >= 60:
        return (
            "★★☆☆☆",
            "Low"
        )

    return (
        "★☆☆☆☆",
        "Very Low"
    )