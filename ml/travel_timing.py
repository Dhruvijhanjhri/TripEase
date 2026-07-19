def analyze_booking_timing(current_price, predicted_price, fare_calendar):
    """
    Analyze whether this is a good time to book.
    Returns a dictionary with timing insights.
    """

    prices = [item["predicted_price"] for item in fare_calendar]

    lowest = min(prices)
    highest = max(prices)
    average = sum(prices) / len(prices)

    # Demand level
    if current_price <= average * 0.95:
        demand_level = "Low"
    elif current_price <= average * 1.05:
        demand_level = "Medium"
    else:
        demand_level = "High"

    # Price trend
    first_price = prices[0]
    last_price = prices[-1]

    if last_price > first_price * 1.03:
        price_trend = "Increasing"
    elif last_price < first_price * 0.97:
        price_trend = "Decreasing"
    else:
        price_trend = "Stable"

    # Booking window
    if price_trend == "Increasing":
        booking_window = "Today – Tomorrow"
    elif price_trend == "Decreasing":
        booking_window = "Wait 1–3 days"
    else:
        booking_window = "Book within 2–3 days"

    # Savings estimate
    estimated_savings = max(current_price - lowest, 0)

    # Confidence
    spread = highest - lowest

    if spread > 1500:
        confidence = "Very High"
    elif spread > 700:
        confidence = "High"
    elif spread > 300:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "demand_level": demand_level,
        "price_trend": price_trend,
        "booking_window": booking_window,
        "estimated_savings": int(round(estimated_savings)),
        "confidence": confidence,
        "lowest_price": lowest,
        "highest_price": highest,
        "average_price": int(round(average)),
    }