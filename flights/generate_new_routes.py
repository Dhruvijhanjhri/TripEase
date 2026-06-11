from flights.models import Airport, Flight
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
import uuid

print("Generating realistic flight schedules...")

# Clear old flights
Flight.objects.all().delete()

HUBS = ['DEL', 'BOM', 'BLR', 'HYD', 'MAA', 'CCU']

AIRLINES = [
    ("6E", "Indigo"),
    ("AI", "Air India"),
    ("SG", "SpiceJet"),
    ("QP", "Akasa Air"),
    ("IX", "Air India Express"),
    ("UK", "Vistara"),
]

airports = {
    airport.code: airport
    for airport in Airport.objects.all()
}

today = timezone.now()

new_flights = []
created_count = 0

for source_code, source_airport in airports.items():

    # Hub logic
    if source_code in HUBS:
        destinations = [
            code for code in airports.keys()
            if code != source_code
        ]
    else:
        destinations = HUBS.copy()

    for destination_code in destinations:

        if source_code == destination_code:
            continue

        destination_airport = airports[destination_code]

        # Next 90 days
        for day in range(90):

            travel_date = today + timedelta(days=day)

            # 2–4 flights/day
            flights_per_day = random.randint(2, 4)

            for _ in range(flights_per_day):

                departure_hour = random.randint(5, 22)
                departure_minute = random.choice(
                    [0, 15, 30, 45]
                )

                departure_time = timezone.make_aware(
                    timezone.datetime(
                        travel_date.year,
                        travel_date.month,
                        travel_date.day,
                        departure_hour,
                        departure_minute
                    )
                )

                duration = random.randint(60, 240)

                arrival_time = (
                    departure_time +
                    timedelta(minutes=duration)
                )

                base_price = random.randint(
                    2500,
                    9000
                )

                code_prefix, airline = random.choice(
                    AIRLINES
                )

                # GUARANTEED UNIQUE
                unique_id = uuid.uuid4().hex[:8]

                flight_number = (
                    f"{code_prefix}-"
                    f"{source_code}"
                    f"{destination_code}-"
                    f"{unique_id}"
                )

                new_flights.append(
                    Flight(
                        flight_number=flight_number,
                        airline=airline,
                        source=source_airport,
                        destination=destination_airport,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration_minutes=duration,
                        economy_price=Decimal(base_price),
                        business_price=Decimal(
                            base_price * 1.8
                        ),
                        first_class_price=Decimal(
                            base_price * 3
                        ),
                        total_seats=180,
                        available_seats=random.randint(
                            40,
                            180
                        ),
                        is_non_stop=True
                    )
                )

                created_count += 1

                # Batch insert for speed
                if len(new_flights) >= 1000:
                    Flight.objects.bulk_create(
                        new_flights,
                        batch_size=1000
                    )
                    print(
                        f"Created {created_count} flights..."
                    )
                    new_flights = []

# Insert remaining
if new_flights:
    Flight.objects.bulk_create(
        new_flights,
        batch_size=1000
    )

print("Done!")
print("Created:", created_count)
print(
    "Total Flights:",
    Flight.objects.count()
)