from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q

from users.consants import (CONFIRMATION_CODE_LENGHT, EMAIL_FIELD_LENGHT,
                            ROLE_FIELD_LENGHT, USER_ROLE_NAME,
                            MODERATOR_ROLE_NAME, ADMIN_ROLE_NAME)


class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ('user', USER_ROLE_NAME),
        ('moderator', MODERATOR_ROLE_NAME),
        ('admin', ADMIN_ROLE_NAME),
    )

    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGHT,
        null=True,
        blank=True,
        verbose_name='Confirmation code'
    )
    email = models.EmailField(
        max_length=EMAIL_FIELD_LENGHT,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Email addres'
    )
    role = models.CharField(
        max_length=ROLE_FIELD_LENGHT,
        choices=USER_ROLE_CHOICES,
        default='user',
        verbose_name='Rola'
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='User biography'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            CheckConstraint(
                check=~Q(username='me'), name='username_me_banned_word'
            )
        ]
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username
