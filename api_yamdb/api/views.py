from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from reviews.models import Category, Genre, Title
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleCreateSerializer, TitleReadSerializer)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleCreateSerializer

    def resolve_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class GenreViewSet(CreateModelMixin, ListModelMixin,
                   DestroyModelMixin, GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
