from collections import defaultdict, Counter
from datetime import datetime, date, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Max, Sum, Count, Avg, Q,F
from django.shortcuts import render
from django.utils import timezone
from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking
from payments.models import Payment
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from bookings.models import Booking
from hotels.models import HotelBooking
from packages.models import PackageBooking
from django.contrib.admin.views.decorators import staff_member_required
import pandas as pd
from ml.revenue_forecaster import RevenueForecaster
from .analytics import get_revenue_forecast_data
from .analytics import get_booking_analytics
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@staff_member_required
def dashboard_home(request):

    # -------------------------------------------------------
    # Dashboard Filters
    # -------------------------------------------------------

    period = request.GET.get("period", "all")
    booking_type = request.GET.get("booking_type", "all")
    payment_status = request.GET.get("payment_status", "all")
    booking_status = request.GET.get("booking_status", "all")
    flight_bookings = Booking.objects.all()
    hotel_bookings = HotelBooking.objects.all()
    package_bookings = PackageBooking.objects.all()
    payments = Payment.objects.all()

    today = timezone.now()

    if period == "today":
        flight_bookings = flight_bookings.filter(created_at__date=today.date())
        hotel_bookings = hotel_bookings.filter(created_at__date=today.date())
        package_bookings = package_bookings.filter(created_at__date=today.date())
        payments = payments.filter(payment_date__date=today.date())

    elif period == "this_week":
        start = today - timedelta(days=today.weekday())

        flight_bookings = flight_bookings.filter(created_at__gte=start)
        hotel_bookings = hotel_bookings.filter(created_at__gte=start)
        package_bookings = package_bookings.filter(created_at__gte=start)
        payments = payments.filter(payment_date__gte=start)

    elif period == "this_month":

        flight_bookings = flight_bookings.filter(
            created_at__month=today.month,
            created_at__year=today.year
        )

        hotel_bookings = hotel_bookings.filter(
            created_at__month=today.month,
            created_at__year=today.year
        )

        package_bookings = package_bookings.filter(
            created_at__month=today.month,
            created_at__year=today.year
        )

        payments = payments.filter(
            payment_date__month=today.month,
            payment_date__year=today.year
        )

    # ------------------------------------------------------------------
    # Base querysets — unchanged from original
    # ------------------------------------------------------------------
    flight_bookings_qs = Booking.objects.select_related(
        'flight',
        'flight__source',
        'flight__destination'
    )
    hotel_bookings_qs = HotelBooking.objects.select_related('hotel', 'user')
    package_bookings_qs = PackageBooking.objects.select_related('package', 'user')

    flight_bookings = flight_bookings_qs.count()
    hotel_bookings = hotel_bookings_qs.count()
    package_bookings = package_bookings_qs.count()

    total_bookings = flight_bookings + hotel_bookings + package_bookings

    successful_payments = Payment.objects.filter(
        payment_status='success'
    ).order_by('-payment_date')

    total_revenue = successful_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # ------------------------------------------------------------------
    # Monthly booking trend — unchanged from original
    # ------------------------------------------------------------------
    monthly_data = defaultdict(
        lambda: {'flights': 0, 'hotels': 0, 'packages': 0}
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

    sorted_months = sorted(monthly_data.keys(), key=month_sort_key)

    monthly_labels  = sorted_months
    monthly_flights  = [monthly_data[m]['flights']  for m in sorted_months]
    monthly_hotels   = [monthly_data[m]['hotels']   for m in sorted_months]
    monthly_packages = [monthly_data[m]['packages'] for m in sorted_months]
    monthly_total    = [
        monthly_data[m]['flights'] + monthly_data[m]['hotels'] + monthly_data[m]['packages']
        for m in sorted_months
    ]

    # ------------------------------------------------------------------
    # Top routes / cities / destinations — unchanged from original
    # ------------------------------------------------------------------
    route_counter = Counter()
    for booking in flight_bookings_qs:
        if booking.flight:
            route = (
                f"{booking.flight.source.code} → "
                f"{booking.flight.destination.code}"
            )
            route_counter[route] += 1
    top_routes = route_counter.most_common(5)

    hotel_city_counter = Counter()
    for booking in hotel_bookings_qs:
        if booking.hotel:
            hotel_city_counter[booking.hotel.city] += 1
    top_hotel_cities = hotel_city_counter.most_common(5)

    package_destination_counter = Counter()
    for booking in package_bookings_qs:
        if booking.package:
            package_destination_counter[booking.package.destination] += 1
    top_package_destinations = package_destination_counter.most_common(5)

    recent_payments = successful_payments[:5]

    # ------------------------------------------------------------------
    # NEW: Booking status counts
    # ------------------------------------------------------------------
    flight_confirmed  = flight_bookings_qs.filter(booking_status='confirmed').count()
    flight_pending    = flight_bookings_qs.filter(booking_status='pending').count()
    flight_cancelled  = flight_bookings_qs.filter(booking_status='cancelled').count()

    hotel_confirmed   = hotel_bookings_qs.filter(booking_status='confirmed').count()
    hotel_pending     = hotel_bookings_qs.filter(booking_status='pending').count()
    hotel_cancelled   = hotel_bookings_qs.filter(booking_status='cancelled').count()

    pkg_confirmed     = package_bookings_qs.filter(booking_status='confirmed').count()
    pkg_pending       = package_bookings_qs.filter(booking_status='pending').count()
    pkg_cancelled     = package_bookings_qs.filter(booking_status='cancelled').count()

    total_confirmed  = flight_confirmed + hotel_confirmed + pkg_confirmed
    total_pending    = flight_pending   + hotel_pending   + pkg_pending
    total_cancelled  = flight_cancelled + hotel_cancelled + pkg_cancelled

    # ------------------------------------------------------------------
    # NEW: Payment method distribution
    # ------------------------------------------------------------------
    payment_method_data = (
        Payment.objects
        .filter(payment_status='success')
        .values('payment_method')
        .annotate(count=Count('id'), revenue=Sum('amount'))
        .order_by('-count')
    )
    payment_methods        = [p['payment_method'] or 'Unknown' for p in payment_method_data]
    payment_method_counts  = [p['count'] for p in payment_method_data]
    payment_method_revenue = [float(p['revenue'] or 0) for p in payment_method_data]

    # ------------------------------------------------------------------
    # NEW: Revenue by booking type
    # ------------------------------------------------------------------
    flight_revenue = (
        Payment.objects
        .filter(payment_status='success', booking__isnull=False)
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    hotel_revenue = (
        Payment.objects
        .filter(payment_status='success', hotel_booking__isnull=False)
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    package_revenue = (
        Payment.objects
        .filter(payment_status='success', package_booking__isnull=False)
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    # ------------------------------------------------------------------
    # NEW: Monthly revenue trend
    # ------------------------------------------------------------------
    monthly_revenue_data = defaultdict(float)
    for payment in successful_payments:
        month_key = payment.payment_date.strftime('%b %Y')
        monthly_revenue_data[month_key] += float(payment.amount)

    monthly_revenue = [monthly_revenue_data.get(m, 0) for m in sorted_months]

    # ------------------------------------------------------------------
    # NEW: Active users
    # ------------------------------------------------------------------
    active_users = User.objects.filter(is_active=True).count()

    # ------------------------------------------------------------------
    # NEW: Today / this-month stats
    # ------------------------------------------------------------------
    today = date.today()
    month_start = today.replace(day=1)

    # bookings today
    flight_today  = flight_bookings_qs.filter(created_at__date=today).count()
    hotel_today   = hotel_bookings_qs.filter(created_at__date=today).count()
    pkg_today     = package_bookings_qs.filter(created_at__date=today).count()
    bookings_today = flight_today + hotel_today + pkg_today

    # revenue today
    revenue_today = (
        Payment.objects
        .filter(payment_status='success', payment_date__date=today)
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    # bookings this month
    flight_month  = flight_bookings_qs.filter(created_at__date__gte=month_start).count()
    hotel_month   = hotel_bookings_qs.filter(created_at__date__gte=month_start).count()
    pkg_month     = package_bookings_qs.filter(created_at__date__gte=month_start).count()
    bookings_this_month = flight_month + hotel_month + pkg_month

    # revenue this month
    revenue_this_month = (
        Payment.objects
        .filter(payment_status='success', payment_date__date__gte=month_start)
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    # ------------------------------------------------------------------
    # NEW: Business insights
    # ------------------------------------------------------------------
    avg_booking_value = (
        float(total_revenue) / total_bookings
        if total_bookings > 0 else 0
    )

    cancellation_pct = (
        round((total_cancelled / total_bookings) * 100, 1)
        if total_bookings > 0 else 0
    )

    # Most booked destination (flight routes)
    most_booked_destination = top_routes[0][0] if top_routes else 'N/A'

    # Most booked hotel city
    most_booked_hotel = top_hotel_cities[0][0] if top_hotel_cities else 'N/A'

    # Most booked package destination
    most_booked_package = top_package_destinations[0][0] if top_package_destinations else 'N/A'

    # Highest spending customer
    customer_spending = {}

    payments = Payment.objects.select_related(
        "booking__user",
        "hotel_booking__user",
        "package_booking__user",
    ).filter(payment_status="success")

    for payment in payments:

        if payment.booking:
            user = payment.booking.user

        elif payment.hotel_booking:
            user = payment.hotel_booking.user

        elif payment.package_booking:
            user = payment.package_booking.user

        else:
            continue

        if user.id not in customer_spending:
            customer_spending[user.id] = {
                "name": user.get_full_name() or user.username,
                "spent": 0
            }

        customer_spending[user.id]["spent"] += float(payment.amount)

    if customer_spending:

        top_spender = max(
            customer_spending.values(),
            key=lambda x: x["spent"]
        )

        highest_spender_name = top_spender["name"]
        highest_spender_amount = top_spender["spent"]

    else:

        highest_spender_name = "N/A"
        highest_spender_amount = 0

    
    # ------------------------------------------------------------------
    # NEW: Recent bookings table (all types merged, last 10)
    # ------------------------------------------------------------------
    recent_flight_bookings = list(
        flight_bookings_qs.order_by('-created_at')
        .select_related('user', 'flight', 'flight__source', 'flight__destination')[:10]
    )
    recent_hotel_bookings  = list(
        hotel_bookings_qs.order_by('-created_at')
        .select_related('user', 'hotel')[:10]
    )
    recent_pkg_bookings    = list(
        package_bookings_qs.order_by('-created_at')
        .select_related('user', 'package')[:10]
    )

    # Build a unified list for the recent activity table
    recent_activity = []
    for b in recent_flight_bookings:
        recent_activity.append({
            'ref': b.booking_reference,
            'customer': b.user.get_full_name() or b.user.username,
            'type': 'Flight',
            'amount': None,          # amount comes from payment
            'booking_status': b.booking_status,
            'date': b.created_at,
            'detail_url': f"/bookings/{b.booking_reference}/",
        })
    for b in recent_hotel_bookings:
        recent_activity.append({
            'ref': b.booking_reference,
            'customer': b.user.get_full_name() or b.user.username,
            'type': 'Hotel',
            'amount': b.total_price,
            'booking_status': b.booking_status,
            'date': b.created_at,
            'detail_url': f"/hotels/booking/{b.booking_reference}/",
        })
    for b in recent_pkg_bookings:
        recent_activity.append({
            'ref': b.booking_reference,
            'customer': b.user.get_full_name() or b.user.username,
            'type': 'Package',
            'amount': b.total_price,
            'booking_status': b.booking_status,
            'date': b.created_at,
            'detail_url': f"/packages/booking/{b.booking_reference}/",
        })

    # sort by date desc and keep top 10
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]

    # ------------------------------------------------------------------
    # NEW: Recent payments (extended — last 10)
    # ------------------------------------------------------------------
    recent_payments_extended = (
        Payment.objects
        .select_related(
            "booking__user",
            "hotel_booking__user",
            "package_booking__user"
        )
        .order_by("-payment_date")[:10]
    )

    # ------------------------------------------------------------------
    # NEW: Top customers by spend
    # ------------------------------------------------------------------
    customer_stats = {}

    payments = Payment.objects.select_related(
        "booking__user",
        "hotel_booking__user",
        "package_booking__user"
    ).filter(payment_status="success")

    for payment in payments:

        if payment.booking:
            user = payment.booking.user

        elif payment.hotel_booking:
            user = payment.hotel_booking.user

        elif payment.package_booking:
            user = payment.package_booking.user

        else:
            continue

        if user.id not in customer_stats:

            customer_stats[user.id] = {
                "username": user.get_full_name() or user.username,
                "total_spent": 0,
                "bookings": 0,
            }

        customer_stats[user.id]["total_spent"] += float(payment.amount)
        customer_stats[user.id]["bookings"] += 1

    top_customers = sorted(
        customer_stats.values(),
        key=lambda x: x["total_spent"],
        reverse=True
    )[:5]

    # ------------------------------------------------------------------
    # NEW: Highest / lowest revenue day
    # ------------------------------------------------------------------
    from django.db.models.functions import TruncDate
    daily_revenue_qs = (
        Payment.objects
        .filter(payment_status='success')
        .annotate(day=TruncDate('payment_date'))
        .values('day')
        .annotate(rev=Sum('amount'))
        .order_by('day')
    )
    daily_revenue_list = list(daily_revenue_qs)

    highest_revenue_day = max(daily_revenue_list, key=lambda x: x['rev'], default=None)
    lowest_revenue_day  = min(daily_revenue_list, key=lambda x: x['rev'], default=None)

    highest_rev_day_label  = highest_revenue_day['day'].strftime('%d %b %Y') if highest_revenue_day else 'N/A'
    highest_rev_day_amount = float(highest_revenue_day['rev']) if highest_revenue_day else 0
    lowest_rev_day_label   = lowest_revenue_day['day'].strftime('%d %b %Y') if lowest_revenue_day else 'N/A'
    lowest_rev_day_amount  = float(lowest_revenue_day['rev']) if lowest_revenue_day else 0

    # ------------------------------------------------------------------
    # Build context
    # ------------------------------------------------------------------
    context = {
        # ---- original variables (DO NOT REMOVE) ----
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

        # ---- new variables ----
        'active_users': active_users,
        'total_confirmed': total_confirmed,
        'total_pending': total_pending,
        'total_cancelled': total_cancelled,

        'monthly_total': monthly_total,
        'monthly_revenue': monthly_revenue,

        'payment_methods': payment_methods,
        'payment_method_counts': payment_method_counts,
        'payment_method_revenue': payment_method_revenue,

        'flight_revenue': float(flight_revenue),
        'hotel_revenue': float(hotel_revenue),
        'package_revenue': float(package_revenue),

        'bookings_today': bookings_today,
        'revenue_today': revenue_today,
        'bookings_this_month': bookings_this_month,
        'revenue_this_month': revenue_this_month,

        'avg_booking_value': round(avg_booking_value, 2),
        'cancellation_pct': cancellation_pct,
        'most_booked_destination': most_booked_destination,
        'most_booked_hotel': most_booked_hotel,
        'most_booked_package': most_booked_package,
        'highest_spender_name': highest_spender_name,
        'highest_spender_amount': highest_spender_amount,

        'recent_activity': recent_activity,
        'recent_payments_extended': recent_payments_extended,
        'top_customers': top_customers,

        'highest_rev_day_label': highest_rev_day_label,
        'highest_rev_day_amount': highest_rev_day_amount,
        'lowest_rev_day_label': lowest_rev_day_label,
        'lowest_rev_day_amount': lowest_rev_day_amount,

        'now': datetime.now(),
    }

    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def booking_trend(request):

    flight_trend = (
        Booking.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    hotel_trend = (
        HotelBooking.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    package_trend = (
        PackageBooking.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    popular_routes = (
        Booking.objects
        .filter(flight__isnull=False)
        .values(
            "flight__source__city",
            "flight__destination__city",
        )
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    
    )

    popular_airlines = (
        Booking.objects
        .filter(flight__isnull=False)
        .values("flight__airline")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # ---------------------------------------
    # Peak Booking Analysis
    # ---------------------------------------

    weekday_counter = Counter()
    hour_counter = Counter()

    for booking in Booking.objects.all():

        weekday_counter[
            booking.created_at.strftime("%A")
        ] += 1

        hour_counter[
            booking.created_at.hour
        ] += 1

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    weekday_labels = weekday_order

    weekday_data = [
        weekday_counter.get(day, 0)
        for day in weekday_order
    ]

    hour_labels = list(range(24))

    hour_data = [
        hour_counter.get(hour, 0)
        for hour in hour_labels
    ]

    peak_day = max(
        weekday_counter,
        key=weekday_counter.get,
        default="N/A"
    )

    peak_hour = max(
        hour_counter,
        key=hour_counter.get,
        default=0
    )

    # ----------------------------------------------------
    # Cancellation Analytics
    # ----------------------------------------------------

    flight_cancelled = Booking.objects.filter(
        booking_status="cancelled"
    ).count()

    hotel_cancelled = HotelBooking.objects.filter(
        booking_status="cancelled"
    ).count()

    package_cancelled = PackageBooking.objects.filter(
        booking_status="cancelled"
    ).count()

    total_cancelled = (
        flight_cancelled +
        hotel_cancelled +
        package_cancelled
    )

    total_bookings_all = (
        Booking.objects.count() +
        HotelBooking.objects.count() +
        PackageBooking.objects.count()
    )

    cancellation_rate = (
        round((total_cancelled / total_bookings_all) * 100, 2)
        if total_bookings_all else 0
    )

    refund_total = (
        Booking.objects.aggregate(
            total=Sum("refund_amount")
        )["total"] or 0
    )

    # ----------------------------------------------------
    # Customer Analytics
    # ----------------------------------------------------

    total_customers = Booking.objects.values("user").distinct().count()

    average_booking_value = (
        Payment.objects.filter(payment_status="success")
        .aggregate(avg=Avg("amount"))["avg"] or 0
    )

    repeat_customers = (
        Booking.objects
        .values("user")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .count()
    )

    repeat_percentage = (
        round((repeat_customers / total_customers) * 100, 1)
        if total_customers else 0
    )

    top_customers = (
        Booking.objects
        .values(
            "user__first_name",
            "user__last_name",
            "user__email",
        )
        .annotate(
            bookings=Count("id"),
            total_spent=Sum("payment__amount"),
        )
        .order_by("-total_spent")[:10]
    )

    # ----------------------------------------------------
    # Customer Segmentation
    # ----------------------------------------------------

    customer_segments = []

    for customer in top_customers:

        spent = float(customer["total_spent"] or 0)
        bookings = customer["bookings"]

        if bookings >= 15 or spent >= 60000:
            segment = "VIP"

        elif bookings >= 8:
            segment = "Frequent"

        elif bookings >= 3:
            segment = "Returning"

        else:
            segment = "New"

        customer_segments.append({
            "name": (
                f'{customer["user__first_name"]} '
                f'{customer["user__last_name"]}'
            ).strip(),
            "email": customer["user__email"],
            "bookings": bookings,
            "spent": spent,
            "segment": segment,
        })

    # ----------------------------------------------------
    # Revenue Distribution
    # ----------------------------------------------------

    flight_revenue = (
        Payment.objects.filter(
            payment_status="success",
            booking__isnull=False
        ).aggregate(total=Sum("amount"))["total"] or 0
    )

    hotel_revenue = (
        Payment.objects.filter(
            payment_status="success",
            hotel_booking__isnull=False
        ).aggregate(total=Sum("amount"))["total"] or 0
    )

    package_revenue = (
        Payment.objects.filter(
            payment_status="success",
            package_booking__isnull=False
        ).aggregate(total=Sum("amount"))["total"] or 0
    )

    segment_counts = {
        "VIP": 0,
        "Frequent": 0,
        "Returning": 0,
        "New": 0,
    }

    for customer in customer_segments:
        segment_counts[customer["segment"]] += 1

    # ----------------------------------------------------
    # Booking Status Analytics
    # ----------------------------------------------------

    booking_status = (
        Booking.objects
        .values("booking_status")
        .annotate(total=Count("id"))
    )

    status_labels = [
        item["booking_status"].title()
        for item in booking_status
    ]

    status_data = [
        item["total"]
        for item in booking_status
    ]

    # ----------------------------------------------------
    # Payment Method Analytics
    # ----------------------------------------------------

    payment_methods = (
        Payment.objects
        .filter(payment_status="success")
        .values("payment_method")
        .annotate(total=Count("id"))
    )

    payment_labels = [
        item["payment_method"].upper()
        for item in payment_methods
    ]

    payment_data = [
        item["total"]
        for item in payment_methods
    ]

    # ----------------------------------------------------
    # Revenue Forecasting (Weighted Moving Average)
    # ----------------------------------------------------

    daily_revenue = (
        Payment.objects
        .filter(payment_status="success")
        .annotate(day=TruncDate("payment_date"))
        .values("day")
        .annotate(
            revenue=Sum("amount")
        )
        .order_by("day")
    )

    revenue_history = [
        float(item["revenue"])
        for item in daily_revenue
    ]

    forecast_labels = []
    forecast_data = []
    forecast_upper = []
    forecast_lower = []

    if revenue_history:

        forecaster = RevenueForecaster()

        (
            forecast_data,
            forecast_upper,
            forecast_lower,
        ) = forecaster.forecast(
            revenue_history,
            future_days=30,
        )

        forecast_labels = [
            f"Day {i}"
            for i in range(1, 31)
        ]
    
    booking_analytics = get_booking_analytics()

    # -------------------------------
    # Forecast Accuracy Metrics
    # -------------------------------

    if len(revenue_history) >= 4:

        actual = revenue_history[-1]
        predicted = forecast_data[0]

        if actual != 0:
            mape = abs(actual - predicted) / actual * 100
            accuracy = round(100 - mape, 2)
        else:
            accuracy = 0

    else:
        accuracy = None

    # -----------------------------
    # Forecast Evaluation
    # -----------------------------

    mae = 0
    rmse = 0
    mape = 0

    if len(revenue_history) >= 5:

        actual = revenue_history[-4:]

        predicted = forecast_data[:4]

        errors = [
            abs(a - p)
            for a, p in zip(actual, predicted)
        ]

        mae = round(sum(errors) / len(errors), 2)

        rmse = round(
            (
                sum((a - p) ** 2 for a, p in zip(actual, predicted))
                / len(actual)
            ) ** 0.5,
            2,
        )

        percentage_errors = []

        for a, p in zip(actual, predicted):

            if a != 0:

                percentage_errors.append(
                    abs((a - p) / a)
                )

        if percentage_errors:

            mape = round(
                sum(percentage_errors)
                / len(percentage_errors)
                * 100,
                2,
            )

    # ----------------------------------------------------
    # Cancellation Chart Data
    # ----------------------------------------------------

    cancel_labels = [
        "Flights",
        "Hotels",
        "Packages",
    ]

    cancel_data = [
        flight_cancelled,
        hotel_cancelled,
        package_cancelled,
    ]

    # ----------------------------------------------------
    # Refund Summary
    # ----------------------------------------------------

    average_refund = (
        Booking.objects.filter(
            booking_status="cancelled"
        ).aggregate(
            avg=Avg("refund_amount")
        )["avg"] or 0
    )

    largest_refund = (
        Booking.objects.filter(
            booking_status="cancelled"
        ).aggregate(
            maximum=Max("refund_amount")
        )["maximum"] or 0
    )

    cancelled_bookings = Booking.objects.filter(
        booking_status="cancelled"
    ).select_related(
        "user",
        "flight"
    ).order_by("-cancelled_at")[:10]

    context = {

        "flight_labels": [
            x["day"].strftime("%d %b")
            for x in flight_trend
        ],

        "flight_data": [
            x["total"]
            for x in flight_trend
        ],

        "hotel_labels": [
            x["day"].strftime("%d %b")
            for x in hotel_trend
        ],

        "hotel_data": [
            x["total"]
            for x in hotel_trend
        ],

        "package_labels": [
            x["day"].strftime("%d %b")
            for x in package_trend
        ],

        "package_data": [
            x["total"]
            for x in package_trend
        ],
        "popular_routes": popular_routes,
        "popular_airlines": popular_airlines,
        "weekday_labels": weekday_labels,
        "weekday_data": weekday_data,

        "hour_labels": hour_labels,
        "hour_data": hour_data,

        "peak_day": peak_day,
        "peak_hour": peak_hour,
        "forecast_labels": forecast_labels,
        "forecast_data": forecast_data,
        "forecast_upper": forecast_upper,
        "forecast_lower": forecast_lower,
        "total_bookings": booking_analytics["total_bookings"],
        "total_revenue": booking_analytics["total_revenue"],
        "average_booking": booking_analytics["average_booking"],
        "forecast_accuracy": accuracy,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "total_customers": total_customers,
        "average_booking_value": average_booking_value,
        "repeat_percentage": repeat_percentage,
        "top_customers": top_customers,
        "customer_segments": customer_segments,
        "flight_revenue": float(flight_revenue),
        "hotel_revenue": float(hotel_revenue),
        "package_revenue": float(package_revenue),

        "vip_count": segment_counts["VIP"],
        "frequent_count": segment_counts["Frequent"],
        "returning_count": segment_counts["Returning"],
        "new_count": segment_counts["New"],
        "status_labels": status_labels,
        "status_data": status_data,

        "payment_labels": payment_labels,
        "payment_data": payment_data,
        "flight_cancelled": flight_cancelled,
        "hotel_cancelled": hotel_cancelled,
        "package_cancelled": package_cancelled,
        "total_cancelled": total_cancelled,
        "cancellation_rate": cancellation_rate,
        "refund_total": refund_total,
        "cancel_labels": cancel_labels,
        "cancel_data": cancel_data,
        "average_refund": average_refund,
        "largest_refund": largest_refund,
        "cancelled_bookings": cancelled_bookings,
    }

    return render(
        request,
        "dashboard/booking_trend.html",
        context
    )

def revenue_forecast(request):
    """
    Revenue Forecast Analytics
    """

    context = get_revenue_forecast_data()

    return render(
        request,
        "dashboard/revenue_forecast.html",
        context,
    )