from django.db import models
from django.conf import settings


class TripPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    destination = models.CharField(max_length=100)
    budget = models.IntegerField()
    days = models.IntegerField()
    interests = models.TextField()

    generated_plan = models.TextField(blank=True)

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    recommended_hotels = models.TextField(
        blank=True,
        help_text="Comma separated hotel IDs"
    )

    recommended_packages = models.TextField(
        blank=True,
        help_text="Comma separated package IDs"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.destination}"