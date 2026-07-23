import random

from django.core.management.base import BaseCommand

from flights.models import Flight

TRACKING_NUMBERS = {
    "IndiGo": [
        "6E203",
        "6E449",
        "6E512",
        "6E621",
        "6E315",
    ],
    "Air India": [
        "AI101",
        "AI302",
        "AI505",
        "AI607",
    ],
    "Akasa Air": [
        "QP1401",
        "QP1403",
        "QP1405",
    ],
    "SpiceJet": [
        "SG8169",
        "SG2481",
    ],
    "Air India Express": [
        "IX1452",
        "IX274",
    ],
}


class Command(BaseCommand):

    help = "Assign tracking numbers to existing flights"

    def handle(self, *args, **kwargs):

        flights = Flight.objects.filter(tracking_flight_number__isnull=True)

        batch = []

        updated = 0

        for flight in flights:

            if not flight.tripease_flight_id:
                flight.tripease_flight_id = f"TP{100000 + flight.id}"

            flight.tracking_flight_number = random.choice(
                TRACKING_NUMBERS.get(flight.airline, ["AI101"])
            )

            batch.append(flight)

            if len(batch) == 5000:

                Flight.objects.bulk_update(
                    batch,
                    [
                        "tripease_flight_id",
                        "tracking_flight_number",
                    ],
                )

                updated += len(batch)

                self.stdout.write(self.style.SUCCESS(f"{updated} flights updated..."))

                batch = []

        if batch:

            Flight.objects.bulk_update(
                batch,
                [
                    "tripease_flight_id",
                    "tracking_flight_number",
                ],
            )

            updated += len(batch)

        self.stdout.write(
            self.style.SUCCESS(f"{updated} flights updated successfully.")
        )
