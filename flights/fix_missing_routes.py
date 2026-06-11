from flights.models import Airport, Flight
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
import uuid

print("Fixing missing/weak airports...")

hub_codes = ['DEL', 'BLR', 'MAA', 'BOM', 'HYD', 'CCU']

airlines = [
    'Indigo',
    'Air India',
    'Akasa Air',
    'SpiceJet',
    'Air India Express'
]

# Airports with poor coverage
target_airports = [
    'IXE', 'NAG', 'IXZ', 'IXB', 'SXR',
    'IXM', 'GOX', 'IMF', 'IXJ', 'IXL', 'IXR'
]

airports = {
    airport.code: airport
    for airport in Airport.objects.all()
}

created_count = 0

new_flights = []

for airport_code in target_airports:

    source_airport = airports.get(airport_code)

    if not source_airport:
        continue

    for hub_code in hub_codes:

        if airport_code == hub_code:
            continue

        destination_airport = airports[hub_code]

        # Create 2 flights/day for 30 days
        for day in range(30):

            date = timezone.now() + timedelta(days=day)

            for _ in range(2):

                departure_hour = random.randint(5, 22)
                departure_minute = random.choice([0, 15, 30, 45])

                departure_time = timezone.make_aware(
                    timezone.datetime(
                        date.year,
                        date.month,
                        date.day,
                        departure_hour,
                        departure_minute
                    )
                )

                duration = random.randint(60, 240)

                arrival_time = (
                    departure_time +
                    timedelta(minutes=duration)
                )

                base_price = random.randint(2500, 8500)

                # guaranteed unique flight number
                unique_id = uuid.uuid4().hex[:6].upper()

                flight_number = (
                    f"{random.choice(['AI','6E','SG','QP'])}-"
                    f"{airport_code}{unique_id}"
                )

                new_flights.append(
                    Flight(
                        flight_number=flight_number,
                        airline=random.choice(airlines),
                        source=source_airport,
                        destination=destination_airport,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration_minutes=duration,
                        economy_price=Decimal(base_price),
                        business_price=Decimal(base_price * 2.2),
                        first_class_price=Decimal(base_price * 4),
                        total_seats=180,
                        available_seats=random.randint(50, 180),
                        is_non_stop=True
                    )
                )

                created_count += 1

# bulk insert = fast
Flight.objects.bulk_create(new_flights)

print(f"Created {created_count} flights")
print("Total flights:", Flight.objects.count())