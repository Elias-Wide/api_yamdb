from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets, generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAdminOrModeratorOrAuthor,
    IsAuthenticated
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateSerializer,
    TitleReadSerializer,
    SignUpSerializer,
    GetTokenSerializer,
    UsersSerializer,
    UserProfileSerializer
)
from reviews.models import (
    Category,
    Comment,
    CustomUser,
    Genre,
    Review,
    Title
)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleCreateSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def resolve_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class GenreViewSet(CreateModelMixin, ListModelMixin,
                   DestroyModelMixin, GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignUpView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            confirmation_code = serializer.validated_data.get('confirmation_code')
            user = CustomUser.objects.filter(
                username=username, confirmation_code=confirmation_code).first()
            if user:
                refresh = RefreshToken.for_user(user)
                user.confirmation_code = None
                user.save()
                return Response(
                    {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    },
                    status=status.HTTP_200_OK)
            return Response(
                {'error': 'Invalid username or verification code'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get(self, request, format=None):
        serializer = UserProfileSerializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request, format=None):
        instance = self.get_object()
        serializer = UserProfileSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title_id=self.get_title(self.kwargs['title_id'])
        )

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        elif self.action in ['partial_update', 'destroy']:
            return (IsAdminOrModeratorOrAuthor(),)
        return (permissions.AllowAny(),)

    @staticmethod
    def get_title(title_id):
        return get_object_or_404(Title, id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = self.get_review(self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review(self.kwargs['review_id'])
        serializer.save(author=self.request.user, review_id=review)

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        elif self.action in ['partial_update', 'destroy']:
            return (IsAdminOrModeratorOrAuthor(),)
        return (permissions.AllowAny(),)

    @staticmethod
    def get_review(review_id):
        return get_object_or_404(Review, id=review_id)
