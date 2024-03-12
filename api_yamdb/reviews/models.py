from django.db import models
from django.db.models import CheckConstraint, Q
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import BaseUserManager

from api.constants import MAX_SCORE_VALUE, MIN_SCORE_VALUE
from .validators import validate_year


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, role='user',
                    bio=None, confirmation_code=None, password=None):
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            role=role,
            bio=bio,
            confirmation_code=confirmation_code
        )
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):

        if password is None:
            raise TypeError('Password is required.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.role = 'admin'
        user.save()
        return user


class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )

    confirmation_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Код подтверждения'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Биография'
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            CheckConstraint(
                check=~Q(username='me'), name='username_me_banned_word'
            )
        ]
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
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
    rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Рейтинг'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение"
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(MAX_SCORE_VALUE),
            MinValueValidator(MIN_SCORE_VALUE)
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('author', 'title')

    def str(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = 'comments'

    def str(self):
        return self.text
