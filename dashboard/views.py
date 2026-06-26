from collections import defaultdict, Counter
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
    flight_bookings_qs = Booking.objects.select_related(
        'flight',
        'flight__source',
        'flight__destination'
    )
    hotel_bookings_qs = HotelBooking.objects.select_related('hotel')
    package_bookings_qs = PackageBooking.objects.select_related('package')

    flight_bookings = flight_bookings_qs.count()
    hotel_bookings = hotel_bookings_qs.count()
    package_bookings = package_bookings_qs.count()

    total_bookings = (
        flight_bookings +
        hotel_bookings +
        package_bookings
    )

    successful_payments = Payment.objects.filter(
        payment_status='success'
    ).order_by('-payment_date')

    total_revenue = successful_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # ---------------------------------
    # Monthly booking trend
    # ---------------------------------
    monthly_data = defaultdict(
        lambda: {
            'flights': 0,
            'hotels': 0,
            'packages': 0
        }
    )

    for booking in flight_bookings_qs:
        month_key = booking.created_at.strftime('%b %Y')
        monthly_data[month_key]['flights'] += 1

    for booking in hotel_bookings_qs:
        month_key = booking.created_at.strftime('%b %Y')
        monthly_data[month_key]['hotels'] += 1

    for booking in package_bookings_qs:
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

    # ---------------------------------
    # Top flight routes
    # ---------------------------------
    route_counter = Counter()

    for booking in flight_bookings_qs:
        if booking.flight:
            route = (
                f"{booking.flight.source.code} → "
                f"{booking.flight.destination.code}"
            )
            route_counter[route] += 1

    top_routes = route_counter.most_common(5)

    # ---------------------------------
    # Top hotel cities
    # ---------------------------------
    hotel_city_counter = Counter()

    for booking in hotel_bookings_qs:
        if booking.hotel:
            hotel_city_counter[booking.hotel.city] += 1

    top_hotel_cities = hotel_city_counter.most_common(5)

    # ---------------------------------
    # Top package destinations
    # ---------------------------------
    package_destination_counter = Counter()

    for booking in package_bookings_qs:
        if booking.package:
            package_destination_counter[
                booking.package.destination
            ] += 1

    top_package_destinations = package_destination_counter.most_common(5)

    # ---------------------------------
    # Recent successful payments
    # ---------------------------------
    recent_payments = successful_payments[:5]

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

        'top_routes': top_routes,
        'top_hotel_cities': top_hotel_cities,
        'top_package_destinations': top_package_destinations,
        'recent_payments': recent_payments,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )