from datetime import timedelta
from django.utils import timezone


def generate_nearby_dates(selected_date, days_before=3, days_after=3):
    """
    Generate nearby future dates around the selected travel date.
    Past dates are excluded.
    """

    today = timezone.localdate()

    dates = []

    for offset in range(-days_before, days_after + 1):

        candidate = selected_date + timedelta(days=offset)

        # Skip past dates
        if candidate <= today:
            continue

        dates.append(candidate)

    return dates


def generate_fare_calendar(
    predictor,
    source,
    destination,
    stops,
    duration_minutes,
    departure_hour,
    airline,
    selected_date,
):
    """
    Generate predicted fares for nearby dates.
    Returns a list of dictionaries:
    [
        {
            'date': date,
            'predicted_price': 4890,
            'is_selected': True,
        },
        ...
    ]
    """

    nearby_dates = generate_nearby_dates(selected_date)

    fare_calendar = []

    for travel_date in nearby_dates:

        predicted_price = predictor.predict(
            source=source,
            destination=destination,
            stops=stops,
            duration_minutes=duration_minutes,
            departure_date=travel_date,
            departure_hour=departure_hour,
            airline=airline,
        )

        fare_calendar.append(
            {
                "date": travel_date,
                "predicted_price": int(round(predicted_price)),
                "is_selected": travel_date == selected_date,
            }
        )

    return fare_calendar


def find_cheapest_date(fare_calendar):
    """
    Find the cheapest date from the fare calendar.
    Returns a dictionary with cheapest date and savings info.
    """

    cheapest = min(fare_calendar, key=lambda x: x["predicted_price"])

    selected = next(item for item in fare_calendar if item["is_selected"])

    savings = selected["predicted_price"] - cheapest["predicted_price"]

    return {
        "cheapest_date": cheapest["date"],
        "cheapest_price": cheapest["predicted_price"],
        "selected_price": selected["predicted_price"],
        "savings": max(savings, 0),
        "is_selected_cheapest": cheapest["date"] == selected["date"],
    }
