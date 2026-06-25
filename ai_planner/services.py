from decimal import Decimal

from hotels.models import Hotel
from packages.models import TravelPackage


def normalize_text(value):
    return value.strip().lower() if value else ""


def split_interests(interests_text):
    if not interests_text:
        return []

    return [
        item.strip().lower()
        for item in interests_text.split(",")
        if item.strip()
    ]


def get_matching_hotels(destination, budget, days):
    destination = normalize_text(destination)

    hotels = Hotel.objects.filter(
        city__icontains=destination
    ).order_by("-user_rating", "-star_rating")

    matched_hotels = []
    hotel_ids = []

    hotel_budget_limit = Decimal(str(budget)) * Decimal("0.40")
    per_night_limit = hotel_budget_limit / max(days - 1, 1)

    selected_room_prices = []

    for hotel in hotels:
        room = hotel.rooms.order_by("price_per_night").first()

        if room and room.price_per_night <= per_night_limit:
            matched_hotels.append({
                "id": hotel.id,
                "name": hotel.name,
                "city": hotel.city,
                "rating": hotel.user_rating,
                "price_per_night": room.price_per_night,
                "hotel_type": hotel.hotel_type,
            })
            hotel_ids.append(str(hotel.id))
            selected_room_prices.append(room.price_per_night)

        if len(matched_hotels) == 3:
            break

    estimated_hotel_cost = sum(
        selected_room_prices,
        Decimal("0.00")
    ) * max(days - 1, 1)

    return matched_hotels, hotel_ids, estimated_hotel_cost


def get_matching_packages(destination, budget, days, interests):
    destination = normalize_text(destination)
    interest_list = split_interests(interests)

    packages = TravelPackage.objects.filter(
        destination__icontains=destination,
        is_active=True
    ).order_by("-rating")

    package_budget_limit = Decimal(str(budget)) * Decimal("0.60")

    matched_within_budget = []
    matched_fallback = []

    for package in packages:
        score = 0

        if package.duration_days == days:
            score += 3
        elif abs(package.duration_days - days) <= 1:
            score += 2

        if package.package_type.lower() in interest_list:
            score += 3

        if package.price <= budget:
            score += 2

        item = (score, package)

        if package.price <= package_budget_limit:
            matched_within_budget.append(item)
        else:
            matched_fallback.append(item)

    matched_within_budget.sort(
        key=lambda x: (x[0], x[1].rating),
        reverse=True
    )
    matched_fallback.sort(
        key=lambda x: (x[0], x[1].rating),
        reverse=True
    )

    selected = [
        pkg for score, pkg in matched_within_budget[:3]
        if score > 0
    ]

    if not selected:
        selected = [
            pkg for score, pkg in matched_fallback[:3]
            if score > 0
        ]

    package_data = []
    package_ids = []
    selected_package_prices = []

    for package in selected:
        is_budget_friendly = package.price <= package_budget_limit

        package_data.append({
            "id": package.id,
            "name": package.name,
            "destination": package.destination,
            "price": package.price,
            "duration_days": package.duration_days,
            "package_type": package.package_type,
            "rating": package.rating,
            "is_budget_friendly": is_budget_friendly,
        })
        package_ids.append(str(package.id))

        if is_budget_friendly:
            selected_package_prices.append(package.price)

    estimated_package_cost = sum(
        selected_package_prices,
        Decimal("0.00")
    )

    return package_data, package_ids, estimated_package_cost


def build_day_wise_plan(destination, days, interests):
    interest_list = split_interests(interests)
    interest_text = (
        ", ".join(interest_list)
        if interest_list else "local sightseeing"
    )

    plan_lines = [
        f"Trip Plan for {destination}",
        f"Duration: {days} days",
        f"Focus: {interest_text}",
        ""
    ]

    for day in range(1, days + 1):
        if day == 1:
            activity = (
                f"Arrival in {destination}, hotel check-in "
                f"and nearby exploration."
            )
        elif day == days:
            activity = (
                f"Relaxed morning, local shopping and "
                f"departure from {destination}."
            )
        else:
            activity = (
                f"Day {day} activities based on your interests: "
                f"{interest_text}."
            )

        plan_lines.append(f"Day {day}: {activity}")

    return "\n".join(plan_lines)


def estimate_total_cost(hotel_cost, package_cost, budget):
    total = hotel_cost + package_cost

    if total > budget:
        return Decimal(str(budget))

    return total


def generate_trip_plan(destination, budget, days, interests):
    hotels, hotel_ids, hotel_cost = get_matching_hotels(
        destination,
        budget,
        days
    )

    packages, package_ids, package_cost = get_matching_packages(
        destination,
        budget,
        days,
        interests
    )

    itinerary_text = build_day_wise_plan(
        destination,
        days,
        interests
    )

    estimated_cost = estimate_total_cost(
        hotel_cost,
        package_cost,
        budget
    )

    return {
        "generated_plan": itinerary_text,
        "estimated_cost": estimated_cost,
        "recommended_hotels": hotels,
        "recommended_packages": packages,
        "hotel_ids": ",".join(hotel_ids),
        "package_ids": ",".join(package_ids),
    }