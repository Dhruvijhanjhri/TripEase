from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from hotels.models import Hotel
from packages.models import TravelPackage
from flights.models import Flight


class HotelReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    review_text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "hotel")

    def __str__(self):
        return f"{self.user} - {self.hotel.name}"


class PackageReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    package = models.ForeignKey(
        TravelPackage,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    review_text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "package")

    def __str__(self):
        return f"{self.user} - {self.package.name}"


class FlightReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    review_text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "flight")

    def __str__(self):
        return f"{self.user} - {self.flight.flight_number}"