from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta

from .models import Flight
from .forms import FlightSearchForm
from .realism import format_duration_minutes, get_route_price


def flight_search(request):

    form = FlightSearchForm(request.GET or None)

    direct_flights = []
    via_flights = []
    search_performed = False

    cabin_class = "economy"
    passengers = 1

    if form.is_valid():

        source = form.cleaned_data["source"]
        destination = form.cleaned_data["destination"]
        departure_date = form.cleaned_data["departure_date"]
        cabin_class = form.cleaned_data["cabin_class"]
        passengers = form.cleaned_data["passengers"]

        search_performed = True

        if source == destination:

            form.add_error(
                None,
                "Source and destination cannot be same"
            )

        else:

            # ==================================
            # DIRECT FLIGHTS
            # ==================================

            direct_flights = list(
                Flight.objects.filter(
                    source=source,
                    destination=destination,
                    available_seats__gte=passengers
                )
                .order_by("departure_time")[:20]
            )

            for flight in direct_flights:

                flight.display_departure = (
                    flight.departure_time.replace(
                        year=departure_date.year,
                        month=departure_date.month,
                        day=departure_date.day
                    )
                )

                flight.display_arrival = (
                    flight.arrival_time.replace(
                        year=departure_date.year,
                        month=departure_date.month,
                        day=departure_date.day
                    )
                )

                flight.price = (
                    get_route_price(
                        flight.source.code,
                        flight.destination.code,
                        cabin_class
                    ) * passengers
                )
                flight.seat_display = flight.get_seat_display()
                flight.cabin_price = get_route_price(
                    flight.source.code,
                    flight.destination.code,
                    cabin_class
                )

            # ==================================
            # VIA FLIGHTS (REALISTIC)
            # ==================================

            first_legs = Flight.objects.filter(
                source=source,
                available_seats__gte=passengers
            ).exclude(
                destination=destination
            ).order_by("departure_time")[:20]

            for first_leg in first_legs:

                layover_min = 60
                layover_max = 480

                earliest_departure = (
                    first_leg.arrival_time
                    + timedelta(minutes=layover_min)
                )

                latest_departure = (
                    first_leg.arrival_time
                    + timedelta(minutes=layover_max)
                )

                second_leg = Flight.objects.filter(
                    source=first_leg.destination,
                    destination=destination,
                    available_seats__gte=passengers,
                    departure_time__gte=earliest_departure,
                    departure_time__lte=latest_departure
                ).order_by("departure_time").first()

                if second_leg:

                    total_price = (
                        get_route_price(
                            first_leg.source.code,
                            first_leg.destination.code,
                            cabin_class
                        )
                        +
                        get_route_price(
                            second_leg.source.code,
                            second_leg.destination.code,
                            cabin_class
                        )
                    ) * passengers

                    total_duration = int(
                        (
                            second_leg.arrival_time
                            -
                            first_leg.departure_time
                        ).total_seconds() / 60
                    )

                    via_flights.append({
                        "first_leg": first_leg,
                        "second_leg": second_leg,
                        "total_price": total_price,
                        "total_duration": total_duration,
                        "total_duration_display": format_duration_minutes(total_duration),
                        "first_leg_seat_display": first_leg.get_seat_display(),
                        "second_leg_seat_display": second_leg.get_seat_display(),
                        "first_leg_price": get_route_price(
                            first_leg.source.code,
                            first_leg.destination.code,
                            cabin_class
                        ),
                        "second_leg_price": get_route_price(
                            second_leg.source.code,
                            second_leg.destination.code,
                            cabin_class
                        ),
                    })

            via_flights = via_flights[:10]

    context = {
        "form": form,
        "direct_flights": direct_flights,
        "via_flights": via_flights,
        "search_performed": search_performed,
        "cabin_class": cabin_class,
        "passengers": passengers,
    }

    return render(
        request,
        "flights/search.html",
        context
    )


def flight_detail(request, flight_id):

    flight = get_object_or_404(
        Flight,
        id=flight_id
    )

    cabin_class = request.GET.get(
        "cabin_class",
        "economy"
    ).strip()

    passengers = int(
        request.GET.get(
            "passengers",
            1
        )
    )

    departure_date = request.GET.get(
        "departure_date",
        ""
    ).strip()

    is_via = request.GET.get(
        "is_via"
    )

    second_leg = None
    total_price = 0
    total_duration = 0
    total_duration_display = ""
    if departure_date:

        selected_date = datetime.strptime(
            departure_date,
            "%Y-%m-%d"
        ).date()

    # ==================================
    # VIA FLIGHT DETAILS
    # ==================================

    if is_via:

        second_leg_id = request.GET.get(
            "second_leg_id"
        )

        if second_leg_id:

            second_leg = get_object_or_404(
                Flight,
                id=second_leg_id
            )

        if selected_date:

            flight.departure_time = (
                flight.departure_time.replace(
                    year=selected_date.year,
                    month=selected_date.month,
                    day=selected_date.day
                )
            )

            flight.arrival_time = (
                flight.arrival_time.replace(
                    year=selected_date.year,
                    month=selected_date.month,
                    day=selected_date.day
                )
            )

            if second_leg:

                second_leg.departure_time = (
                    second_leg.departure_time.replace(
                        year=selected_date.year,
                        month=selected_date.month,
                        day=selected_date.day
                    )
                )

                second_leg.arrival_time = (
                    second_leg.arrival_time.replace(
                        year=selected_date.year,
                        month=selected_date.month,
                        day=selected_date.day
                    )
                )

        total_price = (
            get_route_price(
                flight.source.code,
                flight.destination.code,
                cabin_class
            )
            +
            get_route_price(
                second_leg.source.code,
                second_leg.destination.code,
                cabin_class
            )
        ) * passengers

        total_duration = (
            flight.duration_minutes
            +
            second_leg.duration_minutes
        )

    # ==================================
    # DIRECT FLIGHT DETAILS
    # ==================================

    else:

        if selected_date:

            flight.departure_time = (
                flight.departure_time.replace(
                    year=selected_date.year,
                    month=selected_date.month,
                    day=selected_date.day
                )
            )

            flight.arrival_time = (
                flight.arrival_time.replace(
                    year=selected_date.year,
                    month=selected_date.month,
                    day=selected_date.day
                )
            )

        total_price = (
            get_route_price(
                flight.source.code,
                flight.destination.code,
                cabin_class
            ) * passengers
        )

        total_duration = (
            flight.duration_minutes
        )
        total_duration_display = format_duration_minutes(total_duration)

    selected_departure_date = selected_date or flight.departure_time.date()

    context = {
        'flight': flight,
        'second_leg': second_leg,
        'is_via': is_via,
        'price': total_price,
        'total_price': total_price,
        'cabin_class': cabin_class,
        'passengers': passengers,
        'departure_date': departure_date,
        'selected_departure_date': selected_departure_date,
        'total_duration': total_duration,
        'total_duration_display': total_duration_display,
        'seat_display': flight.get_seat_display(),
        'cabin_price': get_route_price(
            flight.source.code,
            flight.destination.code,
            cabin_class
        ) if not second_leg else (
            get_route_price(
                flight.source.code,
                flight.destination.code,
                cabin_class
            ) + get_route_price(
                second_leg.source.code,
                second_leg.destination.code,
                cabin_class
            )
        ),
        'flight_number_display': flight.get_display_flight_number(),
        'second_leg_flight_number_display': second_leg.get_display_flight_number() if second_leg else None,
    }

    return render(
        request,
        "flights/detail.html",
        context
    )

