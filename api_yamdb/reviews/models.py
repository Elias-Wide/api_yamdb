from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )

    confirmation_code = models.CharField(
        max_length=20, 
        null=True, 
        blank=True
    )
    email = models.EmailField(
        verbose_name="email_address",
        max_length=255,
        unique=True
    )
    role = models.CharField(
        max_length=20, 
        choices=USER_ROLE_CHOICES, 
        default='user'
    )
    bio = models.TextField(blank=True)
