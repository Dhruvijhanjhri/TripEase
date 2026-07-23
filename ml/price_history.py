from statistics import mean


def generate_price_history(current_price):
    """
    Generate simulated historical prices around the current fare.
    """

    current_price = float(current_price)

    history = [
        round(current_price * 1.08),
        round(current_price * 1.05),
        round(current_price * 1.03),
        round(current_price * 1.01),
        round(current_price),
        round(current_price * 0.99),
        round(current_price * 1.02),
    ]

    return history


def get_price_statistics(history):
    """
    Calculate useful fare statistics.
    """

    return {
        "lowest": min(history),
        "highest": max(history),
        "average": round(mean(history)),
        "current": history[4],
    }
