from django.db import models
from django.contrib.auth import get_user_model
from flights.models import Flight
from datetime import timedelta

User = get_user_model()


class Passenger(models.Model):
    """Passenger information model"""

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    booking = models.ForeignKey(
        "Booking", on_delete=models.CASCADE, related_name="passengers"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    seat_number = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    """Booking model"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")

    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="bookings"
    )

    cabin_class = models.CharField(max_length=20)

    number_of_passengers = models.IntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    travel_date = models.DateField(null=True, blank=True)

    booking_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    booking_reference = models.CharField(max_length=20, unique=True)

    # ----------------------------
    # Flight Check-in
    # ----------------------------

    checked_in = models.BooleanField(default=False)

    checked_in_at = models.DateTimeField(null=True, blank=True)

    terminal = models.CharField(max_length=10, blank=True, null=True)

    gate = models.CharField(max_length=10, blank=True, null=True)

    boarding_time = models.DateTimeField(blank=True, null=True)

    second_flight = models.ForeignKey(
        Flight,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connecting_bookings",
    )

    boarding_pass = models.FileField(
        upload_to="boarding_passes/", blank=True, null=True
    )

    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random
            import string

            self.booking_reference = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )

        super().save(*args, **kwargs)

    @property
    def journey_origin(self):
        return self.flight.source.city

    @property
    def journey_destination(self):
        if self.second_flight:
            return self.second_flight.destination.city
        return self.flight.destination.city

    @property
    def via_city(self):
        if self.second_flight:
            return self.flight.destination.city
        return None

    @property
    def journey_route(self):

        return f"{self.journey_origin} → " f"{self.journey_destination}"

    @property
    def journey_route_with_via(self):

        if self.second_flight:

            return (
                f"{self.journey_origin} → "
                f"{self.via_city} → "
                f"{self.journey_destination}"
            )

        return self.journey_route

    @property
    def total_journey_duration(self):

        if not self.second_flight:
            return timedelta(minutes=self.flight.duration_minutes)

        flight1 = timedelta(minutes=self.flight.duration_minutes)

        flight2 = timedelta(minutes=self.second_flight.duration_minutes)

        layover = self.second_flight.departure_time - self.flight.arrival_time

        return flight1 + layover + flight2

    @property
    def total_duration_display(self):

        duration = self.total_journey_duration

        total_minutes = int(duration.total_seconds() // 60)

        hours = total_minutes // 60

        minutes = total_minutes % 60

        return f"{hours}h {minutes}m"

    cancelled_at = models.DateTimeField(null=True, blank=True)

    cancellation_reason = models.TextField(blank=True)

    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
