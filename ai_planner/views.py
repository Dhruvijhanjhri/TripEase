from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import TripPlannerForm
from .models import TripPlan
from .services import generate_trip_plan


@login_required
def planner_home(request):
    if request.method == "POST":
        form = TripPlannerForm(request.POST)

        if form.is_valid():
            destination = form.cleaned_data["destination"]
            budget = form.cleaned_data["budget"]
            days = form.cleaned_data["days"]
            interests = form.cleaned_data["interests"]

            planner_output = generate_trip_plan(
                destination=destination,
                budget=budget,
                days=days,
                interests=interests
            )

            trip = TripPlan.objects.create(
                user=request.user,
                destination=destination,
                budget=budget,
                days=days,
                interests=interests,
                generated_plan=planner_output["generated_plan"],
                estimated_cost=planner_output["estimated_cost"],
                recommended_hotels=planner_output["hotel_ids"],
                recommended_packages=planner_output["package_ids"],
            )

            return redirect("ai_planner:result", trip.id)

    else:
        form = TripPlannerForm()

    return render(request, "ai_planner/planner.html", {"form": form})


@login_required
def planner_result(request, trip_id):
    trip = get_object_or_404(
        TripPlan,
        id=trip_id,
        user=request.user
    )

    hotel_ids = [
        int(x) for x in trip.recommended_hotels.split(",")
        if x.strip()
    ] if trip.recommended_hotels else []

    package_ids = [
        int(x) for x in trip.recommended_packages.split(",")
        if x.strip()
    ] if trip.recommended_packages else []

    from hotels.models import Hotel
    from packages.models import TravelPackage

    hotels = Hotel.objects.filter(id__in=hotel_ids)
    packages = list(TravelPackage.objects.filter(id__in=package_ids))

    # mark budget-friendly / above-budget in result page
    package_budget_limit = trip.budget * 0.60
    for package in packages:
        package.is_budget_friendly = float(package.price) <= package_budget_limit

    return render(
        request,
        "ai_planner/result.html",
        {
            "trip": trip,
            "hotels": hotels,
            "packages": packages,
        }
    )


@login_required
def planner_history(request):
    trips = TripPlan.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "ai_planner/history.html",
        {
            "trips": trips
        }
    )