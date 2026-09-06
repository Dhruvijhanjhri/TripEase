ROWS = 30
SEATS_PER_ROW = ["A", "B", "C", "D", "E", "F"]

# Generic narrow-body domestic aircraft layout
EMERGENCY_EXIT_ROWS = {12, 13}
EXTRA_LEGROOM_ROWS = {11, 14}


def generate_seat_map(booked_seats=None):

    if booked_seats is None:
        booked_seats = []

    seat_map = []

    for row in range(1, ROWS + 1):

        row_seats = []

        for letter in SEATS_PER_ROW:

            seat = f"{row}{letter}"

            if letter in ["A", "F"]:
                seat_type = "window"
            elif letter in ["C", "D"]:
                seat_type = "aisle"
            else:
                seat_type = "middle"

            row_seats.append(
                {
                    "seat_number": seat,
                    "booked": seat in booked_seats,
                    "seat_type": seat_type,
                    "is_emergency_exit": row in EMERGENCY_EXIT_ROWS,
                    "is_extra_legroom": row in EXTRA_LEGROOM_ROWS,
                }
            )

        seat_map.append(row_seats)

    return seat_map
