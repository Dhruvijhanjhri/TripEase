from django.contrib import admin
from .models import Airport, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country')
    list_filter = ('country', 'city')
    search_fields = ('code', 'name', 'city')
    ordering = ('city', 'name')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'source', 'destination', 'departure_time', 'arrival_time', 'available_seats', 'is_non_stop')
    list_filter = ('airline', 'is_non_stop', 'source', 'destination', 'departure_time')
    search_fields = ('flight_number', 'airline', 'source__code', 'destination__code')
    date_hierarchy = 'departure_time'
    ordering = ('-departure_time',)
    
    fieldsets = (
        ('Flight Information', {
            'fields': ('flight_number', 'airline', 'source', 'destination', 'is_non_stop')
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time', 'duration_minutes')
        }),
        ('Pricing', {
            'fields': ('economy_price', 'business_price', 'first_class_price')
        }),
        ('Seats', {
            'fields': ('total_seats', 'available_seats')
        }),
    )



