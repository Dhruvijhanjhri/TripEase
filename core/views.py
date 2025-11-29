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

