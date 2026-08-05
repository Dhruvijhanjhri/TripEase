import pandas as pd
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Input files
AIRPORTS_FILE = DATA_DIR / "ourairports.csv"
REGIONS_FILE = DATA_DIR / "regions.csv"

# Output file
OUTPUT_FILE = DATA_DIR / "indian_airports.csv"

print("Loading datasets...")

airports = pd.read_csv(AIRPORTS_FILE, low_memory=False)
regions = pd.read_csv(REGIONS_FILE)

# -----------------------------
# Keep only Indian airports
# -----------------------------
airports = airports[
    airports["iso_country"] == "IN"
].copy()

# -----------------------------
# Keep only airports having IATA
# -----------------------------
airports = airports[
    airports["iata_code"].notna()
]

# -----------------------------
# Keep only major commercial airports
# -----------------------------
airports = airports[
    airports["type"].isin([
        "large_airport",
        "medium_airport",
    ])
]

# -----------------------------
# Keep scheduled airports
# -----------------------------
airports = airports[
    airports["scheduled_service"] == "yes"
]

# -----------------------------
# Merge state names
# -----------------------------
regions = regions[
    regions["code"].str.startswith("IN-")
][["code", "name"]]

airports = airports.merge(
    regions,
    left_on="iso_region",
    right_on="code",
    how="left"
)

# -----------------------------
# Final columns
# -----------------------------
airports = airports[
    [
        "iata_code",
        "name_x",
        "municipality",
        "name_y",
        "latitude_deg",
        "longitude_deg",
    ]
]

airports.columns = [
    "iata_code",
    "airport_name",
    "city",
    "state",
    "latitude",
    "longitude",
]

# Remove Air Force / Defence airports
airports = airports[
    ~airports["airport_name"].str.contains(
        "Air Force|AFS|Defence|Naval|INS",
        case=False,
        na=False,
    )
]

# Remove airports without city names
airports = airports.dropna(subset=["city"])

# Remove duplicate airports
airports = airports.drop_duplicates(subset=["iata_code"])

# Sort alphabetically by city
airports = airports.sort_values(
    by=["city", "airport_name"]
).reset_index(drop=True)

airports.to_csv(
    OUTPUT_FILE,
    index=False
)

print("--------------------------------")
print(f"Indian Airports : {len(airports)}")
print(f"Saved to : {OUTPUT_FILE}")
print("--------------------------------")