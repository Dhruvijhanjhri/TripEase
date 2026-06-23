from django.contrib import admin
from .models import (
    Hotel,
    Room,
    HotelBooking
)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'city',
        'star_rating'
    )

    search_fields = (
        'name',
        'city'
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'hotel',
        'room_name',
        'price_per_night',
        'available_rooms'
    )

    search_fields = (
        'hotel__name',
        'room_name'
    )


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):

    list_display = (
        'booking_reference',
        'user',
        'hotel',
        'booking_status'
    )

    list_filter = (
        'booking_status',
    )