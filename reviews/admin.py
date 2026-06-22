from django.contrib import admin

from .models import (
    HotelReview,
    PackageReview
)


admin.site.register(HotelReview)
admin.site.register(PackageReview)