from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta

from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking


@login_required
def user_dashboard(request):
    user = request.user
    now = timezone.now()

    # ─────────────────────────────────────────────────────────────
    # FETCH ALL BOOKINGS — OPTIMIZED QUERIES (evaluated once each)
    # ─────────────────────────────────────────────────────────────

    flight_bookings = list(
        Booking.objects
        .filter(user=user)
        .select_related('flight', 'flight__source', 'flight__destination')
    )

    hotel_bookings = list(
        HotelBooking.objects
        .filter(user=user)
        .select_related('hotel', 'room')
    )

    package_bookings = list(
        PackageBooking.objects
        .filter(user=user)
        .select_related('package')
    )

    # ─────────────────────────────────────────────────────────────
    # 1. TRAVEL SNAPSHOT — COUNTS
    # ─────────────────────────────────────────────────────────────

    total_flight_bookings  = len(flight_bookings)
    total_hotel_bookings   = len(hotel_bookings)
    total_package_bookings = len(package_bookings)
    total_bookings         = total_flight_bookings + total_hotel_bookings + total_package_bookings

    # ─────────────────────────────────────────────────────────────
    # 2. SPENDING TOTALS
    # ─────────────────────────────────────────────────────────────

    flight_spending  = sum((b.total_price for b in flight_bookings),  Decimal('0.00'))
    hotel_spending   = sum((b.total_price for b in hotel_bookings),   Decimal('0.00'))
    package_spending = sum((b.total_price for b in package_bookings), Decimal('0.00'))
    total_spending   = flight_spending + hotel_spending + package_spending

    # ─────────────────────────────────────────────────────────────
    # 3. UPCOMING TRIPS
    # ─────────────────────────────────────────────────────────────

    today = now.date()

    upcoming_flights = sum(
        1 for b in flight_bookings
        if b.travel_date and b.travel_date >= today
        and b.booking_status in ('pending', 'confirmed')
    )

    upcoming_hotels = sum(
        1 for b in hotel_bookings
        if b.check_in_date and b.check_in_date >= today
        and b.booking_status in ('pending', 'confirmed')
    )

    upcoming_packages = sum(
        1 for b in package_bookings
        if b.travel_date and b.travel_date >= today
        and b.booking_status in ('pending', 'confirmed')
    )

    upcoming_trips = upcoming_flights + upcoming_hotels + upcoming_packages

    # ─────────────────────────────────────────────────────────────
    # 4. COMPLETED TRIPS
    # ─────────────────────────────────────────────────────────────

    completed_flights = sum(
        1 for b in flight_bookings
        if b.booking_status == 'completed'
    )

    completed_hotels = sum(
        1 for b in hotel_bookings
        if b.check_out_date and b.check_out_date < today
        and b.booking_status == 'confirmed'
    )

    completed_packages = sum(
        1 for b in package_bookings
        if b.travel_date and b.travel_date < today
        and b.booking_status == 'confirmed'
    )

    completed_trips = completed_flights + completed_hotels + completed_packages

    # ─────────────────────────────────────────────────────────────
    # 5. BOOKING DISTRIBUTION
    # ─────────────────────────────────────────────────────────────

    booking_distribution_labels = ['Flights', 'Hotels', 'Packages']
    booking_distribution_values = [
        total_flight_bookings,
        total_hotel_bookings,
        total_package_bookings,
    ]

    # ─────────────────────────────────────────────────────────────
    # 6. BOOKING STATUS — COMBINED ACROSS ALL TYPES
    # ─────────────────────────────────────────────────────────────

    status_counter = Counter()

    for b in flight_bookings:
        status_counter[b.booking_status] += 1

    for b in hotel_bookings:
        status_counter[b.booking_status] += 1

    for b in package_bookings:
        status_counter[b.booking_status] += 1

    all_statuses         = ['pending', 'confirmed', 'cancelled', 'completed']
    booking_status_labels = [s.capitalize() for s in all_statuses]
    booking_status_values = [status_counter.get(s, 0) for s in all_statuses]

    confirmed_count   = status_counter.get('confirmed', 0)
    cancelled_count   = status_counter.get('cancelled', 0)
    pending_count     = status_counter.get('pending', 0)
    completed_count   = status_counter.get('completed', 0)

    # ─────────────────────────────────────────────────────────────
    # 7. MONTHLY SPENDING — LAST 12 MONTHS
    # ─────────────────────────────────────────────────────────────

    monthly_spending   = defaultdict(Decimal)
    twelve_months_ago  = now - timedelta(days=365)

    for b in flight_bookings:
        if b.created_at >= twelve_months_ago:
            monthly_spending[b.created_at.strftime('%b %Y')] += b.total_price

    for b in hotel_bookings:
        if b.created_at >= twelve_months_ago:
            monthly_spending[b.created_at.strftime('%b %Y')] += b.total_price

    for b in package_bookings:
        if b.created_at >= twelve_months_ago:
            monthly_spending[b.created_at.strftime('%b %Y')] += b.total_price

    # Build ordered deduplicated list of last 12 months
    seen                 = set()
    unique_ordered_months = []
    for i in range(11, -1, -1):
        month_key = (now - timedelta(days=i * 30)).strftime('%b %Y')
        if month_key not in seen:
            seen.add(month_key)
            unique_ordered_months.append(month_key)

    monthly_labels = unique_ordered_months
    monthly_values = [
        float(monthly_spending.get(m, Decimal('0.00')))
        for m in monthly_labels
    ]

    # Determine busiest month (highest spend)
    favourite_month = None
    if any(v > 0 for v in monthly_values):
        max_idx         = monthly_values.index(max(monthly_values))
        favourite_month = monthly_labels[max_idx]

    # ─────────────────────────────────────────────────────────────
    # 8. FAVOURITE DESTINATIONS — TOP 5
    # ─────────────────────────────────────────────────────────────

    destination_counter = Counter()

    for b in flight_bookings:
        city = b.flight.destination.city
        if city:
            destination_counter[city] += 1

    for b in hotel_bookings:
        city = b.hotel.city
        if city:
            destination_counter[city] += 1

    for b in package_bookings:
        dest = b.package.destination
        if dest:
            destination_counter[dest] += 1

    top_destinations   = destination_counter.most_common(5)
    destination_labels = [d[0] for d in top_destinations]
    destination_values = [d[1] for d in top_destinations]

    favourite_destination = destination_labels[0] if destination_labels else None

    # ─────────────────────────────────────────────────────────────
    # 9. FAVOURITE HOTELS — TOP 5
    # ─────────────────────────────────────────────────────────────

    hotel_counter = Counter()
    for b in hotel_bookings:
        if b.hotel.name:
            hotel_counter[b.hotel.name] += 1

    top_hotels     = hotel_counter.most_common(5)
    favorite_hotels = [
        {'hotel_name': name, 'booking_count': count}
        for name, count in top_hotels
    ]

    # ─────────────────────────────────────────────────────────────
    # 10. ANALYTICS — DERIVED METRICS
    # ─────────────────────────────────────────────────────────────

    # Average booking value (all bookings combined)
    avg_booking_value = (
        (total_spending / total_bookings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if total_bookings > 0
        else None
    )

    # Average flight cost
    avg_flight_cost = (
        (flight_spending / total_flight_bookings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if total_flight_bookings > 0
        else None
    )

    # Average hotel cost
    avg_hotel_cost = (
        (hotel_spending / total_hotel_bookings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if total_hotel_bookings > 0
        else None
    )

    # Average package cost
    avg_package_cost = (
        (package_spending / total_package_bookings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if total_package_bookings > 0
        else None
    )

    # Booking success rate (confirmed + completed vs total)
    success_rate = None
    if total_bookings > 0:
        success_rate = round(
            ((confirmed_count + completed_count) / total_bookings) * 100, 1
        )

    # Cancellation rate
    cancellation_rate = None
    if total_bookings > 0:
        cancellation_rate = round(
            (cancelled_count / total_bookings) * 100, 1
        )

    # Travel frequency — bookings per month over active period
    travel_frequency = None
    if total_bookings > 0:
        all_dates = []
        for b in flight_bookings:
            all_dates.append(b.created_at)
        for b in hotel_bookings:
            all_dates.append(b.created_at)
        for b in package_bookings:
            all_dates.append(b.created_at)

        if all_dates:
            earliest = min(all_dates)
            delta_days = (now - earliest).days or 1
            months_active = max(delta_days / 30, 1)
            travel_frequency = round(total_bookings / months_active, 1)

    # ─────────────────────────────────────────────────────────────
    # 11. AI-STYLE TRAVEL INSIGHTS (DYNAMIC, GENERATED IN PYTHON)
    # ─────────────────────────────────────────────────────────────

    insights = []

    # Insight: dominant booking type
    if total_bookings > 0:
        type_map = {
            'Flights':  total_flight_bookings,
            'Hotels':   total_hotel_bookings,
            'Packages': total_package_bookings,
        }
        dominant_type  = max(type_map, key=type_map.get)
        dominant_pct   = round((type_map[dominant_type] / total_bookings) * 100, 1)
        if dominant_pct > 0:
            insights.append(
                f"{dominant_type} account for {dominant_pct}% of your total travel bookings."
            )

    # Insight: favourite destination
    if favourite_destination:
        visit_count = destination_counter[favourite_destination]
        insights.append(
            f"Your favourite destination is {favourite_destination}"
            f" — visited {visit_count} time{'s' if visit_count != 1 else ''}."
        )

    # Insight: average booking value
    if avg_booking_value:
        insights.append(
            f"Your average booking value is ₹{avg_booking_value:,.2f}."
        )

    # Insight: busiest month
    if favourite_month:
        insights.append(
            f"{favourite_month} is your highest-spending month."
        )

    # Insight: cancellation behaviour
    if cancellation_rate is not None:
        if cancellation_rate == 0:
            insights.append("You have a perfect booking record — zero cancellations!")
        elif cancellation_rate < 10:
            insights.append(
                f"You rarely cancel bookings — your cancellation rate is only {cancellation_rate}%."
            )
        else:
            insights.append(
                f"Your cancellation rate is {cancellation_rate}%. "
                "Booking closer to travel dates may help reduce cancellations."
            )

    # Insight: upcoming trips
    if upcoming_trips > 0:
        insights.append(
            f"You have {upcoming_trips} upcoming trip{'s' if upcoming_trips != 1 else ''} — exciting times ahead!"
        )

    # Insight: success rate
    if success_rate is not None and success_rate >= 80:
        insights.append(
            f"Your booking success rate is {success_rate}% — excellent planning!"
        )

    # Fallback if no data at all
    if not insights:
        insights.append(
            "Start booking flights, hotels, or packages to unlock personalised travel insights."
        )

    # ─────────────────────────────────────────────────────────────
    # 12. RECENT ACTIVITY — MERGED, NEWEST FIRST, TOP 10
    # ─────────────────────────────────────────────────────────────

    recent_activity = []

    for b in flight_bookings:
        recent_activity.append({
            'type':   'Flight',
            'title':  (
                f"{b.flight.source.city} → {b.flight.destination.city}"
                f" ({b.flight.airline})"
            ),
            'date':   b.created_at,
            'status': b.booking_status.capitalize(),
            'amount': b.total_price,
        })

    for b in hotel_bookings:
        recent_activity.append({
            'type':   'Hotel',
            'title':  f"{b.hotel.name}, {b.hotel.city}",
            'date':   b.created_at,
            'status': b.booking_status.capitalize(),
            'amount': b.total_price,
        })

    for b in package_bookings:
        recent_activity.append({
            'type':   'Package',
            'title':  f"{b.package.name} — {b.package.destination}",
            'date':   b.created_at,
            'status': b.booking_status.capitalize(),
            'amount': b.total_price,
        })

    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]

    # ─────────────────────────────────────────────────────────────
    # 13. CONTEXT — SINGLE DICTIONARY, NO DUPLICATES
    # ─────────────────────────────────────────────────────────────

    context = {
        # ── Snapshot
        'total_bookings':          total_bookings,
        'total_flight_bookings':   total_flight_bookings,
        'total_hotel_bookings':    total_hotel_bookings,
        'total_package_bookings':  total_package_bookings,
        'total_spending':          total_spending,
        'upcoming_trips':          upcoming_trips,
        'completed_trips':         completed_trips,

        # ── Distribution chart
        'booking_distribution_labels': booking_distribution_labels,
        'booking_distribution_values': booking_distribution_values,

        # ── Status chart
        'booking_status_labels': booking_status_labels,
        'booking_status_values': booking_status_values,

        # ── Monthly spending chart
        'monthly_labels': monthly_labels,
        'monthly_values': monthly_values,

        # ── Destinations chart
        'destination_labels': destination_labels,
        'destination_values': destination_values,

        # ── Hotels table
        'favorite_hotels': favorite_hotels,

        # ── Recent activity
        'recent_activity': recent_activity,

        # ── Analytics metrics
        'avg_booking_value':  avg_booking_value,
        'avg_flight_cost':    avg_flight_cost,
        'avg_hotel_cost':     avg_hotel_cost,
        'avg_package_cost':   avg_package_cost,
        'success_rate':       success_rate,
        'cancellation_rate':  cancellation_rate,
        'travel_frequency':   travel_frequency,
        'favourite_month':    favourite_month,

        # ── Travel insights
        'insights': insights,

        # ── Helper for template guards
        'has_spending': total_spending > Decimal('0.00'),
        'has_destinations': bool(destination_labels),
    }

    return render(request, 'dashboard/user_dashboard.html', context)
