ROWS = 30
SEATS_PER_ROW = ["A", "B", "C", "D", "E", "F"]


def generate_seat_map(booked_seats=None):

    if booked_seats is None:
        booked_seats = []

    seat_map = []

    for row in range(1, ROWS + 1):

        row_seats = []

        for letter in SEATS_PER_ROW:

            seat = f"{row}{letter}"

            row_seats.append(
                {
                    "seat_number": seat,
                    "booked": seat in booked_seats,
                }
            )

        seat_map.append(row_seats)

    return seat_map
