from django.contrib import admin
from .models import Airport, Flight
from .models import PriceAlert

admin.site.register(PriceAlert)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):

    list_display = ("code", "city", "name")

    search_fields = ("code", "city", "name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):

    list_display = (
        "airline",
        "flight_number",
        "source",
        "destination",
        "duration_minutes",
    )

    search_fields = ("airline", "flight_number")

    list_filter = ("airline",)
