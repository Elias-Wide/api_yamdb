from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets, generics, permissions
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAdminOrModeratorOrAuthor,
    IsAuthorOrReadOnly,
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
    CustomTokenObtainPairSerializer,
    UsersSerializer,
    UserProfileSerializer
)
from reviews.models import (
    Category,
    CustomUser,
    Genre,
    Review,
    Title
)

from rest_framework_simplejwt.views import TokenObtainPairView


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
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
    lookup_field = 'slug'


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class SignUpView(TokenObtainPairView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.filter('username').first()
            user = CustomUser.objects.get(username=username)
            refresh = AccessToken.for_user(user)
            user.confirmation_code = None
            user.save()
            return Response(
                {
                    'token': str(refresh.access_token)
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class TokenView(views.APIView):
#     permission_classes = (permissions.AllowAny,)
#     def post(self, request, *args, **kwargs):
#         serializer = GetTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data.get('username')
#             confirmation_code = serializer.validated_data.get('confirmation_code')
#             user = CustomUser.objects.get(username=username)
#             if not user:
#                 return Response(
#                     {'error': 'Invalid username'},
#                     status=status.HTTP_404_NOT_FOUND)
#             if user.confirmation_code != confirmation_code:
#                 return Response(
#                     {'error': 'Invalid username'},
#                     status=status.HTTP_400_BAD_REQUEST)
#             refresh = RefreshToken.for_user(user)
#             user.confirmation_code = None
#             user.save()
#             return Response(
#                 {
#                     'token': str(refresh.access_token)
#                 },
#                 status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get_user(self):
        return self.request.user

    def get(self, request, format=None):
        serializer = UserProfileSerializer(self.get_user())
        return Response(serializer.data)

    def patch(self, request, format=None):
        instance = self.get_user()
        serializer = UserProfileSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username', )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        self.add_title_rating(serializer.validated_data['score'])
        serializer.save(
            author=self.request.user,
            title=self.get_title(self.kwargs['title_id'])
        )

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        elif self.action in ['partial_update', 'destroy']:
            return (IsAdminOrModeratorOrAuthor(),)
        return (permissions.AllowAny(),)

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
        serializer.save(author=self.request.user, review=review)

    def get_permissions(self):
        if self.request.method == 'POST':
            return (IsAuthenticated(),)
        if self.action == 'create':
            return (IsAuthorOrReadOnly(),)
        elif self.action in ['partial_update', 'destroy']:
            return (IsAdminOrModeratorOrAuthor(),)
        return (permissions.AllowAny(),)

    @staticmethod
    def get_review(review_id):
        return get_object_or_404(Review, id=review_id)
