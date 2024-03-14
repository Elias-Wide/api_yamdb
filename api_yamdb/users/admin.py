from django.contrib import admin

from users.models import User
from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
admin.site.register(Review)
admin.site.register(Comment)
