from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Airport(models.Model):
    """Airport model"""
    code = models.CharField(max_length=3, unique=True, help_text="IATA code (e.g., BLR, DEL)")
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}, {self.city}"


class Flight(models.Model):
    """Flight model"""
    CABIN_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    flight_number = models.CharField(max_length=20, unique=True)
    airline = models.CharField(max_length=100)
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration_minutes = models.IntegerField(help_text="Flight duration in minutes")
    economy_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    business_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    first_class_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_seats = models.IntegerField(default=180, validators=[MinValueValidator(1)])
    available_seats = models.IntegerField(default=180, validators=[MinValueValidator(0)])
    is_non_stop = models.BooleanField(default=True, help_text="Non-stop flight")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['departure_time']

    def __str__(self):
        return f"{self.flight_number} - {self.source.code} to {self.destination.code}"

    def get_price(self, cabin_class):
        """Get price for specific cabin class"""
        price_map = {
            'economy': self.economy_price,
            'business': self.business_price,
            'first': self.first_class_price,
        }
        return price_map.get(cabin_class, self.economy_price)

    def get_duration_display(self):
        """Get formatted duration string"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"

