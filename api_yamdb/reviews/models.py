from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_year


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год релиза'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


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
        max_length=254,
        unique=True
    )
    role = models.CharField(
        max_length=20, 
        choices=USER_ROLE_CHOICES, 
        default='user'
    )
    bio = models.TextField(blank=True)
