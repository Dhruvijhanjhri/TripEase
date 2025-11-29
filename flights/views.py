from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Flight, Airport
from .forms import FlightSearchForm


def flight_search(request):
    """Flight search view"""
    form = FlightSearchForm(request.GET or None)
    flights = Flight.objects.none()
    
    if form.is_valid():
        source = form.cleaned_data['source']
        destination = form.cleaned_data['destination']
        departure_date = form.cleaned_data['departure_date']
        cabin_class = form.cleaned_data.get('cabin_class', 'economy')
        passengers = form.cleaned_data.get('passengers', 1)
        
        # Filter flights
        flights_list = Flight.objects.filter(
            source=source,
            destination=destination,
            departure_time__date=departure_date,
            available_seats__gte=passengers,
            departure_time__gte=timezone.now()
        ).order_by('departure_time')
        
        # Add price to each flight for template
        flights_with_price = []
        for flight in flights_list:
            flight.price = flight.get_price(cabin_class)
            flights_with_price.append(flight)
        
        context = {
            'form': form,
            'flights': flights_with_price,
            'cabin_class': cabin_class,
            'passengers': passengers,
            'search_performed': True,
        }
    else:
        context = {
            'form': form,
            'flights': flights,
            'search_performed': False,
        }
    
    return render(request, 'flights/search.html', context)


def flight_detail(request, flight_id):
    """Flight detail view"""
    flight = get_object_or_404(Flight, id=flight_id)
    cabin_class = request.GET.get('cabin_class', 'economy')
    passengers = int(request.GET.get('passengers', 1))
    
    price = flight.get_price(cabin_class)
    total_price = price * passengers
    
    context = {
        'flight': flight,
        'cabin_class': cabin_class,
        'passengers': passengers,
        'price': price,
        'total_price': total_price,
    }
    
    return render(request, 'flights/detail.html', context)

