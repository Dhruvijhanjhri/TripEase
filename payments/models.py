from django.db import models
from bookings.models import Booking
from hotels.models import HotelBooking


class Payment(models.Model):
    """Universal Payment Model"""

    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Flight Booking
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )

    # Hotel Booking
    hotel_booking = models.OneToOneField(
        HotelBooking,
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):

        if self.booking:
            return (
                f"Flight Payment - "
                f"{self.booking.booking_reference}"
            )

        elif self.hotel_booking:
            return (
                f"Hotel Payment - "
                f"{self.hotel_booking.booking_reference}"
            )

        return "Payment"