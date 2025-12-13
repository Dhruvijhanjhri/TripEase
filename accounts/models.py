from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    email = models.EmailField(unique=True, verbose_name='email address')
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    id_document = models.FileField(upload_to='id_documents/', blank=True, null=True)
    user_id = models.UUIDField(null=True, blank=True, unique=True, editable=False, help_text='Supabase Auth user ID (UUID)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email or self.username

    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

