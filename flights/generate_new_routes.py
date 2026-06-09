from flights.models import Airport, Flight
from datetime import datetime, timedelta
from random import randint, choice
from decimal import Decimal
from django.utils import timezone

# Hub airports
HUBS = ['DEL', 'BOM', 'BLR', 'HYD', 'MAA', 'CCU']

# Airlines
AIRLINES = {
    'Indigo': '6E',
    'Air India': 'AI',
    'Akasa Air': 'QP',
    'SpiceJet': 'SG',
    'Air India Express': 'IX'
}

# Existing flight numbers
existing_numbers = set(
    Flight.objects.values_list(
        'flight_number',
        flat=True
    )
)


def generate_unique_flight_number(
    airline_code
):
    """Generate unique flight number fast"""

    while True:
        number = (
            f"{airline_code}-"
            f"{randint(1000,9999)}"
        )

        if number not in existing_numbers:
            existing_numbers.add(number)
            return number


airports = {
    airport.code: airport
    for airport in Airport.objects.all()
}

created_count = 0
new_flights = []

print("Generating routes...")

# Only 15 days
DAYS_TO_GENERATE = 15

for source_code, source_airport in airports.items():

    # Route logic
    if source_code in HUBS:
        destinations = [
            code for code in airports.keys()
            if code != source_code
        ]
    else:
        destinations = [
            hub for hub in HUBS
            if hub != source_code
            and hub in airports
        ]

    for destination_code in destinations:

        destination_airport = (
            airports[destination_code]
        )

        for day in range(
            DAYS_TO_GENERATE
        ):

            base_date = (
                timezone.now() +
                timedelta(days=day)
            )

            flights_per_day = randint(
                1, 2
            )

            for _ in range(
                flights_per_day
            ):

                airline = choice(
                    list(AIRLINES.keys())
                )

                airline_code = (
                    AIRLINES[airline]
                )

                departure_hour = randint(
                    5, 22
                )

                departure_minute = choice(
                    [0, 15, 30, 45]
                )

                departure_time = (
                    timezone.make_aware(
                        datetime(
                            base_date.year,
                            base_date.month,
                            base_date.day,
                            departure_hour,
                            departure_minute
                        )
                    )
                )

                duration = randint(
                    60, 240
                )

                arrival_time = (
                    departure_time +
                    timedelta(
                        minutes=duration
                    )
                )

                base_price = randint(
                    2500, 9000
                )

                flight = Flight(
                    flight_number=
                    generate_unique_flight_number(
                        airline_code
                    ),

                    airline=airline,

                    source=
                    source_airport,

                    destination=
                    destination_airport,

                    departure_time=
                    departure_time,

                    arrival_time=
                    arrival_time,

                    duration_minutes=
                    duration,

                    economy_price=
                    Decimal(base_price),

                    business_price=
                    Decimal(base_price * 2.2),

                    first_class_price=
                    Decimal(base_price * 4),

                    total_seats=180,

                    available_seats=
                    randint(30, 180),

                    is_non_stop=True
                )

                new_flights.append(
                    flight
                )

                created_count += 1


print(
    f"Creating {created_count} flights..."
)

# BULK INSERT (super fast)
Flight.objects.bulk_create(
    new_flights,
    batch_size=1000
)

print("\nDone!")
print(
    f"Created {created_count} flights"
)
print(
    "Total flights:",
    Flight.objects.count()
)