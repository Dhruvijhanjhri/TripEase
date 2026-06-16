from datetime import datetime
from django.db.models import Q

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib import messages

from .models import (
    Hotel,
    Room,
    HotelBooking,
    HotelGuest
)

from .forms import HotelSearchForm


# ==========================================
# HOTEL SEARCH
# ==========================================

def hotel_search(request):

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

        hotels_queryset = Hotel.objects.filter(

            Q(city__icontains=destination) |

            Q(state__icontains=destination) |

            Q(area__icontains=destination) |

            Q(search_keywords__icontains=destination)

        ).prefetch_related(
            "rooms"
        )

        filtered_hotels = []

        for hotel in hotels_queryset:

            room = hotel.rooms.filter(
                available_rooms__gt=0
            ).first()

            if room:

                hotel.display_room = room

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


# ==========================================
# HOTEL DETAIL
# ==========================================

def hotel_detail(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    rooms = hotel.rooms.filter(
        available_rooms__gt=0
    )

    context = {
        "hotel": hotel,
        "rooms": rooms,

        "check_in": request.GET.get(
            "check_in"
        ),

        "check_out": request.GET.get(
            "check_out"
        ),

        "guests": request.GET.get(
            "guests"
        ),

        "rooms_count": request.GET.get(
            "rooms"
        )
    }

    return render(
        request,
        "hotels/detail.html",
        context
    )


# ==========================================
# HOTEL BOOKING
# ==========================================

@login_required
def hotel_booking(
    request,
    room_id
):

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

    guests = request.GET.get(
        "guests"
    )

    rooms_count = request.GET.get(
        "rooms"
    )

   
    # safer conversion
    try:
        guests = int(guests)
    except (TypeError, ValueError):
        guests = 1


    try:
        rooms_count = int(rooms_count)
    except (TypeError, ValueError):
        rooms_count = 1

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

        if not check_in_date or not check_out_date:

            messages.error(
                request,
                "Please select check-in and check-out dates."
            )

            return redirect(
                "hotels:detail",
                hotel_id=room.hotel.id
            )

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


# ==========================================
# BOOKING DETAIL
# ==========================================

@login_required
def hotel_booking_detail(
    request,
    booking_id
):

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

