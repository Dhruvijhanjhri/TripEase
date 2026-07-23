def get_booking_recommendation(
    current_price,
    predicted_price,
):
    """
    Decide whether the user should book now or wait.
    """

    difference = float(predicted_price) - float(current_price)

    percentage = (difference / float(predicted_price)) * 100

    if percentage >= 15:

        return {
            "action": "BOOK NOW",
            "color": "success",
            "icon": "🟢",
            "message": (
                "Prices are expected to increase." " Booking now can save money."
            ),
        }

    elif percentage >= 5:

        return {
            "action": "LIKELY BOOK NOW",
            "color": "primary",
            "icon": "🔵",
            "message": ("Current fare looks good." " Prices may rise soon."),
        }

    elif percentage > -5:

        return {
            "action": "MONITOR",
            "color": "warning",
            "icon": "🟡",
            "message": (
                "Prices appear stable."
                " You may wait if your travel dates are flexible."
            ),
        }

    else:

        return {
            "action": "WAIT",
            "color": "danger",
            "icon": "🔴",
            "message": (
                "The fare appears expensive." " Waiting may result in a lower price."
            ),
        }
