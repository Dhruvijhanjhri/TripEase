from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from flights.models import Flight
from .models import Booking, Passenger
from .forms import PassengerFormSet


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
    # PRICE CALCULATION FIX
    # -------------------------

    if is_via and second_leg_id:

        second_leg = get_object_or_404(
            Flight,
            id=second_leg_id
        )

        first_leg_price = flight.get_price(
            cabin_class
        )

        second_leg_price = second_leg.get_price(
            cabin_class
        )

        price = (
            first_leg_price +
            second_leg_price
        )

    else:

        price = flight.get_price(
            cabin_class
        )

    total_price = (
        price * passengers
    )

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
                        f'Booking created successfully! '
                        f'Reference: {booking.booking_reference}'
                    )

                    return redirect(
                        'bookings:detail',
                        booking_id=booking.id
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
    }

    return render(
        request,
        'bookings/create.html',
        context
    )


@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    context = {
        'booking': booking,
    }

    return render(
        request,
        'bookings/detail.html',
        context
    )


from hotels.models import HotelBooking


@login_required
def booking_list(request):

    flight_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-created_at')

    hotel_bookings = HotelBooking.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'flight_bookings': flight_bookings,
        'hotel_bookings': hotel_bookings,
    }

    return render(
        request,
        'bookings/list.html',
        context
    )