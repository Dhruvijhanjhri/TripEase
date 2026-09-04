from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import TripPlannerForm
from .models import TripPlan
from .services import generate_trip_plan
from django.http import FileResponse
from .pdf_utils import generate_trip_pdf


@login_required
def planner_home(request):
    if request.method == "POST":
        form = TripPlannerForm(request.POST)

        if form.is_valid():
            origin_city = form.cleaned_data["origin_city"]
            destination = form.cleaned_data["destination"]
            budget = form.cleaned_data["budget"]
            days = form.cleaned_data["days"]
            interests = form.cleaned_data["interests"]

            planner_output = generate_trip_plan(
                destination=destination,
                budget=budget,
                days=days,
                interests=interests,
                origin_city=origin_city,  
            )

            trip = TripPlan.objects.create(
                user=request.user,
                origin_city=origin_city,
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
    trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)

    hotel_ids = (
        [int(x) for x in trip.recommended_hotels.split(",") if x.strip()]
        if trip.recommended_hotels
        else []
    )

    package_ids = (
        [int(x) for x in trip.recommended_packages.split(",") if x.strip()]
        if trip.recommended_packages
        else []
    )

    from hotels.models import Hotel
    from packages.models import TravelPackage

    hotels = Hotel.objects.filter(id__in=hotel_ids)
    for hotel in hotels:
        room = hotel.rooms.order_by("price_per_night").first()
        hotel.display_price = room.price_per_night if room else None

    packages = list(TravelPackage.objects.filter(id__in=package_ids))

    # mark budget-friendly / above-budget in result page
    package_budget_limit = trip.budget * 0.60
    for package in packages:
        package.is_budget_friendly = float(package.price) <= package_budget_limit

    from .services import (
        get_best_season,
        get_nearest_airport,
        infer_travel_style,
        get_route_suggestion,
    )

    planner_output = {
        "best_season": get_best_season(trip.destination),
        "nearest_airport": get_nearest_airport(trip.destination),
        "travel_style": infer_travel_style(trip.interests),
        "route_suggestion": get_route_suggestion(
            trip.destination,
            trip.origin_city,
        ),
    }

    import re

    itinerary_lines = trip.generated_plan.splitlines()

    timeline_items = []
    current_day = None
    current_details = []

    for line in itinerary_lines:
        line = line.strip()

        # Match Markdown day headings such as:
        # ### Day 1: Arrival, Heritage & Sarafa's Delights
        # #### Day 1: Arrival, Heritage & Sarafa's Delights
        # Day 1: Arrival, Heritage & Sarafa's Delights
        day_match = re.match(
            r"^\**#{0,6}\s*\**Day\s+(\d+)\s*:?\s*(.*?)\**$",
            line,
            re.IGNORECASE,
        )

        if day_match:
            if current_day:
                timeline_items.append(
                    {
                        "title": current_day,
                        "details": current_details,
                    }
                )

            day_number = day_match.group(1)
            day_title = day_match.group(2).strip("*").strip()

            current_day = (
                f"Day {day_number}: {day_title}"
                if day_title
                else f"Day {day_number}"
            )

            current_details = []

        elif line and not line.startswith("#") and line != "---":
            cleaned_line = line.replace("**", "").strip()

            if cleaned_line:
                current_details.append(cleaned_line)

    if current_day:
        timeline_items.append(
            {
                "title": current_day,
                "details": current_details,
            }
        )

    return render(
        request,
        "ai_planner/result.html",
        {
            "trip": trip,
            "hotels": hotels,
            "packages": packages,
            "best_season": planner_output["best_season"],
            "nearest_airport": planner_output["nearest_airport"],
            "travel_style": planner_output["travel_style"],
            "timeline_items": timeline_items,
            "route_suggestion": planner_output["route_suggestion"],
        },
    )


@login_required
def planner_history(request):
    trips = TripPlan.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "ai_planner/history.html", {"trips": trips})


@login_required
def export_trip_pdf(request, trip_id):

    trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)

    from .services import (
        get_best_season,
        get_nearest_airport,
        infer_travel_style,
        get_route_suggestion,
    )

    trip.best_season = get_best_season(trip.destination)
    trip.nearest_airport = get_nearest_airport(trip.destination)
    trip.travel_style = infer_travel_style(trip.interests)
    trip.suggested_route = get_route_suggestion(trip.destination, "Bengaluru")

    pdf = generate_trip_pdf(trip)

    filename = f"TripEase_{trip.destination}.pdf"

    return FileResponse(pdf, as_attachment=True, filename=filename)
