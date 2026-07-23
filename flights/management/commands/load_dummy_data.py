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


class Command(BaseCommand):
    help = "Loads dummy data for Indian airports and flights"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to load dummy data..."))

        # Indian Airports Data
        airports_data = [
            {
                "code": "BLR",
                "name": "Kempegowda International Airport",
                "city": "Bengaluru",
            },
            {
                "code": "DEL",
                "name": "Indira Gandhi International Airport",
                "city": "Delhi",
            },
            {
                "code": "BOM",
                "name": "Chhatrapati Shivaji Maharaj International Airport",
                "city": "Mumbai",
            },
            {
                "code": "CCU",
                "name": "Netaji Subhas Chandra Bose International Airport",
                "city": "Kolkata",
            },
            {"code": "MAA", "name": "Chennai International Airport", "city": "Chennai"},
            {
                "code": "HYD",
                "name": "Rajiv Gandhi International Airport",
                "city": "Hyderabad",
            },
            {"code": "PNQ", "name": "Pune Airport", "city": "Pune"},
            {"code": "GOI", "name": "Dabolim Airport", "city": "Goa"},
            {"code": "JAI", "name": "Jaipur International Airport", "city": "Jaipur"},
            {
                "code": "AMD",
                "name": "Sardar Vallabhbhai Patel International Airport",
                "city": "Ahmedabad",
            },
            {"code": "COK", "name": "Cochin International Airport", "city": "Kochi"},
            {"code": "IXC", "name": "Chandigarh Airport", "city": "Chandigarh"},
            {"code": "IDR", "name": "Devi Ahilya Bai Holkar Airport", "city": "Indore"},
            {
                "code": "LKO",
                "name": "Chaudhary Charan Singh International Airport",
                "city": "Lucknow",
            },
            {
                "code": "VNS",
                "name": "Lal Bahadur Shastri International Airport",
                "city": "Varanasi",
            },
            {"code": "PAT", "name": "Jay Prakash Narayan Airport", "city": "Patna"},
            {
                "code": "GAU",
                "name": "Lokpriya Gopinath Bordoloi International Airport",
                "city": "Guwahati",
            },
            {
                "code": "TRV",
                "name": "Trivandrum International Airport",
                "city": "Thiruvananthapuram",
            },
        ]

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

        # Generate all possible routes (excluding same airport)
        all_routes = []
        for source_code in airport_codes:
            for dest_code in airport_codes:
                if source_code != dest_code:
                    all_routes.append((source_code, dest_code))

        self.stdout.write(f"Total routes to create: {len(all_routes)}")

        # Generate flights for the next 30 days
        for day in range(30):
            current_date = timezone.now().date() + timedelta(days=day)

            # Create flights for ALL routes - ensure at least 1-2 flights per route per day
            for source_code, dest_code in all_routes:
                source = airports_dict[source_code]
                destination = airports_dict[dest_code]

                # Skip if same airport
                if source == destination:
                    continue

                # Create 1-2 flights per route per day (guaranteed at least 1)
                num_flights = random.randint(1, 2)

                for flight_num in range(num_flights):
                    # Random departure time between 6 AM and 10 PM
                    hour = random.randint(6, 22)
                    minute = random.choice([0, 15, 30, 45])

                    departure_time = timezone.make_aware(
                        datetime.combine(
                            current_date,
                            datetime.min.time().replace(hour=hour, minute=minute),
                        )
                    )

                    # Realistic duration based on route band
                    duration_minutes = get_route_duration_minutes(
                        source_code, dest_code
                    )
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)

                    # Prices (in INR)
                    base_price = get_route_base_fare(source_code, dest_code)
                    economy_price = float(base_price)
                    business_price = float(base_price * 1.8)
                    first_class_price = float(base_price * 1.35)

                    # Flight number - make it unique by including date, route, and flight number
                    airline = normalize_airline_name(random.choice(airlines))
                    airline_code = get_airline_code(airline)
                    route_code = f"{source_code}{dest_code}"
                    flight_num = random.randint(100, 999)
                    flight_number = (
                        f"{airline_code}-{route_code}-{uuid.uuid4().hex[:8]}"
                    )

                    tripease_flight_id = f"TP{100000 + flight_count}"

                    tracking_flight_number = random.choice(
                        tracking_numbers.get(airline, [])
                    )

                    # Check if flight already exists
                    if Flight.objects.filter(flight_number=flight_number).exists():
                        continue

                    # Seats
                    total_seats = random.choice([120, 150, 180, 200])
                    available_seats = random.randint(
                        int(total_seats * 0.3), total_seats
                    )

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
