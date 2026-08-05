import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# Read airports
airports = pd.read_csv("data/indian_airports.csv")

# Airports by IATA
airport_codes = set(airports["iata_code"])
airport_lookup = airports.set_index("iata_code").to_dict("index")

# Airline hubs
AIRLINE_HUBS = {
    "IndiGo": ["DEL", "BLR", "BOM", "HYD"],
    "Air India": ["DEL", "BOM"],
    "Air India Express": ["COK", "TRV", "MAA"],
    "Akasa Air": ["BOM", "BLR"],
    "SpiceJet": ["DEL", "HYD"],
}

# Starting flight numbers
START_NUMBER = {
    "IndiGo": 200,
    "Air India": 800,
    "Air India Express": 500,
    "Akasa Air": 1400,
    "SpiceJet": 400,
}

MAJOR_AIRPORTS = set(AIRLINE_HUBS["IndiGo"])
MAJOR_AIRPORTS.update(AIRLINE_HUBS["Air India"])
MAJOR_AIRPORTS.update(AIRLINE_HUBS["Air India Express"])
MAJOR_AIRPORTS.update(AIRLINE_HUBS["Akasa Air"])
MAJOR_AIRPORTS.update(AIRLINE_HUBS["SpiceJet"])

# Add important metros
MAJOR_AIRPORTS.update({
    "AMD",
    "GOI",
    "PNQ",
    "COK",
    "IXC",
    "LKO",
    "GAU",
    "JAI",
    "TRV",
    "VNS",
    "IDR",
})

ALL_AIRPORTS = set(airport_codes)

REGIONAL_AIRPORTS = sorted(ALL_AIRPORTS - MAJOR_AIRPORTS)

routes = []

def estimate_route(source, destination):

    lat1 = airport_lookup[source]["latitude"]
    lon1 = airport_lookup[source]["longitude"]

    lat2 = airport_lookup[destination]["latitude"]
    lon2 = airport_lookup[destination]["longitude"]

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    # Duration (average cruise speed + taxi time)
    duration = int((distance / 700) * 60 + 30)

    # Base economy fare
    fare = max(2200, int(distance * 3.2))

    return duration, fare

PREFIX = {
    "IndiGo": "6E",
    "Air India": "AI",
    "Air India Express": "IX",
    "Akasa Air": "QP",
    "SpiceJet": "SG",
}

for airline, hubs in AIRLINE_HUBS.items():

    flight_no = START_NUMBER[airline]

    # Hub → Major Airports
    for hub in hubs:

        for airport in MAJOR_AIRPORTS:

            if hub == airport:
                continue

            duration, fare = estimate_route(hub, airport)

            routes.append({
                "flight_number": f"{PREFIX[airline]}{flight_no}",
                "airline": airline,
                "source": hub,
                "destination": airport,
                "duration_minutes": duration,
                "base_fare": fare,
            })
            flight_no += 1

            routes.append({
                "flight_number": f"{PREFIX[airline]}{flight_no}",
                "airline": airline,
                "source": airport,
                "destination": hub,
                "duration_minutes": duration,
                "base_fare": fare,
            })
            flight_no += 1

    # Regional Routes (automatic nearest hubs)

    for regional in REGIONAL_AIRPORTS:

        nearest = []

        for hub in hubs:
            duration, fare = estimate_route(regional, hub)
            nearest.append((duration, fare, hub))

        nearest.sort(key=lambda x: x[0])

        # Connect to the 2 nearest hubs of this airline
        for duration, fare, hub in nearest[:2]:

            routes.append({
                "flight_number": f"{PREFIX[airline]}{flight_no}",
                "airline": airline,
                "source": regional,
                "destination": hub,
                "duration_minutes": duration,
                "base_fare": fare,
            })
            flight_no += 1

            routes.append({
                "flight_number": f"{PREFIX[airline]}{flight_no}",
                "airline": airline,
                "source": hub,
                "destination": regional,
                "duration_minutes": duration,
                "base_fare": fare,
            })
            flight_no += 1

routes_df = pd.DataFrame(routes)

# Remove duplicate routes (same airline + source + destination)
routes_df = routes_df.drop_duplicates(
    subset=["airline", "source", "destination"]
)

# Sort for readability
routes_df = routes_df.sort_values(
    by=["airline", "source", "destination"]
).reset_index(drop=True)

# Save
routes_df.to_csv("data/routes.csv", index=False)

print("--------------------------------")
print(f"Routes Generated : {len(routes_df)}")
print("Saved to : data/routes.csv")
print("--------------------------------")