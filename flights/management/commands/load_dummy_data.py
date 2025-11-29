"""
Django management command to load dummy data for Indian airports and flights
Usage: python manage.py load_dummy_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from flights.models import Airport, Flight
import random


class Command(BaseCommand):
    help = 'Loads dummy data for Indian airports and flights'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load dummy data...'))
        
        # Indian Airports Data
        airports_data = [
            {'code': 'BLR', 'name': 'Kempegowda International Airport', 'city': 'Bengaluru'},
            {'code': 'DEL', 'name': 'Indira Gandhi International Airport', 'city': 'Delhi'},
            {'code': 'BOM', 'name': 'Chhatrapati Shivaji Maharaj International Airport', 'city': 'Mumbai'},
            {'code': 'CCU', 'name': 'Netaji Subhas Chandra Bose International Airport', 'city': 'Kolkata'},
            {'code': 'MAA', 'name': 'Chennai International Airport', 'city': 'Chennai'},
            {'code': 'HYD', 'name': 'Rajiv Gandhi International Airport', 'city': 'Hyderabad'},
            {'code': 'PNQ', 'name': 'Pune Airport', 'city': 'Pune'},
            {'code': 'GOI', 'name': 'Dabolim Airport', 'city': 'Goa'},
            {'code': 'JAI', 'name': 'Jaipur International Airport', 'city': 'Jaipur'},
            {'code': 'AMD', 'name': 'Sardar Vallabhbhai Patel International Airport', 'city': 'Ahmedabad'},
            {'code': 'COK', 'name': 'Cochin International Airport', 'city': 'Kochi'},
            {'code': 'IXC', 'name': 'Chandigarh Airport', 'city': 'Chandigarh'},
        ]
        
        # Airlines
        airlines = [
            'Air India',
            'IndiGo',
            'SpiceJet',
            'Vistara',
            'Go First',
            'AirAsia India',
            'Alliance Air',
        ]
        
        # Create Airports
        airports_dict = {}
        for airport_data in airports_data:
            airport, created = Airport.objects.get_or_create(
                code=airport_data['code'],
                defaults={
                    'name': airport_data['name'],
                    'city': airport_data['city'],
                    'country': 'India'
                }
            )
            airports_dict[airport_data['code']] = airport
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created airport: {airport}'))
            else:
                self.stdout.write(self.style.WARNING(f'Airport already exists: {airport}'))
        
        # Create Flights
        flight_count = 0
        airport_codes = list(airports_dict.keys())
        
        # Generate flights for the next 30 days
        for day in range(30):
            current_date = timezone.now().date() + timedelta(days=day)
            
            # Create 3-5 flights per day between major routes
            major_routes = [
                ('BLR', 'DEL'), ('DEL', 'BLR'),
                ('BOM', 'DEL'), ('DEL', 'BOM'),
                ('BLR', 'BOM'), ('BOM', 'BLR'),
                ('CCU', 'DEL'), ('DEL', 'CCU'),
                ('MAA', 'DEL'), ('DEL', 'MAA'),
                ('HYD', 'BLR'), ('BLR', 'HYD'),
                ('PNQ', 'DEL'), ('DEL', 'PNQ'),
                ('GOI', 'BOM'), ('BOM', 'GOI'),
                ('JAI', 'DEL'), ('DEL', 'JAI'),
                ('AMD', 'BOM'), ('BOM', 'AMD'),
            ]
            
            # Add some random routes too
            for _ in range(10):
                source = random.choice(airport_codes)
                destination = random.choice([c for c in airport_codes if c != source])
                major_routes.append((source, destination))
            
            # Create flights for major routes
            for source_code, dest_code in major_routes[:15]:  # Limit to 15 routes per day
                source = airports_dict[source_code]
                destination = airports_dict[dest_code]
                
                # Skip if same airport
                if source == destination:
                    continue
                
                # Create 1-2 flights per route per day
                num_flights = random.randint(1, 2)
                
                for flight_num in range(num_flights):
                    # Random departure time between 6 AM and 10 PM
                    hour = random.randint(6, 22)
                    minute = random.choice([0, 15, 30, 45])
                    
                    departure_time = timezone.make_aware(
                        datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
                    )
                    
                    # Flight duration between 1.5 to 3.5 hours
                    duration_minutes = random.randint(90, 210)
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)
                    
                    # Prices (in INR)
                    base_price = random.randint(3000, 8000)
                    economy_price = base_price
                    business_price = int(base_price * 2.5)
                    first_class_price = int(base_price * 5)
                    
                    # Flight number - make it unique by including date and route
                    airline = random.choice(airlines)
                    airline_code = airline[:2].upper() if len(airline) >= 2 else 'AI'
                    route_code = f"{source_code}{dest_code}"
                    flight_num = random.randint(100, 999)
                    flight_number = f"{airline_code}-{flight_num}-{route_code}-{day}"
                    
                    # Check if flight already exists
                    if Flight.objects.filter(
                        flight_number=flight_number
                    ).exists():
                        continue
                    
                    # Seats
                    total_seats = random.choice([120, 150, 180, 200])
                    available_seats = random.randint(int(total_seats * 0.3), total_seats)
                    
                    # Non-stop or with stop
                    is_non_stop = random.choice([True, True, True, False])  # 75% non-stop
                    
                    flight = Flight.objects.create(
                        flight_number=flight_number,
                        airline=airline,
                        source=source,
                        destination=destination,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration_minutes=duration_minutes,
                        economy_price=economy_price,
                        business_price=business_price,
                        first_class_price=first_class_price,
                        total_seats=total_seats,
                        available_seats=available_seats,
                        is_non_stop=is_non_stop
                    )
                    
                    flight_count += 1
                    if flight_count % 50 == 0:
                        self.stdout.write(f'Created {flight_count} flights...')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully loaded dummy data!\n'
            f'- Airports: {len(airports_dict)}\n'
            f'- Flights: {flight_count}\n'
        ))

