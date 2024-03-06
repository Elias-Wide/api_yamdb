from rest_framework import routers
from django.urls import path, include

from api.views import SignUpView, TokenView, UserProfileView, UsersViewSet


API_VERSION = 'v1/'


router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')


urlpatterns = [
    path(API_VERSION, include(router.urls)),
    path(API_VERSION + 'auth/signup/', SignUpView.as_view(), name='signup'),
    path(API_VERSION + 'auth/token/', TokenView.as_view(), name='token_obtain'),
    path(API_VERSION + 'users/me/', UserProfileView.as_view(), name='user_profile') 
]

