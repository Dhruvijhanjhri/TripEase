from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from hotels.models import Hotel
from packages.models import TravelPackage

from .models import HotelReview, PackageReview

from .forms import HotelReviewForm, PackageReviewForm

from hotels.models import HotelBooking
from packages.models import PackageBooking
from django.contrib import messages
from flights.models import Flight
from bookings.models import Booking
from .models import FlightReview
from .forms import FlightReviewForm


@login_required
def add_hotel_review(request, hotel_id):

    hotel = get_object_or_404(Hotel, id=hotel_id)
    booking_exists = HotelBooking.objects.filter(
        user=request.user, hotel=hotel, booking_status="confirmed"
    ).exists()

    if not booking_exists:

        messages.error(
            request, "You can review this hotel only after a confirmed booking."
        )

        return redirect("hotels:detail", hotel.id)

    already_reviewed = HotelReview.objects.filter(
        user=request.user, hotel=hotel
    ).exists()

    if already_reviewed:

        messages.warning(request, "You have already reviewed this hotel.")

        return redirect("hotels:detail", hotel.id)

    if request.method == "POST":

        form = HotelReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.user = request.user
            review.hotel = hotel

            review.save()

            return redirect("hotels:detail", hotel.id)

    else:

        form = HotelReviewForm()

    return render(request, "reviews/hotel_review.html", {"hotel": hotel, "form": form})


@login_required
def add_package_review(request, package_id):

    package = get_object_or_404(TravelPackage, id=package_id)

    booking_exists = PackageBooking.objects.filter(
        user=request.user, package=package, booking_status="confirmed"
    ).exists()

    if not booking_exists:

        messages.error(
            request, "You can review this package only after a confirmed booking."
        )

        return redirect("packages:detail", package.id)

    already_reviewed = PackageReview.objects.filter(
        user=request.user, package=package
    ).exists()

    if already_reviewed:

        messages.warning(request, "You have already reviewed this package.")

        return redirect("packages:detail", package.id)

    if request.method == "POST":

        form = PackageReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.user = request.user
            review.package = package

            review.save()

            return redirect("packages:detail", package.id)

    else:

        form = PackageReviewForm()

    return render(
        request, "reviews/package_review.html", {"package": package, "form": form}
    )


@login_required
def add_flight_review(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    booking_exists = Booking.objects.filter(
        user=request.user, flight=flight, booking_status__in=["confirmed", "completed"]
    ).exists()

    if not booking_exists:
        messages.error(
            request,
            "You can review this flight only after a confirmed/completed booking.",
        )
        return redirect("flights:flight_detail", flight.id)

    already_reviewed = FlightReview.objects.filter(
        user=request.user, flight=flight
    ).exists()

    if already_reviewed:
        messages.warning(request, "You have already reviewed this flight.")
        return redirect("flights:flight_detail", flight.id)

    if request.method == "POST":
        form = FlightReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.flight = flight
            review.save()

            messages.success(request, "Flight review added successfully.")
            return redirect("flights:flight_detail", flight.id)
    else:
        form = FlightReviewForm()

    return render(
        request, "reviews/flight_review.html", {"flight": flight, "form": form}
    )
