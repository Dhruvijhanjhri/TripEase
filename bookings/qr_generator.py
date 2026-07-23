import os
import qrcode

from django.conf import settings


def generate_qr_code(booking):

    seat_numbers = ", ".join(booking.passengers.values_list("seat_number", flat=True))

    qr_data = f"""
TripEase Boarding Pass

Booking Reference:
{booking.booking_reference}

Passenger(s):
{booking.number_of_passengers}

Flight:
{booking.flight.get_display_flight_number()}

Route:
{booking.flight.source.code} → {booking.flight.destination.code}

Travel Date:
{booking.travel_date}

Seat(s):
{seat_numbers}
"""

    qr = qrcode.QRCode(version=1, box_size=10, border=4)

    qr.add_data(qr_data)

    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")

    folder = os.path.join(settings.MEDIA_ROOT, "qr_codes")

    os.makedirs(folder, exist_ok=True)

    filename = f"{booking.booking_reference}.png"

    filepath = os.path.join(folder, filename)

    image.save(filepath)

    return os.path.join("qr_codes", filename)
