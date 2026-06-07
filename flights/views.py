from django.shortcuts import render

import flights
from .models import Flight
from .forms import FlightSearchForm
from django.shortcuts import render, get_object_or_404


def flight_search(request):
    """Flight search view"""

    form = FlightSearchForm(request.GET or None)

    flights = []
    search_performed = False
    cabin_class = "economy"
    passengers = 1

    if form.is_valid():

        source = form.cleaned_data["source"]
        destination = form.cleaned_data["destination"]
        departure_date = form.cleaned_data["departure_date"]
        cabin_class = form.cleaned_data.get("cabin_class", "economy")
        passengers = form.cleaned_data.get("passengers", 1)

        search_performed = True

        # Prevent same source and destination
        if source == destination:
            form.add_error(None, "Source and destination cannot be the same")

        else:
            flights = Flight.objects.filter(
            source=source,
            destination=destination,
            available_seats__gte=passengers
        ).order_by("departure_time")[:20]


        # Dynamically update dates to searched date
        for flight in flights:
            flight.departure_time = flight.departure_time.replace(
                year=departure_date.year,
                month=departure_date.month,
                day=departure_date.day
            )

            flight.arrival_time = flight.arrival_time.replace(
                year=departure_date.year,
                month=departure_date.month,
                day=departure_date.day
            )

            flight.price = flight.get_price(cabin_class)

            # Add price dynamically
            for flight in flights:
                flight.price = flight.get_price(cabin_class)

    context = {
        "form": form,
        "flights": flights,
        "search_performed": search_performed,
        "cabin_class": cabin_class,
        "passengers": passengers,
    }

    return render(request, "flights/search.html", context)

def flight_detail(request, flight_id):
    """Show detailed information about a flight"""

    flight = get_object_or_404(Flight, id=flight_id)

    cabin_class = request.GET.get("cabin_class", "economy")
    passengers = request.GET.get("passengers", 1)
    departure_date = request.GET.get("departure_date")

    # Update displayed date if searched date exists
    if departure_date:
        from datetime import datetime

        selected_date = datetime.strptime(
            departure_date,
            "%Y-%m-%d"
        ).date()

        flight.departure_time = flight.departure_time.replace(
            year=selected_date.year,
            month=selected_date.month,
            day=selected_date.day
        )

        flight.arrival_time = flight.arrival_time.replace(
            year=selected_date.year,
            month=selected_date.month,
            day=selected_date.day
        )

    price = flight.get_price(cabin_class)

    context = {
        "flight": flight,
        "price": price,
        "cabin_class": cabin_class,
        "passengers": passengers,
        "departure_date": departure_date,
    }

    return render(request, "flights/detail.html", context)
    