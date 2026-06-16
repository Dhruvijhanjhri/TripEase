from hotels.models import Hotel, Room
from datetime import time
import random

Hotel.objects.all().delete()

city_hotels = {
    "Delhi": [
        ("Taj Palace Delhi", "Diplomatic Enclave"),
        ("The Leela Palace New Delhi", "Chanakyapuri"),
        ("ITC Maurya", "Chanakyapuri"),
    ],

    "Mumbai": [
        ("The Taj Mahal Palace", "Colaba"),
        ("The Oberoi Mumbai", "Nariman Point"),
        ("Trident Nariman Point", "Marine Drive"),
    ],

    "Bengaluru": [
        ("Taj West End Bengaluru", "Race Course Road"),
        ("The Oberoi Bengaluru", "MG Road"),
        ("ITC Gardenia", "Residency Road"),
    ],

    "Hyderabad": [
        ("Taj Falaknuma Palace", "Falaknuma"),
        ("ITC Kohenur", "Hitech City"),
        ("Park Hyatt Hyderabad", "Banjara Hills"),
    ],

    "Chennai": [
        ("ITC Grand Chola", "Guindy"),
        ("Taj Club House", "Anna Salai"),
        ("The Leela Palace Chennai", "MRC Nagar"),
    ],

    "Kolkata": [
        ("ITC Royal Bengal", "EM Bypass"),
        ("The Oberoi Grand", "New Market"),
        ("Taj Bengal", "Alipore"),
    ],

    "Pune": [
        ("JW Marriott Pune", "Senapati Bapat Road"),
        ("Conrad Pune", "Bund Garden"),
        ("The Westin Pune", "Koregaon Park"),
    ],

    "Indore": [
        ("Radisson Blu Indore", "Ring Road"),
        ("Sayaji Indore", "Vijay Nagar"),
        ("Marriott Indore", "MR10 Road"),
    ],

    "Mysore": [
        ("Royal Orchid Metropole", "Jhansi Lakshmibai Road"),
        ("Fortune JP Palace", "Nazarbad"),
        ("Radisson Blu Mysore", "MG Road"),
    ],

    "Goa": [
        ("Taj Exotica Goa", "Benaulim"),
        ("W Goa", "Vagator"),
        ("Grand Hyatt Goa", "Bambolim"),
    ],

    "Jaipur": [
        ("Rambagh Palace", "Bhawani Singh Road"),
        ("ITC Rajputana", "Palace Road"),
        ("Holiday Inn Jaipur", "Tonk Road"),
    ],

    "Udaipur": [
        ("The Oberoi Udaivilas", "Lake Pichola"),
        ("Taj Fateh Prakash", "City Palace"),
        ("Trident Udaipur", "Haridasji Ki Magri"),
    ],
}

hotel_images = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=1200",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=1200",
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200",
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1200",
]

room_types = [
    ("standard", "Standard Room"),
    ("deluxe", "Deluxe Room"),
    ("suite", "Luxury Suite"),
]

for city, hotels in city_hotels.items():

    for name, area in hotels:

        hotel = Hotel.objects.create(
            name=name,
            city=city,
            state="India",
            area=area,
            address=f"{area}, {city}",
            description=f"Luxury stay in {city}",
            search_keywords=f"{city.lower()}, {city.lower().replace('bengaluru','bangalore')}",
            star_rating=random.choice([4.0, 4.5, 5.0]),
            user_rating=round(random.uniform(4.0, 4.9), 1),
            total_reviews=random.randint(500, 12000),
            image_url=random.choice(hotel_images),
            breakfast_available=True,
            free_cancellation=True,
            couple_friendly=True,
            check_in_time=time(12, 0),
            check_out_time=time(11, 0),
        )

        for room_type, room_name in room_types:

            Room.objects.create(
                hotel=hotel,
                room_type=room_type,
                room_name=room_name,
                max_guests=random.randint(2, 5),
                total_rooms=20,
                available_rooms=random.randint(3, 15),
                room_size=random.randint(200, 600),
                price_per_night=random.randint(3500, 20000),
                breakfast_included=True,
                refundable=True,
                free_cancellation=True,
                ac=True,
                wifi=True,
                tv=True,
            )

print("Hotels Added Successfully")

