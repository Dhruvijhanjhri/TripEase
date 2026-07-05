import pickle
from pathlib import Path
import numpy as np
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "fare_model_final.pkl", "rb") as f:
    MODEL = pickle.load(f)

with open(BASE_DIR / "fare_preprocessing.pkl", "rb") as f:
    PREP = pickle.load(f)


ENCODINGS = PREP["target_encodings"]
GLOBAL_MEAN = PREP["global_mean"]
FEATURE_COLUMNS = PREP["feature_columns"]
SCALER = PREP["scaler"]
SCALE_FEATURES = PREP["scale_features"]


def encode(column, value):
    """
    Target encoding lookup.
    """
    mapping = ENCODINGS.get(column, {})
    return mapping.get(value, GLOBAL_MEAN)


def predict_fare(
    airline,
    source_city,
    destination_city,
    departure_date,
    departure_time,
    duration_minutes,
    stops=0,
):
    """
    Returns predicted fare.
    """

    departure_hour = departure_time.hour
    departure_month = departure_date.month
    departure_day_of_week = departure_date.weekday()
    is_weekend = 1 if departure_day_of_week >= 5 else 0

    features = {
        "Number Of Stops": stops,
        "total_duration_minutes": duration_minutes,
        "departure_day_of_week": departure_day_of_week,
        "departure_month": departure_month,
        "departure_hour": departure_hour,

        "is_weekend": is_weekend,

        "Source_encoded": encode("Source", source_city),
        "Destination_encoded": encode("Destination", destination_city),
        "Layover1_encoded": encode(
            "Layover1",
            "NoStop" if stops == 0 else "Layover"
        ),
        "Layover2_encoded": encode("Layover2", "NoStop"),
        "Layover3_encoded": encode("Layover3", "NoStop"),
        "primary_airline_encoded": encode(
            "primary_airline",
            airline
        ),
    }

    X = np.array([
        [features[col] for col in FEATURE_COLUMNS]
    ])

    if SCALE_FEATURES and SCALER is not None:
        X = SCALER.transform(X)

    prediction = MODEL.predict(X)[0]

    return round(float(prediction), 2)