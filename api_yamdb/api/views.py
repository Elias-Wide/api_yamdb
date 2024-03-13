from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
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
from reviews.models import Category, CustomUser, Genre, Review, Title


class TitleViewSet(PutNotAllowedMixin, viewsets.ModelViewSet):
    queryset = Title.objects.all()
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomTokenObtainPairSerializer(
            data=request.data
        )
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            user = CustomUser.objects.get(username=username)
            refresh = AccessToken.for_user(user)
            user.confirmation_code = None
            user.save()
            return Response(
                {
                    'token': str(refresh)
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(PutNotAllowedMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UsersSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'


class ReviewViewSet(ReviewCommentMixin):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer

    def perform_create(self, serializer):
        self.add_title_rating(serializer.validated_data['score'])
        serializer.save(
            author=self.request.user,
            title=self.get_db_object(Title, self.kwargs['title_id'])
        )

    def add_title_rating(self, score):
        title = Title.objects.get(id=self.kwargs['title_id'])
        if title.rating is None:
            title.rating = score
            title.save()
        all_scores = [
            review.score for review in Review.objects.filter(title=title)
        ]
        title.rating = (sum(all_scores) + score) / (len(all_scores) + 1)
        title.save()


class CommentViewSet(ReviewCommentMixin):
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        review = self.get_db_object(Review, self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_db_object(Review, self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
