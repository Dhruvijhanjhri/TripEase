from django.contrib import admin
from .models import Booking, Passenger


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'flight', 'cabin_class', 'number_of_passengers', 'total_price', 'booking_status', 'created_at')
    list_filter = ('booking_status', 'cabin_class', 'created_at')
    search_fields = ('booking_reference', 'user__email', 'flight__flight_number')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [PassengerInline]
    
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'gender', 'booking')
    list_filter = ('gender', 'booking__booking_status')
    search_fields = ('first_name', 'last_name', 'booking__booking_reference')



