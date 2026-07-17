from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from payments.models import Payment
from ml.revenue_forecaster import RevenueForecaster
from django.db.models import Count, Avg, Sum
from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking


def get_revenue_forecast_data():
    """
    Prepare historical revenue data
    and generate revenue forecast.
    """

    today = timezone.now().date()

    revenue_history = []

    labels = []

    # Last 30 days revenue
    for i in range(29, -1, -1):

        day = today - timedelta(days=i)

        total = (
            Payment.objects.filter(
                payment_status="SUCCESS",
                payment_date__date=day
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        revenue_history.append(float(total))
        labels.append(day.strftime("%d %b"))

    forecaster = RevenueForecaster()

    predictions, upper, lower = forecaster.forecast(
        revenue_history,
        future_days=30
    )

    prediction_labels = []

    for i in range(1, 31):

        prediction_labels.append(
            (today + timedelta(days=i)).strftime("%d %b")
        )

    return {

        "labels": labels,

        "revenue_history": revenue_history,

        "prediction_labels": prediction_labels,

        "predictions": predictions,

        "upper": upper,

        "lower": lower,

    }

def get_booking_analytics():

    total_bookings = (
        Booking.objects.count() +
        HotelBooking.objects.count() +
        PackageBooking.objects.count()
    )

    total_revenue = (
        sum(
            booking.total_price
            for booking in Booking.objects.all()
        )
        +
        sum(
            booking.total_price
            for booking in HotelBooking.objects.all()
        )
        +
        sum(
            booking.total_price
            for booking in PackageBooking.objects.all()
        )
    )

    average_booking = (
        round(total_revenue / total_bookings, 2)
        if total_bookings else 0
    )

    return {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "average_booking": average_booking,
    }