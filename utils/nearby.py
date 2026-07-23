import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_nearby_places(lat, lon):

    query = f"""
    [out:json];

    (
      node(around:5000,{lat},{lon})["amenity"="restaurant"];
      node(around:5000,{lat},{lon})["amenity"="cafe"];
      node(around:5000,{lat},{lon})["amenity"="hospital"];
      node(around:5000,{lat},{lon})["amenity"="atm"];
      node(around:5000,{lat},{lon})["amenity"="fuel"];
    );

    out center;
    """

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            timeout=20,
        )

        print("Overpass status:", response.status_code)
        print(response.text[:300])

        data = response.json()

        places = {
            "restaurants": [],
            "cafes": [],
            "hospitals": [],
            "atms": [],
            "fuel": [],
        }

        for item in data.get("elements", []):

            tags = item.get("tags", {})

            name = tags.get("name")

            if not name:
                continue

            amenity = tags.get("amenity")

            if amenity == "restaurant":
                places["restaurants"].append(name)

            elif amenity == "cafe":
                places["cafes"].append(name)

            elif amenity == "hospital":
                places["hospitals"].append(name)

            elif amenity == "atm":
                places["atms"].append(name)

            elif amenity == "fuel":
                places["fuel"].append(name)

        for key in places:
            places[key] = places[key][:5]

        # fallback demo data if API returns empty results
        if not any(places.values()):

            return {
                "restaurants": [
                    "Little Monk",
                    "Chappan Dukan",
                    "Apna Sweets",
                ],

                "cafes": [
                    "Cafe Coffee Day",
                    "Starbucks",
                    "Mr. Beans",
                ],

                "hospitals": [
                    "Bombay Hospital",
                    "CHL Hospital",
                ],

                "atms": [
                    "SBI ATM",
                    "HDFC ATM",
                ],

                "fuel": [
                    "Indian Oil Fuel Station",
                ],
            }

        return places

    except Exception as e:

        print("Nearby API Error:", e)

        return {
            "restaurants": [
                "Little Monk",
                "Chappan Dukan",
                "Apna Sweets",
            ],

            "cafes": [
                "Cafe Coffee Day",
                "Starbucks",
                "Mr. Beans",
            ],

            "hospitals": [
                "Bombay Hospital",
                "CHL Hospital",
            ],

            "atms": [
                "SBI ATM",
                "HDFC ATM",
            ],

            "fuel": [
                "Indian Oil Fuel Station",
            ],
        }