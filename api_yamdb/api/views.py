from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, views, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api import serializers
from api.mixins import (
    CategoryGenreMixin,
    PutNotAllowedMixin,
    ReviewCommentMixin
)
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
)
from api.filters import TitleFilter
from reviews.models import Category, Genre, Review, Title
from users.models import User


class TitleViewSet(PutNotAllowedMixin, viewsets.ModelViewSet):
    queryset = Title.objects.annotate(title_rating=Avg(
        'reviews__score'
    )).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleCreateSerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomTokenObtainPairSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access = AccessToken.for_user(user)
        user.confirmation_code = None
        user.save()
        return Response({'token': str(access)})


class UserProfileView(views.APIView):

    def get_user(self):
        return self.request.user

    def get(self, request, format=None):
        serializer = serializers.UserProfileSerializer(self.get_user())
        return Response(serializer.data)

    def patch(self, request, format=None):
        instance = self.get_user()
        serializer = serializers.UserProfileSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UsersViewSet(PutNotAllowedMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UsersSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'


class ReviewViewSet(ReviewCommentMixin):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_db_object(Title, self.kwargs['title_id'])
        )


class CommentViewSet(ReviewCommentMixin):
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        review = self.get_db_object(
            Review,
            self.kwargs['review_id'],
            title=self.kwargs['title_id']
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_db_object(
            Review,
            self.kwargs['review_id'],
            title=self.kwargs['title_id']
        )
        serializer.save(author=self.request.user, review=review)
