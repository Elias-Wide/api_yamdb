from django.urls import path

from api.views import SignUpView, TokenView, UserProfileView


API_VERSION = 'v1/'


urlpatterns = [
    path(API_VERSION + 'auth/signup/', SignUpView.as_view(), name='signup'),
    path(API_VERSION + 'auth/token/', TokenView.as_view(), name='token_obtain'),
    path(API_VERSION + 'users/me/', UserProfileView.as_view(), name='user_profile') 
]

