from django.contrib.auth import admin
from django.contrib import admin, auth
from rest_framework.authtoken.models import TokenProxy as DRFToken

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class TitleInline(admin.StackedInline):
    model = Title
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        TitleInline,
    )
    list_display = (
        'name',
        'slug',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'description',
    )
    list_editable = (
        'category',
    )
    search_fields = ('name',)
    list_filter = ('genre', 'category', 'year')


@admin.register(Review)
class ReviewtAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'score',
        'pub_date'
    )
    search_fields = ('title', 'author',)
    list_filter = ('author', 'title')


@admin.register(Comment)
class CommenttAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'text',
        'author',
        'pub_date'
    )
    search_fields = ('review', 'author',)
    list_filter = ('pub_date', 'review')


@admin.register(User)
class UsertAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'bio',
        'role',
        'email',
    )
    search_fields = ('username', 'email',)
    list_filter = ('role',)
    list_editable = (
        'role',
    )


admin.site.empty_value_display = 'Not specified'
admin.site.unregister(auth.models.Group)
admin.site.unregister(DRFToken)
