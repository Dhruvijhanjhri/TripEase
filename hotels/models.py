from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Hotel(models.Model):
    """Hotel Model"""

    HOTEL_TYPE_CHOICES = [
        ("luxury", "Luxury"),
        ("budget", "Budget"),
        ("business", "Business"),
        ("resort", "Resort"),
        ("boutique", "Boutique"),
    ]

    PROPERTY_TYPE_CHOICES = [
        ("hotel", "Hotel"),
        ("resort", "Resort"),
        ("villa", "Villa"),
        ("homestay", "Homestay"),
        ("apartment", "Apartment"),
    ]

    name = models.CharField(max_length=255)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    area = models.CharField(max_length=150, blank=True, null=True)

    search_keywords = models.TextField(
        help_text="Search aliases like bangalore,bengaluru,blr"
    )

    address = models.TextField()

    description = models.TextField(blank=True)

    hotel_type = models.CharField(
        max_length=20, choices=HOTEL_TYPE_CHOICES, default="budget"
    )

    property_type = models.CharField(
        max_length=20, choices=PROPERTY_TYPE_CHOICES, default="hotel"
    )

    star_rating = models.DecimalField(max_digits=2, decimal_places=1, default=3.5)

    user_rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)

    total_reviews = models.IntegerField(default=0)

    image_url = models.URLField(blank=True)

    check_in_time = models.TimeField()
    check_out_time = models.TimeField()

    latitude = models.FloatField(blank=True, null=True)

    longitude = models.FloatField(blank=True, null=True)

    # Amenities
    free_wifi = models.BooleanField(default=True)
    swimming_pool = models.BooleanField(default=False)
    spa = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    parking = models.BooleanField(default=True)
    restaurant = models.BooleanField(default=True)
    airport_shuttle = models.BooleanField(default=False)
    pet_friendly = models.BooleanField(default=False)

    breakfast_available = models.BooleanField(default=False)
    couple_friendly = models.BooleanField(default=True)
    free_cancellation = models.BooleanField(default=False)
    pay_at_hotel = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-star_rating", "-user_rating"]

    def __str__(self):
        return f"{self.name} - {self.city}"


class Room(models.Model):
    """Hotel Room Model"""

    ROOM_TYPE_CHOICES = [
        ("standard", "Standard Room"),
        ("deluxe", "Deluxe Room"),
        ("suite", "Suite"),
        ("family", "Family Room"),
        ("executive", "Executive Room"),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")

    room_type = models.CharField(max_length=30, choices=ROOM_TYPE_CHOICES)

    room_name = models.CharField(max_length=200)

    max_guests = models.IntegerField(default=2)

    total_rooms = models.IntegerField(default=10)

    available_rooms = models.IntegerField(default=10)

    room_size = models.IntegerField(help_text="Room size in sqft", default=200)

    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))]
    )

    extra_bed_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    breakfast_included = models.BooleanField(default=False)

    refundable = models.BooleanField(default=False)

    free_cancellation = models.BooleanField(default=False)

    ac = models.BooleanField(default=True)
    tv = models.BooleanField(default=True)
    wifi = models.BooleanField(default=True)

    room_image = models.URLField(blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_name}"


class HotelBooking(models.Model):
    """Hotel Booking"""

    BOOKING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    booking_reference = models.CharField(max_length=12, unique=True, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    check_in_date = models.DateField()

    check_out_date = models.DateField()

    # total guests in booking
    guests = models.IntegerField(default=1)

    # number of rooms booked
    rooms_count = models.IntegerField(default=1)

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    booking_status = models.CharField(
        max_length=20, choices=BOOKING_STATUS_CHOICES, default="pending"
    )

    special_request = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # generate booking reference
        if not self.booking_reference:
            self.booking_reference = str(uuid.uuid4()).replace("-", "")[:10].upper()

        # validate guest capacity
        max_capacity = self.room.max_guests * self.rooms_count

        if self.guests > max_capacity:
            raise ValueError(
                f"Maximum {max_capacity} guests allowed "
                f"for {self.rooms_count} room(s)"
            )

        super().save(*args, **kwargs)

    @property
    def total_nights(self):
        return (self.check_out_date - self.check_in_date).days

    @property
    def max_guest_capacity(self):
        return self.room.max_guests * self.rooms_count

    def __str__(self):
        return f"{self.booking_reference}"


class HotelGuest(models.Model):
    """Guest Details"""

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    booking = models.ForeignKey(
        HotelBooking, on_delete=models.CASCADE, related_name="guests_details"
    )

    full_name = models.CharField(max_length=100)

    age = models.IntegerField()

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name
