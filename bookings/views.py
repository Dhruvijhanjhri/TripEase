from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from flights.models import Flight
from .models import Booking, Passenger
from .forms import PassengerFormSet


@login_required
def create_booking(request, flight_id):
    """Create booking view"""
    flight = get_object_or_404(Flight, id=flight_id)
    cabin_class = request.GET.get('cabin_class', 'economy')
    passengers = int(request.GET.get('passengers', 1))
    
    price = flight.get_price(cabin_class)
    total_price = price * passengers
    
    if request.method == 'POST':
        formset = PassengerFormSet(request.POST)
        
        if formset.is_valid():
            # Check seat availability
            if flight.available_seats < passengers:
                messages.error(request, 'Not enough seats available.')
                return redirect('flights:detail', flight_id=flight_id)
            
            try:
                with transaction.atomic():
                    # Create booking
                    booking = Booking.objects.create(
                        user=request.user,
                        flight=flight,
                        cabin_class=cabin_class,
                        number_of_passengers=passengers,
                        total_price=total_price,
                        booking_status='pending'
                    )
                    
                    # Create passengers
                    for form in formset:
                        if form.cleaned_data:
                            Passenger.objects.create(
                                booking=booking,
                                **form.cleaned_data
                            )
                    
                    # Update available seats
                    flight.available_seats -= passengers
                    flight.save()
                    
                    messages.success(request, f'Booking created successfully! Reference: {booking.booking_reference}')
                    return redirect('bookings:detail', booking_id=booking.id)
                    
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
    else:
        # Pre-populate formset with number of passengers
        formset = PassengerFormSet(initial=[{} for _ in range(passengers)])
    
    context = {
        'flight': flight,
        'cabin_class': cabin_class,
        'passengers': passengers,
        'price': price,
        'total_price': total_price,
        'formset': formset,
    }
    
    return render(request, 'bookings/create.html', context)


@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'bookings/detail.html', context)


@login_required
def booking_list(request):
    """User's booking list"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    
    return render(request, 'bookings/list.html', context)


