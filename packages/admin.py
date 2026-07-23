from django.contrib import admin
from .models import TravelPackage, PackageBooking


@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "destination",
        "package_type",
        "price",
        "rating",
        "is_active",
    )

    search_fields = ("name", "destination")

    list_filter = ("package_type", "is_active")


@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):

    list_display = ("booking_reference", "user", "package", "booking_status")

    list_filter = ("booking_status",)
