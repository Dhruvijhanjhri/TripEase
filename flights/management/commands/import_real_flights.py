import csv
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from flights.models import Flight, Airport

class Command(BaseCommand):

    help = "Import real flight data"

    def handle(self, *args, **kwargs):

        file_path = "data/Clean_Dataset.csv"

        with open(file_path, newline='', encoding='utf-8') as file:

            reader = csv.DictReader(file)

            count = 0

            for row in reader:

                # Create / get source airport
                source_airport, _ = Airport.objects.get_or_create(
                    code=row['source_city'][:3].upper(),
                    defaults={
                        "name": row['source_city'] + " Airport",
                        "city": row['source_city'],
                        "country": "India",
                    }
                )

                # Create / get destination airport
                destination_airport, _ = Airport.objects.get_or_create(
                    code=row['destination_city'][:3].upper(),
                    defaults={
                        "name": row['destination_city'] + " Airport",
                        "city": row['destination_city'],
                        "country": "India",
                    }
                )

                # Convert duration like "2h 30m" to minutes
                duration_text = row['duration']

                hours = 0
                minutes = 0

                if "h" in duration_text:
                    hours = int(duration_text.split("h")[0])

                if "m" in duration_text:
                    minutes = int(duration_text.split("m")[0].split()[-1])

                duration_minutes = hours * 60 + minutes

                # Create departure & arrival times
                departure_time = timezone.now()

                arrival_time = departure_time + timedelta(
                    minutes=duration_minutes
                )

                # Convert stops to boolean
                is_non_stop = row['stops'].lower() == "non-stop"

                # Base price
                base_price = float(row['price'])

                # Prices for classes
                economy_price = base_price

                business_price = base_price * 1.8

                first_class_price = base_price * 2.5

                # Seat configuration
                total_seats = 180

                available_seats = random.randint(20, 180)

                # Use dataset flight number
                flight_number = row['flight']

                # Create or update flight
                Flight.objects.update_or_create(

                    flight_number=flight_number,

                    defaults={

                        'airline': row['airline'],

                        'source': source_airport,

                        'destination': destination_airport,

                        'departure_time': departure_time,

                        'arrival_time': arrival_time,

                        'duration_minutes': duration_minutes,

                        'economy_price': economy_price,

                        'business_price': business_price,

                        'first_class_price': first_class_price,

                        'total_seats': total_seats,

                        'available_seats': available_seats,

                        'is_non_stop': is_non_stop,
                    }
                )

                count += 1

                if count % 500 == 0:

                    print(count, "records imported")

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} flights imported successfully"
            )
        )