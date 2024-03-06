from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    SignUpView,
    TitleViewSet,
    TokenView,
    UserProfileView,
    UsersViewSet
)

API_VERSION = 'v1/'

app_name = 'api'

router = SimpleRouter()

router.register('categories', CategoryViewSet, basename='сategories')
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')
router.register(r'users', UsersViewSet, basename='users')


urlpatterns = [
    path(API_VERSION, include(router.urls)),
    path(API_VERSION + 'auth/signup/', SignUpView.as_view(), name='signup'),
    path(API_VERSION + 'auth/token/', TokenView.as_view(), name='token_obtain'),
    path(API_VERSION + 'users/me/', UserProfileView.as_view(), name='user_profile'),
    path(API_VERSION, include(router.urls))
]
