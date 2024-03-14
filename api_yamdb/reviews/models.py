from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import MAX_SCORE_VALUE, MIN_SCORE_VALUE, TEXT_FIELD_LENGTH
from reviews.validators import validate_year
from users.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Name'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Name'
    )
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'genres'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Name'
    )
    year = models.SmallIntegerField(
        validators=(validate_year,),
        verbose_name='Release year'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Category',
        null=True,
        blank=True
    )
    description = models.TextField(
        max_length=TEXT_FIELD_LENGTH,
        null=True,
        blank=True,
        verbose_name='Description'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Genre'
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Rating'
    )

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'titles'
        ordering = ('name',)

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
        verbose_name='Title'
    )
    text = models.TextField(verbose_name='Review text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Author'
    )
    score = models.PositiveSmallIntegerField(
        validators=(
            MaxValueValidator(MAX_SCORE_VALUE),
            MinValueValidator(MIN_SCORE_VALUE)
        ),
        verbose_name='Review rating'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique review'
            )
        ]
        ordering = ('pub_date',)
        default_related_name = 'reviews'

    def str(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Review'
    )
    text = models.TextField(verbose_name='Comment text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        default_related_name = 'comments'
        ordering = ('pub_date',)

    def str(self):
        return self.text
