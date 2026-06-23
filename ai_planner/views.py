from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import TripPlannerForm
from .models import TripPlan


@login_required
def planner_home(request):

    if request.method == "POST":

        form = TripPlannerForm(request.POST)

        if form.is_valid():

            trip = TripPlan.objects.create(
                user=request.user,
                destination=form.cleaned_data[
                    "destination"
                ],
                budget=form.cleaned_data[
                    "budget"
                ],
                days=form.cleaned_data[
                    "days"
                ],
                interests=form.cleaned_data[
                    "interests"
                ],
                generated_plan="Generating..."
            )

            return redirect(
                "ai_planner:result",
                trip.id
            )

    else:

        form = TripPlannerForm()

    return render(
        request,
        "ai_planner/planner.html",
        {
            "form": form
        }
    )

@login_required
def planner_result(
    request,
    trip_id
):

    trip = TripPlan.objects.get(
        id=trip_id,
        user=request.user
    )

    return render(
        request,
        "ai_planner/result.html",
        {
            "trip": trip
        }
    )