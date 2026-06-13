from datetime import datetime

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib import messages

from .models import Hotel
from .models import Room
from .models import HotelBooking
from .models import HotelGuest

from .forms import HotelSearchForm
from .forms import HotelGuestFormSet


def hotel_search(request):
    """Search hotels"""

    form = HotelSearchForm(
        request.GET or None
    )

    hotels = []
    search_performed = False

    if form.is_valid():

        search_performed = True

        destination = form.cleaned_data[
            "destination"
        ].strip().lower()

        check_in = form.cleaned_data[
            "check_in"
        ]

        check_out = form.cleaned_data[
            "check_out"
        ]

        guests = form.cleaned_data[
            "guests"
        ]

        rooms = form.cleaned_data[
            "rooms"
        ]

        hotels = Hotel.objects.filter(
            search_keywords__icontains=destination
        ).prefetch_related(
            "rooms"
        )

        filtered_hotels = []

        for hotel in hotels:

            available_room = hotel.rooms.filter(
                available_rooms__gte=rooms,
                max_guests__gte=guests
            ).first()

            if available_room:

                hotel.display_room = (
                    available_room
                )

                filtered_hotels.append(
                    hotel
                )

        hotels = filtered_hotels

    context = {
        "form": form,
        "hotels": hotels,
        "search_performed": search_performed
    }

    return render(
        request,
        "hotels/search.html",
        context
    )


def hotel_detail(
    request,
    hotel_id
):
    """Hotel detail page"""

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    rooms = hotel.rooms.filter(
        available_rooms__gt=0
    )

    context = {
        "hotel": hotel,
        "rooms": rooms
    }

    return render(
        request,
        "hotels/detail.html",
        context
    )


@login_required
def hotel_booking(
    request,
    room_id
):
    """Create hotel booking"""

    room = get_object_or_404(
        Room,
        id=room_id
    )

    check_in = request.GET.get(
        "check_in"
    )

    check_out = request.GET.get(
        "check_out"
    )

    guests = int(
        request.GET.get(
            "guests",
            1
        )
    )

    rooms_count = int(
        request.GET.get(
            "rooms",
            1
        )
    )

    nights = 1

    check_in_date = None
    check_out_date = None

    if check_in and check_out:

        check_in_date = datetime.strptime(
            check_in,
            "%Y-%m-%d"
        ).date()

        check_out_date = datetime.strptime(
            check_out,
            "%Y-%m-%d"
        ).date()

        nights = (
            check_out_date -
            check_in_date
        ).days

    total_price = (
        room.price_per_night *
        nights *
        rooms_count
    )

    if request.method == "POST":

        if room.available_rooms < rooms_count:

            messages.error(
                request,
                "Not enough rooms available."
            )

            return redirect(
                "hotels:detail",
                hotel_id=room.hotel.id
            )

        booking = HotelBooking.objects.create(
            user=request.user,
            hotel=room.hotel,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests=guests,
            rooms_count=rooms_count,
            total_price=total_price
        )

        # reduce room count
        room.available_rooms -= (
            rooms_count
        )

        room.save()

        messages.success(
            request,
            "Hotel booked successfully!"
        )

        return redirect(
            "hotels:booking_detail",
            booking_id=booking.id
        )

    context = {
        "room": room,
        "guests": guests,
        "rooms_count": rooms_count,
        "nights": nights,
        "total_price": total_price,
        "check_in": check_in,
        "check_out": check_out
    }

    return render(
        request,
        "hotels/booking.html",
        context
    )


@login_required
def hotel_booking_detail(
    request,
    booking_id
):
    """Hotel booking details"""

    booking = get_object_or_404(
        HotelBooking,
        id=booking_id,
        user=request.user
    )

    context = {
        "booking": booking
    }

    return render(
        request,
        "hotels/booking_detail.html",
        context
    )