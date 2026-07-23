from django.db import models
from django.conf import settings
import uuid


class TravelPackage(models.Model):

    PACKAGE_TYPES = [
        ("beach", "Beach"),
        ("hill_station", "Hill Station"),
        ("adventure", "Adventure"),
        ("honeymoon", "Honeymoon"),
        ("family", "Family"),
        ("wildlife", "Wildlife"),
        ("pilgrimage", "Pilgrimage"),
        ("heritage", "Heritage"),
        ("luxury", "Luxury"),
    ]

    name = models.CharField(max_length=255)

    destination = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    package_type = models.CharField(max_length=30, choices=PACKAGE_TYPES)

    duration_days = models.IntegerField()

    duration_nights = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)

    description = models.TextField()

    itinerary = models.TextField()

    image_url = models.URLField(blank=True)

    inclusions = models.TextField(blank=True)

    things_to_carry = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["destination", "name"]

    def __str__(self):
        return self.name


class PackageBooking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    booking_reference = models.CharField(max_length=12, unique=True, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE)

    travel_date = models.DateField()

    travellers_count = models.IntegerField(default=1)

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    booking_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.booking_reference:

            self.booking_reference = str(uuid.uuid4()).replace("-", "")[:10].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_reference


class PackageTraveller(models.Model):

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    booking = models.ForeignKey(
        PackageBooking, on_delete=models.CASCADE, related_name="travellers"
    )

    full_name = models.CharField(max_length=100)

    age = models.IntegerField()

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name
