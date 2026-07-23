from datetime import date

from ml.fare_service import fare_predictor

price = fare_predictor.predict(
    source="Delhi",
    destination="Mumbai",
    stops=0,
    duration_minutes=130,
    departure_date=date(2026, 8, 10),
    departure_hour=10,
    airline="IndiGo",
)

print(price)
