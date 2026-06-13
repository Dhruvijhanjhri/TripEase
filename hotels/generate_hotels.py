from hotels.models import Hotel, Room
from datetime import time
import random

print("Deleting old hotels...")
Room.objects.all().delete()
Hotel.objects.all().delete()

# Major India cities
india_locations = {
    "Ahmedabad": "Gujarat",
    "Bengaluru": "Karnataka",
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Pune": "Maharashtra",
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Jaipur": "Rajasthan",
    "Goa": "Goa",
    "Lucknow": "Uttar Pradesh",
    "Indore": "Madhya Pradesh",
    "Bhopal": "Madhya Pradesh",
    "Kochi": "Kerala",
    "Srinagar": "Jammu & Kashmir",
    "Jammu": "Jammu & Kashmir",
    "Leh": "Ladakh",
    "Chandigarh": "Chandigarh",
    "Nagpur": "Maharashtra",
    "Patna": "Bihar",
    "Guwahati": "Assam",
    "Mangalore": "Karnataka",
    "Mysore": "Karnataka",
    "Udaipur": "Rajasthan",
    "Agra": "Uttar Pradesh",
    "Varanasi": "Uttar Pradesh",
    "Ranchi": "Jharkhand",
    "Bhubaneswar": "Odisha",
    "Imphal": "Manipur",
    "Madurai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Port Blair": "Andaman & Nicobar",
    "Thiruvananthapuram": "Kerala",
    "Amritsar": "Punjab",
    "Shimla": "Himachal Pradesh",
    "Manali": "Himachal Pradesh",
    "Darjeeling": "West Bengal",
    "Gangtok": "Sikkim",
    "Ooty": "Tamil Nadu",
    "Nainital": "Uttarakhand",
}

areas = [
    "City Center",
    "Railway Station Area",
    "Airport Road",
    "MG Road",
    "Business District",
    "Mall Road",
    "Beach Road",
    "Tourist Area",
    "Civil Lines",
]

hotel_prefix = [
    "The Grand",
    "Royal",
    "Elite",
    "Blue Orchid",
    "Hotel",
    "Regency",
    "Comfort",
    "Urban Stay",
    "Luxury Inn",
    "Skyline",
]

hotel_suffix = [
    "Residency",
    "Suites",
    "Palace",
    "Inn",
    "Retreat",
    "Heights",
    "Plaza",
    "Stay",
]

hotel_images = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
]

room_images = [
    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461",
]

created = 0

print("Generating hotels...")

for city, state in india_locations.items():

    hotel_count = random.randint(20, 50)

    for _ in range(hotel_count):

        hotel_name = (
            random.choice(hotel_prefix)
            + " "
            + city
            + " "
            + random.choice(hotel_suffix)
        )

        hotel = Hotel.objects.create(
            name=hotel_name,
            city=city,
            state=state,
            area=random.choice(areas),
            search_keywords=f"{city.lower()},{state.lower()}",
            address=f"{random.randint(1,200)} Main Road, {city}",
            description=f"Comfortable stay in {city}",
            hotel_type=random.choice([
                'luxury',
                'budget',
                'business',
                'resort'
            ]),
            property_type=random.choice([
                'hotel',
                'resort',
                'villa',
                'apartment'
            ]),
            star_rating=random.choice([
                3.0,
                3.5,
                4.0,
                4.5,
                5.0
            ]),
            user_rating=round(
                random.uniform(3.5, 4.9),
                1
            ),
            total_reviews=random.randint(
                100,
                15000
            ),
            image_url=random.choice(
                hotel_images
            ),
            check_in_time=time(12, 0),
            check_out_time=time(11, 0),

            free_wifi=True,
            swimming_pool=random.choice([True, False]),
            spa=random.choice([True, False]),
            gym=random.choice([True, False]),
            parking=True,
            restaurant=True,
            airport_shuttle=random.choice([True, False]),
            pet_friendly=random.choice([True, False]),
            breakfast_available=random.choice([True, False]),
            couple_friendly=random.choice([True, False]),
            free_cancellation=random.choice([True, False]),
            pay_at_hotel=random.choice([True, False]),
        )

        room_types = [
            "Standard Room",
            "Deluxe Room",
            "Executive Room",
            "Suite Room",
        ]

        for room_name in room_types:

            price = random.randint(
                1500,
                15000
            )

            Room.objects.create(
                hotel=hotel,
                room_type='deluxe',
                room_name=room_name,
                max_guests=random.randint(2, 5),
                total_rooms=random.randint(10, 50),
                available_rooms=random.randint(5, 30),
                room_size=random.randint(180, 600),
                price_per_night=price,
                extra_bed_price=random.randint(
                    500,
                    2500
                ),
                breakfast_included=random.choice(
                    [True, False]
                ),
                refundable=random.choice(
                    [True, False]
                ),
                free_cancellation=random.choice(
                    [True, False]
                ),
                room_image=random.choice(
                    room_images
                ),
            )

        created += 1

        if created % 100 == 0:
            print(f"Created {created} hotels...")

print("Done!")
print("Hotels:", Hotel.objects.count())
print("Rooms:", Room.objects.count())