import os

from fpdf import FPDF

from django.conf import settings

from bookings.qr_generator import generate_qr_code


def generate_boarding_pass(booking):

    passenger = booking.passengers.first()

    qr_relative = generate_qr_code(booking)

    qr_path = os.path.join(
        settings.MEDIA_ROOT,
        qr_relative
    )

    folder = os.path.join(
        settings.MEDIA_ROOT,
        "boarding_passes"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    pdf_path = os.path.join(
        folder,
        f"{booking.booking_reference}.pdf"
    )

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(False)

    pdf.set_font("Helvetica", "B", 22)

    pdf.cell(
        0,
        12,
        "TripEase Boarding Pass",
        ln=True,
        align="C"
    )

    pdf.ln(8)

    pdf.set_font("Helvetica", "", 13)

    pdf.cell(
        0,
        8,
        f"Passenger : {passenger.first_name} {passenger.last_name}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Booking Ref : {booking.booking_reference}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Airline : {booking.flight.airline}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Flight : {booking.flight.get_display_flight_number()}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Route : {booking.flight.source.code} -> {booking.flight.destination.code}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Travel Date : {booking.travel_date}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Seat : {passenger.seat_number or 'Not Assigned'}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Cabin : {booking.cabin_class.title()}",
        ln=True
    )

    pdf.ln(10)

    if os.path.exists(qr_path):

        pdf.image(
            qr_path,
            x=75,
            w=60
        )

    pdf.ln(70)

    pdf.set_font(
        "Helvetica",
        "I",
        11
    )

    pdf.cell(
        0,
        8,
        "Powered by TripEase",
        align="C"
    )

    pdf.output(pdf_path)

    return f"boarding_passes/{booking.booking_reference}.pdf"