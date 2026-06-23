from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import (
    login_required
)

from hotels.models import Hotel
from packages.models import TravelPackage

from .models import (
    HotelReview,
    PackageReview
)

from .forms import (
    HotelReviewForm,
    PackageReviewForm
)


@login_required
def add_hotel_review(
    request,
    hotel_id
):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    if request.method == "POST":

        form = HotelReviewForm(
            request.POST
        )

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.user = request.user
            review.hotel = hotel

            review.save()

            return redirect(
                "hotels:detail",
                hotel.id
            )

    else:

        form = HotelReviewForm()

    return render(
        request,
        "reviews/hotel_review.html",
        {
            "hotel": hotel,
            "form": form
        }
    )


@login_required
def add_package_review(
    request,
    package_id
):

    package = get_object_or_404(
        TravelPackage,
        id=package_id
    )

    if request.method == "POST":

        form = PackageReviewForm(
            request.POST
        )

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.user = request.user
            review.package = package

            review.save()

            return redirect(
                "packages:detail",
                package.id
            )

    else:

        form = PackageReviewForm()

    return render(
        request,
        "reviews/package_review.html",
        {
            "package": package,
            "form": form
        }
    )