from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from flights.models import Flight
from flights.realism import format_duration_minutes, get_route_price
from .models import Booking, Passenger
from .forms import PassengerFormSet
from hotels.models import HotelBooking
from packages.models import PackageBooking
from django.contrib.auth.decorators import login_required
from .models import Booking
from django.utils import timezone
from integrations.flight_status_service import FlightStatusService
from bookings.seat_utils import generate_seat_map
from bookings.boarding_pass import generate_boarding_pass
import random
from datetime import timedelta
from django.http import FileResponse

@login_required
def create_booking(request, flight_id):
    """Create booking"""

    flight = get_object_or_404(
        Flight,
        id=flight_id
    )

    cabin_class = request.GET.get(
    'cabin_class',
    'economy'
    ).strip()

    passengers = int(
        request.GET.get(
            'passengers',
            1
        )
    )

    departure_date = request.GET.get(
        'departure_date'
    )

    is_via = request.GET.get(
    'is_via',
    ''
    ).strip()

    second_leg_id = request.GET.get(
    'second_leg_id',
    ''
    ).strip()

    second_leg = None

    travel_date = None

    if departure_date:
        try:
            travel_date = datetime.strptime(
                departure_date.strip(),
                "%Y-%m-%d"
            ).date()
        except:
            travel_date = None

    # -------------------------
    # REAL FLIGHT PRICING
    # -------------------------

    if is_via and second_leg_id:

        second_leg = get_object_or_404(
            Flight,
            id=second_leg_id
        )

        first_leg_price = flight.get_price(cabin_class)
        second_leg_price = second_leg.get_price(cabin_class)

        price = first_leg_price + second_leg_price

    else:

        price = flight.get_price(cabin_class)

    total_price = price * passengers

    if second_leg:
        duration_minutes = int(
            (
                second_leg.arrival_time - flight.departure_time
            ).total_seconds() / 60
        )
    else:
        duration_minutes = flight.duration_minutes

    duration_display = format_duration_minutes(duration_minutes)

    # -------------------------
    # POST REQUEST
    # -------------------------

    if request.method == 'POST':

        formset = PassengerFormSet(
            request.POST
        )

        if formset.is_valid():

            # seat check
            if (
                flight.available_seats
                < passengers
            ):
                messages.error(
                    request,
                    'Not enough seats available.'
                )

                return redirect(
                    'flights:flight_detail',
                    flight_id=flight_id
                )

            if second_leg:
                if (
                    second_leg.available_seats
                    < passengers
                ):
                    messages.error(
                        request,
                        'Not enough seats on connecting flight.'
                    )

                    return redirect(
                        'flights:flight_detail',
                        flight_id=flight_id
                    )

            try:
                with transaction.atomic():

                    booking = Booking.objects.create(
                        user=request.user,
                        flight=flight,
                        second_flight=second_leg,
                        cabin_class=cabin_class,
                        number_of_passengers=passengers,
                        total_price=total_price,
                        travel_date=travel_date,
                        booking_status='pending'
                    )

                    for form in formset:

                        if form.cleaned_data:

                            Passenger.objects.create(
                                booking=booking,
                                **form.cleaned_data
                            )

                    # reduce seats
                    flight.available_seats -= passengers
                    flight.save()

                    if second_leg:
                        second_leg.available_seats -= passengers
                        second_leg.save()

                    messages.success(
                        request,
                        "Passenger details saved successfully. Please select your seats."
                    )

                    return redirect(
                        "bookings:select_seats",
                        booking_reference=booking.booking_reference
                    )

            except Exception as e:

                messages.error(
                    request,
                    f'Error creating booking: {str(e)}'
                )

    else:

        formset = PassengerFormSet(
            initial=[
                {}
                for _ in range(passengers)
            ]
        )

    context = {
        'flight': flight,
        'second_leg': second_leg,
        'cabin_class': cabin_class,
        'passengers': passengers,
        'price': price,
        'total_price': total_price,
        'formset': formset,
        'is_via': is_via,
        'second_leg_id': second_leg_id,
        'departure_date': departure_date,
        'travel_date': travel_date,
        'duration_display': duration_display,
        'seat_display': flight.get_seat_display(),
        'flight_number_display': flight.get_display_flight_number(),
    }

    return render(
        request,
        'bookings/create.html',
        context
    )

@login_required
def booking_list(request):

    status = request.GET.get("status")
    month = request.GET.get("month")

    flight_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-created_at')

    if status:
        flight_bookings = flight_bookings.filter(
            booking_status=status
        )

    hotel_bookings = HotelBooking.objects.filter(
        user=request.user
    )

    if status:
        hotel_bookings = hotel_bookings.filter(
            booking_status=status
        )

    hotel_bookings = hotel_bookings.order_by('-created_at')

    package_bookings = PackageBooking.objects.filter(
        user=request.user
    )

    if status:
        package_bookings = package_bookings.filter(
            booking_status=status
        )

    package_bookings = package_bookings.order_by('-created_at')

    if month:

        try:

            month_date = datetime.strptime(
                month,
                "%b %Y"
            )

            flight_bookings = flight_bookings.filter(
                travel_date__year=month_date.year,
                travel_date__month=month_date.month
            )

            hotel_bookings = hotel_bookings.filter(
                check_in_date__year=month_date.year,
                check_in_date__month=month_date.month
            )

            package_bookings = package_bookings.filter(
                travel_date__year=month_date.year,
                travel_date__month=month_date.month
            )

        except:

            pass

    context = {
        'flight_bookings': flight_bookings,
        'hotel_bookings': hotel_bookings,
        'package_bookings': package_bookings,
    }

    return render(
        request,
        'bookings/list.html',
        context
    )


