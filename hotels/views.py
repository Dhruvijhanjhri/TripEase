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
from .models import Hotel
from .models import Room
from .models import HotelBooking
from .models import HotelGuest
from payments.models import Payment
from .forms import HotelSearchForm
from .forms import HotelGuestFormSet
from .forms import HotelPaymentForm
from reviews.models import HotelReview
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .models import HotelBooking

def hotel_search(request):

    form = HotelSearchForm(
        request.GET or None
    )

    hotels = []
    search_performed = False

    if form.is_valid():

        search_performed = True

        destination = (
            form.cleaned_data["destination"]
            .strip()
            .lower()
        )

        hotels_queryset = Hotel.objects.filter(
            Q(city__icontains=destination) |
            Q(state__icontains=destination) |
            Q(area__icontains=destination) |
            Q(search_keywords__icontains=destination)
        ).prefetch_related("rooms")

        filtered_hotels = []

        for hotel in hotels_queryset:

            available_room = hotel.rooms.filter(
                available_rooms__gt=0
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

def hotel_detail(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    rooms = hotel.rooms.filter(
        available_rooms__gt=0
    )

    average_rating = hotel.reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    review_count = hotel.reviews.count()

    reviews = hotel.reviews.all()

    can_review = False
    already_reviewed = False

    if request.user.is_authenticated:

        booking_exists = HotelBooking.objects.filter(
            user=request.user,
            hotel=hotel,
            booking_status="confirmed"
        ).exists()

        already_reviewed = HotelReview.objects.filter(
            user=request.user,
            hotel=hotel
        ).exists()

        if booking_exists and not already_reviewed:
            can_review = True

    context = {
        "hotel": hotel,
        "rooms": rooms,
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
        "guests": request.GET.get("guests"),
        "rooms_count": request.GET.get("rooms"),
        "average_rating": average_rating,
        "review_count": review_count,
        "reviews": reviews,
        "can_review": can_review,
        "already_reviewed": already_reviewed,
    }

    return render(
        request,
        "hotels/detail.html",
        context
    )


@login_required
def hotel_booking(request, room_id):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    check_in = request.GET.get(
        "check_in",
        ""
    )

    check_out = request.GET.get(
        "check_out",
        ""
    )

    guests = request.GET.get(
        "guests",
        "1"
    )

    rooms_count = request.GET.get(
        "rooms",
        "1"
    )

    try:
        guests = int(guests)
    except:
        guests = 1

    try:
        rooms_count = int(
            rooms_count
        )
    except:
        rooms_count = 1

    check_in_date = None
    check_out_date = None
    nights = 1

    if check_in and check_out:

        try:

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

            if nights <= 0:
                nights = 1

        except:
            nights = 1

    total_price = (
        room.price_per_night *
        nights *
        rooms_count
    )

    if request.method == "POST":

        guests = int(
            request.POST.get(
                "guests",
                guests
            )
        )

        rooms_count = int(
            request.POST.get(
                "rooms_count",
                rooms_count
            )
        )

        if (
            room.available_rooms
            < rooms_count
        ):

            messages.error(
                request,
                "Not enough rooms available."
            )

            return redirect(
                "hotels:detail",
                hotel_id=room.hotel.id
            )

        max_allowed_guests = (
            room.max_guests *
            rooms_count
        )

        if guests > max_allowed_guests:

            messages.error(
                request,
                f"Maximum {max_allowed_guests} guests allowed "
                f"for {rooms_count} room(s)."
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
            total_price=total_price,
            booking_status="pending"
        )

        room.available_rooms -= (
            rooms_count
        )
        room.save()

        return redirect(
            "hotels:payment",
            booking_id=booking.id
        )

    context = {
        "room": room,
        "guests": guests,
        "rooms_count": rooms_count,
        "nights": nights,
        "total_price": total_price,
        "check_in": check_in,
        "check_out": check_out,
    }

    return render(
        request,
        "hotels/booking.html",
        context
    )


@login_required
def hotel_booking_detail(request, booking_reference):

    booking = get_object_or_404(
        HotelBooking.objects.select_related(
            "hotel",
            "room"
        ),
        booking_reference=booking_reference,
        user=request.user
    )

    return render(
        request,
        "hotels/hotel_booking_detail.html",
        {
            "booking": booking
        }
    )

@login_required
def hotel_payment(
    request,
    booking_id
):

    booking = get_object_or_404(
        HotelBooking,
        id=booking_id,
        user=request.user
    )

    nights = (
        booking.check_out_date -
        booking.check_in_date
    ).days

    if nights <= 0:
        nights = 1

    if hasattr(booking, 'payment'):
        messages.info(
            request,
            'Payment already processed.'
        )

        return redirect(
            'hotels:booking_detail',
            booking_reference=booking.booking_reference
        )

    if request.method == "POST":

        form = HotelPaymentForm(request.POST)

        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']

            payment = Payment.objects.create(
                hotel_booking=booking,
                amount=booking.total_price,
                payment_method=payment_method,
                payment_status='success',
                transaction_id=f'HOTEL{booking.id:06d}'
            )

            booking.booking_status = "confirmed"
            booking.save()

            messages.success(
                request,
                "Payment successful!"
            )

            return redirect(
                "hotels:booking_detail",
                booking_reference=booking.booking_reference
            )
    else:
        form = HotelPaymentForm()

    context = {
        "booking": booking,
        "nights": nights,
        "form": form,
    }

    return render(
        request,
        "hotels/payment.html",
        context
    )

@login_required
def cancel_booking(request, booking_reference):

    booking = get_object_or_404(
        HotelBooking,
        booking_reference=booking_reference,
        user=request.user
    )

    if booking.booking_status == "cancelled":

        messages.warning(
            request,
            "Booking already cancelled."
        )

        return redirect(
            "hotels:booking_detail",
            booking_reference=booking.booking_reference
        )

    booking.booking_status = "cancelled"

    booking.save()

    booking.room.available_rooms += booking.rooms_count

    booking.room.save()

    messages.success(
        request,
        "Hotel booking cancelled successfully."
    )

    return redirect(
        "hotels:booking_detail",
        booking_reference=booking.booking_reference
    )