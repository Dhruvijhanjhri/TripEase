from django.shortcuts import render
from django.utils import timezone
from flights.models import Airport

def home(request):
    """Home page view"""
    airports = Airport.objects.all().order_by('city', 'name')
    context = {
        'airports': airports,
        'today': timezone.now().date(),
    }
    return render(request, 'core/home.html', context)


def hotels_search(request):
    """Hotel search view"""
    # Dummy hotel data
    cities = [
        {'name': 'Delhi', 'code': 'DEL'},
        {'name': 'Mumbai', 'code': 'BOM'},
        {'name': 'Bengaluru', 'code': 'BLR'},
        {'name': 'Kolkata', 'code': 'CCU'},
        {'name': 'Chennai', 'code': 'MAA'},
        {'name': 'Hyderabad', 'code': 'HYD'},
        {'name': 'Pune', 'code': 'PNQ'},
        {'name': 'Goa', 'code': 'GOI'},
        {'name': 'Jaipur', 'code': 'JAI'},
        {'name': 'Indore', 'code': 'IDR'},
    ]
    
    city = request.GET.get('city', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    guests = request.GET.get('guests', '1')
    
    # Dummy hotels list
    hotels = []
    if city:
        hotel_names = [
            'Grand Plaza Hotel',
            'Royal Heritage Resort',
            'City Center Inn',
            'Luxury Suites',
            'Comfort Stay Hotel',
            'Business Tower Hotel',
            'Riverside Retreat',
            'Mountain View Lodge',
        ]
        
        for i, name in enumerate(hotel_names[:6]):  # Show 6 hotels
            hotels.append({
                'id': i + 1,
                'name': name,
                'city': city,
                'rating': round(3.5 + (i * 0.3), 1),
                'price_per_night': 1500 + (i * 500),
                'image': f'images/{7 + (i % 3)}.jpg',  # Use existing images
                'amenities': ['WiFi', 'Pool', 'Restaurant', 'Spa', 'Gym'][:3 + (i % 3)],
                'description': f'Comfortable stay in the heart of {city} with modern amenities and excellent service.',
            })
    
    context = {
        'cities': cities,
        'hotels': hotels,
        'city': city,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'today': timezone.now().date(),
    }
    return render(request, 'core/hotels_search.html', context)


def hotel_detail(request, hotel_id):
    """Hotel detail view"""
    # Dummy hotel detail
    hotel = {
        'id': hotel_id,
        'name': 'Grand Plaza Hotel',
        'city': request.GET.get('city', 'Delhi'),
        'rating': 4.5,
        'price_per_night': 2500,
        'image': 'images/8.jpg',
        'amenities': ['Free WiFi', 'Swimming Pool', 'Restaurant', 'Spa & Wellness', 'Fitness Center', 'Parking', 'Room Service', '24/7 Front Desk'],
        'description': 'Experience luxury and comfort at Grand Plaza Hotel. Located in the heart of the city, our hotel offers modern amenities, spacious rooms, and exceptional service. Perfect for both business and leisure travelers.',
        'address': '123 Main Street, City Center',
        'phone': '+91 9876543210',
        'check_in': request.GET.get('check_in', ''),
        'check_out': request.GET.get('check_out', ''),
        'guests': request.GET.get('guests', '1'),
    }
    
    context = {
        'hotel': hotel,
    }
    return render(request, 'core/hotel_detail.html', context)


def packages_view(request):
    """Packages/holiday packages view"""
    # Dummy packages data
    packages = [
        {
            'id': 1,
            'name': 'Goa Beach Paradise',
            'destination': 'Goa',
            'duration': '3 Days / 2 Nights',
            'price': 15000,
            'original_price': 18000,
            'discount_amount': 3000,
            'discount_percent': 17,
            'image': 'images/9.jpg',
            'description': 'Experience the sun, sand, and sea in beautiful Goa. Includes beachfront hotel, breakfast, and airport transfers.',
            'highlights': ['Beach Activities', 'Water Sports', 'Nightlife', 'Local Cuisine'],
            'inclusions': ['Hotel Stay', 'Breakfast', 'Airport Transfer', 'Sightseeing'],
        },
        {
            'id': 2,
            'name': 'Rajasthan Royal Heritage',
            'destination': 'Jaipur, Udaipur',
            'duration': '5 Days / 4 Nights',
            'price': 25000,
            'original_price': 30000,
            'discount_amount': 5000,
            'discount_percent': 17,
            'image': 'images/4.png',
            'description': 'Explore the royal palaces and forts of Rajasthan. Visit Jaipur and Udaipur with guided tours.',
            'highlights': ['Palace Tours', 'Fort Visits', 'Cultural Shows', 'Shopping'],
            'inclusions': ['Hotel Stay', 'All Meals', 'Transport', 'Guide', 'Entry Tickets'],
        },
        {
            'id': 3,
            'name': 'Kerala Backwaters',
            'destination': 'Kochi, Alleppey',
            'duration': '4 Days / 3 Nights',
            'price': 20000,
            'original_price': 24000,
            'discount_amount': 4000,
            'discount_percent': 17,
            'image': 'images/3.png',
            'description': 'Cruise through the serene backwaters of Kerala. Stay in houseboats and enjoy authentic South Indian cuisine.',
            'highlights': ['Houseboat Stay', 'Backwater Cruise', 'Spice Plantation', 'Ayurveda'],
            'inclusions': ['Houseboat', 'Hotel Stay', 'All Meals', 'Transport', 'Activities'],
        },
        {
            'id': 4,
            'name': 'Himalayan Adventure',
            'destination': 'Manali, Shimla',
            'duration': '6 Days / 5 Nights',
            'price': 30000,
            'original_price': 35000,
            'discount_amount': 5000,
            'discount_percent': 14,
            'image': 'images/1.png',
            'description': 'Adventure in the mountains with trekking, paragliding, and scenic views of the Himalayas.',
            'highlights': ['Trekking', 'Paragliding', 'Mountain Views', 'Adventure Sports'],
            'inclusions': ['Hotel Stay', 'Breakfast & Dinner', 'Transport', 'Activities', 'Guide'],
        },
        {
            'id': 5,
            'name': 'South India Temple Tour',
            'destination': 'Chennai, Madurai, Rameswaram',
            'duration': '5 Days / 4 Nights',
            'price': 22000,
            'original_price': 27000,
            'discount_amount': 5000,
            'discount_percent': 19,
            'image': 'images/5.png',
            'description': 'Spiritual journey through ancient temples of South India. Visit historic sites and experience local culture.',
            'highlights': ['Temple Visits', 'Cultural Heritage', 'Local Cuisine', 'Photography'],
            'inclusions': ['Hotel Stay', 'Breakfast', 'Transport', 'Guide', 'Temple Entry'],
        },
        {
            'id': 6,
            'name': 'Mumbai City Explorer',
            'destination': 'Mumbai',
            'duration': '3 Days / 2 Nights',
            'price': 12000,
            'original_price': 15000,
            'discount_amount': 3000,
            'discount_percent': 20,
            'image': 'images/2.png',
            'description': 'Discover the vibrant city of Mumbai. Visit Gateway of India, Marine Drive, and enjoy street food.',
            'highlights': ['City Tour', 'Bollywood Tour', 'Street Food', 'Shopping'],
            'inclusions': ['Hotel Stay', 'Breakfast', 'City Tour', 'Transport'],
        },
    ]
    
    # Filter by destination if provided
    destination_filter = request.GET.get('destination', '')
    if destination_filter:
        packages = [p for p in packages if destination_filter.lower() in p['destination'].lower()]
    
    context = {
        'packages': packages,
        'destination_filter': destination_filter,
    }
    return render(request, 'core/packages.html', context)


def package_detail(request, package_id):
    """Package detail view"""
    # Dummy package details
    all_packages = {
        1: {
            'id': 1,
            'name': 'Goa Beach Paradise',
            'destination': 'Goa',
            'duration': '3 Days / 2 Nights',
            'price': 15000,
            'original_price': 18000,
            'discount_amount': 3000,
            'discount_percent': 17,
            'image': 'images/9.jpg',
            'description': 'Experience the sun, sand, and sea in beautiful Goa. This package includes a beachfront hotel stay, daily breakfast, and convenient airport transfers. Perfect for couples and families looking for a relaxing beach vacation.',
            'highlights': ['Beach Activities', 'Water Sports', 'Nightlife', 'Local Cuisine'],
            'inclusions': ['2 Nights Hotel Stay', 'Daily Breakfast', 'Airport Transfer', 'Sightseeing Tour', 'Beach Access'],
            'itinerary': [
                {'day': 'Day 1', 'title': 'Arrival & Beach Time', 'description': 'Arrive in Goa, check-in to hotel, and spend the day at the beach.'},
                {'day': 'Day 2', 'title': 'Water Sports & Sightseeing', 'description': 'Enjoy water sports in the morning, followed by a city tour in the afternoon.'},
                {'day': 'Day 3', 'title': 'Departure', 'description': 'Check-out and transfer to airport.'},
            ],
        },
        2: {
            'id': 2,
            'name': 'Rajasthan Royal Heritage',
            'destination': 'Jaipur, Udaipur',
            'duration': '5 Days / 4 Nights',
            'price': 25000,
            'original_price': 30000,
            'discount_amount': 5000,
            'discount_percent': 17,
            'image': 'images/4.png',
            'description': 'Explore the royal palaces and forts of Rajasthan. Visit the Pink City of Jaipur and the City of Lakes, Udaipur. Includes guided tours, cultural shows, and shopping experiences.',
            'highlights': ['Palace Tours', 'Fort Visits', 'Cultural Shows', 'Shopping'],
            'inclusions': ['4 Nights Hotel Stay', 'All Meals', 'Transport', 'Professional Guide', 'Entry Tickets', 'Cultural Show'],
            'itinerary': [
                {'day': 'Day 1', 'title': 'Arrival in Jaipur', 'description': 'Arrive and check-in. Evening free for local exploration.'},
                {'day': 'Day 2', 'title': 'Jaipur City Tour', 'description': 'Visit Amber Fort, City Palace, and Hawa Mahal.'},
                {'day': 'Day 3', 'title': 'Travel to Udaipur', 'description': 'Transfer to Udaipur, check-in and evening boat ride on Lake Pichola.'},
                {'day': 'Day 4', 'title': 'Udaipur Sightseeing', 'description': 'Visit City Palace, Jagdish Temple, and enjoy cultural show.'},
                {'day': 'Day 5', 'title': 'Departure', 'description': 'Check-out and transfer to airport.'},
            ],
        },
        3: {
            'id': 3,
            'name': 'Kerala Backwaters',
            'destination': 'Kochi, Alleppey',
            'duration': '4 Days / 3 Nights',
            'price': 20000,
            'original_price': 24000,
            'discount_amount': 4000,
            'discount_percent': 17,
            'image': 'images/3.png',
            'description': 'Cruise through the serene backwaters of Kerala. Stay in traditional houseboats and enjoy authentic South Indian cuisine. Visit spice plantations and experience Ayurveda treatments.',
            'highlights': ['Houseboat Stay', 'Backwater Cruise', 'Spice Plantation', 'Ayurveda'],
            'inclusions': ['1 Night Houseboat', '2 Nights Hotel', 'All Meals', 'Transport', 'Activities', 'Ayurveda Session'],
            'itinerary': [
                {'day': 'Day 1', 'title': 'Arrival in Kochi', 'description': 'Arrive in Kochi, check-in and explore Fort Kochi.'},
                {'day': 'Day 2', 'title': 'Houseboat Experience', 'description': 'Transfer to Alleppey and board houseboat for overnight stay.'},
                {'day': 'Day 3', 'title': 'Spice Plantation & Ayurveda', 'description': 'Visit spice plantation and enjoy Ayurveda treatment.'},
                {'day': 'Day 4', 'title': 'Departure', 'description': 'Check-out and transfer to airport.'},
            ],
        },
    }
    
    package = all_packages.get(package_id, all_packages[1])
    
    context = {
        'package': package,
    }
    return render(request, 'core/package_detail.html', context)

