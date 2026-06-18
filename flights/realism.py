from decimal import Decimal
import hashlib


ACTIVE_AIRLINES = [
    "Air India",
    "Air India Express",
    "IndiGo",
    "Akasa Air",
    "SpiceJet",
]

AIRLINE_CODE_MAP = {
    "Air India": "AI",
    "Air India Express": "IX",
    "IndiGo": "6E",
    "Akasa Air": "QP",
    "SpiceJet": "SG",
}

AIRLINE_NORMALIZATION_MAP = {
    "Indigo": "IndiGo",
}

ROUTE_ZONE_MAP = {
    "DEL": "north",
    "IXC": "north",
    "LKO": "north",
    "PAT": "east",
    "VNS": "east",
    "SXR": "north",
    "IXJ": "north",
    "IXL": "north",
    "BOM": "west",
    "AMD": "west",
    "PNQ": "west",
    "GOI": "west",
    "GOX": "west",
    "NAG": "central",
    "BHO": "central",
    "IDR": "central",
    "JAI": "north",
    "BLR": "south",
    "HYD": "south",
    "MAA": "south",
    "COK": "south",
    "TRV": "south",
    "CJB": "south",
    "IXM": "south",
    "IXE": "south",
    "CCU": "east",
    "BBI": "east",
    "IXB": "east",
    "GAU": "east",
    "IXA": "east",
    "IMF": "east",
    "NAG": "central",
}

ROUTE_OVERRIDES = {
    ("DEL", "IDR"): {"duration": 90, "base_fare": Decimal("3400")},
    ("BOM", "BLR"): {"duration": 105, "base_fare": Decimal("4200")},
    ("DEL", "CCU"): {"duration": 120, "base_fare": Decimal("5200")},
    ("BOM", "DEL"): {"duration": 125, "base_fare": Decimal("5200")},
    ("BLR", "HYD"): {"duration": 70, "base_fare": Decimal("3100")},
    ("MAA", "BLR"): {"duration": 80, "base_fare": Decimal("3300")},
    ("DEL", "BLR"): {"duration": 150, "base_fare": Decimal("6500")},
    ("DEL", "BOM"): {"duration": 130, "base_fare": Decimal("5600")},
}

DISTANCE_BANDS = {
    "short": {
        "duration_min": 75,
        "duration_max": 110,
        "base_min": Decimal("2500"),
        "base_max": Decimal("6000"),
    },
    "medium": {
        "duration_min": 110,
        "duration_max": 160,
        "base_min": Decimal("4000"),
        "base_max": Decimal("9000"),
    },
    "long": {
        "duration_min": 165,
        "duration_max": 240,
        "base_min": Decimal("6000"),
        "base_max": Decimal("15000"),
    },
}

CABIN_MULTIPLIERS = {
    "economy": Decimal("1.00"),
    "first": Decimal("1.35"),
    "business": Decimal("2.10"),
}

CABIN_LABELS = {
    "economy": "Economy",
    "first": "Premium Economy",
    "business": "Business",
}


def normalize_airline_name(name):
    clean_name = (name or "").strip()
    return AIRLINE_NORMALIZATION_MAP.get(clean_name, clean_name)


def get_airline_code(airline):
    return AIRLINE_CODE_MAP.get(airline, airline[:2].upper() if airline else "AI")


def get_cabin_label(cabin_class):
    return CABIN_LABELS.get(cabin_class, CABIN_LABELS["economy"])


def get_cabin_multiplier(cabin_class):
    return CABIN_MULTIPLIERS.get(cabin_class, CABIN_MULTIPLIERS["economy"])


def get_seat_label(available_seats):
    if available_seats <= 0:
        return "Sold Out"
    if available_seats <= 3:
        return f"⚠ Only {available_seats} Seats Left"
    if available_seats <= 5:
        return f"Only {available_seats} Seats Left"
    return f"{available_seats} Seats Available"


def format_duration_minutes(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m"


def get_display_flight_number(flight_number, airline=None):
    flight_number = (flight_number or "").strip()

    if not flight_number:
        return "Flight No: N/A"

    parts = flight_number.split("-")

    if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
        return f"Flight No: {flight_number}"

    airline_code = get_airline_code(airline or parts[0])
    digest = hashlib.sha1(flight_number.encode("utf-8")).hexdigest()
    numeric_id = 100 + (int(digest[:6], 16) % 900)

    return f"Flight No: {airline_code}-{numeric_id}"


def _route_key(source_code, destination_code):
    return tuple(sorted([source_code, destination_code]))


def _band_from_zones(source_code, destination_code):
    source_zone = ROUTE_ZONE_MAP.get(source_code, "other")
    destination_zone = ROUTE_ZONE_MAP.get(destination_code, "other")

    if source_zone == destination_zone:
        return "short"

    zones = {source_zone, destination_zone}

    if zones == {"north", "west"}:
        return "short"
    if zones == {"west", "south"}:
        return "short"
    if zones == {"south", "central"}:
        return "short"
    if zones == {"north", "central"}:
        return "short"

    if zones == {"north", "east"}:
        return "medium"
    if zones == {"west", "east"}:
        return "medium"
    if zones == {"south", "east"}:
        return "medium"
    if zones == {"north", "south"}:
        return "medium"
    if zones == {"west", "south"}:
        return "medium"

    return "long"


def get_route_band(source_code, destination_code):
    route_key = _route_key(source_code, destination_code)
    if route_key in ROUTE_OVERRIDES:
        if ROUTE_OVERRIDES[route_key]["base_fare"] <= Decimal("3999"):
            return "short"
        if ROUTE_OVERRIDES[route_key]["base_fare"] <= Decimal("8999"):
            return "medium"
        return "long"

    return _band_from_zones(source_code, destination_code)


def _stable_offset(route_key, span):
    digest = hashlib.sha1("-".join(route_key).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % span


def get_route_duration_minutes(source_code, destination_code):
    route_key = _route_key(source_code, destination_code)
    override = ROUTE_OVERRIDES.get(route_key)

    if override:
        return override["duration"]

    band = DISTANCE_BANDS[get_route_band(source_code, destination_code)]
    spread = band["duration_max"] - band["duration_min"]
    return band["duration_min"] + _stable_offset(route_key, spread + 1)


def get_route_base_fare(source_code, destination_code):
    route_key = _route_key(source_code, destination_code)
    override = ROUTE_OVERRIDES.get(route_key)

    if override:
        return override["base_fare"]

    band = DISTANCE_BANDS[get_route_band(source_code, destination_code)]
    spread = band["base_max"] - band["base_min"]
    step = Decimal(_stable_offset(route_key, 12)) * Decimal("100")
    return min(band["base_min"] + step, band["base_max"])


def get_route_price(source_code, destination_code, cabin_class):
    base_fare = get_route_base_fare(source_code, destination_code)
    return (base_fare * get_cabin_multiplier(cabin_class)).quantize(Decimal("1.00"))