from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from .models import Flight, PriceAlert
from .forms import FlightSearchForm, PriceAlertForm
from .realism import format_duration_minutes, get_route_price
from django.db.models import Avg
from reviews.models import FlightReview
from bookings.models import Booking
from ml.fare_service import fare_predictor
from utils.weather import get_weather
from ml.recommendation import (
    calculate_recommendation_score,
    get_confidence,
)
from ml.personalization import get_user_preferences
from ml.similar_flights import get_similar_flights
from ml.booking_advisor import get_booking_recommendation
from ml.explainability import explain_recommendation
from ml.trending import get_trending_flights
from ml.price_history import (
    generate_price_history,
    get_price_statistics,
)

def flight_search(request):

    form = FlightSearchForm(request.GET or None)

    preferences = None

    if request.user.is_authenticated:
        preferences = get_user_preferences(request.user)
        trending = get_trending_flights()

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

                flight.cabin_price = flight.get_price(cabin_class)
                flight.price = flight.cabin_price * passengers

                # Average rating
                average_rating = (
                    FlightReview.objects
                    .filter(flight=flight)
                    .aggregate(Avg("rating"))["rating__avg"]
                )

                flight.recommendation_score = calculate_recommendation_score(
                    price=flight.price,
                    duration=flight.duration_minutes,
                    rating=average_rating,
                    stops=0,
                    available_seats=flight.available_seats,
                )

                (
                    flight.confidence_stars,
                    flight.confidence_level,
                ) = get_confidence(
                    flight.recommendation_score
                )

                # Personalization bonus
                preferred_airline = False

                if preferences:
                    if (
                        preferences["preferred_airline"]
                        and
                        flight.airline == preferences["preferred_airline"]
                    ):
                        flight.recommendation_score += 5
                        preferred_airline = True

                # Explain AI recommendation
                flight.ai_reasons = explain_recommendation(
                    price=flight.price,
                    duration=flight.duration_minutes,
                    rating=average_rating,
                    stops=0,
                    available_seats=flight.available_seats,
                    preferred_airline=preferred_airline,
                )

                score = flight.recommendation_score

                if score >= 90:
                    flight.ai_confidence = "Very High"
                elif score >= 80:
                    flight.ai_confidence = "High"
                elif score >= 70:
                    flight.ai_confidence = "Medium"
                else:
                    flight.ai_confidence = "Low"

                if score >= 90:
                    flight.recommendation_badge = "🏆 AI Recommended"

                elif score >= 80:
                    flight.recommendation_badge = "⭐ Best Value"

                elif score >= 70:
                    flight.recommendation_badge = "👍 Good Choice"

                else:
                    flight.recommendation_badge = "Standard Option"
                
                if preferences and flight.airline == preferences["preferred_airline"]:
                    flight.personalized_reason = (
                        "Recommended because you frequently fly with this airline."
                    )
                else:
                    flight.personalized_reason = ""
                
                booking_count = Booking.objects.filter(
                    flight=flight,
                    booking_status="confirmed",
                ).count()

                if booking_count >= 2:
                    flight.trending_badge = "🔥 Trending Choice"
                elif booking_count >= 1:
                    flight.trending_badge = "📈 Popular Flight"
                else:
                    flight.trending_badge = ""


            direct_flights.sort(
                key=lambda flight: flight.recommendation_score,
                reverse=True,
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

                    first_leg_price = first_leg.get_price(cabin_class)
                    second_leg_price = second_leg.get_price(cabin_class)

                    total_price = (
                        first_leg_price +
                        second_leg_price
                    ) * passengers

                    total_duration = int(
                        (
                            second_leg.arrival_time
                            -
                            first_leg.departure_time
                        ).total_seconds() / 60
                    )

                    average_rating = (
                        FlightReview.objects
                        .filter(flight=first_leg)
                        .aggregate(Avg("rating"))["rating__avg"]
                    )

                    recommendation_score = calculate_recommendation_score(
                        price=total_price,
                        duration=total_duration,
                        rating=average_rating,
                        stops=1,
                        available_seats=min(
                            first_leg.available_seats,
                            second_leg.available_seats
                        ),
                    )

                    route = {
                        "first_leg": first_leg,
                        "second_leg": second_leg,
                        "total_price": total_price,
                        "total_duration": total_duration,
                        "total_duration_display": format_duration_minutes(total_duration),
                        "first_leg_seat_display": first_leg.get_seat_display(),
                        "second_leg_seat_display": second_leg.get_seat_display(),
                        "first_leg_price": first_leg_price,
                        "second_leg_price": second_leg_price,
                        "recommendation_score": recommendation_score,
                    }

                    if preferences:

                        if (
                            preferences["preferred_airline"]
                            and
                            first_leg.airline == preferences["preferred_airline"]
                        ):
                            recommendation_score += 5

                    score = recommendation_score

                    if recommendation_score >= 90:
                        ai_confidence = "Very High"
                    elif recommendation_score >= 80:
                        ai_confidence = "High"
                    elif recommendation_score >= 70:
                        ai_confidence = "Medium"
                    else:
                        ai_confidence = "Low"

                    if score >= 90:
                        route["recommendation_badge"] = "🏆 AI Recommended"
                    elif score >= 80:
                        route["recommendation_badge"] = "⭐ Best Value"
                    elif score >= 70:
                        route["recommendation_badge"] = "👍 Good Choice"
                    else:
                        route["recommendation_badge"] = "Standard Option"

                    booking_count = (
                        trending.get(first_leg.id, 0)
                        +
                        trending.get(second_leg.id, 0)
                    )

                    if booking_count >= 2:
                        trending_badge = "🔥 Trending Choice"
                    elif booking_count >= 1:
                        trending_badge = "📈 Popular Flight"
                    else:
                        trending_badge = ""
                    

                    via_flights.append({
                        "first_leg": first_leg,
                        "second_leg": second_leg,
                        "total_price": total_price,
                        "total_duration": total_duration,
                        "total_duration_display": format_duration_minutes(total_duration),
                        "first_leg_seat_display": first_leg.get_seat_display(),
                        "second_leg_seat_display": second_leg.get_seat_display(),
                        
                        "first_leg_price": first_leg_price,
                        "second_leg_price": second_leg_price,
                        "recommendation_score": recommendation_score,
                        "booking_count": booking_count,
                        "trending_badge": trending_badge,
                        "ai_confidence": ai_confidence,
                    })

            via_flights.sort(
                key=lambda flight: flight["recommendation_score"],
                reverse=True,
            )

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
    selected_date = None
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

        first_leg_price = flight.get_price(cabin_class)
        second_leg_price = second_leg.get_price(cabin_class)

        cabin_price = first_leg_price + second_leg_price

        total_price = cabin_price * passengers

        total_duration = int(
            (
                second_leg.arrival_time
                -
                flight.departure_time
            ).total_seconds() / 60
        )

        total_duration_display = format_duration_minutes(
            total_duration
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

        cabin_price = flight.get_price(cabin_class)

        total_price = cabin_price * passengers

        total_duration = (
            flight.duration_minutes
        )
        total_duration_display = format_duration_minutes(total_duration)

    selected_departure_date = selected_date or flight.departure_time.date()

        # ==================================
    # FLIGHT REVIEWS LOGIC
    # ==================================
    average_rating = flight.reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    review_count = flight.reviews.count()

    reviews = flight.reviews.all()

    can_review = False
    already_reviewed = False

    if request.user.is_authenticated:
        booking_exists = Booking.objects.filter(
            user=request.user,
            flight=flight,
            booking_status__in=["confirmed", "completed"]
        ).exists()

        already_reviewed = FlightReview.objects.filter(
            user=request.user,
            flight=flight
        ).exists()

        can_review = booking_exists and not already_reviewed

    # ==================================
    # AI Fare Prediction
    # ==================================

    predicted_price = None

    try:

        predicted_price = fare_predictor.predict(

            source=flight.source.city,

            destination=(
                second_leg.destination.city
                if second_leg
                else flight.destination.city
            ),

            stops=1 if second_leg else 0,

            duration_minutes=total_duration,

            departure_date=selected_departure_date,

            departure_hour=flight.departure_time.hour,

            airline=flight.airline,

        )

    except Exception as e:

        print("AI Prediction Error:", e)

    deal_status = None
    deal_message = None
    price_difference = None
    price_difference_percent = None

    if predicted_price:

        current_price = float(total_price)

        price_difference = round(
            predicted_price - current_price,
            2
        )

        price_difference_percent = round(
            abs(price_difference) / predicted_price * 100,
            1
        )

        if current_price <= predicted_price * 0.80:
            deal_status = "excellent"
            deal_message = "Excellent Deal! This fare is significantly below the expected market price."

        elif current_price <= predicted_price * 0.95:
            deal_status = "good"
            deal_message = "Good Deal! This fare is below the expected market price."

        elif current_price <= predicted_price * 1.10:
            deal_status = "fair"
            deal_message = "Fair Price. This fare is close to the expected market price."

        else:
            deal_status = "expensive"
            deal_message = "Expensive. This fare is above the expected market price."

    booking_advice = None

    if predicted_price:

        booking_advice = get_booking_recommendation(
            current_price=total_price,
            predicted_price=predicted_price,
        )
    
    # ==================================
    # Price History Analytics
    # ==================================

    price_history = generate_price_history(total_price)

    price_stats = {
        "min_price": min(price_history),
        "max_price": max(price_history),
        "avg_price": round(sum(price_history) / len(price_history)),
        "current_price": price_history[4],
    }

    # weather 
    if second_leg:
        weather = get_weather(second_leg.destination.city)
    else:
        weather = get_weather(flight.destination.city)
    
    # ==================================
    # Similar Flights
    # ==================================

    similar_flights = get_similar_flights(
        current_flight=flight,
        cabin_class=cabin_class,
        passengers=passengers,
    )

    price_alert_form = None

    if request.user.is_authenticated:

        if request.method == "POST":

            price_alert_form = PriceAlertForm(request.POST)

            if price_alert_form.is_valid():

                alert = price_alert_form.save(commit=False)
                alert.user = request.user
                alert.flight = flight

                existing = PriceAlert.objects.filter(
                    user=request.user,
                    flight=flight,
                    active=True,
                ).first()

                if existing:
                    existing.target_price = alert.target_price
                    existing.save()
                else:
                    alert.save()

                price_alert_form = PriceAlertForm()

        else:
            price_alert_form = PriceAlertForm()

        

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
        'cabin_price': cabin_price,
        'flight_number_display': flight.get_display_flight_number(),
        'second_leg_flight_number_display': second_leg.get_display_flight_number() if second_leg else None,
        "average_rating": average_rating,
        "review_count": review_count,
        "reviews": reviews,
        "can_review": can_review,
        "already_reviewed": already_reviewed,
        "predicted_price": predicted_price,
        "deal_status": deal_status,
        "deal_message": deal_message,
        "price_difference": price_difference,
        "price_difference_percent": price_difference_percent,
        "weather": weather,
        "similar_flights": similar_flights,
        "booking_advice": booking_advice,
        "price_history": price_history,
        "price_stats": price_stats,
        "price_alert_form": price_alert_form,
    }

    return render(
        request,
        "flights/detail.html",
        context
    )