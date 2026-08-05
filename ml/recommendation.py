import random

def calculate_recommendation_score(
    price,
    duration,
    rating,
    stops,
    available_seats,
):
    """
    AI recommendation score (0-100)
    """

    score = 90

    # -----------------------
    # Price
    # -----------------------

    if price <= 5000:
        score += 8
    elif price <= 6500:
        score += 5
    elif price <= 8000:
        score += 2
    elif price <= 10000:
        score -= 3
    elif price <= 12000:
        score -= 8
    else:
        score -= 15

    # -----------------------
    # Duration
    # -----------------------

    if duration <= 90:
        score += 6
    elif duration <= 180:
        score += 4
    elif duration <= 300:
        score += 1
    elif duration <= 420:
        score -= 5
    else:
        score -= 10

    # -----------------------
    # Stops
    # -----------------------

    if stops == 0:
        score += 5
    elif stops == 1:
        score -= 8
    else:
        score -= 18

    # -----------------------
    # Seat availability
    # -----------------------

    if available_seats >= 120:
        score += 4
    elif available_seats >= 80:
        score += 2
    elif available_seats >= 50:
        score += 0
    elif available_seats >= 20:
        score -= 3
    else:
        score -= 8

    # -----------------------
    # Reviews
    # -----------------------

    if rating:
        if rating >= 4.7:
            score += 3
        elif rating >= 4.3:
            score += 2
        elif rating >= 4.0:
            score += 1
        elif rating < 3.5:
            score -= 5

    return max(50, min(round(score), 99))


def get_confidence(score):

    if score >= 90:
        return ("★★★★★", "Very High")

    elif score >= 82:
        return ("★★★★☆", "High")

    elif score >= 74:
        return ("★★★☆☆", "Medium")

    elif score >= 66:
        return ("★★☆☆☆", "Low")

    return ("★☆☆☆☆", "Very Low")