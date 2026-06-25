from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking
from payments.models import Payment


@login_required
def user_dashboard(request):
    user = request.user

    flight_bookings_qs = Booking.objects.filter(user=user)
    hotel_bookings_qs = HotelBooking.objects.filter(user=user)
    package_bookings_qs = PackageBooking.objects.filter(user=user)

    flight_count = flight_bookings_qs.count()
    hotel_count = hotel_bookings_qs.count()
    package_count = package_bookings_qs.count()

    total_bookings = (
        flight_count +
        hotel_count +
        package_count
    )

    successful_payments = (
        Payment.objects.filter(
            payment_status='success',
            booking__user=user
        )
        |
        Payment.objects.filter(
            payment_status='success',
            hotel_booking__user=user
        )
        |
        Payment.objects.filter(
            payment_status='success',
            package_booking__user=user
        )
    ).distinct()

    total_spent = successful_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    recent_flights = list(
        flight_bookings_qs.select_related('flight').order_by('-created_at')[:5]
    )
    recent_hotels = list(
        hotel_bookings_qs.select_related('hotel').order_by('-created_at')[:5]
    )
    recent_packages = list(
        package_bookings_qs.select_related('package').order_by('-created_at')[:5]
    )

    recent_items = []

    for b in recent_flights:
        recent_items.append({
            'type': 'Flight',
            'title': f"{b.flight.source.code} → {b.flight.destination.code}",
            'date': b.created_at,
            'status': b.booking_status,
            'price': b.total_price,
        })

    for b in recent_hotels:
        recent_items.append({
            'type': 'Hotel',
            'title': b.hotel.name,
            'date': b.created_at,
            'status': b.booking_status,
            'price': b.total_price,
        })

    for b in recent_packages:
        recent_items.append({
            'type': 'Package',
            'title': b.package.name,
            'date': b.created_at,
            'status': b.booking_status,
            'price': b.total_price,
        })

    recent_items = sorted(
        recent_items,
        key=lambda x: x['date'],
        reverse=True
    )[:5]

    booking_breakdown = [
        flight_count,
        hotel_count,
        package_count
    ]

    booking_labels = [
        'Flights',
        'Hotels',
        'Packages'
    ]

    top_category = 'No bookings yet'
    category_map = {
        'Flights': flight_count,
        'Hotels': hotel_count,
        'Packages': package_count,
    }
    if total_bookings > 0:
        top_category = max(
            category_map,
            key=category_map.get
        )

    context = {
        'total_bookings': total_bookings,
        'flight_count': flight_count,
        'hotel_count': hotel_count,
        'package_count': package_count,
        'total_spent': total_spent,
        'recent_items': recent_items,
        'booking_breakdown': booking_breakdown,
        'booking_labels': booking_labels,
        'top_category': top_category,
    }

    return render(
        request,
        'dashboard/user_dashboard.html',
        context
    )