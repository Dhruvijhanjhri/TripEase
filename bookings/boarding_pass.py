import os

from django.conf import settings
from django.template.loader import render_to_string

from weasyprint import HTML


def generate_boarding_pass(booking):

    passenger = booking.passengers.first()

    qr_relative_path = os.path.join(
        settings.MEDIA_URL,
        "qr_codes",
        f"{booking.booking_reference}.png"
    )

    context = {

        "booking": booking,

        "passenger": passenger,

        "qr_path": os.path.join(
            settings.MEDIA_ROOT,
            "qr_codes",
            f"{booking.booking_reference}.png"
        )

    }

    html_string = render_to_string(
        "bookings/boarding_pass.html",
        context
    )

    folder = os.path.join(
        settings.MEDIA_ROOT,
        "boarding_passes"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    filename = f"{booking.booking_reference}.pdf"

    output_path = os.path.join(
        folder,
        filename
    )

    HTML(
        string=html_string,
        base_url=settings.MEDIA_ROOT
    ).write_pdf(output_path)

    return os.path.join(
        "boarding_passes",
        filename
    )