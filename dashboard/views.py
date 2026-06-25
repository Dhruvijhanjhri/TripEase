from collections import defaultdict
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import render

from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking
from payments.models import Payment


@staff_member_required
def dashboard_home(request):
    flight_bookings = Booking.objects.count()
    hotel_bookings = HotelBooking.objects.count()
    package_bookings = PackageBooking.objects.count()

    total_bookings = (
        flight_bookings +
        hotel_bookings +
        package_bookings
    )

    successful_payments = Payment.objects.filter(
        payment_status='success'
    )

    total_revenue = successful_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # -----------------------------
    # Monthly booking trend
    # -----------------------------
    monthly_data = defaultdict(
        lambda: {
            'flights': 0,
            'hotels': 0,
            'packages': 0
        }
    )

    for booking in Booking.objects.all():
        month_key = booking.created_at.strftime('%b %Y')
        monthly_data[month_key]['flights'] += 1

    for booking in HotelBooking.objects.all():
        month_key = booking.created_at.strftime('%b %Y')
        monthly_data[month_key]['hotels'] += 1

    for booking in PackageBooking.objects.all():
        month_key = booking.created_at.strftime('%b %Y')
        monthly_data[month_key]['packages'] += 1

    def month_sort_key(label):
        return datetime.strptime(label, '%b %Y')

    sorted_months = sorted(
        monthly_data.keys(),
        key=month_sort_key
    )

    monthly_labels = sorted_months
    monthly_flights = [
        monthly_data[m]['flights']
        for m in sorted_months
    ]
    monthly_hotels = [
        monthly_data[m]['hotels']
        for m in sorted_months
    ]
    monthly_packages = [
        monthly_data[m]['packages']
        for m in sorted_months
    ]

    # -----------------------------
    # Top flight destinations
    # -----------------------------
    destination_counts = defaultdict(int)

    for booking in Booking.objects.select_related('flight'):
        if booking.flight:
            destination = booking.flight.destination
            destination_counts[destination] += 1

    top_destinations = sorted(
        destination_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # -----------------------------
    # Recent successful payments
    # -----------------------------
    recent_payments = successful_payments.order_by(
        '-payment_date'
    )[:5]

    context = {
        'flight_bookings': flight_bookings,
        'hotel_bookings': hotel_bookings,
        'package_bookings': package_bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'successful_payments_count': successful_payments.count(),

        'monthly_labels': monthly_labels,
        'monthly_flights': monthly_flights,
        'monthly_hotels': monthly_hotels,
        'monthly_packages': monthly_packages,

        'top_destinations': top_destinations,
        'recent_payments': recent_payments,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )