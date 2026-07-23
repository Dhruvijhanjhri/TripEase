from packages.models import TravelPackage
from packages.package_destinations import INDIA_PACKAGES
import random

print("Deleting old packages...")
TravelPackage.objects.all().delete()

# ====================================================
# DESTINATION DETAILS
# ====================================================

DESTINATION_DETAILS = {
    "Goa": {
        "description": "Experience golden beaches, thrilling water sports, vibrant nightlife and stunning sunsets in India's most loved beach destination.",
        "itinerary": """Day 1: Arrival in Goa, hotel check-in and beach relaxation.

Day 2: North Goa sightseeing including Fort Aguada, Calangute Beach and water sports activities.

Day 3: South Goa churches, local markets, sunset cruise and cultural experiences.

Day 4: Breakfast and departure.""",
    },
    "Manali": {
        "description": "Discover snow-capped mountains, scenic valleys, adventure sports and unforgettable Himalayan landscapes.",
        "itinerary": """Day 1: Arrival in Manali and evening visit to Mall Road.

Day 2: Solang Valley excursion with adventure activities.

Day 3: Rohtang Pass sightseeing and snow activities.

Day 4: Local sightseeing, shopping and departure.""",
    },
    "Shimla": {
        "description": "Enjoy colonial charm, mountain views, pine forests and relaxing walks through Himachal Pradesh.",
        "itinerary": """Day 1: Arrival and Mall Road exploration.

Day 2: Kufri excursion and scenic viewpoints.

Day 3: Local sightseeing, shopping and leisure.

Day 4: Departure.""",
    },
    "Jaipur": {
        "description": "Explore royal palaces, majestic forts, colorful bazaars and rich Rajasthani culture in the Pink City.",
        "itinerary": """Day 1: Arrival and local market visit.

Day 2: Amber Fort, Jal Mahal and Hawa Mahal.

Day 3: City Palace, Jantar Mantar and cultural evening.

Day 4: Departure.""",
    },
    "Udaipur": {
        "description": "Experience beautiful lakes, royal heritage and romantic sunsets in the City of Lakes.",
        "itinerary": """Day 1: Arrival and Lake Pichola boat ride.

Day 2: City Palace, Jag Mandir and local sightseeing.

Day 3: Shopping and cultural experiences.

Day 4: Departure.""",
    },
    "Leh": {
        "description": "Witness breathtaking landscapes, monasteries, mountain passes and unique Ladakhi culture.",
        "itinerary": """Day 1: Arrival and acclimatization.

Day 2: Monastery tour and local sightseeing.

Day 3: Nubra Valley excursion.

Day 4: Pangong Lake visit.

Day 5: Departure.""",
    },
    "Rishikesh": {
        "description": "Enjoy river rafting, yoga retreats, spiritual experiences and Himalayan beauty.",
        "itinerary": """Day 1: Arrival and Ganga Aarti.

Day 2: River rafting and adventure activities.

Day 3: Yoga session and ashram visits.

Day 4: Departure.""",
    },
    "Kerala": {
        "description": "Explore lush greenery, tea plantations, backwaters and authentic South Indian hospitality.",
        "itinerary": """Day 1: Arrival in Kochi.

Day 2: Alleppey backwater cruise.

Day 3: Munnar sightseeing.

Day 4: Departure.""",
    },
    "Kashmir": {
        "description": "Experience breathtaking valleys, houseboats, snow-covered mountains and unforgettable natural beauty.",
        "itinerary": """Day 1: Arrival in Srinagar and Dal Lake.

Day 2: Gulmarg excursion.

Day 3: Pahalgam sightseeing.

Day 4: Departure.""",
    },
}

# ====================================================
# PACKAGE VARIANTS
# ====================================================

PACKAGE_VARIANTS = {
    "beach": [
        (
            "Beach Escape",
            12000,
            22000,
            "Hotel Stay\nBreakfast\nAirport Transfer\nBeach Activities",
            "Sunscreen\nSwimwear\nHat\nLight Clothes",
        ),
        (
            "Adventure Trail",
            18000,
            32000,
            "Hotel Stay\nBreakfast\nWater Sports\nTransfers",
            "Sports Shoes\nSwimwear\nSunglasses",
        ),
        (
            "Honeymoon Retreat",
            30000,
            55000,
            "Luxury Resort\nCandle Light Dinner\nBreakfast",
            "Camera\nLight Clothes\nSunscreen",
        ),
        (
            "Family Holiday",
            18000,
            35000,
            "Hotel Stay\nBreakfast\nSightseeing",
            "Medicines\nComfortable Clothes",
        ),
    ],
    "hill_station": [
        (
            "Mountain Escape",
            12000,
            22000,
            "Hotel Stay\nBreakfast\nSightseeing",
            "Jacket\nWoollens\nSports Shoes",
        ),
        (
            "Snow Adventure",
            22000,
            38000,
            "Adventure Activities\nHotel Stay",
            "Gloves\nJacket\nTrekking Shoes",
        ),
        (
            "Honeymoon Retreat",
            28000,
            50000,
            "Luxury Stay\nBreakfast\nPrivate Tour",
            "Warm Clothes\nCamera",
        ),
        (
            "Family Explorer",
            18000,
            32000,
            "Family Hotel\nBreakfast\nLocal Tours",
            "Warm Clothes\nMedicines",
        ),
    ],
    "heritage": [
        (
            "Heritage Tour",
            15000,
            25000,
            "Hotel Stay\nBreakfast\nMonument Entry",
            "Comfortable Shoes\nCap\nCamera",
        ),
        (
            "Royal Experience",
            25000,
            45000,
            "Heritage Hotel\nGuide\nBreakfast",
            "Camera\nLight Clothes",
        ),
        (
            "Cultural Discovery",
            18000,
            32000,
            "Hotel Stay\nGuide\nExperiences",
            "Comfortable Clothes\nShoes",
        ),
        (
            "Family Heritage Trip",
            18000,
            32000,
            "Hotel Stay\nBreakfast\nSightseeing",
            "Camera\nMedicines",
        ),
    ],
    "adventure": [
        (
            "Adventure Expedition",
            28000,
            45000,
            "Activities\nHotel Stay\nBreakfast",
            "Trekking Shoes\nPower Bank",
        ),
        (
            "Thrill Seeker",
            30000,
            50000,
            "Adventure Sports\nHotel Stay",
            "Sports Wear\nShoes",
        ),
        (
            "Explorer Package",
            25000,
            42000,
            "Local Tours\nHotel\nBreakfast",
            "Backpack\nShoes",
        ),
        (
            "Premium Adventure",
            40000,
            70000,
            "Premium Hotel\nActivities",
            "Warm Clothes\nPower Bank",
        ),
    ],
    "nature": [
        (
            "Nature Escape",
            15000,
            28000,
            "Hotel Stay\nNature Tours",
            "Camera\nWalking Shoes",
        ),
        ("Eco Retreat", 18000, 32000, "Resort Stay\nMeals", "Comfortable Clothes"),
        ("Green Paradise", 20000, 35000, "Premium Stay\nSightseeing", "Camera\nShoes"),
        (
            "Forest Explorer",
            18000,
            30000,
            "Guided Tours\nHotel Stay",
            "Shoes\nBackpack",
        ),
    ],
    "family": [
        (
            "Family Vacation",
            18000,
            32000,
            "Hotel Stay\nBreakfast\nSightseeing",
            "Medicines\nComfortable Clothes",
        ),
        ("Family Retreat", 22000, 38000, "Resort Stay\nMeals", "Camera\nShoes"),
        (
            "Holiday Package",
            20000,
            35000,
            "Hotel Stay\nLocal Tours",
            "Power Bank\nMedicines",
        ),
        (
            "Relaxation Tour",
            25000,
            40000,
            "Premium Stay\nSightseeing",
            "Comfortable Clothes",
        ),
    ],
    "pilgrimage": [
        (
            "Spiritual Journey",
            12000,
            22000,
            "Temple Visits\nHotel Stay",
            "Traditional Wear\nComfortable Footwear",
        ),
        (
            "Divine Darshan",
            15000,
            25000,
            "Temple Tour\nBreakfast",
            "ID Proof\nComfortable Clothes",
        ),
        ("Sacred Escape", 18000, 28000, "Hotel Stay\nGuide", "Medicines\nShoes"),
        ("Temple Trail", 16000, 26000, "Transport\nHotel Stay", "Traditional Wear"),
    ],
    "wildlife": [
        ("Wildlife Safari", 18000, 30000, "Safari\nHotel Stay", "Binoculars\nCamera"),
        ("Jungle Adventure", 22000, 35000, "Safari\nGuide", "Neutral Colored Clothes"),
        ("Nature Explorer", 20000, 32000, "Safari\nBreakfast", "Camera\nShoes"),
        (
            "Safari Escape",
            25000,
            40000,
            "Luxury Stay\nSafari",
            "Binoculars\nPower Bank",
        ),
    ],
}

# ====================================================
# IMAGES
# ====================================================

IMAGES = [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
    "https://images.unsplash.com/photo-1500534623283-312aade485b7",
    "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
    "https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0",
]

# ====================================================
# CREATE PACKAGES
# ====================================================

created = 0

for destination, details in INDIA_PACKAGES.items():

    package_type = details["type"]
    state = details["state"]

    variants = PACKAGE_VARIANTS[package_type]

    for variant in variants:

        duration_days = random.randint(3, 8)

        package_info = DESTINATION_DETAILS.get(
            destination,
            {
                "description": f"Discover the beauty of {destination} through sightseeing, local experiences and comfortable stays.",
                "itinerary": f"""Day 1: Arrival in {destination}

Day 2: Local sightseeing and activities

Day 3: Leisure and shopping

Day {duration_days}: Departure""",
            },
        )

        TravelPackage.objects.create(
            name=f"{destination} {variant[0]}",
            destination=destination,
            state=state,
            package_type=package_type,
            duration_days=duration_days,
            duration_nights=duration_days - 1,
            price=random.randint(variant[1], variant[2]),
            rating=round(random.uniform(4.0, 4.9), 1),
            description=package_info["description"],
            itinerary=package_info["itinerary"],
            image_url=random.choice(IMAGES),
            inclusions=variant[3],
            things_to_carry=variant[4],
            is_active=True,
        )

        created += 1

print("Packages Created:", created)
