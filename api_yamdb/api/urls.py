from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet)

API_VERSION = 'v1/'

app_name = 'api'

router = SimpleRouter()

router.register('categories', CategoryViewSet, basename='сategories')
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path(API_VERSION, include(router.urls))
]
