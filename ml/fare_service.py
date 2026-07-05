import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "fare_model_final.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_DIR,
    "fare_preprocessing.pkl"
)


class FarePredictionService:

    def __init__(self):

        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

        with open(PREPROCESSOR_PATH, "rb") as f:
            self.preprocessing = pickle.load(f)

        self.encodings = self.preprocessing["target_encodings"]
        self.global_mean = self.preprocessing["global_mean"]
        self.scaler = self.preprocessing["scaler"]
        self.feature_columns = self.preprocessing["feature_columns"]
        self.scale_features = self.preprocessing["scale_features"]

    def _encode(self, column, value):

        mapping = self.encodings.get(column, {})

        return mapping.get(value, self.global_mean)

    def prepare_features(
        self,
        source,
        destination,
        stops,
        duration_minutes,
        departure_date,
        departure_hour,
        airline,
    ):

        departure_day = departure_date.weekday()

        departure_month = departure_date.month

        is_weekend = (
            1 if departure_day >= 5 else 0
        )

        row = {
            "Number Of Stops": stops,
            "total_duration_minutes": duration_minutes,
            "departure_day_of_week": departure_day,
            "departure_month": departure_month,
            "departure_hour": departure_hour,
            "is_weekend": is_weekend,

            "Source_encoded":
                self._encode(
                    "Source",
                    source
                ),

            "Destination_encoded":
                self._encode(
                    "Destination",
                    destination
                ),

            "Layover1_encoded":
                self._encode(
                    "Layover1",
                    "NoStop" if stops == 0 else "Unknown"
                ),

            "Layover2_encoded":
                self._encode(
                    "Layover2",
                    "NoStop"
                ),

            "Layover3_encoded":
                self._encode(
                    "Layover3",
                    "NoStop"
                ),

            "primary_airline_encoded":
                self._encode(
                    "primary_airline",
                    airline
                ),
        }

        df = pd.DataFrame([row])

        df = df[self.feature_columns]

        if self.scale_features:
            df = self.scaler.transform(df)

        return df

    def predict(
        self,
        source,
        destination,
        stops,
        duration_minutes,
        departure_date,
        departure_hour,
        airline,
    ):

        features = self.prepare_features(
            source,
            destination,
            stops,
            duration_minutes,
            departure_date,
            departure_hour,
            airline,
        )

        prediction = self.model.predict(features)[0]

        return round(float(prediction), 2)


fare_predictor = FarePredictionService()