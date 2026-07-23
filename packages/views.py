from django.shortcuts import render, get_object_or_404
from .models import TravelPackage
from .forms import PackageSearchForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import PackageBookingForm
from .models import PackageBooking
from reviews.models import PackageReview
from django.db.models import Avg
from django.contrib import messages
from utils.weather import (
    get_weather,
)


def package_search(request):

    form = PackageSearchForm(request.GET or None)

    packages = []
    search_performed = False

    if form.is_valid():

        search_performed = True

        destination = form.cleaned_data["destination"].strip()

        packages = TravelPackage.objects.filter(
            destination__icontains=destination, is_active=True
        )

    return render(
        request,
        "packages/search.html",
        {"form": form, "packages": packages, "search_performed": search_performed},
    )


def package_detail(request, package_id):

    package = get_object_or_404(TravelPackage, id=package_id)

    weather = get_weather(package.destination)

    average_rating = package.reviews.aggregate(Avg("rating"))["rating__avg"]

    review_count = package.reviews.count()

    reviews = package.reviews.all()

    can_review = False
    already_reviewed = False

    if request.user.is_authenticated:

        booking_exists = PackageBooking.objects.filter(
            user=request.user, package=package, booking_status="confirmed"
        ).exists()

        already_reviewed = PackageReview.objects.filter(
            user=request.user, package=package
        ).exists()

        if booking_exists and not already_reviewed:
            can_review = True

    return render(
        request,
        "packages/detail.html",
        {
            "package": package,
            "average_rating": average_rating,
            "review_count": review_count,
            "reviews": reviews,
            "can_review": can_review,
            "already_reviewed": already_reviewed,
            "weather": weather,
        },
    )


@login_required
def package_booking(request, package_id):

    package = get_object_or_404(TravelPackage, id=package_id)

    if request.method == "POST":

        form = PackageBookingForm(request.POST)

        if form.is_valid():

            travellers = form.cleaned_data["travellers_count"]

            total_price = package.price * travellers

            booking = PackageBooking.objects.create(
                user=request.user,
                package=package,
                travel_date=form.cleaned_data["travel_date"],
                travellers_count=travellers,
                total_price=total_price,
                booking_status="pending",
            )

            return redirect("payments:package_payment", booking.id)

    else:

        form = PackageBookingForm()

    return render(request, "packages/booking.html", {"package": package, "form": form})


@login_required
def booking_success(request, booking_id):

    booking = get_object_or_404(PackageBooking, id=booking_id, user=request.user)

    return render(request, "packages/booking_success.html", {"booking": booking})


@login_required
def package_booking_detail(request, booking_reference):

    booking = get_object_or_404(
        PackageBooking.objects.select_related("package"),
        booking_reference=booking_reference,
        user=request.user,
    )

    return render(request, "packages/package_booking_detail.html", {"booking": booking})


@login_required
def cancel_booking(request, booking_reference):

    booking = get_object_or_404(
        PackageBooking, booking_reference=booking_reference, user=request.user
    )

    if request.method == "POST":

        if booking.booking_status != "cancelled":

            booking.booking_status = "cancelled"
            booking.save()

            messages.success(request, "Package booking cancelled successfully.")

    return redirect(
        "packages:booking_detail", booking_reference=booking.booking_reference
    )
