"""
Django management command to load dummy data for Indian airports and flights
Usage: python manage.py load_dummy_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from flights.models import Airport, Flight
from flights.realism import (
    get_airline_code,
    get_route_base_fare,
    get_route_duration_minutes,
    normalize_airline_name,
)
import random
import uuid
import csv
from pathlib import Path
from django.conf import settings
import csv
import os
from django.conf import settings

ROUTES_CSV = settings.BASE_DIR / "data" / "routes.csv"

def load_airports_csv():

    file_path = os.path.join(
        settings.BASE_DIR,
        "data",
        "indian_airports.csv"
    )

    airports = []

    with open(file_path, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            airports.append({
                "code": row["iata_code"],
                "name": row["airport_name"],
                "city": row["city"],
                "country": "India",
            })

    return airports

def load_routes():
    with open(ROUTES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Command(BaseCommand):
    help = "Loads dummy data for Indian airports and flights"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to load dummy data..."))

        routes = load_routes()

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(routes)} routes from routes.csv")
        )

        airports_data = load_airports_csv()

        # Airlines
        airlines = [
            "Air India",
            "Air India Express",
            "IndiGo",
            "Akasa Air",
            "SpiceJet",
        ]

        tracking_numbers = {
            "IndiGo": ["6E203", "6E449", "6E6314", "6E512", "6E725", "6E315"],
            "Air India": ["AI101", "AI302", "AI507", "AI401", "AI605"],
            "Air India Express": ["IX344", "IX196", "IX1458", "IX276"],
            "Akasa Air": ["QP1405", "QP1123", "QP1712", "QP1810"],
            "SpiceJet": ["SG8169", "SG202", "SG468", "SG871"],
        }

        # Create Airports
        airports_dict = {}
        for airport_data in airports_data:
            airport, created = Airport.objects.get_or_create(
                code=airport_data["code"],
                defaults={
                    "name": airport_data["name"],
                    "city": airport_data["city"],
                    "country": "India",
                },
            )
            airports_dict[airport_data["code"]] = airport
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created airport: {airport}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Airport already exists: {airport}")
                )

        # Create Flights
        flight_count = 0
        airport_codes = list(airports_dict.keys())

        # Load routes from CSV
        all_routes = []

        for route in routes:
            source_code = route["source"].strip().upper()
            destination_code = route["destination"].strip().upper()

            if (
                source_code in airports_dict
                and destination_code in airports_dict
                and source_code != destination_code
            ):
                all_routes.append(route)

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(all_routes)} valid routes.")
        )

        # Generate flights for the next 30 days
        for day in range(30):
            current_date = timezone.now().date() + timedelta(days=day)

            # Create flights for ALL routes - ensure at least 1-2 flights per route per day
            for route in all_routes:

                source_code = route["source"]
                dest_code = route["destination"]

                airline = route["airline"]
                airline_code = get_airline_code(airline)

                flight_number = (
                    f"{airline_code}-"
                    f"{random.randint(100, 999)}"
                )

                source = airports_dict[source_code]
                destination = airports_dict[dest_code]

                # Skip if same airport
                if source == destination:
                    continue

                # Create 1-2 flights per route per day (guaranteed at least 1)
                num_flights = random.randint(1, 2)

                for flight_num in range(num_flights):
                    # Airline-specific preferred departure windows
                    departure_windows = {
                        "IndiGo": [(5, 9), (10, 14), (17, 22)],
                        "Air India": [(6, 10), (15, 22)],
                        "Air India Express": [(5, 8), (18, 23)],
                        "Akasa Air": [(6, 11), (16, 22)],
                        "SpiceJet": [(5, 9), (16, 22)],
                    }

                    windows = departure_windows.get(
                        airline,
                        [(6, 22)]
                    )

                    start_hour, end_hour = random.choice(windows)

                    hour = random.randint(start_hour, end_hour)
                    minute = random.choice([0, 10, 15, 20, 30, 40, 45, 50])

                    departure_time = timezone.make_aware(
                        datetime.combine(
                            current_date,
                            datetime.min.time().replace(
                                hour=hour,
                                minute=minute,
                            ),
                        )
                    )

                    # Realistic duration based on route band
                    duration_minutes = int(route["duration_minutes"])
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)

                    # Base fare from route
                    base_price = float(route["base_fare"])

                    # Weekend surcharge
                    weekend_multiplier = (
                        1.10 if current_date.weekday() >= 5 else 1.00
                    )

                    # Peak hour surcharge
                    peak_multiplier = (
                        1.08 if hour in [7, 8, 9, 18, 19, 20] else 1.00
                    )

                    # Random market demand
                    demand_multiplier = random.uniform(0.90, 1.18)

                    economy_price = round(
                        base_price
                        * weekend_multiplier
                        * peak_multiplier
                        * demand_multiplier
                    )

                    business_price = round(
                        economy_price * random.uniform(1.65, 1.90)
                    )

                    first_class_price = round(
                        business_price * random.uniform(1.30, 1.55)
                    )

                    # Peak hour pricing
                    if 6 <= hour <= 9:
                        economy_price = round(economy_price * 1.15)
                        business_price = round(business_price * 1.12)
                        first_class_price = round(first_class_price * 1.10)

                    elif 17 <= hour <= 21:
                        economy_price = round(economy_price * 1.12)
                        business_price = round(business_price * 1.10)
                        first_class_price = round(first_class_price * 1.08)

                    elif 22 <= hour or hour <= 5:
                        economy_price = round(economy_price * 0.90)
                        business_price = round(business_price * 0.92)
                        first_class_price = round(first_class_price * 0.94)

                    # Flight number - make it unique by including date, route, and flight number
                    
                    tripease_flight_id = f"TP{uuid.uuid4().hex[:10].upper()}"

                    tracking_flight_number = random.choice(
                        tracking_numbers.get(airline, [])
                    )

                    # Check if flight already exists
                    if Flight.objects.filter(
                        flight_number=flight_number,
                        departure_time=departure_time,
                    ).exists():
                        continue

                    # Seats
                    total_seats = random.choice([120, 150, 180, 200])

                    # Realistic occupancy (45%–95% full)
                    occupancy = random.uniform(0.45, 0.95)

                    available_seats = max(
                        5,
                        int(total_seats * (1 - occupancy))
                    )

                    # Last-seat premium
                    if available_seats < 15:
                        economy_price = round(economy_price * 1.15)
                        business_price = round(business_price * 1.12)
                        first_class_price = round(first_class_price * 1.10)

                    # Non-stop or with stop
                    is_non_stop = random.choice(
                        [True, True, True, False]
                    )  # 75% non-stop

                    flight = Flight.objects.create(
                        flight_number=flight_number,
                        tripease_flight_id=tripease_flight_id,
                        tracking_flight_number=tracking_flight_number,
                        airline=airline,
                        source=source,
                        destination=destination,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration_minutes=duration_minutes,
                        economy_price=economy_price,
                        business_price=business_price,
                        first_class_price=first_class_price,
                        total_seats=total_seats,
                        available_seats=available_seats,
                        is_non_stop=is_non_stop,
                    )

                    flight_count += 1
                    if flight_count % 50 == 0:
                        self.stdout.write(f"Created {flight_count} flights...")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully loaded dummy data!\n"
                f"- Airports: {len(airports_dict)}\n"
                f"- Flights: {flight_count}\n"
            )
        )