@login_required
def booking_detail(request, booking_reference):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'flight__source',
            'flight__destination'
        ).prefetch_related('passengers'),
        booking_reference=booking_reference,
        user=request.user
    )

    live_status = None

    try:
        flight_number = booking.flight.get_display_flight_number()

        print("=" * 50)
        print("Flight Number Sent:", flight_number)
        print("=" * 50)

        response = FlightStatusService.get_flight_status(flight_number)

        print(response)

        if response.get("data"):
            live_status = response["data"][0]

    except Exception:
        live_status = None

    return render(
        request,
        'bookings/booking_detail.html',
        {
            'booking': booking,
            "live_status": live_status,
        }
    )

@login_required
def cancel_booking(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user
    )

    if booking.booking_status == "cancelled":

        messages.warning(
            request,
            "Booking already cancelled."
        )

        return redirect(
            "bookings:detail",
            booking_reference=booking.booking_reference
        )

    booking.booking_status = "cancelled"

    booking.cancelled_at = timezone.now()

    booking.refund_amount = booking.total_price

    booking.save()

    booking.flight.available_seats += booking.number_of_passengers

    booking.flight.save()

    messages.success(
        request,
        "Booking cancelled successfully."
    )

    return redirect(
        "bookings:detail",
        booking_reference=booking.booking_reference
    )

@login_required
def check_in_confirm(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user
    )

    context = {
        "booking": booking,
    }

    return render(
        request,
        "bookings/check_in_confirm.html",
        context
    )

@login_required
def check_in(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user
    )

    if booking.booking_status != "confirmed":

        messages.error(
            request,
            "Only confirmed bookings can be checked in."
        )

        return redirect(
            "bookings:detail",
            booking_reference=booking.booking_reference
        )

    if booking.checked_in:

        messages.info(
            request,
            "You have already checked in."
        )

        return redirect(
            "bookings:detail",
            booking_reference=booking.booking_reference
        )

    booking.checked_in = True
    booking.checked_in_at = timezone.now()
    booking.terminal = f"T{random.randint(1,3)}"

    booking.gate = f"G{random.randint(1,25)}"

    booking.boarding_time = (
        booking.flight.departure_time
        - timedelta(minutes=45)
    )

    booking.save()

    pdf_path = generate_boarding_pass(booking)

    print("=" * 60)
    print("Returned path:", pdf_path)
    print("=" * 60)

    booking.boarding_pass.name = pdf_path
    booking.save()

    booking.refresh_from_db()

    print("Saved in DB:", booking.boarding_pass.name)
    print("=" * 60)

    messages.success(
        request,
        "Check-in completed successfully!"
    )

    return redirect(
        "bookings:detail",
        booking_reference=booking.booking_reference
    )

@login_required
def select_seats(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user
    )

    booked_seats = list(
        Passenger.objects.filter(
            booking__flight=booking.flight
        ).exclude(
            seat_number__isnull=True
        ).exclude(
            seat_number=""
        ).values_list(
            "seat_number",
            flat=True
        )
    )

    seat_map = generate_seat_map(booked_seats)

    if request.method == "POST":

        selected_seats = request.POST.getlist("seats")

        already_booked = set(
            Passenger.objects.filter(
                booking__flight=booking.flight,
                seat_number__in=selected_seats
            ).values_list(
                "seat_number",
                flat=True
            )
        )

        if already_booked:

            messages.error(
                request,
                f"Seat(s) already booked: {', '.join(already_booked)}"
            )

            return render(
                request,
                "bookings/select_seats.html",
                {
                    "booking": booking,
                    "seat_map": generate_seat_map(
                        list(
                            Passenger.objects.filter(
                                booking__flight=booking.flight
                            ).exclude(
                                seat_number__isnull=True
                            ).exclude(
                                seat_number=""
                            ).values_list(
                                "seat_number",
                                flat=True
                            )
                        )
                    ),
                }
        )

        if len(selected_seats) != booking.number_of_passengers:

            messages.error(
                request,
                f"Please select exactly {booking.number_of_passengers} seat(s)."
            )

        else:

            passengers = booking.passengers.all()

            for passenger, seat in zip(passengers, selected_seats):
                passenger.seat_number = seat
                passenger.save()

            messages.success(
                request,
                "Seats selected successfully."
            )

            return redirect(
                "payments:payment",
                booking.id
            )

    return render(
        request,
        "bookings/select_seats.html",
        {
            "booking": booking,
            "seat_map": seat_map,
        }
    )

@login_required
def download_boarding_pass(request, booking_reference):

    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user
    )

    if not booking.boarding_pass:

        messages.error(
            request,
            "Boarding pass not available."
        )

        return redirect(
            "bookings:detail",
            booking_reference=booking_reference
        )

    return FileResponse(
        booking.boarding_pass.open("rb"),
        as_attachment=True,
        filename=f"{booking.booking_reference}.pdf"
    )