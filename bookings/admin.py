from django.contrib import admin
from .models import Booking, Passenger


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = ("booking_reference", "user", "flight", "booking_status")

    list_filter = ("booking_status",)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):

    list_display = ("first_name", "last_name", "age", "gender", "seat_number")

    search_fields = ("first_name", "last_name", "seat_number")
